<?php
/**
 * The money rules of the ad network, kept in one place.
 *
 *  - Advertisers fund an account by sending coins to the network wallet (see economy.py, which credits confirmed
 *    deposits). Each click is charged to that account the moment it is recorded, and the ad stops when the funds,
 *    the daily budget or the daily click limit run out.
 *  - Nothing is served or paid for until a person has approved the ad (ad_approvals).
 *  - A click is not payable straight away: it is held for click_hold_minutes so fraud can be caught first.
 *  - An advertiser cannot earn from its own ad, and a visitor's clicks are capped per ad and per day.
 *
 * All amounts are whole base units ("sat": 1 coin = 100,000,000), never floats.
 */
require_once __DIR__ . '/security.php';

function econ_settings() {
    static $cfg = null;
    if ($cfg === null) {
        $cfg = [
            'network_fee_percent' => 0, 'click_hold_minutes' => 1440, 'max_clicks_per_ip_per_ad_per_day' => 3,
            'max_clicks_per_ip_per_day' => 20, 'allow_self_clicks' => false, 'deposit_confirmations' => 6,
            'retention_impression_days' => 30, 'retention_ip_days' => 90,
        ];
        $file = __DIR__ . '/economy.json';
        if (is_file($file)) {
            $json = json_decode((string)file_get_contents($file), true);
            if (is_array($json)) $cfg = array_merge($cfg, $json);
        }
    }
    return $cfg;
}

function econ_sat($amount) { return (int)round(((float)$amount) * 100000000); }

/** What the advertiser is charged for a click that pays the publisher $payoutSat (the network fee defaults to 0%: at cost). */
function econ_charge_sat($payoutSat, $feePercent = null) {
    $fee = $feePercent === null ? (float)econ_settings()['network_fee_percent'] : (float)$feePercent;
    return $payoutSat + (int)ceil($payoutSat * $fee / 100.0);
}

/** True for crawlers, scripts and empty user agents - their clicks are never paid. */
function econ_is_bot_agent($ua) {
    if (!is_string($ua) || strlen($ua) < 12) return true;
    return (bool)preg_match('~bot|crawl|spider|slurp|scrap|monitor|uptime|checker|probe|curl|wget|httpclient|http-client|python|java/|libwww|go-http|okhttp|axios|postman|headless|phantom|lighthouse|preview~i', $ua);
}

/** 'approved' | 'pending' | 'rejected'. An ad seen for the first time is recorded as pending for review. */
function econ_approval_status(PDO $pdo, $adId) {
    $st = $pdo->prepare("SELECT status FROM ad_approvals WHERE ad_id = ?");
    $st->execute([$adId]);
    $status = $st->fetchColumn();
    if ($status === false) {
        $pdo->prepare("INSERT IGNORE INTO ad_approvals (ad_id, status) VALUES (?, 'pending')")->execute([$adId]);
        return 'pending';
    }
    return $status;
}

function econ_balance_sat(PDO $pdo, $address) {
    $st = $pdo->prepare("SELECT balance_sat FROM advertiser_accounts WHERE address = ?");
    $st->execute([$address]);
    $v = $st->fetchColumn();
    return $v === false ? 0 : (int)$v;
}

/** Clicks and charges so far today for one ad (today = the database server's calendar day). */
function econ_today_for_ad(PDO $pdo, $adId) {
    $st = $pdo->prepare("SELECT COUNT(*), COALESCE(SUM(charged_sat), 0) FROM ad_clicks
                          WHERE ad_id = ? AND click_time >= CURDATE() AND payment_status <> 'rejected'");
    $st->execute([$adId]);
    [$n, $sum] = $st->fetch(PDO::FETCH_NUM);
    return [(int)$n, (int)$sum];
}

/**
 * Should this ad be shown to publishers right now?  Returns [bool, reason].
 * $ad: ['id', 'advertiser', 'payout' (coins), 'daily_budget' (coins|null), 'max_clicks' (int|null)]
 */
function econ_ad_serveable(PDO $pdo, array $ad) {
    $adId = (string)($ad['id'] ?? '');
    if ($adId === '' || !sec_safe_id($adId, 100)) return [false, 'invalid ad id'];
    if (econ_approval_status($pdo, $adId) !== 'approved') return [false, 'not approved'];
    $adv = (string)($ad['advertiser'] ?? '');
    if ($adv === '') return [false, 'no advertiser account'];
    $charge = econ_charge_sat(econ_sat($ad['payout'] ?? 0));
    if ($charge <= 0) return [false, 'pays nothing'];
    if (econ_balance_sat($pdo, $adv) < $charge) return [false, 'advertiser out of funds'];
    [$clicks, $spent] = econ_today_for_ad($pdo, $adId);
    if (!empty($ad['max_clicks']) && $clicks >= (int)$ad['max_clicks']) return [false, 'daily click limit reached'];
    if (isset($ad['daily_budget']) && $ad['daily_budget'] !== null && $spent + $charge > econ_sat($ad['daily_budget'])) {
        return [false, 'daily budget used up'];
    }
    return [true, 'ok'];
}

/** Keep only the ads that may be served. Unknown ads are queued for review. Order is preserved. */
function econ_filter_serveable(PDO $pdo, array $ads) {
    $out = [];
    foreach ($ads as $ad) {
        if (!is_array($ad)) continue;
        $info = [
            'id' => $ad['id'] ?? ($ad['ad_id'] ?? ''),
            'advertiser' => $ad['advertiser_address'] ?? ($ad['advertiser'] ?? ''),
            'payout' => $ad['payout_amount'] ?? ($ad['payout_rate'] ?? ($ad['payout'] ?? 0)),
            'daily_budget' => $ad['targeting']['budget_daily'] ?? ($ad['daily_budget'] ?? null),
            'max_clicks' => $ad['targeting']['max_clicks_daily'] ?? ($ad['max_clicks_daily'] ?? null),
        ];
        [$ok] = econ_ad_serveable($pdo, $info);
        if ($ok) $out[] = $ad;
    }
    return $out;
}

/**
 * Charge the advertiser and write the click row in ONE transaction, so a click can never be recorded without being
 * paid for, nor charged without being recorded.  Returns ['ok'=>bool, 'id'=>?int, 'error'=>string].
 * $row: the column => value map for ad_clicks (without charged_sat / payable_after / advertiser_address).
 */
function econ_charge_and_insert(PDO $pdo, $advertiser, $adId, $payoutSat, array $limits, array $row) {
    $cfg = econ_settings();
    $charge = econ_charge_sat($payoutSat);
    $pdo->beginTransaction();
    try {
        $st = $pdo->prepare("SELECT balance_sat FROM advertiser_accounts WHERE address = ? FOR UPDATE");
        $st->execute([$advertiser]);
        $balance = $st->fetchColumn();
        if ($balance === false || (int)$balance < $charge) {
            $pdo->rollBack();
            return ['ok' => false, 'id' => null, 'error' => 'Advertiser out of funds'];
        }
        [$clicks, $spent] = econ_today_for_ad($pdo, $adId);
        if (!empty($limits['max_clicks']) && $clicks >= (int)$limits['max_clicks']) {
            $pdo->rollBack();
            return ['ok' => false, 'id' => null, 'error' => 'Daily click limit reached'];
        }
        if (isset($limits['daily_budget']) && $limits['daily_budget'] !== null && $spent + $charge > econ_sat($limits['daily_budget'])) {
            $pdo->rollBack();
            return ['ok' => false, 'id' => null, 'error' => 'Daily budget used up'];
        }
        $row['charged_sat'] = $charge;
        $row['advertiser_address'] = $advertiser;
        $cols = array_keys($row);
        $sql = "INSERT INTO ad_clicks (" . implode(',', $cols) . ", payable_after) VALUES ("
             . implode(',', array_fill(0, count($cols), '?')) . ", DATE_ADD(NOW(), INTERVAL " . (int)$cfg['click_hold_minutes'] . " MINUTE))";
        $pdo->prepare($sql)->execute(array_values($row));
        $id = (int)$pdo->lastInsertId();
        $pdo->prepare("UPDATE advertiser_accounts SET balance_sat = balance_sat - ?, spent_sat = spent_sat + ? WHERE address = ?")
            ->execute([$charge, $charge, $advertiser]);
        $pdo->prepare("INSERT INTO advertiser_ledger (address, kind, amount_sat, ref) VALUES (?, 'click', ?, ?)")
            ->execute([$advertiser, -$charge, 'click:' . $id]);
        $pdo->commit();
        return ['ok' => true, 'id' => $id, 'error' => ''];
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) $pdo->rollBack();
        error_log('econ_charge_and_insert: ' . $e->getMessage());
        return ['ok' => false, 'id' => null, 'error' => 'Internal error'];
    }
}
