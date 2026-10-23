<?php
// Shared input-validation and abuse-protection helpers for the P2P ad network endpoints.

/** Return $v if it is a safe identifier (letters, digits, _ - . @), else null. */
function sec_safe_id($v, $max = 64) {
    if (!is_string($v) || $v === '' || strlen($v) > $max) return null;
    if (!preg_match('/^[A-Za-z0-9_@-][A-Za-z0-9_.@-]*$/', $v)) return null;
    if (strpos($v, '..') !== false) return null;
    return $v;
}

/** True for a public/LAN IPv4/IPv6 address or a plain hostname; false for loopback, link-local, any-address. */
function sec_valid_host($h) {
    if (!is_string($h) || $h === '' || strlen($h) > 253) return false;
    if (filter_var($h, FILTER_VALIDATE_IP)) {
        if (!filter_var($h, FILTER_VALIDATE_IP, FILTER_FLAG_NO_RES_RANGE)) {
            // Reserved range: allow only RFC1918 LAN ranges, not loopback/link-local/0.0.0.0
            return (bool)preg_match('/^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/', $h);
        }
        return true;
    }
    if (!preg_match('/^(?=.{1,253}$)([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$/', $h)) return false;
    return strtolower($h) !== 'localhost';
}

function sec_valid_port($p) {
    return filter_var($p, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1024, 'max_range' => 65535]]) !== false;
}

/** Only http(s) URLs (blocks javascript:, data:, file: ...). */
function sec_valid_url($u, $max = 500) {
    if (!is_string($u) || $u === '' || strlen($u) > $max) return false;
    $p = parse_url($u);
    return $p && isset($p['scheme'], $p['host']) && in_array(strtolower($p['scheme']), ['http', 'https'], true);
}

/** Fixed-window rate limit per client IP. Returns true if the request is allowed. */
function sec_rate_limit($bucket, $max, $windowSec) {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $dir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'pyc_ratelimit';
    if (!is_dir($dir)) @mkdir($dir, 0700, true);
    $file = $dir . DIRECTORY_SEPARATOR . hash('sha256', $bucket . '|' . $ip) . '.json';
    $now = time();
    $fh = @fopen($file, 'c+');
    if (!$fh) return true; // fail open rather than break the network
    flock($fh, LOCK_EX);
    $d = json_decode(stream_get_contents($fh), true);
    if (!is_array($d) || ($d['t'] ?? 0) + $windowSec < $now) $d = ['t' => $now, 'n' => 0];
    $d['n']++;
    ftruncate($fh, 0); rewind($fh);
    fwrite($fh, json_encode($d));
    flock($fh, LOCK_UN); fclose($fh);
    return $d['n'] <= $max;
}

function sec_fail($code, $msg) {
    http_response_code($code);
    echo json_encode(['success' => false, 'message' => $msg]);
    exit;
}

/** Verify a username/password against ad_members. Returns the member row or null. */
function sec_check_login($pdo, $user, $pass) {
    if (!sec_safe_id($user) || !is_string($pass) || $pass === '') return null;
    $stmt = $pdo->prepare("SELECT * FROM ad_members WHERE username = ?");
    $stmt->execute([$user]);
    $m = $stmt->fetch(PDO::FETCH_ASSOC);
    return ($m && password_verify($pass, $m['password_hash'])) ? $m : null;
}

// ---------------------------------------------------------------------------
// Encrypted reporting envelopes (ECDH P-256 + HKDF-SHA256 + AES-256-GCM)
// Browser/client sends {"enc":{"v":1,"epk":b64(65-byte point),"iv":b64(12),"ct":b64(ciphertext||tag16)}}
// Plaintext JSON must contain "ts" (unix secs, +-120s) and "nonce" (single use).
// ---------------------------------------------------------------------------
// Key folder: site_config.json "key_dir" (written by the setup wizard), else the folder the original installation used.
$__kd = null;
if (is_readable(__DIR__ . '/site_config.json')) { $__sc = json_decode((string)file_get_contents(__DIR__ . '/site_config.json'), true); if (is_array($__sc) && !empty($__sc['key_dir'])) $__kd = $__sc['key_dir']; }
define('PYC_KEY_DIR', $__kd ?: 'C:\xampp\pyc_keys');
unset($__kd, $__sc);

function sec_public_key_b64() {
    $f = PYC_KEY_DIR . DIRECTORY_SEPARATOR . 'report_public.b64';
    return is_readable($f) ? trim(file_get_contents($f)) : '';
}

/** Decrypt an envelope. Returns the inner array, or null if invalid/replayed/stale. */
function sec_decrypt_envelope($env) {
    if (!is_array($env) || ($env['v'] ?? 0) !== 1) return null;
    $epk = base64_decode($env['epk'] ?? '', true);
    $iv  = base64_decode($env['iv'] ?? '', true);
    $ct  = base64_decode($env['ct'] ?? '', true);
    if ($epk === false || strlen($epk) !== 65 || $epk[0] !== "\x04" || $iv === false || strlen($iv) !== 12
        || $ct === false || strlen($ct) < 17 || strlen($ct) > 65536) return null;
    $privPem = @file_get_contents(PYC_KEY_DIR . DIRECTORY_SEPARATOR . 'report_private.pem');
    if (!$privPem) return null;
    // Wrap the raw uncompressed point in an SPKI DER header so OpenSSL accepts it
    $spki = hex2bin('3059301306072a8648ce3d020106082a8648ce3d030107034200') . $epk;
    $pubPem = "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($spki), 64, "\n") . "-----END PUBLIC KEY-----\n";
    $priv = openssl_pkey_get_private($privPem);
    $pub  = @openssl_pkey_get_public($pubPem);
    if (!$priv || !$pub) return null;
    $secret = @openssl_pkey_derive($pub, $priv, 32);
    if ($secret === false) return null;
    $key = hash_hkdf('sha256', $secret, 32, 'pyc-report-v1', '');
    $tag = substr($ct, -16);
    $plain = openssl_decrypt(substr($ct, 0, -16), 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag);
    if ($plain === false) return null;
    $data = json_decode($plain, true);
    if (!is_array($data)) return null;
    $ts = (int)($data['ts'] ?? 0);
    $nonce = (string)($data['nonce'] ?? '');
    if (abs(time() - $ts) > 120 || !preg_match('/^[A-Za-z0-9_-]{16,64}$/', $nonce)) return null;
    // Replay protection: each nonce is accepted once
    $dir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'pyc_nonces';
    if (!is_dir($dir)) @mkdir($dir, 0700, true);
    $nf = $dir . DIRECTORY_SEPARATOR . hash('sha256', $nonce);
    $h = @fopen($nf, 'x');
    if (!$h) return null; // already used
    fclose($h);
    foreach (glob($dir . DIRECTORY_SEPARATOR . '*') ?: [] as $old) { // prune stale nonces
        if (filemtime($old) < time() - 600) @unlink($old);
    }
    unset($data['ts'], $data['nonce']);
    return $data;
}

/**
 * Call right after decoding the request body. If the body is an envelope, returns the decrypted data.
 * When config 'security.require_encrypted' is true, plaintext reports are rejected.
 */
function sec_unwrap_input($input, $config) {
    require_once __DIR__ . '/pinwheel.php';
    // 1) Pinwheel query: decrypt it and transparently seal whatever the handler prints
    if (is_array($input) && isset($input['pw'])) {
        $r = pw_decrypt_query($input['pw']);
        if ($r === null) sec_fail(400, 'Invalid or expired encrypted query');
        pw_seal_output($r[1], $r[2]);
        return $r[0];
    }
    // 2) Session handshake: root secret arrives inside the ECDH envelope; reply is sealed under it
    if (is_array($input) && isset($input['enc'])) {
        $data = sec_decrypt_envelope($input['enc']);
        if ($data === null) sec_fail(400, 'Invalid or expired encrypted report');
        if (($data['action'] ?? '') === 'pw_open') {
            if (!sec_rate_limit('pw_open', 30, 60)) sec_fail(429, 'Too many requests');
            $root = base64_decode((string)($data['root'] ?? ''), true);
            $info = ($root !== false) ? pw_open_session($root) : null;
            if ($info === null) sec_fail(400, 'Could not open session');
            pw_seal_output(pw_hkdf($root, 'pw-open'), 'pw-open');
            echo json_encode(['success' => true] + $info);
            exit;
        }
        return $data;
    }
    if (!empty($config['security']['require_encrypted']) && ($input['action'] ?? '') !== 'public_key') {
        sec_fail(400, 'Encrypted queries required');
    }
    return $input;
}
