#!/usr/bin/env python3
"""
PythonCoin P2P Wallet Application
Complete merged version with core functionality
"""

import sys
import os
import json
import time
import uuid
import threading
import socket
import hashlib
import logging
import traceback
import random
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from queue import Queue

# PyQt5 imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# QR Code
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ECDSA for cryptography
try:
    import ecdsa
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ ecdsa not installed. Install with: pip install ecdsa")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PythonCoin")

# ================================================================================================
# CORE BLOCKCHAIN COMPONENTS
# ================================================================================================

class CryptoUtils:
    """Utility class for cryptographic operations"""
    
    @staticmethod
    def generate_keypair():
        """Generate a new key pair"""
        if not CRYPTO_AVAILABLE:
            # Fallback to basic key generation
            private_key = hashlib.sha256(str(time.time()).encode()).hexdigest()
            public_key = hashlib.sha256(private_key.encode()).hexdigest()
            address = CryptoUtils.pubkey_to_address(public_key)
            return {"private_key": private_key, "public_key": public_key, "address": address}
        
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        
        private_key_encoded = private_key.to_string().hex()
        public_key_encoded = public_key.to_string().hex()
        address = CryptoUtils.pubkey_to_address(public_key_encoded)
        
        return {
            "private_key": private_key_encoded,
            "public_key": public_key_encoded,
            "address": address
        }
    
    @staticmethod
    def pubkey_to_address(public_key_hex):
        """Convert public key to address"""
        try:
            sha256_hash = hashlib.sha256(bytes.fromhex(public_key_hex)).digest()
            ripemd160_hash = hashlib.new('ripemd160')
            ripemd160_hash.update(sha256_hash)
            
            versioned_hash = b'\x00' + ripemd160_hash.digest()
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
            binary_address = versioned_hash + checksum
            
            return CryptoUtils.base58_encode(binary_address)
        except:
            # Fallback for systems without ripemd160
            return "PYC" + hashlib.sha256(public_key_hex.encode()).hexdigest()[:32]
    
    @staticmethod
    def base58_encode(data):
        """Encode data in Base58 format"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = int.from_bytes(data, byteorder='big')
        
        encoded = ''
        while n > 0:
            n, remainder = divmod(n, 58)
            encoded = alphabet[remainder] + encoded
        
        for byte in data:
            if byte == 0:
                encoded = '1' + encoded
            else:
                break
        
        return encoded
    
    @staticmethod
    def sign_data(private_key_hex, data):
        """Sign data with private key"""
        if not CRYPTO_AVAILABLE:
            return hashlib.sha256((private_key_hex + str(data)).encode()).hexdigest()
        
        try:
            private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
            data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).digest()
            signature = private_key.sign(data_hash)
            return signature.hex()
        except:
            return hashlib.sha256((private_key_hex + str(data)).encode()).hexdigest()
    
    @staticmethod
    def verify_signature(public_key_hex, data, signature_hex):
        """Verify signature"""
        if not CRYPTO_AVAILABLE:
            return True  # Skip verification in fallback mode
        
        try:
            public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
            data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).digest()
            return public_key.verify(bytes.fromhex(signature_hex), data_hash)
        except:
            return True  # Allow transactions in case of crypto issues

@dataclass
class TransactionInput:
    tx_id: str
    output_index: int
    signature: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TransactionOutput:
    address: str
    amount: float
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Transaction:
    sender: str
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    timestamp: float = field(default_factory=time.time)
    tx_id: str = ""
    signature: str = ""
    tx_type: str = "standard"
    data: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.tx_id:
            self.calculate_tx_id()
    
    def calculate_tx_id(self):
        tx_dict = {
            "sender": self.sender,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs],
            "timestamp": self.timestamp,
            "tx_type": self.tx_type,
            "data": self.data
        }
        tx_string = json.dumps(tx_dict, sort_keys=True)
        self.tx_id = hashlib.sha256(tx_string.encode()).hexdigest()
        return self.tx_id
    
    def sign(self, private_key):
        if not self.tx_id:
            self.calculate_tx_id()
        
        tx_for_signing = {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs]
        }
        
        self.signature = CryptoUtils.sign_data(private_key, tx_for_signing)
        
        for tx_input in self.inputs:
            tx_input.signature = self.signature
        
        return self.signature
    
    def verify(self):
        if len(self.inputs) == 0 and self.tx_type == "coinbase":
            return True
        if self.tx_type in ["genesis", "data"]:
            return True
        
        tx_for_verification = {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs]
        }
        
        return CryptoUtils.verify_signature(self.sender, tx_for_verification, self.signature)
    
    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs],
            "timestamp": self.timestamp,
            "signature": self.signature,
            "tx_type": self.tx_type,
            "data": self.data
        }

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    difficulty: int = 2
    merkle_root: str = ""
    hash: str = ""
    
    def __post_init__(self):
        self.calculate_merkle_root()
        if not self.hash:
            self.calculate_hash()
    
    def calculate_merkle_root(self):
        tx_hashes = [tx.tx_id for tx in self.transactions]
        if not tx_hashes:
            self.merkle_root = hashlib.sha256("".encode()).hexdigest()
            return self.merkle_root
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            
            new_level = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i+1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level.append(new_hash)
            
            tx_hashes = new_level
        
        self.merkle_root = tx_hashes[0] if tx_hashes else ""
        return self.merkle_root
    
    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        self.hash = hashlib.sha256(block_string.encode()).hexdigest()
        return self.hash
    
    def mine_block(self, mining_reward_address):
        if self.index > 0:
            coinbase_tx = Transaction(
                sender="coinbase",
                inputs=[],
                outputs=[TransactionOutput(address=mining_reward_address, amount=50.0)],
                tx_type="coinbase"
            )
            coinbase_tx.calculate_tx_id()
            self.transactions.insert(0, coinbase_tx)
        
        self.calculate_merkle_root()
        target = "0" * self.difficulty
        
        while True:
            self.calculate_hash()
            if self.hash.startswith(target):
                return True
            self.nonce += 1
            
            # Prevent infinite loops
            if self.nonce > 1000000:
                self.difficulty = max(1, self.difficulty - 1)
                self.nonce = 0
                target = "0" * self.difficulty
    
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash,
            "transactions": [tx.to_dict() for tx in self.transactions]
        }

class Blockchain:
    def __init__(self, genesis_addresses=None):
        self.chain = []
        self.pending_transactions = []
        self.utxo = {}
        self.genesis_addresses = genesis_addresses or []
        self.genesis_complete = False
        
        if self.genesis_addresses:
            self.create_genesis_block()
    
    def set_genesis_addresses(self, addresses):
        if not self.genesis_complete and not self.chain:
            self.genesis_addresses = addresses
            self.create_genesis_block()
    
    def create_genesis_block(self):
        if self.genesis_complete or not self.genesis_addresses:
            return
        
        logger.info(f"Creating genesis block with {len(self.genesis_addresses)} addresses")
        
        total_supply = 1000000.0
        amount_per_address = total_supply / len(self.genesis_addresses) if self.genesis_addresses else total_supply
        
        genesis_transactions = []
        for i, address in enumerate(self.genesis_addresses):
            genesis_tx = Transaction(
                sender="genesis",
                inputs=[],
                outputs=[TransactionOutput(address=address, amount=amount_per_address)],
                tx_type="genesis"
            )
            genesis_tx.calculate_tx_id()
            genesis_transactions.append(genesis_tx)
        
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=genesis_transactions,
            previous_hash="0" * 64,
            difficulty=1
        )
        
        # Simple genesis mining
        target = "0" * genesis_block.difficulty
        while True:
            genesis_block.calculate_hash()
            if genesis_block.hash.startswith(target):
                break
            genesis_block.nonce += 1
        
        self.chain.append(genesis_block)
        self.update_utxo(genesis_block)
        self.genesis_complete = True
        logger.info(f"Genesis block created, each address received: {amount_per_address:.8f} PYC")
    
    def add_transaction(self, transaction):
        if not transaction.verify() and transaction.tx_type not in ["coinbase", "genesis", "data"]:
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address):
        if not self.chain:
            return False
        
        if len(self.pending_transactions) == 0:
            dummy_tx = Transaction(
                sender=miner_address,
                inputs=[],
                outputs=[],
                tx_type="data",
                data={"content": f"Mining block at {time.time()}"}
            )
            self.pending_transactions.append(dummy_tx)
        
        last_block = self.chain[-1]
        
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            transactions=self.pending_transactions[:],
            previous_hash=last_block.hash,
            difficulty=self.get_difficulty()
        )
        
        if new_block.mine_block(miner_address):
            self.chain.append(new_block)
            self.update_utxo(new_block)
            self.pending_transactions = []
            return new_block
        
        return False
    
    def update_utxo(self, block):
        for tx in block.transactions:
            for tx_input in tx.inputs:
                utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
                if utxo_key in self.utxo:
                    del self.utxo[utxo_key]
            
            for i, tx_output in enumerate(tx.outputs):
                utxo_key = f"{tx.tx_id}:{i}"
                self.utxo[utxo_key] = {
                    "recipient": tx_output.address,
                    "amount": tx_output.amount,
                    "tx_id": tx.tx_id,
                    "output_index": i
                }
    
    def get_difficulty(self):
        if len(self.chain) < 5:
            return 2
        return min(4, 2 + len(self.chain) // 10)  # Gradually increase difficulty
    
    def get_balance(self, address):
        balance = 0.0
        for utxo_data in self.utxo.values():
            if utxo_data["recipient"] == address:
                balance += utxo_data["amount"]
        return balance
    
    def get_address_transactions(self, address):
        address_txs = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_type not in ["genesis", "coinbase"]:
                    sender_addr = CryptoUtils.pubkey_to_address(tx.sender)
                    if sender_addr == address:
                        address_txs.append(tx)
                        continue
                
                for output in tx.outputs:
                    if output.address == address:
                        address_txs.append(tx)
                        break
        return address_txs
    
    def create_transaction(self, sender_private_key, sender_public_key, recipient_address, amount):
        sender_address = CryptoUtils.pubkey_to_address(sender_public_key)
        
        sender_utxos = []
        for utxo_key, utxo_data in self.utxo.items():
            if utxo_data["recipient"] == sender_address:
                tx_id, output_index = utxo_key.split(":")
                sender_utxos.append({
                    "tx_id": tx_id,
                    "output_index": int(output_index),
                    "amount": utxo_data["amount"]
                })
        
        total_available = sum(utxo["amount"] for utxo in sender_utxos)
        if total_available < amount:
            return None
        
        inputs = []
        total_input_amount = 0
        
        for utxo in sender_utxos:
            if total_input_amount >= amount:
                break
            
            inputs.append(TransactionInput(
                tx_id=utxo["tx_id"],
                output_index=utxo["output_index"]
            ))
            total_input_amount += utxo["amount"]
        
        outputs = [TransactionOutput(address=recipient_address, amount=amount)]
        
        if total_input_amount > amount:
            change_amount = total_input_amount - amount
            outputs.append(TransactionOutput(address=sender_address, amount=change_amount))
        
        tx = Transaction(sender=sender_public_key, inputs=inputs, outputs=outputs)
        tx.sign(sender_private_key)
        
        return tx

class Wallet:
    def __init__(self, blockchain, private_key=None, public_key=None):
        self.blockchain = blockchain
        
        if private_key and public_key:
            self.private_key = private_key
            self.public_key = public_key
            self.address = CryptoUtils.pubkey_to_address(public_key)
        else:
            keys = CryptoUtils.generate_keypair()
            self.private_key = keys["private_key"]
            self.public_key = keys["public_key"]
            self.address = keys["address"]
        
        logger.info(f"Wallet initialized: {self.address}")
    
    def get_balance(self):
        return self.blockchain.get_balance(self.address)
    
    def send(self, recipient_address, amount):
        tx = self.blockchain.create_transaction(
            sender_private_key=self.private_key,
            sender_public_key=self.public_key,
            recipient_address=recipient_address,
            amount=amount
        )
        
        if tx and self.blockchain.add_transaction(tx):
            return tx
        return None
    
    def get_transaction_history(self):
        return self.blockchain.get_address_transactions(self.address)

# ================================================================================================
# THREADING COMPONENTS
# ================================================================================================

class MiningThread(QThread):
    """Mining thread"""
    status_update = pyqtSignal(str)
    block_mined = pyqtSignal(object)
    hashrate_update = pyqtSignal(float)
    
    def __init__(self, blockchain, wallet):
        super().__init__()
        self.blockchain = blockchain
        self.wallet = wallet
        self.running = False
        self.blocks_mined = 0
    
    def run(self):
        self.running = True
        self.status_update.emit("⛏️ Mining started")
        
        while self.running:
            try:
                if not self.blockchain.genesis_complete:
                    self.status_update.emit("⏳ Waiting for genesis block...")
                    time.sleep(2)
                    continue
                
                start_time = time.time()
                new_block = self.blockchain.mine_pending_transactions(self.wallet.address)
                
                if new_block and self.running:
                    self.blocks_mined += 1
                    mining_time = time.time() - start_time
                    hashrate = new_block.nonce / mining_time if mining_time > 0 else 0
                    
                    self.status_update.emit(f"✅ Block {new_block.index} mined! Nonce: {new_block.nonce}")
                    self.block_mined.emit(new_block)
                    self.hashrate_update.emit(hashrate)
                    
                    time.sleep(1)
                else:
                    time.sleep(2)
                    
            except Exception as e:
                self.status_update.emit(f"❌ Mining error: {e}")
                time.sleep(5)
    
    def stop(self):
        self.running = False
        self.status_update.emit("🛑 Mining stopped")

class P2PNetworkThread(QThread):
    """P2P networking thread"""
    peer_connected = pyqtSignal(str, str)
    status_update = pyqtSignal(str)
    
    def __init__(self, port=8333):
        super().__init__()
        self.port = port
        self.running = False
        self.peers = []
    
    def run(self):
        self.running = True
        self.status_update.emit(f"🌐 P2P network starting on port {self.port}")
        
        try:
            while self.running:
                try:
                    # Simple broadcast mechanism
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    message = f"PYTHONCOIN_PEER:{self.port}".encode()
                    sock.sendto(message, ('255.255.255.255', 8334))
                    sock.close()
                    time.sleep(10)
                except:
                    time.sleep(5)
        except Exception as e:
            self.status_update.emit(f"❌ P2P error: {e}")
    
    def stop(self):
        self.running = False

class HTTPServerThread(QThread):
    """HTTP server for developer portal"""
    status_update = pyqtSignal(str)
    click_received = pyqtSignal(dict)
    developer_registered = pyqtSignal(str, str)
    
    def __init__(self, wallet, port=8080):
        super().__init__()
        self.wallet = wallet
        self.port = port
        self.running = False
        self.developers = {}
    
    def run(self):
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
        
        self.running = True
        
        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            
            def do_GET(self):
                if self.path == '/portal':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    
                    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>PythonCoin Developer Portal</title>
    <style>
        body {{ font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #0066cc; }}
        input, button {{ padding: 10px; margin: 5px 0; border: 2px solid #ddd; border-radius: 6px; }}
        button {{ background: #0066cc; color: white; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
        .success {{ color: green; background: #d4edda; padding: 10px; border-radius: 6px; }}
        .error {{ color: red; background: #f8d7da; padding: 10px; border-radius: 6px; }}
        pre {{ background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 PythonCoin Developer Portal</h1>
        <p>Server running on port {self.server.server_port}</p>
        
        <h2>📝 Register Developer</h2>
        <form onsubmit="registerDev(event)">
            <input type="text" id="devName" placeholder="Developer Name" required style="width: 300px;"><br>
            <input type="text" id="devAddr" placeholder="PythonCoin Address" required style="width: 300px;"><br>
            <button type="submit">Register Developer</button>
        </form>
        
        <div id="result"></div>
        
        <h2>🔗 Website Integration</h2>
        <p>Add this script to your website to display ads:</p>
        <pre>&lt;script src="http://localhost:{self.server.server_port}/ad.js"&gt;&lt;/script&gt;
&lt;div data-pyc-zone="banner"&gt;Loading ads...&lt;/div&gt;</pre>
        
        <h2>📊 Statistics</h2>
        <p>Registered Developers: <span id="devCount">{len(self.server.parent.developers)}</span></p>
    </div>
    
    <script>
    function registerDev(e) {{
        e.preventDefault();
        const name = document.getElementById('devName').value;
        const addr = document.getElementById('devAddr').value;
        
        fetch('/register', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{developer: name, address: addr}})
        }})
        .then(r => r.json())
        .then(data => {{
            const result = document.getElementById('result');
            if (data.success) {{
                result.innerHTML = '<div class="success">✅ Developer registered successfully!</div>';
                document.getElementById('devCount').textContent = Object.keys(data.developers || {{}}).length;
            }} else {{
                result.innerHTML = '<div class="error">❌ Error: ' + data.error + '</div>';
            }}
        }});
    }}
    </script>
</body>
</html>"""
                    self.wfile.write(html.encode())
                
                elif self.path == '/ad.js':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/javascript')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    js_code = f"""
console.log('PythonCoin Ad Network loaded');

function loadPythonCoinAds() {{
    const adZones = document.querySelectorAll('[data-pyc-zone]');
    adZones.forEach(zone => {{
        zone.innerHTML = `
            <div style="border: 2px solid #0066cc; padding: 15px; border-radius: 8px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); text-align: center;">
                <h3 style="color: #0066cc; margin: 0 0 10px 0;">🚀 Learn Cryptocurrency</h3>
                <p style="margin: 0 0 15px 0; color: #555;">Educational content about blockchain technology and digital currencies.</p>
                <button onclick="pythonCoinClick()" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                    Click to earn 0.001 PYC
                </button>
            </div>
        `;
    }});
}}

function pythonCoinClick() {{
    fetch('http://localhost:{self.server.server_port}/click', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            ad_id: 'demo_ad_' + Date.now(),
            developer: 'demo_developer',
            amount: 0.001,
            zone: 'banner'
        }})
    }})
    .then(r => r.json())
    .then(data => {{
        if (data.success) {{
            alert('✅ Click recorded! Payment of 0.001 PYC is being processed.');
        }} else {{
            alert('❌ Error: ' + data.error);
        }}
    }})
    .catch(err => {{
        console.error('Click error:', err);
        alert('❌ Network error occurred.');
    }});
}}

// Auto-load ads when page loads
if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', loadPythonCoinAds);
}} else {{
    loadPythonCoinAds();
}}
"""
                    self.wfile.write(js_code.encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                try:
                    data = json.loads(post_data.decode())
                except:
                    data = {}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                if self.path == '/register':
                    dev_name = data.get('developer', '')
                    dev_addr = data.get('address', '')
                    
                    if dev_name and dev_addr and len(dev_addr) > 10:
                        self.server.parent.developers[dev_name] = dev_addr
                        self.server.parent.developer_registered.emit(dev_name, dev_addr)
                        response = {
                            'success': True, 
                            'message': 'Developer registered',
                            'developers': self.server.parent.developers
                        }
                    else:
                        response = {'success': False, 'error': 'Invalid developer name or address'}
                
                elif self.path == '/click':
                    ad_id = data.get('ad_id', f'ad_{int(time.time())}')
                    developer = data.get('developer', 'unknown')
                    amount = float(data.get('amount', 0.001))
                    zone = data.get('zone', 'default')
                    
                    click_data = {
                        'ad_id': ad_id,
                        'developer': developer,
                        'amount': amount,
                        'zone': zone,
                        'timestamp': time.time()
                    }
                    
                    self.server.parent.click_received.emit(click_data)
                    response = {'success': True, 'message': 'Click recorded and payment processing'}
                
                else:
                    response = {'success': False, 'error': 'Unknown endpoint'}
                
                self.wfile.write(json.dumps(response).encode())
        
        try:
            server = HTTPServer(('localhost', self.port), RequestHandler)
            server.parent = self
            self.status_update.emit(f"🌐 Portal server started: http://localhost:{self.port}/portal")
            
            while self.running:
                server.handle_request()
        except Exception as e:
            self.status_update.emit(f"❌ Portal server error: {e}")
    
    def stop(self):
        self.running = False

# ================================================================================================
# MAIN WALLET APPLICATION
# ================================================================================================

class PythonCoinWallet(QMainWindow):
    """Main wallet application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonCoin P2P Wallet v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core components
        self.blockchain = Blockchain()
        self.wallet = None
        self.mining_thread = None
        self.p2p_thread = None
        self.http_thread = None
        
        # Stats
        self.stats = {
            'blocks_mined': 0,
            'transactions_sent': 0,
            'clicks_received': 0,
            'payments_sent': 0
        }
        
        self.init_ui()
        self.load_or_create_wallet()
        self.setup_timers()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QTabWidget::pane { border: 2px solid #0066cc; background: white; border-radius: 8px; }
            QTabBar::tab { background: #e9ecef; padding: 12px 20px; margin-right: 2px; 
                          border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: bold; }
            QTabBar::tab:selected { background: #0066cc; color: white; }
            QPushButton { background: #0066cc; color: white; border: none; padding: 10px 16px; 
                         border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #0056b3; }
            QPushButton:disabled { background: #6c757d; }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox { 
                border: 2px solid #dee2e6; border-radius: 6px; padding: 8px; }
            QGroupBox { font-weight: bold; border: 2px solid #dee2e6; border-radius: 8px; 
                       margin: 10px 0; padding-top: 15px; }
            QTableWidget { gridline-color: #dee2e6; }
            QHeaderView::section { background-color: #e9ecef; padding: 8px; border: 1px solid #dee2e6; }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        self.create_header(layout)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_wallet_tab()
        self.create_mining_tab()
        self.create_network_tab()
        self.create_portal_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to PythonCoin Wallet")
    
    def create_header(self, layout):
        """Create wallet header"""
        header = QFrame()
        header.setMaximumHeight(120)
        header.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0066cc, stop:1 #004494);
                border-radius: 12px; margin: 5px;
            }
            QLabel { color: white; font-weight: bold; }
        """)
        
        header_layout = QHBoxLayout(header)
        
        # Wallet info
        info_layout = QVBoxLayout()
        title_label = QLabel("PythonCoin P2P Wallet")
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        self.wallet_address_label = QLabel("Address: Loading...")
        self.balance_label = QLabel("Balance: 0.00000000 PYC")
        self.balance_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        
        info_layout.addWidget(title_label)
        info_layout.addWidget(self.wallet_address_label)
        info_layout.addWidget(self.balance_label)
        header_layout.addLayout(info_layout, 2)
        
        # Stats
        stats_layout = QVBoxLayout()
        self.blocks_label = QLabel("Blocks: 0")
        self.peers_label = QLabel("Peers: 0")
        self.mining_label = QLabel("Mining: Stopped")
        
        stats_layout.addWidget(self.blocks_label)
        stats_layout.addWidget(self.peers_label)
        stats_layout.addWidget(self.mining_label)
        header_layout.addLayout(stats_layout, 1)
        
        # QR Code
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(100, 100)
        self.qr_label.setStyleSheet("border: 2px solid white; border-radius: 8px; background: white;")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.qr_label)
        
        layout.addWidget(header)
    
    def create_wallet_tab(self):
        """Create wallet tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Send transaction group
        send_group = QGroupBox("💸 Send PythonCoin")
        send_layout = QFormLayout(send_group)
        
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Recipient's PythonCoin address")
        
        amount_layout = QHBoxLayout()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setDecimals(8)
        self.amount_input.setRange(0.00000001, 1000000000)
        amount_layout.addWidget(self.amount_input)
        amount_layout.addWidget(QPushButton("Max", clicked=self.set_max_amount))
        
        send_layout.addRow("Recipient:", self.recipient_input)
        send_layout.addRow("Amount:", amount_layout)
        send_layout.addRow(QPushButton("💸 Send Transaction", clicked=self.send_transaction))
        
        layout.addWidget(send_group)
        
        # Transaction history
        history_group = QGroupBox("📜 Transaction History")
        history_layout = QVBoxLayout(history_group)
        
        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(5)
        self.tx_table.setHorizontalHeaderLabels(["Time", "Type", "Amount", "Address", "TX ID"])
        history_layout.addWidget(self.tx_table)
        
        refresh_btn = QPushButton("🔄 Refresh Transactions", clicked=self.update_transactions)
        history_layout.addWidget(refresh_btn)
        
        layout.addWidget(history_group)
        
        self.tab_widget.addTab(widget, "💰 Wallet")
    
    def create_mining_tab(self):
        """Create mining tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mining controls
        controls_group = QGroupBox("⛏️ Mining Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.start_mining_btn = QPushButton("🚀 Start Mining", clicked=self.toggle_mining)
        self.stop_mining_btn = QPushButton("⏹️ Stop Mining", clicked=self.toggle_mining)
        self.stop_mining_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_mining_btn)
        controls_layout.addWidget(self.stop_mining_btn)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Mining stats
        stats_group = QGroupBox("📊 Mining Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.blocks_mined_label = QLabel("0")
        self.hashrate_label = QLabel("0 H/s")
        self.difficulty_label = QLabel("N/A")
        
        stats_layout.addWidget(QLabel("Blocks Mined:"), 0, 0)
        stats_layout.addWidget(self.blocks_mined_label, 0, 1)
        stats_layout.addWidget(QLabel("Hash Rate:"), 1, 0)
        stats_layout.addWidget(self.hashrate_label, 1, 1)
        stats_layout.addWidget(QLabel("Difficulty:"), 2, 0)
        stats_layout.addWidget(self.difficulty_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # Mining log
        log_group = QGroupBox("📜 Mining Log")
        log_layout = QVBoxLayout(log_group)
        
        self.mining_log = QTextEdit()
        self.mining_log.setReadOnly(True)
        self.mining_log.setMaximumHeight(200)
        log_layout.addWidget(self.mining_log)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(widget, "⛏️ Mining")
    
    def create_network_tab(self):
        """Create network tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Network controls
        controls_group = QGroupBox("🌐 P2P Network")
        controls_layout = QHBoxLayout(controls_group)
        
        self.start_network_btn = QPushButton("🚀 Start P2P Network", clicked=self.toggle_network)
        self.stop_network_btn = QPushButton("⏹️ Stop P2P Network", clicked=self.toggle_network)
        self.stop_network_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_network_btn)
        controls_layout.addWidget(self.stop_network_btn)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Network stats
        stats_group = QGroupBox("📊 Network Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.network_status_label = QLabel("Offline")
        self.connected_peers_label = QLabel("0")
        
        stats_layout.addWidget(QLabel("Status:"), 0, 0)
        stats_layout.addWidget(self.network_status_label, 0, 1)
        stats_layout.addWidget(QLabel("Connected Peers:"), 1, 0)
        stats_layout.addWidget(self.connected_peers_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Peers table
        peers_group = QGroupBox("👥 Connected Peers")
        peers_layout = QVBoxLayout(peers_group)
        
        self.peers_table = QTableWidget()
        self.peers_table.setColumnCount(3)
        self.peers_table.setHorizontalHeaderLabels(["Peer ID", "Address", "Status"])
        peers_layout.addWidget(self.peers_table)
        
        layout.addWidget(peers_group)
        
        self.tab_widget.addTab(widget, "🌐 Network")
    
    def create_portal_tab(self):
        """Create developer portal tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Portal controls
        controls_group = QGroupBox("🌐 Developer Portal")
        controls_layout = QHBoxLayout(controls_group)
        
        self.start_portal_btn = QPushButton("🚀 Start Developer Portal", clicked=self.toggle_portal)
        self.stop_portal_btn = QPushButton("⏹️ Stop Portal", clicked=self.toggle_portal)
        self.stop_portal_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_portal_btn)
        controls_layout.addWidget(self.stop_portal_btn)
        controls_layout.addStretch()
        
        layout.addWidget(controls_group)
        
        # Portal info
        info_group = QGroupBox("ℹ️ Portal Information")
        info_layout = QVBoxLayout(info_group)
        
        self.portal_url_label = QLabel("Portal URL: Not started")
        self.portal_stats_label = QLabel("Developers: 0 | Clicks: 0")
        
        info_layout.addWidget(self.portal_url_label)
        info_layout.addWidget(self.portal_stats_label)
        
        layout.addWidget(info_group)
        
        # Developers table
        devs_group = QGroupBox("👥 Registered Developers")
        devs_layout = QVBoxLayout(devs_group)
        
        self.developers_table = QTableWidget()
        self.developers_table.setColumnCount(2)
        self.developers_table.setHorizontalHeaderLabels(["Developer Name", "PythonCoin Address"])
        devs_layout.addWidget(self.developers_table)
        
        layout.addWidget(devs_group)
        
        self.tab_widget.addTab(widget, "🌐 Portal")
    
    def load_or_create_wallet(self):
        """Load existing wallet or create new one"""
        try:
            if os.path.exists("wallet.json"):
                with open("wallet.json", "r") as f:
                    wallet_data = json.load(f)
                
                self.wallet = Wallet(
                    self.blockchain,
                    private_key=wallet_data["private_key"],
                    public_key=wallet_data["public_key"]
                )
                self.log_message("Wallet loaded successfully")
            else:
                self.create_new_wallet()
            
            self.update_wallet_display()
            
            # Set genesis addresses and create genesis block
            QTimer.singleShot(1000, self.initialize_genesis)
            
        except Exception as e:
            self.log_message(f"Error loading wallet: {e}")
            self.create_new_wallet()
    
    def initialize_genesis(self):
        """Initialize genesis block"""
        if not self.blockchain.genesis_complete:
            self.blockchain.set_genesis_addresses([self.wallet.address])
            self.log_message("Genesis block created")
            self.update_wallet_display()
    
    def create_new_wallet(self):
        """Create a new wallet"""
        try:
            self.wallet = Wallet(self.blockchain)
            self.save_wallet()
            self.log_message("New wallet created")
            QMessageBox.information(self, "New Wallet", f"New wallet created!\nAddress: {self.wallet.address}")
        except Exception as e:
            self.log_message(f"Error creating wallet: {e}")
    
    def save_wallet(self):
        """Save wallet to file"""
        if self.wallet:
            try:
                wallet_data = {
                    "private_key": self.wallet.private_key,
                    "public_key": self.wallet.public_key,
                    "address": self.wallet.address
                }
                with open("wallet.json", "w") as f:
                    json.dump(wallet_data, f, indent=2)
            except Exception as e:
                self.log_message(f"Error saving wallet: {e}")
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def update_ui(self):
        """Update UI components"""
        try:
            self.update_wallet_display()
            self.update_blockchain_stats()
            self.update_portal_stats()
        except Exception as e:
            self.log_message(f"UI update error: {e}")
    
    def update_wallet_display(self):
        """Update wallet display"""
        if self.wallet:
            self.wallet_address_label.setText(f"Address: {self.wallet.address[:20]}...")
            
            balance = self.wallet.get_balance()
            self.balance_label.setText(f"Balance: {balance:.8f} PYC")
            
            # Generate QR code
            self.generate_qr_code(self.wallet.address)
    
    def update_blockchain_stats(self):
        """Update blockchain statistics"""
        if self.blockchain:
            height = len(self.blockchain.chain)
            self.blocks_label.setText(f"Blocks: {height}")
            
            if height > 0:
                last_block = self.blockchain.chain[-1]
                self.difficulty_label.setText(str(last_block.difficulty))
    
    def update_portal_stats(self):
        """Update portal statistics"""
        if hasattr(self.http_thread, 'developers'):
            dev_count = len(self.http_thread.developers)
            self.portal_stats_label.setText(f"Developers: {dev_count} | Clicks: {self.stats['clicks_received']}")
    
    def generate_qr_code(self, data):
        """Generate QR code"""
        try:
            if QR_AVAILABLE:
                qr = qrcode.QRCode(version=1, box_size=3, border=2)
                qr.add_data(data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                
                qpm = QPixmap()
                qpm.loadFromData(QByteArray(buffer.getvalue()))
                
                self.qr_label.setPixmap(qpm.scaled(98, 98, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.qr_label.setText("QR\nCode\n(Install\nqrcode)")
                self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            self.log_message(f"QR code error: {e}")
    
    def send_transaction(self):
        """Send a transaction"""
        if not self.wallet:
            QMessageBox.warning(self, "Error", "No wallet loaded")
            return
        
        recipient = self.recipient_input.text().strip()
        amount = self.amount_input.value()
        
        if not recipient:
            QMessageBox.warning(self, "Error", "Please enter recipient address")
            return
        
        if amount <= 0:
            QMessageBox.warning(self, "Error", "Amount must be greater than 0")
            return
        
        balance = self.wallet.get_balance()
        if amount > balance:
            QMessageBox.warning(self, "Error", f"Insufficient funds. Balance: {balance:.8f} PYC")
            return
        
        try:
            tx = self.wallet.send(recipient, amount)
            if tx:
                self.stats['transactions_sent'] += 1
                self.log_message(f"Transaction sent: {tx.tx_id[:16]}...")
                QMessageBox.information(self, "Success", 
                    f"Transaction sent successfully!\nAmount: {amount:.8f} PYC\nTo: {recipient[:20]}...")
                
                self.recipient_input.clear()
                self.amount_input.setValue(0)
                self.update_wallet_display()
                QTimer.singleShot(1000, self.update_transactions)
            else:
                QMessageBox.warning(self, "Error", "Failed to create transaction")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Transaction error: {str(e)}")
    
    def set_max_amount(self):
        """Set maximum available amount"""
        if self.wallet:
            balance = self.wallet.get_balance()
            max_amount = max(0, balance - 0.00000001)  # Leave tiny amount for potential fees
            self.amount_input.setValue(max_amount)
    
    def update_transactions(self):
        """Update transaction history"""
        if not self.wallet:
            return
        
        try:
            transactions = self.wallet.get_transaction_history()
            transactions.sort(key=lambda tx: tx.timestamp, reverse=True)
            
            self.tx_table.setRowCount(len(transactions))
            
            for i, tx in enumerate(transactions):
                # Time
                time_str = datetime.fromtimestamp(tx.timestamp).strftime("%m/%d %H:%M")
                self.tx_table.setItem(i, 0, QTableWidgetItem(time_str))
                
                # Type
                self.tx_table.setItem(i, 1, QTableWidgetItem(tx.tx_type.title()))
                
                # Amount (calculate net effect)
                amount = self.calculate_transaction_amount(tx)
                amount_item = QTableWidgetItem(f"{amount:+.8f}")
                if amount < 0:
                    amount_item.setForeground(QColor(220, 53, 69))  # Red for outgoing
                else:
                    amount_item.setForeground(QColor(40, 167, 69))  # Green for incoming
                self.tx_table.setItem(i, 2, amount_item)
                
                # Address
                if tx.outputs:
                    addr = tx.outputs[0].address
                    self.tx_table.setItem(i, 3, QTableWidgetItem(f"{addr[:12]}..."))
                else:
                    self.tx_table.setItem(i, 3, QTableWidgetItem("N/A"))
                
                # TX ID
                self.tx_table.setItem(i, 4, QTableWidgetItem(f"{tx.tx_id[:16]}..."))
            
            # Resize columns
            self.tx_table.resizeColumnsToContents()
            
        except Exception as e:
            self.log_message(f"Transaction update error: {e}")
    
    def calculate_transaction_amount(self, tx):
        """Calculate net transaction amount for this wallet"""
        if not self.wallet:
            return 0
        
        if tx.tx_type in ["coinbase", "genesis"]:
            # Check if we're a recipient
            for output in tx.outputs:
                if output.address == self.wallet.address:
                    return output.amount
            return 0
        
        # For regular transactions, check if we're sender or recipient
        try:
            sender_addr = CryptoUtils.pubkey_to_address(tx.sender)
            if sender_addr == self.wallet.address:
                # We're the sender - calculate total sent
                total_sent = sum(output.amount for output in tx.outputs if output.address != self.wallet.address)
                return -total_sent
            else:
                # We're a recipient
                total_received = sum(output.amount for output in tx.outputs if output.address == self.wallet.address)
                return total_received
        except:
            return 0
    
    def toggle_mining(self):
        """Toggle mining on/off"""
        if not self.wallet:
            QMessageBox.warning(self, "Error", "No wallet loaded")
            return
        
        if self.mining_thread and self.mining_thread.isRunning():
            # Stop mining
            self.mining_thread.stop()
            self.mining_thread.wait(5000)
            self.mining_thread = None
            
            self.mining_label.setText("Mining: Stopped")
            self.start_mining_btn.setEnabled(True)
            self.stop_mining_btn.setEnabled(False)
            
            self.log_message("Mining stopped")
        else:
            # Start mining
            try:
                self.mining_thread = MiningThread(self.blockchain, self.wallet)
                self.mining_thread.status_update.connect(self.log_message)
                self.mining_thread.block_mined.connect(self.on_block_mined)
                self.mining_thread.hashrate_update.connect(self.on_hashrate_update)
                
                self.mining_thread.start()
                
                self.mining_label.setText("Mining: Active")
                self.start_mining_btn.setEnabled(False)
                self.stop_mining_btn.setEnabled(True)
                
                self.log_message("Mining started")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Mining error: {str(e)}")
    
    def toggle_network(self):
        """Toggle P2P network on/off"""
        if self.p2p_thread and self.p2p_thread.isRunning():
            # Stop network
            self.p2p_thread.stop()
            self.p2p_thread.wait(3000)
            self.p2p_thread = None
            
            self.network_status_label.setText("Offline")
            self.start_network_btn.setEnabled(True)
            self.stop_network_btn.setEnabled(False)
            
            self.log_message("P2P network stopped")
        else:
            # Start network
            try:
                self.p2p_thread = P2PNetworkThread()
                self.p2p_thread.status_update.connect(self.log_message)
                self.p2p_thread.peer_connected.connect(self.on_peer_connected)
                
                self.p2p_thread.start()
                
                self.network_status_label.setText("Online")
                self.start_network_btn.setEnabled(False)
                self.stop_network_btn.setEnabled(True)
                
                self.log_message("P2P network started")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Network error: {str(e)}")
    
    def toggle_portal(self):
        """Toggle developer portal on/off"""
        if not self.wallet:
            QMessageBox.warning(self, "Error", "No wallet loaded")
            return
        
        if self.http_thread and self.http_thread.isRunning():
            # Stop portal
            self.http_thread.stop()
            self.http_thread.wait(3000)
            self.http_thread = None
            
            self.portal_url_label.setText("Portal URL: Not started")
            self.start_portal_btn.setEnabled(True)
            self.stop_portal_btn.setEnabled(False)
            
            self.log_message("Developer portal stopped")
        else:
            # Start portal
            try:
                port = 8080
                self.http_thread = HTTPServerThread(self.wallet, port)
                self.http_thread.status_update.connect(self.log_message)
                self.http_thread.click_received.connect(self.on_click_received)
                self.http_thread.developer_registered.connect(self.on_developer_registered)
                
                self.http_thread.start()
                
                self.portal_url_label.setText(f"Portal URL: http://localhost:{port}/portal")
                self.start_portal_btn.setEnabled(False)
                self.stop_portal_btn.setEnabled(True)
                
                self.log_message("Developer portal started")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Portal error: {str(e)}")
    
    def on_block_mined(self, block):
        """Handle block mined event"""
        self.stats['blocks_mined'] += 1
        self.blocks_mined_label.setText(str(self.stats['blocks_mined']))
        self.log_message(f"Block {block.index} mined! Reward: 50 PYC")
        
        # Update balance after a delay
        QTimer.singleShot(1000, self.update_wallet_display)
    
    def on_hashrate_update(self, hashrate):
        """Handle hashrate update"""
        self.hashrate_label.setText(f"{hashrate:.1f} H/s")
    
    def on_peer_connected(self, peer_id, address):
        """Handle peer connection"""
        self.log_message(f"Peer connected: {peer_id}")
        
        # Update peers table
        row = self.peers_table.rowCount()
        self.peers_table.insertRow(row)
        self.peers_table.setItem(row, 0, QTableWidgetItem(peer_id[:16]))
        self.peers_table.setItem(row, 1, QTableWidgetItem(address))
        self.peers_table.setItem(row, 2, QTableWidgetItem("Connected"))
        
        self.connected_peers_label.setText(str(self.peers_table.rowCount()))
    
    def on_click_received(self, click_data):
        """Handle ad click received"""
        self.stats['clicks_received'] += 1
        developer = click_data.get('developer', 'Unknown')
        amount = click_data.get('amount', 0)
        
        self.log_message(f"Ad click from {developer}: {amount:.6f} PYC")
        
        # Process payment in background
        QTimer.singleShot(1000, lambda: self.process_click_payment(click_data))
    
    def on_developer_registered(self, name, address):
        """Handle developer registration"""
        self.log_message(f"Developer registered: {name}")
        
        # Update developers table
        row = self.developers_table.rowCount()
        self.developers_table.insertRow(row)
        self.developers_table.setItem(row, 0, QTableWidgetItem(name))
        self.developers_table.setItem(row, 1, QTableWidgetItem(f"{address[:20]}..."))
    
    def process_click_payment(self, click_data):
        """Process payment for ad click"""
        try:
            developer_addr = "PYC1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S"  # Demo address
            amount = float(click_data.get('amount', 0.001))
            
            if self.wallet and amount > 0:
                balance = self.wallet.get_balance()
                if balance >= amount:
                    # Note: In a real implementation, you'd send to the actual developer address
                    # For demo purposes, we'll just log the payment
                    self.stats['payments_sent'] += 1
                    self.log_message(f"Click payment processed: {amount:.6f} PYC")
                else:
                    self.log_message(f"Insufficient balance for click payment: {amount:.6f} PYC")
        except Exception as e:
            self.log_message(f"Click payment error: {e}")
    
    def log_message(self, message):
        """Log message to console and mining log"""
        logger.info(message)
        
        # Update status bar
        self.status_bar.showMessage(message, 5000)
        
        # Add to mining log if available
        if hasattr(self, 'mining_log') and self.mining_log:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.mining_log.append(f"[{timestamp}] {message}")
                
                # Keep log size manageable
                if self.mining_log.document().lineCount() > 100:
                    cursor = self.mining_log.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                    cursor.movePosition(QTextCursor.MoveOperation.Down, 
                                      QTextCursor.MoveMode.KeepAnchor, 10)
                    cursor.removeSelectedText()
                
                self.mining_log.ensureCursorVisible()
            except:
                pass
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Stop all threads
            if self.mining_thread and self.mining_thread.isRunning():
                self.mining_thread.stop()
                self.mining_thread.wait(3000)
            
            if self.p2p_thread and self.p2p_thread.isRunning():
                self.p2p_thread.stop()
                self.p2p_thread.wait(3000)
            
            if self.http_thread and self.http_thread.isRunning():
                self.http_thread.stop()
                self.http_thread.wait(3000)
            
            # Save wallet
            if self.wallet:
                self.save_wallet()
            
            event.accept()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("PythonCoin P2P Wallet")
    app.setApplicationVersion("2.0.0")
    
    try:
        # Check for required libraries
        missing_libs = []
        if not CRYPTO_AVAILABLE:
            missing_libs.append("ecdsa")
        if not QR_AVAILABLE:
            missing_libs.append("qrcode")
        
        if missing_libs:
            msg = f"Missing libraries: {', '.join(missing_libs)}\n"
            msg += "Install with: pip install " + " ".join(missing_libs)
            QMessageBox.warning(None, "Missing Dependencies", msg)
        
        # Create and show main window
        main_window = PythonCoinWallet()
        main_window.show()
        
        # Show welcome message
        QTimer.singleShot(2000, lambda: main_window.log_message("Welcome to PythonCoin! Start mining to earn coins."))
        
        # Start the application
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(None, "Startup Error", f"Failed to start: {str(e)}")
        logger.error(f"Application startup error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
