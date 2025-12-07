#!/usr/bin/env python3
"""
URL Shortener (Hash-based)
Shorten URLs and manage shortened links
"""

import json
import logging
import hashlib
import base64
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for URL mappings
url_mappings = {}
reverse_mappings = {}


def generate_short_code(url, length=6):
    """
    Generate short code for URL
    
    Args:
        url: Original URL
        length: Length of short code
    
    Returns:
        str: Short code
    """
    # Hash the URL
    hash_obj = hashlib.sha256(url.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Base64 encode and clean
    b64 = base64.urlsafe_b64encode(hash_bytes).decode('utf-8')
    short_code = b64[:length].rstrip('=')
    
    return short_code


def validate_url(url):
    """
    Validate URL format
    
    Args:
        url: URL to validate
    
    Returns:
        bool: True if valid
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def shorten_url(url, custom_code=None):
    """
    Shorten URL
    
    Args:
        url: Original URL
        custom_code: Optional custom short code
    
    Returns:
        dict: Shortened URL information
    """
    if not validate_url(url):
        raise ValueError("Invalid URL format")
    
    # Check if URL already shortened
    if url in reverse_mappings:
        short_code = reverse_mappings[url]
        return {
            'original_url': url,
            'short_code': short_code,
            'shortened_url': f'https://short.url/{short_code}',
            'existing': True
        }
    
    # Generate or use custom code
    if custom_code:
        short_code = custom_code
        if short_code in url_mappings:
            raise ValueError(f"Short code '{short_code}' already in use")
    else:
        short_code = generate_short_code(url)
        
        # Handle collisions (very rare)
        counter = 0
        original_code = short_code
        while short_code in url_mappings and url_mappings[short_code] != url:
            counter += 1
            short_code = f"{original_code}{counter}"
    
    # Store mapping
    url_mappings[short_code] = url
    reverse_mappings[url] = short_code
    
    return {
        'original_url': url,
        'short_code': short_code,
        'shortened_url': f'https://short.url/{short_code}',
        'existing': False
    }


def expand_url(short_code):
    """
    Expand shortened URL
    
    Args:
        short_code: Short code
    
    Returns:
        dict: Original URL information
    """
    if short_code not in url_mappings:
        raise ValueError(f"Short code '{short_code}' not found")
    
    original_url = url_mappings[short_code]
    
    return {
        'short_code': short_code,
        'original_url': original_url,
        'shortened_url': f'https://short.url/{short_code}'
    }


def delete_shortened_url(short_code):
    """
    Delete shortened URL
    
    Args:
        short_code: Short code to delete
    
    Returns:
        dict: Deletion result
    """
    if short_code not in url_mappings:
        raise ValueError(f"Short code '{short_code}' not found")
    
    original_url = url_mappings[short_code]
    
    del url_mappings[short_code]
    del reverse_mappings[original_url]
    
    return {
        'short_code': short_code,
        'original_url': original_url,
        'deleted': True
    }


def get_statistics():
    """
    Get URL shortener statistics
    
    Returns:
        dict: Statistics
    """
    return {
        'total_urls': len(url_mappings),
        'total_mappings': len(url_mappings),
        'codes': list(url_mappings.keys())[:10]  # First 10 codes
    }


def handle(event, context):
    """
    OpenFaaS handler for URL shortening
    
    Request body for shortening:
    {
        "operation": "shorten",
        "url": "https://example.com/very/long/url",
        "custom_code": "mycode"  # optional
    }
    
    Request body for expanding:
    {
        "operation": "expand",
        "short_code": "abc123"
    }
    
    Request body for deletion:
    {
        "operation": "delete",
        "short_code": "abc123"
    }
    
    Request body for batch shortening:
    {
        "operation": "batch_shorten",
        "urls": ["https://example.com/url1", "https://example.com/url2"]
    }
    
    Request body for statistics:
    {
        "operation": "statistics"
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received URL shortening request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'shorten')
        
        if operation == 'shorten':
            url = payload.get('url', '')
            custom_code = payload.get('custom_code')
            
            if not url:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'url' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Shortening URL: {url}")
            result = shorten_url(url, custom_code)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "URL shortened successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'expand':
            short_code = payload.get('short_code', '')
            
            if not short_code:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'short_code' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Expanding short code: {short_code}")
            result = expand_url(short_code)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "URL expanded successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'delete':
            short_code = payload.get('short_code', '')
            
            if not short_code:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'short_code' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Deleting short code: {short_code}")
            result = delete_shortened_url(short_code)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "URL deleted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'batch_shorten':
            urls = payload.get('urls', [])
            
            if not urls:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'urls' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Shortening {len(urls)} URLs...")
            results = []
            
            for url in urls:
                try:
                    result = shorten_url(url)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'original_url': url,
                        'error': str(e)
                    })
            
            successful = sum(1 for r in results if 'error' not in r)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "total": len(results),
                    "successful": successful,
                    "message": "Batch shortening complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'statistics':
            logger.info("Getting statistics...")
            stats = get_statistics()
            
            return {
                "statusCode": 200,
                "body": {
                    "statistics": stats,
                    "message": "Statistics retrieved"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
    
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        logger.error(f"Error in URL shortening: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
