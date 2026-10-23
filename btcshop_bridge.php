<?php
/**
 * Connects the ad network to the Operator's btcshop: submitting an ad needs one PAID "ad-upload" order, which is used up
 * by that submission (so each upload is paid for exactly once).
 *
 * Settings in economy.json:
 *   ad_upload_fee_required  true/false   (default true - remote submissions must be paid for)
 *   btcshop_db              path to btcshop's data/shop.sqlite (default: ../../btcshop/data/shop.sqlite)
 *   btcshop_product         product id in btcshop's products.json (default "ad-upload")
 *   btcshop_url             public address of the shop, shown to advertisers
 */
require_once __DIR__ . '/economy.php';

function bridge_cfg() {
    $cfg = econ_settings() + ['ad_upload_fee_required' => true, 'btcshop_db' => '', 'btcshop_product' => 'ad-upload', 'btcshop_url' => ''];
    if ($cfg['btcshop_db'] === '') {
        // the shop is normally a sibling folder of this one inside the web server's folder
        foreach ([dirname(__DIR__, 1), dirname(__DIR__, 2)] as $base) {
            $guess = $base . DIRECTORY_SEPARATOR . 'btcshop' . DIRECTORY_SEPARATOR . 'data' . DIRECTORY_SEPARATOR . 'shop.sqlite';
            if (is_file($guess)) break;
        }
        $cfg['btcshop_db'] = $guess;
    }
    return $cfg;
}

/** What advertisers are told about the fee. */
function bridge_fee_info() {
    $cfg = bridge_cfg();
    $btc = null;
    $catalog = dirname(dirname($cfg['btcshop_db'])) . DIRECTORY_SEPARATOR . 'products.json';
    if (is_file($catalog)) {
        foreach ((json_decode((string)file_get_contents($catalog), true) ?: []) as $p) {
            if (($p['id'] ?? '') === $cfg['btcshop_product']) { $btc = (string)$p['btc']; break; }
        }
    }
    return ['required' => (bool)$cfg['ad_upload_fee_required'], 'product' => $cfg['btcshop_product'], 'btc' => $btc, 'shop_url' => $cfg['btcshop_url']];
}

function bridge_open() {
    $cfg = bridge_cfg();
    if (!is_file($cfg['btcshop_db'])) return null;
    $pdo = new PDO('sqlite:' . $cfg['btcshop_db']);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $cols = array_column($pdo->query("PRAGMA table_info(orders)")->fetchAll(PDO::FETCH_ASSOC), 'name');
    if (!in_array('used_for', $cols, true)) $pdo->exec('ALTER TABLE orders ADD COLUMN used_for TEXT');
    if (!in_array('used_at', $cols, true)) $pdo->exec('ALTER TABLE orders ADD COLUMN used_at INTEGER');
    return $pdo;
}

/**
 * Check that $order is a PAID, unused upload order belonging to the secure ID $sec, and use it up for $adId.
 * Returns [ok, reason]. The order is claimed atomically, so two submissions can never share one payment.
 */
function bridge_consume_fee($order, $sec, $adId) {
    $cfg = bridge_cfg();
    if (!is_numeric($order) || !is_string($sec) || !preg_match('/^[a-f0-9]{32}$/i', $sec)) return [false, 'A paid upload order number and its secure ID are required'];
    $pdo = bridge_open();
    if (!$pdo) return [false, 'The shop is not available, so the upload fee cannot be checked'];
    $st = $pdo->prepare("SELECT status, product, used_for FROM orders WHERE id = ? AND sec_hash = ?");
    $st->execute([(int)$order, hash('sha256', strtolower($sec))]);
    $o = $st->fetch(PDO::FETCH_ASSOC);
    if (!$o)                                        return [false, 'No such order for that secure ID'];
    if ($o['product'] !== $cfg['btcshop_product'])  return [false, 'That order is not an ad-upload order'];
    if ($o['status'] !== 'paid')                    return [false, 'That order has not been paid yet'];
    $claim = $pdo->prepare("UPDATE orders SET used_for = ?, used_at = ? WHERE id = ? AND (used_for IS NULL OR used_for = '')");
    $claim->execute([$adId, time(), (int)$order]);
    if ($claim->rowCount() !== 1)                   return [false, 'That order has already been used for an upload'];
    return [true, 'ok'];
}

/** Give a claimed order back (used when a submission fails after the fee was taken). */
function bridge_release_fee($order) {
    $pdo = bridge_open();
    if ($pdo) $pdo->prepare("UPDATE orders SET used_for = NULL, used_at = NULL WHERE id = ?")->execute([(int)$order]);
}
