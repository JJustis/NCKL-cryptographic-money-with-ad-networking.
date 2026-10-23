<?php
// P2P Ad Network Configuration
require_once __DIR__ . '/dbconfig.php';   // database login + public address come from dbconfig.json / site_config.json
$__db = pyc_db_config();
$__site = pyc_site();

// Determine protocol and host dynamically
$protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'];
$base_path = rtrim(dirname($_SERVER['PHP_SELF']), '/'); // Get base path, remove trailing slash

return [
    "database" => [
        "host" => $__db['host'],
        "dbname" => $__db['database'],
        "username" => $__db['user'],
        "password" => $__db['password']
    ],
    "servers" => [
        "main_api" => "{$protocol}://{$host}{$base_path}/api.php", // Dynamic API URL
        "commands" => "{$protocol}://{$host}{$base_path}/commands.php", // Dynamic Commands URL
        "js_server" => "http://{$host}:8332", // Dynamic JS Server URL (assuming pyqt.py serves HTTP)
        "websocket" => "wss://" . $__site["public_host"] . ":8083" // Keep as is, it's external
    ],
    "settings" => [
        "heartbeat_interval" => 30,
        "peer_scan_interval" => 45,
        "max_ads_per_peer" => 10,
        "session_timeout" => 3600,
        "debug_mode" => false
    ],
    "security" => [
        // Set true once every embed/client sends encrypted reports; plaintext is then rejected
        "require_encrypted" => true
    ],
    "features" => [
        "real_time_discovery" => true,
        "websocket_support" => true,
        "analytics_tracking" => true,
        "custom_js_generation" => true
    ]
];
?>