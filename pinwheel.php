<?php
// Pinwheel-style encrypted query sessions for the ad network (adapted from pinwheel-freechat).
//
//   handshake : client sends root secret inside the ECDH envelope (security.php) with action "pw_open";
//               the reply is sealed under HKDF(root, "pw-open")
//   per query : epoch_key = HKDF(root, "epoch-<E>")      E = floor((now - session_start) / 20)
//               msg_key   = HKDF(epoch_key, "msg-<N>")   N = per-epoch message index, never reused
//               request   = AES-256-GCM(msg_key, json, aad = "sid|E|N")
//               response  = AES-256-GCM(HKDF(msg_key, "resp"), json, aad = "sid|E|N|r")
// The server keeps the root only AES-GCM-wrapped under a master key stored outside the web root.

const PW_EPOCH_SECONDS = 20;
const PW_SESSION_TTL   = 3600;
const PW_MAX_BODY      = 65536;

function pw_dir() {
    $d = PYC_KEY_DIR . DIRECTORY_SEPARATOR . 'sessions';
    if (!is_dir($d)) @mkdir($d, 0700, true);
    return $d;
}

function pw_hkdf($ikm, $info) { return hash_hkdf('sha256', $ikm, 32, $info, ''); }

function pw_master() {
    $k = @file_get_contents(PYC_KEY_DIR . DIRECTORY_SEPARATOR . 'master.key');
    return ($k !== false && strlen($k) === 32) ? $k : null;
}

function pw_gcm_seal($key, $plain, $aad) {
    $iv = random_bytes(12);
    $ct = openssl_encrypt($plain, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag, $aad, 16);
    return $iv . $ct . $tag;
}

function pw_gcm_open($key, $blob, $aad) {
    if (strlen($blob) < 29) return null;
    $iv = substr($blob, 0, 12); $tag = substr($blob, -16); $ct = substr($blob, 12, -16);
    $p = openssl_decrypt($ct, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag, $aad);
    return $p === false ? null : $p;
}

/** Create a session from a client-chosen 32-byte root. Returns session info array. */
function pw_open_session($root) {
    $master = pw_master();
    if (!$master || strlen($root) !== 32) return null;
    $dir = pw_dir();
    foreach (glob($dir . DIRECTORY_SEPARATOR . '*.json') ?: [] as $f) {      // prune expired sessions
        if (filemtime($f) < time() - PW_SESSION_TTL) {
            @unlink($f);
            foreach (glob(substr($f, 0, -5) . '.used' . DIRECTORY_SEPARATOR . '*') ?: [] as $u) @unlink($u);
            @rmdir(substr($f, 0, -5) . '.used');
        }
    }
    $sid = bin2hex(random_bytes(12));
    $now = time();
    $rec = ['start' => $now, 'root' => base64_encode(pw_gcm_seal($master, $root, 'pw-root|' . $sid))];
    if (file_put_contents($dir . DIRECTORY_SEPARATOR . $sid . '.json', json_encode($rec)) === false) return null;
    @mkdir($dir . DIRECTORY_SEPARATOR . $sid . '.used', 0700, true);
    return ['sid' => $sid, 'start' => $now, 'epoch_seconds' => PW_EPOCH_SECONDS, 'ttl' => PW_SESSION_TTL, 'server_time' => $now];
}

function pw_load_session($sid) {
    if (!preg_match('/^[0-9a-f]{24}$/', $sid)) return null;
    $f = pw_dir() . DIRECTORY_SEPARATOR . $sid . '.json';
    $rec = is_file($f) ? json_decode(file_get_contents($f), true) : null;
    $master = pw_master();
    if (!$rec || !$master || $rec['start'] < time() - PW_SESSION_TTL) return null;
    $root = pw_gcm_open($master, base64_decode($rec['root']), 'pw-root|' . $sid);
    return $root === null ? null : ['root' => $root, 'start' => (int)$rec['start']];
}

/** Decrypt one pinwheel query. Returns [data, responseKey, aad] or null. */
function pw_decrypt_query($q) {
    if (!is_array($q) || ($q['v'] ?? 0) !== 1) return null;
    $sid = (string)($q['sid'] ?? '');
    $E = $q['e'] ?? null; $N = $q['n'] ?? null;
    if (!is_int($E) || !is_int($N) || $E < 0 || $N < 0 || $N > 100000) return null;
    $blob = base64_decode($q['ct'] ?? '', true);
    if ($blob === false || strlen($blob) > PW_MAX_BODY) return null;
    $s = pw_load_session($sid);
    if (!$s) return null;
    $serverEpoch = intdiv(time() - $s['start'], PW_EPOCH_SECONDS);
    if (abs($serverEpoch - $E) > 1) return null;                              // outside the 20s window
    $used = pw_dir() . DIRECTORY_SEPARATOR . $sid . '.used' . DIRECTORY_SEPARATOR . $E . '_' . $N;
    $epochKey = pw_hkdf($s['root'], 'epoch-' . $E);
    $msgKey = pw_hkdf($epochKey, 'msg-' . $N);
    $aad = $sid . '|' . $E . '|' . $N;
    $plain = pw_gcm_open($msgKey, $blob, $aad);
    if ($plain === null) return null;
    $h = @fopen($used, 'x');                                                   // (epoch, n) is single-use
    if (!$h) return null;
    fclose($h);
    $data = json_decode($plain, true);
    if (!is_array($data)) return null;
    return [$data, pw_hkdf($msgKey, 'resp'), $aad . '|r'];
}

/** Seal every byte the script prints from now on, so existing handlers need no changes. */
function pw_seal_output($key, $aad) {
    ob_start(function ($body) use ($key, $aad) {
        return json_encode(['pw' => 1, 'ct' => base64_encode(pw_gcm_seal($key, $body, $aad))]);
    });
}
