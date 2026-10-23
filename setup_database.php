<?php
// setup_database.php - Enhanced database setup
$host = 'localhost';
$dbname = 'reservesphp';
$username = 'root';
$password = '';

try {
    // Connect to MySQL server
    $pdo = new PDO("mysql:host=$host", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create database
    $pdo->exec("CREATE DATABASE IF NOT EXISTS `$dbname` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    $pdo->exec("USE `$dbname`");
    
    // Create enhanced members table
    $createMembersTable = "
    CREATE TABLE IF NOT EXISTS `ad_members` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL UNIQUE,
        `password` varchar(255) NOT NULL,
        `exp` int(11) DEFAULT 0,
        `total_clicks` int(11) DEFAULT 0,
        `total_impressions` int(11) DEFAULT 0,
        `embeds_created` int(11) DEFAULT 0,
        `last_login` timestamp NULL DEFAULT NULL,
        `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
        `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        KEY `username` (`username`),
        KEY `exp` (`exp`),
        KEY `created_at` (`created_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ";
    
    $pdo->exec($createMembersTable);
    
    // Create p2p_clients table for tracking connected clients
    $createClientsTable = "
    CREATE TABLE IF NOT EXISTS `p2p_clients` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `client_id` varchar(50) NOT NULL UNIQUE,
        `name` varchar(100) DEFAULT NULL,
        `host` varchar(255) NOT NULL,
        `port` int(11) NOT NULL,
        `status` enum('online','offline','discovered') DEFAULT 'discovered',
        `category` varchar(50) DEFAULT 'general',
        `ad_count` int(11) DEFAULT 0,
        `peer_count` int(11) DEFAULT 0,
        `last_seen` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        UNIQUE KEY `client_id` (`client_id`),
        KEY `status` (`status`),
        KEY `last_seen` (`last_seen`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ";
    
    $pdo->exec($createClientsTable);
    
    // Create analytics table for aggregated data
    $createAnalyticsTable = "
    CREATE TABLE IF NOT EXISTS `analytics` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL,
        `event_type` enum('click','impression','embed_created','login') NOT NULL,
        `ad_id` varchar(100) DEFAULT NULL,
        `zone` varchar(100) DEFAULT NULL,
        `embed_id` varchar(100) DEFAULT NULL,
        `data` json DEFAULT NULL,
        `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        KEY `username` (`username`),
        KEY `event_type` (`event_type`),
        KEY `created_at` (`created_at`),
        FOREIGN KEY (`username`) REFERENCES `members`(`username`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ";
    
    $pdo->exec($createAnalyticsTable);
    
    // Insert sample P2P clients
    $insertSampleClients = "
    INSERT IGNORE INTO `p2p_clients` (`client_id`, `name`, `host`, `port`, `status`, `category`, `ad_count`, `peer_count`) VALUES
    ('abc12345', 'TechCorp P2P Node', '192.168.1.100', 8080, 'online', 'technology', 15, 3),
    ('def67890', 'AutoDeals P2P Network', '192.168.1.101', 8080, 'online', 'automotive', 8, 2),
    ('ghi11121', 'Fashion P2P Hub', '192.168.1.102', 8080, 'discovered', 'fashion', 22, 5),
    ('jkl31415', 'Travel Network Node', '192.168.1.103', 8080, 'offline', 'travel', 12, 1),
    ('mno16171', 'Foodie P2P Network', '192.168.1.104', 8080, 'online', 'food', 18, 4);
    ";
    
    $pdo->exec($insertSampleClients);
    
    echo "Enhanced database schema created successfully!\n";
    echo "Tables created: members, p2p_clients, analytics\n";
    echo "Sample P2P clients inserted\n";
    echo "You can now use the enhanced P2P Ad Network Developer Portal.\n";
    
} catch(PDOException $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
