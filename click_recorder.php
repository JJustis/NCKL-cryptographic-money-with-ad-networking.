<?php
/**
 * Single place where ad clicks and impressions are recorded.
 *
 *  - ad_clicks     : REAL, paid-for clicks only. Every row carries what the Qt payment step reads (developer_id,
 *                    developer_address, payout_amount, processed = 0, payment_status = 'pending') plus who was charged.
 *  - ad_impressions: ad views. They never go into ad_clicks.
 *
 * The payout is decided here from the ad's own record on the server; a value sent by the browser is ignored. The ad
 * must be real, active and approved, its advertiser must have funds and budget left (economy.php), the visitor must
 * look like a person and stay inside the click limits, and the advertiser cannot earn from its own ad.
 */
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/curl_polyfill.php';   // Apache's PHP currently lacks the curl extension
require_once __DIR__ . '/economy.php';

if (!defined('CLK_DEFAULT_PAYOUT')) define('CLK_DEFAULT_PAYOUT', 0.001);
if (!defined('CLK_MAX_PAYOUT'))     define('CLK_MAX_PAYOUT', 0.1);   // same ceiling as the Qt app's auto-payment limit

/** Find the developer (publisher) by wallet address and/or username. Returns the row or null. */
function clk_find_developer(PDO $pdo, $address = '', $username = '') {
    if (is_string($address) && $address !== '') {
        $st = $pdo->prepare("SELECT id, username, pythoncoin_address FROM developers WHERE pythoncoin_address = ? LIMIT 1");
        $st->execute([$address]);
        if ($row = $st->fetch(PDO::FETCH_ASSOC)) return $row;
    }
    if (is_string($username) && $username !== '') {
        $st = $pdo->prepare("SELECT id, username, pythoncoin_address FROM developers WHERE username = ? LIMIT 1");
        $st->execute([$username]);
        if ($row = $st->fetch(PDO::FETCH_ASSOC)) return $row;
    }
    return null;
}

/** Turn a node's /ads entry or a meta.json into the common shape used for money decisions. */
function clk_normalise_ad(array $a, $adId) {
    $rate = $a['payout_amount'] ?? ($a['payout_rate'] ?? ($a['payout'] ?? CLK_DEFAULT_PAYOUT));
    return [
        'id' => $adId,
        'payout' => (float)$rate,
        'advertiser' => (string)($a['advertiser_address'] ?? ($a['advertiser'] ?? '')),
        'daily_budget' => $a['targeting']['budget_daily'] ?? ($a['daily_budget'] ?? null),
        'max_clicks' => $a['targeting']['max_clicks_daily'] ?? ($a['max_clicks_daily'] ?? null),
    ];
}

/**
 * Ask the advertiser's own node what an ad is. Publishers choose which advertiser nodes feed their embed, so a click
 * can be for an ad that lives on that node and nowhere on this server. The node must be a registered, recently seen
 * client and a safe address (no loopback / link-local); its answer is cached for 60 seconds.
 * Returns the normalised ad, or null if the node is unknown/unreachable or does not list that ad.
 */
function clk_peer_ad(PDO $pdo, $clientId, $adId) {
    if (!sec_safe_id($clientId, 100)) return null;
    $st = $pdo->prepare("SELECT host, port FROM p2p_clients WHERE client_id = ? AND status = 'online'
                          AND last_seen > DATE_SUB(NOW(), INTERVAL 1 DAY) ORDER BY last_seen DESC LIMIT 1");
    $st->execute([$clientId]);
    $node = $st->fetch(PDO::FETCH_ASSOC);
    if (!$node || !sec_valid_host($node['host']) || !sec_valid_port($node['port'])) return null;

    $dir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'pyc_peerads';
    if (!is_dir($dir)) @mkdir($dir, 0700, true);
    $cache = $dir . DIRECTORY_SEPARATOR . hash('sha256', $clientId . '|' . $node['host'] . '|' . $node['port']) . '.json';
    $ads = null;
    if (is_file($cache) && filemtime($cache) > time() - 60) {
        $ads = json_decode((string)file_get_contents($cache), true);
    }
    if (!is_array($ads)) {
        $ch = curl_init("http://{$node['host']}:{$node['port']}/ads");
        curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 3, CURLOPT_CONNECTTIMEOUT => 2,
                                CURLOPT_FOLLOWLOCATION => false, CURLOPT_HTTPHEADER => ['Accept: application/json']]);
        $body = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        $decoded = ($code === 200 && $body) ? json_decode($body, true) : null;
        $ads = (is_array($decoded) && isset($decoded['ads']) && is_array($decoded['ads'])) ? $decoded['ads'] : null;
        if ($ads === null) return null;
        @file_put_contents($cache, json_encode($ads));
    }
    foreach ($ads as $ad) {
        if (!is_array($ad)) continue;
        if ((string)($ad['id'] ?? $ad['ad_id'] ?? '') === $adId) {
            if (($ad['status'] ?? 'active') !== 'active') return null;
            return clk_normalise_ad($ad, $adId);
        }
    }
    return null;
}

/**
 * Everything the server knows about an ad, from its own records: advertiser, price, budget, limits.
 * Looks at this site's ad storage first, then the advertiser's chosen node, then registered peer ads.
 * Returns the normalised ad array, or null if the ad is missing, inactive or expired.
 */
function clk_ad_info(PDO $pdo, $adId, $clientId = '') {
    if (!sec_safe_id($adId, 100)) return null;

    $meta = __DIR__ . '/ads_storage/active/' . $adId . '_meta.json';   // adId is validated: no path separators
    if (is_file($meta)) {
        $m = json_decode((string)file_get_contents($meta), true);
        if (is_array($m)) {
            $active  = !isset($m['status']) || $m['status'] === 'active';
            $expired = !empty($m['expires_at']) && strtotime($m['expires_at']) !== false && strtotime($m['expires_at']) < time();
            return ($active && !$expired) ? clk_normalise_ad($m, $adId) : null;
        }
    }
    if ($clientId !== '' && $clientId !== 'storage') {
        $peer = clk_peer_ad($pdo, $clientId, $adId);
        if ($peer !== null) return $peer;
    }
    try {
        $st = $pdo->prepare("SELECT payout_rate FROM client_ads WHERE ad_id = ? AND active = 1 ORDER BY id DESC LIMIT 1");
        $st->execute([$adId]);
        if (($r = $st->fetchColumn()) !== false) return clk_normalise_ad(['payout_rate' => $r], $adId);   // no advertiser known
    } catch (PDOException $e) { /* table or column missing */ }
    try {
        $st = $pdo->prepare("SELECT payout_amount, advertiser_address FROM ads_cache WHERE ad_id = ? AND is_active = 1 LIMIT 1");
        $st->execute([$adId]);
        if ($r = $st->fetch(PDO::FETCH_ASSOC)) return clk_normalise_ad($r, $adId);
    } catch (PDOException $e) { }
    return null;
}

/** Kept for older callers and tests: [known, payout]. */
function clk_ad_payout(PDO $pdo, $adId, $clientId = '') {
    $info = clk_ad_info($pdo, $adId, $clientId);
    return $info ? [true, $info['payout']] : [false, 0.0];
}

/** Claim a page-load id (first come, first served). False if a click was already paid for that page load. */
function clk_claim_page_load(PDO $pdo, $loadId) {
    $pdo->exec("CREATE TABLE IF NOT EXISTS click_page_loads (load_id VARCHAR(64) NOT NULL PRIMARY KEY, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, KEY idx_created (created_at)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    if (mt_rand(1, 100) === 1) $pdo->exec("DELETE FROM click_page_loads WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 DAY)");
    $st = $pdo->prepare("INSERT IGNORE INTO click_page_loads (load_id) VALUES (?)");
    $st->execute([$loadId]);
    return $st->rowCount() === 1;
}

function clk_release_page_load(PDO $pdo, $loadId) {
    $pdo->prepare("DELETE FROM click_page_loads WHERE load_id = ?")->execute([$loadId]);
}

/**
 * Record one real click.
 * $in: ad_id, client_id, zone, embed_id and either developer_address or developer_username.
 * Returns ['ok' => bool, 'id' => int|null, 'amount' => float, 'error' => string].
 */
function clk_record_click(PDO $pdo, array $in, $status = 'pending') {
    $fail = function ($msg) { return ['ok' => false, 'id' => null, 'amount' => 0.0, 'error' => $msg]; };
    $cfg = econ_settings();

    $adId     = (string)($in['ad_id'] ?? '');
    $clientId = (string)($in['client_id'] ?? '');
    $embedId  = (string)($in['embed_id'] ?? '');
    $zone     = mb_substr(strip_tags((string)($in['zone'] ?? '')), 0, 50);
    $ip       = $_SERVER['REMOTE_ADDR'] ?? '';
    $agent    = mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 255);
    $loadId   = (string)($in['load_id'] ?? '');
    $onePerLoad = !isset($cfg['one_click_per_page_load']) || !empty($cfg['one_click_per_page_load']);

    if (!sec_safe_id($adId, 100))                         return $fail('Invalid ad');
    if ($onePerLoad && !preg_match('/^[A-Za-z0-9_-]{16,64}$/', $loadId)) return $fail('Missing page-load id (regenerate the embed code)');
    if ($clientId !== '' && !sec_safe_id($clientId, 100)) return $fail('Invalid client');
    if ($embedId !== '' && !sec_safe_id($embedId, 100))   return $fail('Invalid embed');
    if (econ_is_bot_agent($agent))                        return $fail('Clicks from automated clients are not paid');

    $dev = clk_find_developer($pdo, (string)($in['developer_address'] ?? ''), (string)($in['developer_username'] ?? ''));
    if (!$dev || (string)$dev['pythoncoin_address'] === '') return $fail('Developer not identified');

    $ad = clk_ad_info($pdo, $adId, $clientId);
    if ($ad === null)                                     return $fail('Unknown or inactive ad');
    if (econ_approval_status($pdo, $adId) !== 'approved') return $fail('Ad is not approved');
    if ($ad['advertiser'] === '')                         return $fail('Ad has no advertiser account');
    // An advertiser cannot earn from its own ad. The click is still counted (statistics only): never charged, never paid.
    $selfClick = empty($cfg['allow_self_clicks']) && $ad['advertiser'] === $dev['pythoncoin_address'];

    $amount = round(min(max($ad['payout'], 0.0), CLK_MAX_PAYOUT), 8);
    if ($amount <= 0)                                     return $fail('Ad pays nothing');
    $payoutSat = econ_sat($amount);

    // Visitor limits: per minute (burst), per ad per day, and per day overall
    if (!sec_rate_limit('clk_all', 60, 60) || !sec_rate_limit('clk_' . $adId . '_' . $dev['id'], 1, 30)) {
        return $fail('Too many clicks');
    }
    if ($ip !== '') {
        $st = $pdo->prepare("SELECT COUNT(*) FROM ad_clicks WHERE ip_address = ? AND click_time >= CURDATE() AND payment_status NOT IN ('rejected', 'self')");
        $st->execute([$ip]);
        if ((int)$st->fetchColumn() >= (int)$cfg['max_clicks_per_ip_per_day']) return $fail('Daily click limit for this visitor reached');
        $st = $pdo->prepare("SELECT COUNT(*) FROM ad_clicks WHERE ip_address = ? AND ad_id = ? AND click_time >= CURDATE() AND payment_status NOT IN ('rejected', 'self')");
        $st->execute([$ip, $adId]);
        if ((int)$st->fetchColumn() >= (int)$cfg['max_clicks_per_ip_per_ad_per_day']) return $fail('Daily click limit for this ad reached');
    }

    if ($selfClick) {
        if ($onePerLoad && !clk_claim_page_load($pdo, $loadId)) return $fail('Only one click is counted per page load');
        $selfRow = [
            'username' => $dev['username'], 'ad_id' => $adId, 'embed_id' => $embedId !== '' ? $embedId : null,
            'client_id' => $clientId, 'zone' => $zone, 'ip_address' => $ip, 'user_agent' => $agent,
            'referer' => mb_substr((string)($_SERVER['HTTP_REFERER'] ?? ''), 0, 500),
            'pyc_earned' => 0, 'payment_processed' => 1, 'developer_id' => $dev['id'], 'payout_amount' => 0, 'processed' => 1,
            'payment_status' => 'self', 'developer_name' => $dev['username'], 'developer_address' => $dev['pythoncoin_address'],
            'advertiser_address' => $ad['advertiser'], 'charged_sat' => 0,
            'metadata' => json_encode(['source' => 'web', 'self_click' => true, 'recorded_at' => date('c')]),
        ];
        $cols = array_keys($selfRow);
        $pdo->prepare("INSERT INTO ad_clicks (" . implode(',', $cols) . ") VALUES (" . implode(',', array_fill(0, count($cols), '?')) . ")")
            ->execute(array_values($selfRow));
        return ['ok' => true, 'id' => (int)$pdo->lastInsertId(), 'amount' => 0.0, 'error' => '', 'developer' => $dev, 'self' => true];
    }

    $row = [
        'username' => $dev['username'], 'ad_id' => $adId, 'embed_id' => $embedId !== '' ? $embedId : null,
        'client_id' => $clientId, 'zone' => $zone, 'ip_address' => $ip, 'user_agent' => $agent,
        'referer' => mb_substr((string)($_SERVER['HTTP_REFERER'] ?? ''), 0, 500),
        'pyc_earned' => $amount, 'payment_processed' => 0,
        'developer_id' => $dev['id'], 'payout_amount' => $amount, 'processed' => 0, 'payment_status' => $status,
        'developer_name' => $dev['username'], 'developer_address' => $dev['pythoncoin_address'],
        'metadata' => json_encode(['source' => 'web', 'recorded_at' => date('c')]),
    ];
    // one click per page load: the page-load id is claimed first and given back if the click is then refused
    if ($onePerLoad && !clk_claim_page_load($pdo, $loadId)) return $fail('Only one click is paid per page load');
    $res = econ_charge_and_insert($pdo, $ad['advertiser'], $adId, $payoutSat,
                                  ['max_clicks' => $ad['max_clicks'], 'daily_budget' => $ad['daily_budget']], $row);
    if (!$res['ok']) {
        if ($onePerLoad) clk_release_page_load($pdo, $loadId);
        return $fail($res['error']);
    }
    return ['ok' => true, 'id' => $res['id'], 'amount' => $amount, 'error' => '', 'developer' => $dev];
}

/** Record an ad view in ad_impressions (never in ad_clicks). Returns true on success. */
function clk_record_impression(PDO $pdo, array $in) {
    $adId     = (string)($in['ad_id'] ?? '');
    $clientId = (string)($in['client_id'] ?? '');
    $embedId  = (string)($in['embed_id'] ?? '');
    if (!sec_safe_id($adId, 100)) return false;
    if ($clientId !== '' && !sec_safe_id($clientId, 100)) return false;
    if ($embedId !== '' && !sec_safe_id($embedId, 100)) $embedId = '';
    if (!sec_rate_limit('imp_all', 600, 60)) return false;

    $dev = clk_find_developer($pdo, (string)($in['developer_address'] ?? ''), (string)($in['developer_username'] ?? ''));
    $st = $pdo->prepare(
        "INSERT INTO ad_impressions (developer_id, ad_id, client_id, embed_id, zone, ip_address, user_agent)
         VALUES (?, ?, ?, ?, ?, ?, ?)"
    );
    return $st->execute([
        $dev ? $dev['id'] : null, $adId, $clientId !== '' ? $clientId : null, $embedId !== '' ? $embedId : null,
        mb_substr(strip_tags((string)($in['zone'] ?? '')), 0, 50),
        $_SERVER['REMOTE_ADDR'] ?? '', mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 255),
    ]);
}
