from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from typing import Optional, Dict, Any
import json

from app.core.config import settings


class Web3Service:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.HYPERION_RPC_URL))
        
        # Add middleware for POA networks (if needed)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABIs (you'll need to add these)
        self.service_registry_abi = self._load_abi("ServiceRegistry")
        self.payment_processor_abi = self._load_abi("PaymentProcessor")
        
        # Initialize contracts
        self.service_registry = self.w3.eth.contract(
            address=settings.SERVICE_REGISTRY_CONTRACT,
            abi=self.service_registry_abi
        )
        
        self.payment_processor = self.w3.eth.contract(
            address=settings.PAYMENT_PROCESSOR_CONTRACT,
            abi=self.payment_processor_abi
        )
        
        # Account for sending transactions
        if settings.PRIVATE_KEY:
            self.account = Account.from_key(settings.PRIVATE_KEY)
    
    def _load_abi(self, contract_name: str) -> list:
        """Load contract ABI from file"""
        try:
            with open(f"app/contracts/{contract_name}.json", "r") as f:
                return json.load(f)["abi"]
        except FileNotFoundError:
            return []  # Return empty ABI for now
    
    async def register_service(
        self, 
        service_id: str, 
        provider_address: str, 
        price: int, 
        metadata_uri: str
    ) -> Optional[str]:
        """Register a service on-chain"""
        try:
            # Build transaction
            tx = self.service_registry.functions.registerService(
                service_id,
                provider_address,
                price,
                metadata_uri
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"Error registering service: {e}")
            return None
    
    async def verify_payment(
        self, 
        service_id: str, 
        user_address: str, 
        amount: int, 
        nonce: str, 
        signature: str
    ) -> bool:
        """Verify payment signature and nonce"""
        try:
            # Check if nonce was already used
            is_used = self.payment_processor.functions.isNonceUsed(
                user_address, nonce
            ).call()
            
            if is_used:
                return False
            
            # Verify signature
            message_hash = self.w3.keccak(
                text=f"{service_id}{user_address}{amount}{nonce}"
            )
            
            recovered_address = self.w3.eth.account.recover_message(
                message_hash, signature=signature
            )
            
            return recovered_address.lower() == user_address.lower()
            
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return False
    
    async def process_payment(
        self, 
        service_id: str, 
        user_address: str, 
        provider_address: str,
        amount: int, 
        nonce: str
    ) -> Optional[str]:
        """Process payment on-chain"""
        try:
            tx = self.payment_processor.functions.processPayment(
                service_id,
                user_address,
                provider_address,
                amount,
                nonce
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 150000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"Error processing payment: {e}")
            return None