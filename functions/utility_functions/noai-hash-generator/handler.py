#!/usr/bin/env python3
"""
Hash Generator Utility
Generate various types of hashes for data
"""

import json
import logging
import hashlib
import hmac
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_hash(data, algorithm='sha256'):
    """
    Generate hash for data
    
    Args:
        data: String data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512, etc.)
    
    Returns:
        str: Hexadecimal hash
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()


def generate_hmac(data, key, algorithm='sha256'):
    """
    Generate HMAC for data
    
    Args:
        data: String data to hash
        key: Secret key
        algorithm: Hash algorithm
    
    Returns:
        str: Hexadecimal HMAC
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hmac_obj = hmac.new(
        key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.new(algorithm)
    )
    return hmac_obj.hexdigest()


def generate_file_hash(file_data_base64, algorithm='sha256'):
    """
    Generate hash for file data
    
    Args:
        file_data_base64: Base64 encoded file data
        algorithm: Hash algorithm
    
    Returns:
        str: Hexadecimal hash
    """
    file_data = base64.b64decode(file_data_base64)
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(file_data)
    return hash_obj.hexdigest()


def verify_hash(data, expected_hash, algorithm='sha256'):
    """
    Verify data against expected hash
    
    Args:
        data: String data to verify
        expected_hash: Expected hash value
        algorithm: Hash algorithm
    
    Returns:
        bool: True if hash matches
    """
    actual_hash = generate_hash(data, algorithm)
    return hmac.compare_digest(actual_hash, expected_hash)


def verify_hmac(data, key, expected_hmac, algorithm='sha256'):
    """
    Verify HMAC
    
    Args:
        data: String data to verify
        key: Secret key
        expected_hmac: Expected HMAC value
        algorithm: Hash algorithm
    
    Returns:
        bool: True if HMAC matches
    """
    actual_hmac = generate_hmac(data, key, algorithm)
    return hmac.compare_digest(actual_hmac, expected_hmac)


def handle(event, context):
    """
    OpenFaaS handler for hash generation
    
    Request body for hash generation:
    {
        "operation": "hash",
        "data": "string to hash",
        "algorithm": "sha256"  # optional
    }
    
    Request body for HMAC generation:
    {
        "operation": "hmac",
        "data": "string to hash",
        "key": "secret_key",
        "algorithm": "sha256"  # optional
    }
    
    Request body for file hash:
    {
        "operation": "file_hash",
        "file_data": "base64_encoded_file",
        "algorithm": "sha256"  # optional
    }
    
    Request body for hash verification:
    {
        "operation": "verify_hash",
        "data": "string to verify",
        "expected_hash": "hash_value",
        "algorithm": "sha256"  # optional
    }
    
    Request body for HMAC verification:
    {
        "operation": "verify_hmac",
        "data": "string to verify",
        "key": "secret_key",
        "expected_hmac": "hmac_value",
        "algorithm": "sha256"  # optional
    }
    
    Request body for batch:
    {
        "operation": "batch",
        "items": ["string1", "string2", ...],
        "algorithm": "sha256"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received hash generation request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'hash')
        algorithm = payload.get('algorithm', 'sha256')
        
        if operation == 'hash':
            # Generate hash
            data = payload.get('data', '')
            if not data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            hash_value = generate_hash(data, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "hash": hash_value,
                    "algorithm": algorithm,
                    "data_length": len(data)
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'hmac':
            # Generate HMAC
            data = payload.get('data', '')
            key = payload.get('key', '')
            
            if not data or not key:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' or 'key' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            hmac_value = generate_hmac(data, key, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "hmac": hmac_value,
                    "algorithm": algorithm,
                    "data_length": len(data)
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'file_hash':
            # Generate file hash
            file_data = payload.get('file_data', '')
            if not file_data:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'file_data' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            hash_value = generate_file_hash(file_data, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "hash": hash_value,
                    "algorithm": algorithm
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'verify_hash':
            # Verify hash
            data = payload.get('data', '')
            expected_hash = payload.get('expected_hash', '')
            
            if not data or not expected_hash:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data' or 'expected_hash' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            is_valid = verify_hash(data, expected_hash, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "valid": is_valid,
                    "algorithm": algorithm
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'verify_hmac':
            # Verify HMAC
            data = payload.get('data', '')
            key = payload.get('key', '')
            expected_hmac = payload.get('expected_hmac', '')
            
            if not data or not key or not expected_hmac:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'data', 'key', or 'expected_hmac' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            is_valid = verify_hmac(data, key, expected_hmac, algorithm)
            
            return {
                "statusCode": 200,
                "body": {
                    "valid": is_valid,
                    "algorithm": algorithm
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'batch':
            # Batch hash generation
            items = payload.get('items', [])
            if not items:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'items' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            results = []
            for item in items:
                hash_value = generate_hash(str(item), algorithm)
                results.append({
                    "data": str(item)[:50] + '...' if len(str(item)) > 50 else str(item),
                    "hash": hash_value
                })
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "algorithm": algorithm,
                    "total_items": len(results)
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
        logger.error(f"Error in hash generation: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
