<?php
/**
 * The advertiser agreement: the current text, who accepted which version, and the address check used by the page.
 * Acceptance is recorded in advertiser_agreements; ad submissions are refused until the submitting wallet address has
 * accepted the CURRENT version (raising VERSION in terms/advertiser_agreement.txt makes everyone accept again).
 */
require_once __DIR__ . '/dbconfig.php';
require_once __DIR__ . '/economy.php';

function agr_ensure_table(PDO $pdo) {
    $pdo->exec("CREATE TABLE IF NOT EXISTS advertiser_agreements (
        id            BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        address       VARCHAR(64) NOT NULL,
        terms_version INT NOT NULL,
        legal_name    VARCHAR(200) NOT NULL,
        contact_email VARCHAR(200) NOT NULL,
        accepted_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ip_address    VARCHAR(45) NULL,
        user_agent    VARCHAR(255) NULL,
        source        VARCHAR(20) NOT NULL DEFAULT 'web',
        UNIQUE KEY uq_address_version (address, terms_version)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
}

function agr_coin() {
    static $c = null;
    if ($c === null) {
        $c = pyc_read_json_config('consensus_params.json', ['coin_name' => 'PythonCoin', 'ticker' => 'PYC', 'address_version' => 0]);
    }
    return $c;
}

/** Operator details shown in the agreement (set by the setup wizard in site_config.json). */
function agr_operator() {
    return pyc_read_json_config('site_config.json', []) + [
        'operator_name' => '[Operator name]', 'operator_contact' => '[contact e-mail or address]', 'governing_law' => '[country]',
    ];
}

function agr_upload_fee_text() {
    require_once __DIR__ . '/btcshop_bridge.php';
    $fee = bridge_fee_info();
    return $fee['btc'] !== null ? $fee['btc'] . ' BTC per submission' : 'the price shown in the Operator\'s shop';
}

/** The current agreement: ['version', 'effective', 'title', 'sections' => [[heading, body], ...]] with placeholders filled in. */
function agr_current_terms() {
    $file = __DIR__ . '/terms/advertiser_agreement.txt';
    $raw = is_file($file) ? (string)file_get_contents($file) : '';
    $op = agr_operator();
    $coin = agr_coin();
    $cfg = econ_settings();
    $vars = [
        '{{OPERATOR_NAME}}' => $op['operator_name'], '{{OPERATOR_CONTACT}}' => $op['operator_contact'],
        '{{GOVERNING_LAW}}' => $op['governing_law'], '{{COIN_NAME}}' => $coin['coin_name'], '{{TICKER}}' => $coin['ticker'],
        '{{UPLOAD_FEE}}' => agr_upload_fee_text(), '{{FEE_PERCENT}}' => rtrim(rtrim(number_format((float)$cfg['network_fee_percent'], 2), '0'), '.'),
        '{{CONFIRMATIONS}}' => (string)(int)$cfg['deposit_confirmations'],
        '{{HOLD_HOURS}}' => rtrim(rtrim(number_format($cfg['click_hold_minutes'] / 60, 1), '0'), '.'),
        '{{RETENTION_DAYS}}' => (string)(int)$cfg['retention_impression_days'], '{{IP_DAYS}}' => (string)(int)$cfg['retention_ip_days'],
    ];
    $terms = ['version' => 1, 'effective' => '', 'title' => 'Advertiser Agreement', 'sections' => []];
    $current = null;
    foreach (preg_split('/\r?\n/', $raw) as $line) {
        if ($line !== '' && $line[0] === '#') continue;
        if (preg_match('/^VERSION:\s*(\d+)/', $line, $m)) { $terms['version'] = (int)$m[1]; continue; }
        if (preg_match('/^EFFECTIVE:\s*(.+)$/', $line, $m)) { $terms['effective'] = trim($m[1]); continue; }
        if (preg_match('/^TITLE:\s*(.+)$/', $line, $m)) { $terms['title'] = trim($m[1]); continue; }
        if (strncmp($line, '== ', 3) === 0) { $current = count($terms['sections']); $terms['sections'][] = ['heading' => substr($line, 3), 'body' => '']; continue; }
        if ($current !== null && trim($line) !== '') $terms['sections'][$current]['body'] .= strtr($line, $vars) . "\n";
    }
    return $terms;
}

function agr_b58_decode($s) {
    $alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    $bytes = [0];
    for ($i = 0, $n = strlen($s); $i < $n; $i++) {
        $p = strpos($alphabet, $s[$i]);
        if ($p === false) return null;
        $carry = $p;
        for ($j = count($bytes) - 1; $j >= 0; $j--) {
            $carry += $bytes[$j] * 58;
            $bytes[$j] = $carry & 0xFF;
            $carry >>= 8;
        }
        while ($carry) { array_unshift($bytes, $carry & 0xFF); $carry >>= 8; }
    }
    $zeros = 0; while ($zeros < strlen($s) && $s[$zeros] === '1') $zeros++;
    while (count($bytes) > 1 && $bytes[0] === 0) array_shift($bytes);
    return str_repeat("\0", $zeros) . ($bytes === [0] ? '' : pack('C*', ...$bytes));
}

/** True for a well-formed address of THIS coin (right version byte, checksum matches). */
function agr_address_valid($address) {
    if (!is_string($address) || strlen($address) < 25 || strlen($address) > 36) return false;
    $raw = agr_b58_decode($address);
    if ($raw === null || strlen($raw) !== 25) return false;
    if (ord($raw[0]) !== (int)agr_coin()['address_version']) return false;
    return substr(hash('sha256', hash('sha256', substr($raw, 0, 21), true), true), 0, 4) === substr($raw, 21);
}

function agr_has_accepted(PDO $pdo, $address, $version) {
    agr_ensure_table($pdo);
    $st = $pdo->prepare("SELECT 1 FROM advertiser_agreements WHERE address = ? AND terms_version = ?");
    $st->execute([$address, (int)$version]);
    return (bool)$st->fetchColumn();
}

function agr_record(PDO $pdo, $address, $version, $name, $email, $source = 'web') {
    agr_ensure_table($pdo);
    $st = $pdo->prepare("INSERT INTO advertiser_agreements (address, terms_version, legal_name, contact_email, ip_address, user_agent, source)
                         VALUES (?, ?, ?, ?, ?, ?, ?)
                         ON DUPLICATE KEY UPDATE legal_name = VALUES(legal_name), contact_email = VALUES(contact_email), accepted_at = CURRENT_TIMESTAMP,
                                                 ip_address = VALUES(ip_address), user_agent = VALUES(user_agent), source = VALUES(source)");
    $st->execute([$address, (int)$version, mb_substr($name, 0, 200), mb_substr($email, 0, 200),
                  $_SERVER['REMOTE_ADDR'] ?? null, mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 255), $source]);
}
