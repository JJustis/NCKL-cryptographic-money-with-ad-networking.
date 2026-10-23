<?php
// websocket_server.php - Real-time WebSocket server for live updates
// This would typically run as a separate service

class P2PWebSocketServer {
    private $clients = [];
    private $socket;
    
    public function __construct($host = 'localhost', $port = 8083) {
        $this->socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        socket_set_option($this->socket, SOL_SOCKET, SO_REUSEADDR, 1);
        socket_bind($this->socket, $host, $port);
        socket_listen($this->socket);
        
        echo "P2P WebSocket Server started on {$host}:{$port}\n";
    }
    
    public function run() {
        while (true) {
            $read = [$this->socket];
            foreach ($this->clients as $client) {
                $read[] = $client['socket'];
            }
            
            socket_select($read, $write, $except, 0, 200000);
            
            if (in_array($this->socket, $read)) {
                $this->handleNewConnection();
            }
            
            foreach ($this->clients as $clientId => $client) {
                if (in_array($client['socket'], $read)) {
                    $this->handleClientMessage($clientId);
                }
            }
            
            // Check for new updates to broadcast
            $this->broadcastUpdates();
        }
    }
    
    private function handleNewConnection() {
        $newSocket = socket_accept($this->socket);
        $this->performHandshake($newSocket);
        
        $clientId = uniqid();
        $this->clients[$clientId] = [
            'socket' => $newSocket,
            'connected_at' => time(),
            'username' => null
        ];
        
        echo "New client connected: {$clientId}\n";
    }
    
    private function performHandshake($socket) {
        $request = socket_read($socket, 2048);
        
        preg_match('/Sec-WebSocket-Key: (.*)\r\n/', $request, $matches);
        $key = base64_encode(pack('H*', sha1($matches[1] . '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')));
        
        $headers = "HTTP/1.1 101 Switching Protocols\r\n";
        $headers .= "Upgrade: websocket\r\n";
        $headers .= "Connection: Upgrade\r\n";
        $headers .= "Sec-WebSocket-Accept: {$key}\r\n\r\n";
        
        socket_write($socket, $headers, strlen($headers));
    }
    
    private function handleClientMessage($clientId) {
        $client = $this->clients[$clientId];
        $message = $this->decodeMessage(socket_read($client['socket'], 2048));
        
        if ($message === false) {
            $this->disconnectClient($clientId);
            return;
        }
        
        $data = json_decode($message, true);
        
        if (isset($data['action']) && $data['action'] === 'authenticate') {
            $this->clients[$clientId]['username'] = $data['username'];
            echo "Client {$clientId} authenticated as {$data['username']}\n";
        }
    }
    
    private function broadcastUpdates() {
        // Check for new updates from all users
        foreach ($this->clients as $clientId => $client) {
            if ($client['username']) {
                $this->sendUserUpdates($clientId, $client['username']);
            }
        }
    }
    
    private function sendUserUpdates($clientId, $username) {
        $updatesFile = "users/{$username}/real_time_updates.json";
        
        if (file_exists($updatesFile)) {
            $updates = json_decode(file_get_contents($updatesFile), true) ?: [];
            
            // Send only recent updates (last 30 seconds)
            $recentUpdates = array_filter($updates, function($update) {
                return (time() - $update['timestamp']) < 30;
            });
            
            if (!empty($recentUpdates)) {
                $message = json_encode([
                    'type' => 'updates',
                    'data' => $recentUpdates
                ]);
                
                $this->sendMessage($clientId, $message);
            }
        }
    }
    
    private function sendMessage($clientId, $message) {
        if (isset($this->clients[$clientId])) {
            $encoded = $this->encodeMessage($message);
            socket_write($this->clients[$clientId]['socket'], $encoded, strlen($encoded));
        }
    }
    
    private function disconnectClient($clientId) {
        if (isset($this->clients[$clientId])) {
            socket_close($this->clients[$clientId]['socket']);
            unset($this->clients[$clientId]);
            echo "Client {$clientId} disconnected\n";
        }
    }
    
    private function decodeMessage($data) {
        $length = ord($data[1]) & 127;
        
        if ($length == 126) {
            $masks = substr($data, 4, 4);
            $data = substr($data, 8);
        } elseif ($length == 127) {
            $masks = substr($data, 10, 4);
            $data = substr($data, 14);
        } else {
            $masks = substr($data, 2, 4);
            $data = substr($data, 6);
        }
        
        $text = '';
        for ($i = 0; $i < strlen($data); ++$i) {
            $text .= $data[$i] ^ $masks[$i % 4];
        }
        
        return $text;
    }
    
    private function encodeMessage($message) {
        $length = strlen($message);
        
        if ($length <= 125) {
            return pack('CC', 129, $length) . $message;
        } elseif ($length <= 65535) {
            return pack('CCn', 129, 126, $length) . $message;
        } else {
            return pack('CCNN', 129, 127, 0, $length) . $message;
        }
    }
}

// Uncomment to run WebSocket server
// $server = new P2PWebSocketServer();
// $server->run();
?>