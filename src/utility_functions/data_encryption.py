#!/usr/bin/env python3
"""
Data Encryption/Decryption Utility
Encrypt and decrypt data using various algorithms
"""

import json
import logging
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global key storage (in production, use secure key management)
keys = {}


def generate_key(password=None, key_id='default'):
    """
    Generate encryption key
    
    Args:
        password: Optional password for key derivation
        key_id: ID for key storage
    
    Returns:
        str: Base64 encoded key
    """
    if password:
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt_for_demo',  # In production, use random salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        # Generate random key
        key = Fernet.generate_key()
    
    keys[key_id] = key
    return key.decode('utf-8')


def encrypt_data(data, key_id='default', key=None):
    """
    Encrypt data
    
    Args:
        data: String data to encrypt
        key_id: ID of stored key
        key: Direct key (overrides key_id)
    
    Returns:
        str: Base64 encoded encrypted data
    """
    if key:
        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
    elif key_id in keys:
        key_bytes = keys[key_id]
    else:
        raise ValueError(f"Key '{key_id}' not found. Generate key first.")
    
    fernet = Fernet(key_bytes)
    encrypted = fernet.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_data(encrypted_data, key_id='default', key=None):
    """
    Decrypt data
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        key_id: ID of stored key
        key: Direct key (overrides key_id)
    
    Returns:
        str: Decrypted data
    """
    if key:
        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
    elif key_id in keys:
        key_bytes = keys[key_id]
    else:
        raise ValueError(f"Key '{key_id}' not found.")
    
    fernet = Fernet(key_bytes)
    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode('utf-8')


def hash_data(data, algorithm='sha256'):
    """
    Hash data (one-way)
    
    Args:
        data: String data to hash
        algorithm: Hash algorithm
    
    Returns:
        str: Hexadecimal hash
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()


def encrypt_dict(data_dict, key_id='default', key=None):
    """
    Encrypt dictionary values
    
    Args:
        data_dict: Dictionary to encrypt
        key_id: ID of stored key
        key: Direct key
    
    Returns:
        dict: Dictionary with encrypted values
    """
    encrypted_dict = {}
    for k, v in data_dict.items():
        encrypted_dict[k] = encrypt_data(str(v), key_id, key)
    return encrypted_dict


def decrypt_dict(encrypted_dict, key_id='default', key=None):
    """
    Decrypt dictionary values
    
    Args:
        encrypted_dict: Dictionary with encrypted values
        key_id: ID of stored key
        key: Direct key
    
    Returns:
        dict: Dictionary with decrypted values
    """
    decrypted_dict = {}
    for k, v in encrypted_dict.items():
        decrypted_dict[k] = decrypt_data(v, key_id, key)
    return decrypted_dict


def handle(event, context):
    """
    OpenFaaS handler for encryption/decryption
    
    Request body for key generation:
    {
        "operation": "generate_key",
        "password": "optional_password",
        "key_id": "my_key"  # optional
    }
    
    Request body for encryption:
    {
        "operation": "encrypt",
        "data": "string to encrypt",
        "key_id": "my_key",  # optional
        "key": "direct_key"  # optional
    }
    
    Request body for decryption:
    {
        "operation": "decrypt",
        "data": "encrypted_data",
        "key_id": "my_key",  # optional
        "key": "direct_key"  # optional
    }
    
    Request body for hashing:
    {
        "operation": "hash",
        "data": "string to hash",
        "algorithm": "sha256"  # optional
    }
    
    Request body for dict encryption:
    {
        "operation": "encrypt_dict",
        "data": {"key1": "value1", "key2": "value2"},
        "key_id": "my_key"  # optional
    }
    
    Request body for dict decryption:
    {
        "operation": "decrypt_dict",
        "data": {"key1": "encrypted1", "key2": "encrypted2"},
        "key_id": "my_key"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received encryption/decryption request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'encrypt')
        key_id = payload.get('key_id', 'default')
        key = payload.get('key')
        
        if operation == 'generate_key':
            password = payload.get('password')
            
            logger.info(f"Generating key '{key_id}'...")
            generated_key = generate_key(password, key_id)
            
            return {
                "statusCode": 200,
                "body": {
                    "key": generated_key,
                    "key_id": key_id,
                    "message": "Key generated successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'encrypt':
            data = payload.get('data', '')
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Encrypting data...")
            encrypted = encrypt_data(data, key_id, key)
            
            return {
                "statusCode": 200,
                "body": {
                    "encrypted_data": encrypted,
                    "key_id": key_id,
                    "original_length": len(data),
                    "message": "Data encrypted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'decrypt':
            data = payload.get('data', '')
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Decrypting data...")
            decrypted = decrypt_data(data, key_id, key)
            
            return {
                "statusCode": 200,
                "body": {
                    "decrypted_data": decrypted,
                    "key_id": key_id,
                    "message": "Data decrypted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'hash':
            data = payload.get('data', '')
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            algorithm = payload.get('algorithm', 'sha256')
            
            logger.info(f"Hashing data with {algorithm}...")
            hashed = hash_data(data, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "hash": hashed,
                    "algorithm": algorithm,
                    "message": "Data hashed successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'encrypt_dict':
            data = payload.get('data', {})
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Encrypting dictionary...")
            encrypted = encrypt_dict(data, key_id, key)
            
            return {
                "statusCode": 200,
                "body": {
                    "encrypted_data": encrypted,
                    "key_id": key_id,
                    "fields_encrypted": len(encrypted),
                    "message": "Dictionary encrypted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'decrypt_dict':
            data = payload.get('data', {})
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info("Decrypting dictionary...")
            decrypted = decrypt_dict(data, key_id, key)
            
            return {
                "statusCode": 200,
                "body": {
                    "decrypted_data": decrypted,
                    "key_id": key_id,
                    "fields_decrypted": len(decrypted),
                    "message": "Dictionary decrypted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
    
    except Exception as e:
        logger.error(f"Error in encryption/decryption: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
