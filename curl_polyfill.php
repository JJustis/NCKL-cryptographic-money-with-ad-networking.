<?php
/**
 * Fallback for the few curl functions this project uses, for PHP builds where the curl extension is not loaded
 * (Apache's PHP currently fails to load it after the PHP upgrade). Does nothing when the real extension is present.
 * Supported: curl_init, curl_setopt, curl_setopt_array, curl_exec, curl_getinfo(HTTP_CODE), curl_error, curl_errno,
 * curl_close - built on PHP's HTTP stream wrapper (allow_url_fopen must be on).
 */
if (!function_exists('curl_init')) {

    foreach ([
        'CURLOPT_URL' => 10002, 'CURLOPT_RETURNTRANSFER' => 19913, 'CURLOPT_TIMEOUT' => 13, 'CURLOPT_CONNECTTIMEOUT' => 78,
        'CURLOPT_HTTPHEADER' => 10023, 'CURLOPT_POST' => 47, 'CURLOPT_POSTFIELDS' => 10015, 'CURLOPT_FOLLOWLOCATION' => 52,
        'CURLOPT_SSL_VERIFYPEER' => 64, 'CURLOPT_SSL_VERIFYHOST' => 81, 'CURLOPT_USERAGENT' => 10018, 'CURLOPT_HEADER' => 42,
        'CURLOPT_CUSTOMREQUEST' => 10036, 'CURLINFO_HTTP_CODE' => 2097154,
    ] as $name => $value) {
        if (!defined($name)) define($name, $value);
    }

    final class PycCurlHandle {
        public array $opts = [];
        public int $code = 0;
        public string $error = '';
        public int $errno = 0;
    }

    function curl_init($url = null) {
        $h = new PycCurlHandle();
        if ($url !== null) $h->opts[CURLOPT_URL] = $url;
        return $h;
    }

    function curl_setopt($ch, $option, $value) { $ch->opts[$option] = $value; return true; }

    function curl_setopt_array($ch, array $options) { foreach ($options as $k => $v) $ch->opts[$k] = $v; return true; }

    function curl_exec($ch) {
        $o = $ch->opts;
        $url = $o[CURLOPT_URL] ?? '';
        $ch->code = 0; $ch->error = ''; $ch->errno = 0;
        if (!preg_match('~^https?://~i', $url)) { $ch->error = 'unsupported URL'; $ch->errno = 3; return false; }

        $method = !empty($o[CURLOPT_POST]) ? 'POST' : ($o[CURLOPT_CUSTOMREQUEST] ?? 'GET');
        $http = [
            'method' => $method,
            'timeout' => (float)($o[CURLOPT_TIMEOUT] ?? 30),
            'follow_location' => !empty($o[CURLOPT_FOLLOWLOCATION]) ? 1 : 0,
            'ignore_errors' => true,                       // we want the body and status of 4xx/5xx too
            'header' => implode("\r\n", array_merge(
                $o[CURLOPT_HTTPHEADER] ?? [],
                isset($o[CURLOPT_USERAGENT]) ? ['User-Agent: ' . $o[CURLOPT_USERAGENT]] : []
            )),
        ];
        if ($method === 'POST' && isset($o[CURLOPT_POSTFIELDS])) {
            $http['content'] = is_array($o[CURLOPT_POSTFIELDS]) ? http_build_query($o[CURLOPT_POSTFIELDS]) : (string)$o[CURLOPT_POSTFIELDS];
        }
        $verify = !isset($o[CURLOPT_SSL_VERIFYPEER]) || (bool)$o[CURLOPT_SSL_VERIFYPEER];
        $ctx = stream_context_create(['http' => $http, 'ssl' => ['verify_peer' => $verify, 'verify_peer_name' => $verify]]);

        $body = @file_get_contents($url, false, $ctx);
        $headers = $http_response_header ?? [];
        if ($headers && preg_match('~^HTTP/\S+\s+(\d{3})~', $headers[0], $m)) $ch->code = (int)$m[1];
        if ($body === false && $ch->code === 0) { $ch->error = 'connection failed'; $ch->errno = 7; return false; }
        if (empty($o[CURLOPT_RETURNTRANSFER])) { echo $body; return true; }
        return $body;
    }

    function curl_getinfo($ch, $option = null) {
        if ($option === CURLINFO_HTTP_CODE) return $ch->code;
        return ['http_code' => $ch->code, 'url' => $ch->opts[CURLOPT_URL] ?? ''];
    }

    function curl_error($ch) { return $ch->error; }
    function curl_errno($ch) { return $ch->errno; }
    function curl_close($ch) { /* nothing to release */ }
}
