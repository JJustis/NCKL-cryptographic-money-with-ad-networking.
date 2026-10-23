<?php
/**
 * Where the database login and the site's public address come from (PHP side of dbconfig.py).
 * Written by the setup wizard into dbconfig.json / site_config.json next to this file (blocked from the web by .htaccess).
 * With no files present the old single-machine defaults apply, so an existing installation keeps working.
 */
function pyc_read_json_config($name, array $defaults) {
    $cfg = $defaults;
    $path = __DIR__ . DIRECTORY_SEPARATOR . $name;
    if (is_file($path)) {
        $json = json_decode((string)file_get_contents($path), true);
        if (is_array($json)) $cfg = array_merge($cfg, $json);
    }
    return $cfg;
}

/** ['host','port','user','password','database'] */
function pyc_db_config() {
    $cfg = pyc_read_json_config('dbconfig.json', ['host' => 'localhost', 'port' => 3306, 'user' => 'root', 'password' => '', 'database' => 'adnetwrk']);
    foreach (['host' => 'NICKLES_DB_HOST', 'port' => 'NICKLES_DB_PORT', 'user' => 'NICKLES_DB_USER', 'password' => 'NICKLES_DB_PASSWORD', 'database' => 'NICKLES_DB_NAME'] as $key => $env) {
        $v = getenv($env);
        if ($v !== false) $cfg[$key] = $v;
    }
    $cfg['port'] = (int)$cfg['port'];
    return $cfg;
}

/** A PDO connection using the configured login (exceptions on error, associative fetch). */
function pyc_pdo(array $options = []) {
    $c = pyc_db_config();
    $dsn = "mysql:host={$c['host']};port={$c['port']};dbname={$c['database']};charset=utf8mb4";
    return new PDO($dsn, $c['user'], $c['password'], $options + [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);
}

/** ['base_url' => 'https://example.com/nickles', 'public_host' => 'example.com'] */
function pyc_site() {
    return pyc_read_json_config('site_config.json', ['base_url' => 'https://secupgrade.com/livepy/pythoncoin', 'public_host' => 'secupgrade.com']);
}
