#!/usr/bin/env python3
"""
Blockchain Validation Script for PythonCoin
Validates blockchain integrity, UTXO consistency, and genesis distribution
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pythoncoin import Blockchain, Wallet, CryptoUtils
except ImportError:
    print("❌ Error: Could not import pythoncoin module")
    print("Make sure pythoncoin.py is in the same directory")
    sys.exit(1)

class BlockchainValidator:
    def __init__(self):
        self.blockchain = None
        self.issues = []
        self.warnings = []
        
    def load_wallet_data(self):
        """Load wallet data if available"""
        wallet_files = ['wallet.json'] + [f'wallet_{i}.json' for i in range(1, 6)]
        wallets = []
        
        for wallet_file in wallet_files:
            if os.path.exists(wallet_file):
                try:
                    with open(wallet_file, 'r') as f:
                        wallet_data = json.load(f)
                        wallets.append({
                            'file': wallet_file,
                            'address': wallet_data.get('address', 'Unknown'),
                            'private_key': wallet_data.get('private_key', ''),
                            'public_key': wallet_data.get('public_key', '')
                        })
                except Exception as e:
                    self.warnings.append(f"Could not load {wallet_file}: {e}")
        
        return wallets
    
    def validate_genesis_block(self):
        """Validate the genesis block structure and distribution"""
        print("🏗️ Validating Genesis Block...")
        
        if not self.blockchain.chain:
            self.issues.append("No blocks in blockchain")
            return False
        
        genesis_block = self.blockchain.chain[0]
        
        # Check genesis block properties
        if genesis_block.index != 0:
            self.issues.append(f"Genesis block index should be 0, got {genesis_block.index}")
        
        if genesis_block.previous_hash != "0" * 64:
            self.issues.append("Genesis block should have null previous hash")
        
        # Check genesis transactions
        genesis_txs = [tx for tx in genesis_block.transactions if tx.tx_type == "genesis"]
        
        if not genesis_txs:
            self.issues.append("No genesis transactions found in genesis block")
            return False
        
        print(f"   ✅ Found {len(genesis_txs)} genesis distribution transactions")
        
        # Calculate total distribution
        total_distributed = 0
        unique_recipients = set()
        
        for tx in genesis_txs:
            for output in tx.outputs:
                total_distributed += output.amount
                unique_recipients.add(output.address)
        
        print(f"   📊 Total distributed: {total_distributed:,.0f} PYC")
        print(f"   👥 Unique recipients: {len(unique_recipients)}")
        
        # Check if distribution totals to expected amount
        expected_total = 1000000.0
        if abs(total_distributed - expected_total) > 0.0001:
            self.issues.append(f"Genesis distribution total {total_distributed} != expected {expected_total}")
        else:
            print(f"   ✅ Distribution total matches expected {expected_total:,.0f} PYC")
        
        # Check if distribution is fair
        amounts = []
        for tx in genesis_txs:
            for output in tx.outputs:
                amounts.append(output.amount)
        
        if len(set(amounts)) == 1:
            print(f"   ✅ Fair distribution: {amounts[0]:,.0f} PYC per recipient")
        else:
            self.warnings.append("Unequal distribution amounts found")
        
        return len(self.issues) == 0
    
    def validate_utxo_consistency(self):
        """Validate UTXO set consistency"""
        print("🔗 Validating UTXO Consistency...")
        
        # Rebuild UTXO from scratch
        rebuilt_utxo = {}
        
        for block in self.blockchain.chain:
            for tx in block.transactions:
                # Remove spent outputs
                for tx_input in tx.inputs:
                    utxo_key = f"{tx_input.tx_id}:{tx_input.output_index}"
                    if utxo_key in rebuilt_utxo:
                        del rebuilt_utxo[utxo_key]
                
                # Add new outputs
                for i, tx_output in enumerate(tx.outputs):
                    utxo_key = f"{tx.tx_id}:{i}"
                    
                    if tx.tx_type in ["genesis", "coinbase"]:
                        owner_pubkey = "system"
                    else:
                        owner_pubkey = tx.sender
                    
                    rebuilt_utxo[utxo_key] = {
                        "owner": owner_pubkey,
                        "recipient": tx_output.address,
                        "amount": tx_output.amount,
                        "tx_id": tx.tx_id,
                        "output_index": i
                    }
        
        # Compare with blockchain's UTXO
        print(f"   📊 Blockchain UTXO count: {len(self.blockchain.utxo)}")
        print(f"   📊 Rebuilt UTXO count: {len(rebuilt_utxo)}")
        
        if len(self.blockchain.utxo) != len(rebuilt_utxo):
            self.issues.append(f"UTXO count mismatch: blockchain={len(self.blockchain.utxo)}, rebuilt={len(rebuilt_utxo)}")
        
        # Check individual UTXOs
        mismatches = 0
        for utxo_key, utxo_data in rebuilt_utxo.items():
            if utxo_key not in self.blockchain.utxo:
                mismatches += 1
                self.issues.append(f"Missing UTXO in blockchain: {utxo_key}")
            else:
                blockchain_utxo = self.blockchain.utxo[utxo_key]
                if blockchain_utxo != utxo_data:
                    mismatches += 1
                    self.issues.append(f"UTXO data mismatch for {utxo_key}")
        
        if mismatches == 0:
            print("   ✅ UTXO set is consistent")
        else:
            print(f"   ❌ Found {mismatches} UTXO inconsistencies")
        
        return mismatches == 0
    
    def validate_blockchain_integrity(self):
        """Validate blockchain structure and hashes"""
        print("⛓️ Validating Blockchain Integrity...")
        
        if not self.blockchain.is_chain_valid():
            self.issues.append("Blockchain validation failed")
            return False
        
        print("   ✅ All block hashes and links are valid")
        
        # Check individual blocks
        for i, block in enumerate(self.blockchain.chain):
            if not block.is_valid():
                self.issues.append(f"Block {i} failed validation")
            
            # Check proof of work
            if not block.hash.startswith("0" * block.difficulty):
                self.issues.append(f"Block {i} doesn't satisfy proof of work")
        
        print(f"   📊 Blockchain height: {len(self.blockchain.chain)}")
        print(f"   📊 Current difficulty: {self.blockchain.chain[-1].difficulty if self.blockchain.chain else 0}")
        
        return len(self.issues) == 0
    
    def validate_balances(self, wallets):
        """Validate wallet balances"""
        print("💰 Validating Wallet Balances...")
        
        total_supply = 0
        
        for wallet_data in wallets:
            address = wallet_data['address']
            balance = self.blockchain.get_balance(address)
            total_supply += balance
            
            print(f"   📍 {wallet_data['file']}: {balance:,.8f} PYC")
            print(f"      Address: {address}")
        
        # Calculate expected supply (genesis + mining rewards)
        genesis_supply = 1000000.0
        mining_blocks = len(self.blockchain.chain) - 1  # Exclude genesis block
        mining_rewards = mining_blocks * 50.0  # 50 PYC per block
        expected_supply = genesis_supply + mining_rewards
        
        print(f"   📊 Total supply: {total_supply:,.8f} PYC")
        print(f"   📊 Expected supply: {expected_supply:,.8f} PYC")
        print(f"   📊 Genesis blocks: 1")
        print(f"   📊 Mined blocks: {mining_blocks}")
        print(f"   📊 Mining rewards: {mining_rewards:,.0f} PYC")
        
        if abs(total_supply - expected_supply) > 0.0001:
            self.issues.append(f"Supply mismatch: got {total_supply}, expected {expected_supply}")
        else:
            print("   ✅ Total supply matches expected amount")
        
        return len(self.issues) == 0
    
    def validate_transactions(self):
        """Validate all transactions in the blockchain"""
        print("📋 Validating All Transactions...")
        
        total_transactions = 0
        transaction_types = {}
        
        for block in self.blockchain.chain:
            for tx in block.transactions:
                total_transactions += 1
                
                tx_type = tx.tx_type
                transaction_types[tx_type] = transaction_types.get(tx_type, 0) + 1
                
                # Verify transaction
                if not tx.verify():
                    self.issues.append(f"Transaction {tx.tx_id} failed verification")
        
        print(f"   📊 Total transactions: {total_transactions}")
        for tx_type, count in transaction_types.items():
            print(f"   📊 {tx_type.title()} transactions: {count}")
        
        return len(self.issues) == 0
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📋 VALIDATION REPORT")
        print("=" * 60)
        
        if not self.issues and not self.warnings:
            print("🎉 ALL VALIDATIONS PASSED!")
            print("✅ Blockchain is healthy and consistent")
        else:
            if self.issues:
                print(f"❌ FOUND {len(self.issues)} CRITICAL ISSUES:")
                for issue in self.issues:
                    print(f"   • {issue}")
                print()
            
            if self.warnings:
                print(f"⚠️ FOUND {len(self.warnings)} WARNINGS:")
                for warning in self.warnings:
                    print(f"   • {warning}")
                print()
        
        # Blockchain summary
        if self.blockchain and self.blockchain.chain:
            print("📊 BLOCKCHAIN SUMMARY:")
            print(f"   • Height: {len(self.blockchain.chain)} blocks")
            print(f"   • Genesis complete: {'✅' if self.blockchain.genesis_complete else '❌'}")
            print(f"   • UTXO entries: {len(self.blockchain.utxo)}")
            print(f"   • Pending transactions: {len(self.blockchain.pending_transactions)}")
            
            # Calculate total value
            total_value = sum(utxo['amount'] for utxo in self.blockchain.utxo.values())
            print(f"   • Total value in circulation: {total_value:,.8f} PYC")
    
    def run_validation(self):
        """Run complete validation"""
        print("🔍 PythonCoin Blockchain Validator")
        print("=" * 60)
        
        # Load wallet data
        wallets = self.load_wallet_data()
        if wallets:
            print(f"📁 Found {len(wallets)} wallet files")
        else:
            self.warnings.append("No wallet files found")
        
        # Initialize blockchain
        genesis_addresses = [w['address'] for w in wallets]
        self.blockchain = Blockchain(genesis_addresses if genesis_addresses else None)
        
        if not self.blockchain.chain:
            print("❌ No blockchain data found")
            print("Make sure to run the wallet application first to create blockchain data")
            return False
        
        print(f"📊 Loaded blockchain with {len(self.blockchain.chain)} blocks")
        print()
        
        # Run validations
        validations = [
            self.validate_genesis_block,
            self.validate_blockchain_integrity,
            self.validate_utxo_consistency,
            self.validate_transactions,
        ]
        
        if wallets:
            validations.append(lambda: self.validate_balances(wallets))
        
        for validation in validations:
            try:
                validation()
                print()
            except Exception as e:
                self.issues.append(f"Validation error: {e}")
                print(f"   ❌ Validation error: {e}")
                print()
        
        # Generate report
        self.generate_report()
        
        return len(self.issues) == 0

def main():
    """Main validation function"""
    validator = BlockchainValidator()
    success = validator.run_validation()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
