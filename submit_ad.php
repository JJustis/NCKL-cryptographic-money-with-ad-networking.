<?php
/**
 * Advertisers push their ads to the network server (so the server never has to reach into anyone's home network).
 *
 * POST JSON: {"payload": "<JSON text>", "public_key": "<128 hex: x||y>", "signature": "<128 hex: r||s>"}
 *   payload = {"ts": unix seconds, "nonce": "...", "ad": {id, title, description, category, click_url, payout_amount,
 *              advertiser_address, expires_at, targeting{budget_daily,max_clicks_daily}, format,
 *              content{svg|html|text|image_b64}}}
 *
 * The signature is the advertiser's wallet key signing SHA-256(payload text). The address derived from that key must be
 * the ad's advertiser_address, so nobody can submit ads in someone else's name. Accepted ads wait in ads_storage/pending
 * until a person approves them (ads_admin.py approve <id>). Re-submitting an ad takes it out of service again until it
 * is re-approved, so approved content cannot be swapped for something else.
 */
require_once __DIR__ . '/security.php';
require_once __DIR__ . '/economy.php';
require_once __DIR__ . '/click_recorder.php';
require_once __DIR__ . '/agreements.php';
require_once __DIR__ . '/btcshop_bridge.php';

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') exit;

/** What a submitter must do first: accept the current terms and (usually) pay the upload fee. */
function sad_requirements() {
    $terms = agr_current_terms();
    $fee = bridge_fee_info();
    $site = pyc_site();
    return ['terms_version' => $terms['version'], 'terms_url' => rtrim($site['base_url'] ?? '', '/') . '/advertiser_terms.php',
            'fee_required' => $fee['required'], 'fee_btc' => $fee['btc'], 'shop_url' => $fee['shop_url'], 'shop_product' => $fee['product'],
            'coin_name' => agr_coin()['coin_name']];
}
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'GET' && isset($_GET['info'])) { echo json_encode(['success' => true] + sad_requirements()); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') sec_fail(405, 'POST only');

// ---------------------------------------------------------------------------------------------------- crypto helpers
function sad_address_version() {
    static $v = null;
    if ($v === null) {
        $v = 0;
        $f = __DIR__ . '/consensus_params.json';
        if (is_file($f)) { $j = json_decode((string)file_get_contents($f), true); if (isset($j['address_version'])) $v = (int)$j['address_version']; }
    }
    return $v;
}

function sad_base58(string $bytes): string {
    $alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    $digits = array_values(unpack('C*', $bytes));
    $zeros = 0; while ($zeros < count($digits) && $digits[$zeros] === 0) $zeros++;
    $out = '';
    $num = $digits;
    while (count($num) > 0) {                       // repeated division of the big number by 58
        $rem = 0; $next = [];
        foreach ($num as $d) {
            $acc = $rem * 256 + $d;
            $q = intdiv($acc, 58); $rem = $acc % 58;
            if ($next || $q) $next[] = $q;
        }
        $out = $alphabet[$rem] . $out;
        $num = $next;
    }
    return str_repeat('1', $zeros) . $out;
}

function sad_pubkey_to_address(string $pubHex): string {
    $pub = hex2bin($pubHex);
    $h = hash('ripemd160', hash('sha256', $pub, true), true);
    $payload = chr(sad_address_version()) . $h;
    return sad_base58($payload . substr(hash('sha256', hash('sha256', $payload, true), true), 0, 4));
}

function sad_der_int(string $b): string {
    $b = ltrim($b, "\0");
    if ($b === '' || ord($b[0]) & 0x80) $b = "\0" . $b;
    return "\x02" . chr(strlen($b)) . $b;
}

/** Verify a python-ecdsa signature (raw r||s over SHA1(SHA256(message))) with PHP's OpenSSL. */
function sad_verify(string $pubHex, string $message, string $sigHex): bool {
    if (!preg_match('/^[0-9a-f]{128}$/i', $pubHex) || !preg_match('/^[0-9a-f]{128}$/i', $sigHex)) return false;
    $spki = hex2bin('3056301006072a8648ce3d020106052b8104000a034200') . "\x04" . hex2bin($pubHex);
    $pem = "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($spki), 64, "\n") . "-----END PUBLIC KEY-----\n";
    $raw = hex2bin($sigHex);
    $body = sad_der_int(substr($raw, 0, 32)) . sad_der_int(substr($raw, 32, 32));
    $der = "\x30" . chr(strlen($body)) . $body;
    return openssl_verify(hash('sha256', $message, true), $der, $pem, OPENSSL_ALGO_SHA1) === 1;
}

// ---------------------------------------------------------------------------------------------------- request
if (!sec_rate_limit('submit_ad', 20, 3600)) sec_fail(429, 'Too many submissions, try again later');
$body = file_get_contents('php://input');
if (strlen($body) > 600000) sec_fail(413, 'Submission too large');
$req = json_decode($body, true);
if (!is_array($req) || !is_string($req['payload'] ?? null) || !is_string($req['public_key'] ?? null) || !is_string($req['signature'] ?? null)) {
    sec_fail(400, 'Malformed submission');
}
if (!sad_verify($req['public_key'], $req['payload'], $req['signature'])) sec_fail(401, 'Signature does not verify');

$payload = json_decode($req['payload'], true);
if (!is_array($payload) || !is_array($payload['ad'] ?? null)) sec_fail(400, 'Malformed payload');
if (abs(time() - (int)($payload['ts'] ?? 0)) > 300) sec_fail(400, 'Submission is stale');
$nonce = (string)($payload['nonce'] ?? '');
if (!preg_match('/^[A-Za-z0-9_-]{16,64}$/', $nonce)) sec_fail(400, 'Bad nonce');
$nonceDir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'pyc_ad_nonces';
if (!is_dir($nonceDir)) @mkdir($nonceDir, 0700, true);
$nf = $nonceDir . DIRECTORY_SEPARATOR . hash('sha256', $nonce);
$h = @fopen($nf, 'x');
if (!$h) sec_fail(400, 'Submission was already used');
fclose($h);

$ad = $payload['ad'];
$id = (string)($ad['id'] ?? '');
if (!sec_safe_id($id, 100)) sec_fail(400, 'Invalid ad id');
$advertiser = (string)($ad['advertiser_address'] ?? '');
if ($advertiser === '' || sad_pubkey_to_address($req['public_key']) !== $advertiser) {
    sec_fail(403, 'The signing key does not belong to the advertiser address');
}

// the advertiser must have accepted the CURRENT agreement
$terms = agr_current_terms();
require_once __DIR__ . '/dbconfig.php';
$pdo = pyc_pdo();
if ((int)($payload['terms_version'] ?? 0) !== (int)$terms['version'] || !agr_has_accepted($pdo, $advertiser, $terms['version'])) {
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'You must accept the current advertiser agreement (version ' . $terms['version'] . ') for this wallet address first',
                      'requirements' => sad_requirements()]);
    exit;
}

$click = (string)($ad['click_url'] ?? '');
if (!sec_valid_url($click)) sec_fail(400, 'click_url must be an http(s) address');
$title = mb_substr(trim(strip_tags((string)($ad['title'] ?? ''))), 0, 100);
if ($title === '') sec_fail(400, 'An ad needs a title');
$payout = (float)($ad['payout_amount'] ?? 0);
if ($payout <= 0 || $payout > CLK_MAX_PAYOUT) sec_fail(400, 'payout_amount must be above 0 and at most ' . CLK_MAX_PAYOUT);
if (empty($ad['expires_at']) || strtotime($ad['expires_at']) === false || strtotime($ad['expires_at']) < time()) sec_fail(400, 'expires_at must be in the future');
$budget = isset($ad['targeting']['budget_daily']) ? (float)$ad['targeting']['budget_daily'] : null;
$maxClicks = isset($ad['targeting']['max_clicks_daily']) ? (int)$ad['targeting']['max_clicks_daily'] : null;

// the ad id belongs to whoever submitted it first
$pendingDir = __DIR__ . '/ads_storage/pending';
$activeDir = __DIR__ . '/ads_storage/active';
foreach ([$pendingDir, $activeDir] as $dir) {
    $existing = $dir . '/' . $id . '_meta.json';
    if (is_file($existing)) {
        $m = json_decode((string)file_get_contents($existing), true);
        if (is_array($m) && ($m['advertiser_address'] ?? '') !== $advertiser) sec_fail(403, 'That ad id belongs to another advertiser');
    }
}

// content: exactly one of svg / html / text / image
$content = is_array($ad['content'] ?? null) ? $ad['content'] : [];
$files = [];
if (isset($content['svg'])) {
    if (!is_string($content['svg']) || strlen($content['svg']) > 200000 || stripos($content['svg'], '<svg') === false) sec_fail(400, 'Invalid svg');
    $files[$id . '_svg.svg'] = $content['svg']; $format = 'svg';
} elseif (isset($content['html'])) {
    if (!is_string($content['html']) || strlen($content['html']) > 200000) sec_fail(400, 'Invalid html');
    $files[$id . '_html.html'] = $content['html']; $format = 'html';
} elseif (isset($content['text'])) {
    if (!is_string($content['text']) || strlen($content['text']) > 2000) sec_fail(400, 'Invalid text');
    $files[$id . '_text.txt'] = $content['text']; $format = 'text';
} elseif (isset($content['image_b64'])) {
    $img = base64_decode((string)$content['image_b64'], true);
    if ($img === false || strlen($img) > 300000) sec_fail(400, 'Invalid image');
    $ext = null;
    if (strncmp($img, "\x89PNG\r\n\x1a\n", 8) === 0) $ext = 'png';
    elseif (strncmp($img, "\xff\xd8\xff", 3) === 0) $ext = 'jpg';
    elseif (strncmp($img, 'GIF8', 4) === 0) $ext = 'gif';
    elseif (strncmp($img, 'RIFF', 4) === 0 && substr($img, 8, 4) === 'WEBP') $ext = 'webp';
    if ($ext === null) sec_fail(400, 'Images must be png, jpeg, gif or webp');
    $files[$id . '_image.' . $ext] = $img; $format = 'picture';
} else {
    sec_fail(400, 'An ad needs content (svg, html, text or image_b64)');
}

// everything checked out: use up the paid upload order (one payment per submission)
$feeOrder = null;
if (bridge_fee_info()['required']) {
    $fee = is_array($payload['fee'] ?? null) ? $payload['fee'] : [];
    [$paid, $why] = bridge_consume_fee($fee['order'] ?? null, $fee['sec'] ?? null, $id);
    if (!$paid) {
        http_response_code(402);
        echo json_encode(['success' => false, 'error' => 'Upload fee: ' . $why, 'requirements' => sad_requirements()]);
        exit;
    }
    $feeOrder = (int)$fee['order'];
}
if (!is_dir($pendingDir) && !@mkdir($pendingDir, 0755, true)) {
    if ($feeOrder !== null) bridge_release_fee($feeOrder);
    sec_fail(500, 'Cannot store the ad');
}
$meta = [
    'id' => $id, 'title' => $title, 'description' => mb_substr(trim(strip_tags((string)($ad['description'] ?? ''))), 0, 300),
    'category' => mb_substr(preg_replace('/[^A-Za-z0-9 _-]/', '', (string)($ad['category'] ?? 'general')), 0, 40),
    'click_url' => $click, 'target_url' => $click, 'payout_amount' => $payout, 'payout_rate' => $payout,
    'advertiser_address' => $advertiser, 'expires_at' => $ad['expires_at'], 'status' => 'pending',
    'format' => $format, 'ad_type' => $format, 'submitted_at' => date('c'),
    'targeting' => ['budget_daily' => $budget, 'max_clicks_daily' => $maxClicks],
];
// re-submission: whatever was approved before is taken out of service until the new content is approved
foreach (glob($activeDir . '/' . $id . '_*') ?: [] as $old) @unlink($old);
foreach (glob($pendingDir . '/' . $id . '_*') ?: [] as $old) @unlink($old);
foreach ($files as $name => $data) file_put_contents($pendingDir . '/' . $name, $data);
file_put_contents($pendingDir . '/' . $id . '_meta.json', json_encode($meta, JSON_PRETTY_PRINT));

try {
    $pdo->prepare("INSERT INTO ad_approvals (ad_id, status, note) VALUES (?, 'pending', 'submitted by advertiser') ON DUPLICATE KEY UPDATE status = 'pending', reviewed_at = NULL, note = 'resubmitted'")
        ->execute([$id]);
} catch (Throwable $e) {
    if ($feeOrder !== null) bridge_release_fee($feeOrder);
    error_log('submit_ad: ' . $e->getMessage());
    sec_fail(500, 'Cannot store the ad');
}

echo json_encode(['success' => true, 'ad_id' => $id, 'status' => 'pending_review', 'advertiser' => $advertiser,
                  'message' => 'Received. The ad is served once it has been approved and the advertiser account has funds.']);
