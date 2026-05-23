"""
Advanced Security Module for Steganography System
Provides AES-256-GCM encryption, key derivation, and authentication
Compatible with cryptography >= 41.0.0
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import struct

class SecurityLayer:
    """
    Implements military-grade encryption for hidden messages
    Uses AES-256 in GCM mode for confidentiality and authentication
    """
    
    def __init__(self):
        self.backend = default_backend()
        self.salt_size = 32  # 256-bit salt
        self.iv_size = 12    # 96-bit IV for GCM
        self.tag_size = 16   # 128-bit authentication tag
        self.key_size = 32   # 256-bit key
        self.iterations = 100000  # PBKDF2 iterations
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """
        Derive encryption key from password using PBKDF2HMAC
        Returns (key, salt)
        """
        if salt is None:
            salt = os.urandom(self.salt_size)
        
        # Updated for newer cryptography versions
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt_message(self, message: bytes, password: str) -> dict:
        """
        Encrypt message using AES-256-GCM
        Returns dict with encrypted data, salt, IV, and tag
        """
        try:
            # Generate key and salt
            key, salt = self.derive_key(password)
            
            # Generate random IV
            iv = os.urandom(self.iv_size)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=self.backend
            )
            
            # Encrypt
            encryptor = cipher.encryptor()
            
            # Add length prefix for message
            message_with_length = struct.pack('>I', len(message)) + message
            
            # Pad to block size if needed
            padded_message = self._pad_data(message_with_length)
            
            # Encrypt and get tag
            ciphertext = encryptor.update(padded_message) + encryptor.finalize()
            
            return {
                'encrypted_data': ciphertext,
                'salt': salt,
                'iv': iv,
                'tag': encryptor.tag
            }
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_message(self, encrypted_data: bytes, salt: bytes, 
                       iv: bytes, tag: bytes, password: str) -> bytes:
        """
        Decrypt and verify message using AES-256-GCM
        Returns original message bytes
        """
        try:
            # Derive key from password and salt
            key, _ = self.derive_key(password, salt)
            
            # Create cipher with same parameters
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            
            # Decrypt and verify
            decryptor = cipher.decryptor()
            padded_message = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Unpad and extract message
            message_with_length = self._unpad_data(padded_message)
            
            # Extract length and message
            message_length = struct.unpack('>I', message_with_length[:4])[0]
            original_message = message_with_length[4:4+message_length]
            
            return original_message
            
        except Exception as e:
            raise Exception("Decryption failed: Invalid password or corrupted data")
    
    def _pad_data(self, data: bytes) -> bytes:
        """PKCS7 padding"""
        padding_length = 16 - (len(data) % 16)
        if padding_length == 0:
            padding_length = 16
        return data + bytes([padding_length] * padding_length)
    
    def _unpad_data(self, data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = data[-1]
        return data[:-padding_length]