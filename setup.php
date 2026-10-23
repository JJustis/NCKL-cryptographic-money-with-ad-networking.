<?php
// setup_p2p_system.php - Complete setup script for P2P Ad Network
echo "🌐 P2P Ad Network Setup Script\n";
echo "==============================\n\n";

// Database configuration
$host = 'localhost';
$dbname = 'adnetwrk'; // Reverted: Using 'adnetwrk' as requested
$username = 'root';
$password = '';

try {
    // Connect to MySQL server
    echo "📡 Connecting to MySQL server...\n";
    $pdo = new PDO("mysql:host=$host", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create database
    echo "🗄️ Creating database: $dbname\n";
    $pdo->exec("CREATE DATABASE IF NOT EXISTS `$dbname` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    $pdo->exec("USE `$dbname`");
    
    // Create enhanced members table
    echo "👥 Creating ad_members table...\n";
    $createMembersTable = "
    CREATE TABLE IF NOT EXISTS `ad_members` ( /* Reverted: Using 'ad_members' as requested */
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL UNIQUE,
        `password` varchar(255) NOT NULL,
        `pyc_address` varchar(255) DEFAULT NULL, /* Added: PythonCoin address column */
        `exp` int(11) DEFAULT 0,
        `total_clicks` int(11) DEFAULT 0,
        `total_impressions` int(11) DEFAULT 0,
        `embeds_created` int(11) DEFAULT 0,
        `last_login` datetime DEFAULT NULL,
        `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
    $pdo->exec($createMembersTable);

    // Create p2p_clients table
    echo "🔗 Creating p2p_clients table...\n";
    $createClientsTable = "
    CREATE TABLE IF NOT EXISTS `p2p_clients` (
        `client_id` varchar(255) NOT NULL PRIMARY KEY,
        `ip_address` varchar(45) NOT NULL,
        `port` int(11) NOT NULL,
        `status` enum('online','offline','suspended') DEFAULT 'online',
        `last_seen` datetime DEFAULT CURRENT_TIMESTAMP,
        `connected_peers` int(11) DEFAULT 0,
        `ads_served` int(11) DEFAULT 0,
        `version` varchar(20) DEFAULT NULL,
        `uptime_seconds` int(11) DEFAULT 0,
        `bandwidth_mbps` decimal(10,2) DEFAULT 0.00
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
    $pdo->exec($createClientsTable);

    // Create ads table
    echo "📈 Creating ads table...\n";
    $createAdsTable = "
    CREATE TABLE IF NOT EXISTS `ads` (
        `ad_id` int(11) NOT NULL AUTO_INCREMENT,
        `client_id` varchar(255) NOT NULL,
        `title` varchar(255) NOT NULL,
        `description` text,
        `url` varchar(255) NOT NULL,
        `image_url` varchar(255) DEFAULT NULL,
        `category` varchar(100) DEFAULT 'general',
        `payout_pyc` decimal(10,8) DEFAULT 0.00000000,
        `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`ad_id`),
        FOREIGN KEY (`client_id`) REFERENCES `p2p_clients`(`client_id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
    $pdo->exec($createAdsTable);

    // Create analytics table
    echo "📊 Creating analytics table...\n";
    $createAnalyticsTable = "
    CREATE TABLE IF NOT EXISTS `analytics` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL,
        `event_type` varchar(50) NOT NULL,
        `data` json DEFAULT NULL,
        `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        INDEX `idx_username` (`username`),
        INDEX `idx_event_type` (`event_type`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
    $pdo->exec($createAnalyticsTable);

    // Insert test data
    echo " seeded with 'demo' and 'developer' accounts.\n";
    
    // Clear existing test accounts to prevent duplicates on re-run
    $pdo->exec("DELETE FROM `ad_members` WHERE username IN ('demo', 'developer')"); // Reverted table name

    $hashedDemoPass = password_hash('demo123', PASSWORD_DEFAULT);
    $hashedDevPass = password_hash('dev123', PASSWORD_DEFAULT);

    $insertTestData = "
    INSERT INTO `ad_members` (username, password, pyc_address, exp, total_clicks, total_impressions, embeds_created, last_login, created_at) VALUES /* Reverted table name */
    ('demo', ?, 'PYCDemoAddress12345678901234567890', 100, 50, 1000, 5, NOW(), NOW()),
    ('developer', ?, 'PYCDevAddressABCDEFGHIJKLMNOPQRS', 500, 200, 5000, 10, NOW(), NOW());
    ";
    $stmt = $pdo->prepare($insertTestData);
    $stmt->execute([$hashedDemoPass, $hashedDevPass]);

    // Create users directories for demo and developer
    function createDemoUserFilesAndFolders($username) {
        $userDir = "users/$username";
        if (!file_exists($userDir)) {
            mkdir($userDir, 0755, true);
        }

        $logsDir = "$userDir/logs";
        if (!file_exists($logsDir)) {
            mkdir($logsDir, 0755, true);
        }

        $embedsData = ['user' => $username, 'embeds' => []];
        file_put_contents("$userDir/embeds.json", json_encode($embedsData, JSON_PRETTY_PRINT));

        $analyticsData = [
            'user' => $username,
            'created' => date('c'),
            'stats' => [
                'total_clicks' => 0,
                'total_impressions' => 0,
                'total_exp' => 0,
                'embeds_created' => 0
            ],
            'daily_stats' => []
        ];
        file_put_contents("$userDir/analytics.json", json_encode($analyticsData, JSON_PRETTY_PRINT));
    }
    
    createDemoUserFilesAndFolders('demo');
    createDemoUserFilesAndFolders('developer');


    // Generate a basic index.php for setup confirmation
    echo "📄 Generating index.php...\n";
    $indexContent = '<?php header("Location: developer_portal.html"); exit; ?>'; // Redirect to developer_portal.html
    
    // Alternatively, you can generate a more descriptive index.php:
    
    $indexContent = '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>P2P Ad Network Setup Complete</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f4f4f4; margin: 0; }
        .container { text-align: center; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1 { color: #28a745; }
        p { color: #555; }
        .btn { display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin: 10px; transition: background-color 0.3s ease; }
        .btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Setup Complete!</h1>
        <p>Your P2P Ad Network has been successfully set up.</p>
        <a href="developer_portal.html" class="btn">📊 Developer Portal</a>
        <a href="api/commands" class="btn">🔗 API Commands</a>
        <a href="js/" class="btn">📁 JS Files</a>
        
        <h2>👤 Test Accounts</h2>
        <p>Use these accounts to test the system:</p>
        <ul>
            <li><strong>Demo User:</strong> <code>demo</code> / <code>demo123</code></li>
            <li><strong>Developer:</strong> <code>developer</code> / <code>dev123</code></li>
        </ul>
        
        <h2>🔧 Configuration</h2>
        <p>System configuration is stored in <code>config.php</code>. API endpoints:</p>
        <ul>
            <li><code>POST /api/commands</code> - Main command API</li>
            <li><code>POST /api/auth</code> - Authentication</li>
            <li><code>GET /js/*.js</code> - Generated JavaScript files</li>
        </ul>
        
        <h2>📚 Documentation</h2>
        <p>For detailed documentation and API reference, please refer to the system documentation or contact your system administrator.</p>
        
        <div style="margin-top: 30px; text-align: center; opacity: 0.8; font-size: 0.9em;">
            <p>P2P Ad Network v2.1 • Generated: <?php echo date("c"); ?></p>
        </div>
    </div>
</body>
</html>';
    
    
    file_put_contents('index.php', $indexContent);
    
} catch(PDOException $e) {
    echo "\n❌ Database Error: " . $e->getMessage() . "\n";
    echo "Please ensure MySQL is running and accessible with the provided credentials.\n";
    exit(1);
} catch(Exception $e) {
    echo "\n❌ Error: " . $e->getMessage() . "\n";
    exit(1);
}

echo "\n🎉 Setup script completed successfully!\n";
echo "You can now access the Developer Portal via your web server.\n";

?>