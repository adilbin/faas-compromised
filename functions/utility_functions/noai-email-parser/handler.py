#!/usr/bin/env python3
"""
Email Parser and Validator
Parse and validate email addresses and extract information
"""

import json
import logging
import re
from email.utils import parseaddr
from email.header import decode_header

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email address string
    
    Returns:
        dict: Validation result
    """
    # RFC 5322 compliant regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    
    parts = email.split('@') if '@' in email else [email, '']
    local_part = parts[0] if len(parts) > 0 else ''
    domain = parts[1] if len(parts) > 1 else ''
    
    return {
        'email': email,
        'valid': is_valid,
        'local_part': local_part,
        'domain': domain,
        'tld': domain.split('.')[-1] if '.' in domain else ''
    }


def parse_email_address(email_string):
    """
    Parse email address with name
    
    Args:
        email_string: Email string (e.g., "John Doe <john@example.com>")
    
    Returns:
        dict: Parsed email information
    """
    name, email = parseaddr(email_string)
    validation = validate_email(email)
    
    return {
        'display_name': name,
        'email': email,
        'valid': validation['valid'],
        'local_part': validation['local_part'],
        'domain': validation['domain'],
        'tld': validation['tld']
    }


def extract_emails(text):
    """
    Extract all email addresses from text
    
    Args:
        text: Text to search
    
    Returns:
        list: List of found email addresses
    """
    pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    emails = re.findall(pattern, text)
    
    results = []
    for email in emails:
        validation = validate_email(email)
        results.append(validation)
    
    return results


def check_disposable_domain(domain):
    """
    Check if domain is a known disposable email provider
    
    Args:
        domain: Email domain
    
    Returns:
        bool: True if disposable
    """
    # Common disposable email domains
    disposable_domains = {
        'tempmail.com', 'guerrillamail.com', 'mailinator.com',
        '10minutemail.com', 'throwaway.email', 'temp-mail.org',
        'yopmail.com', 'maildrop.cc', 'getnada.com'
    }
    
    return domain.lower() in disposable_domains


def check_common_provider(domain):
    """
    Check if domain is a common email provider
    
    Args:
        domain: Email domain
    
    Returns:
        str: Provider name or 'other'
    """
    providers = {
        'gmail.com': 'Google',
        'yahoo.com': 'Yahoo',
        'outlook.com': 'Microsoft',
        'hotmail.com': 'Microsoft',
        'live.com': 'Microsoft',
        'icloud.com': 'Apple',
        'protonmail.com': 'ProtonMail',
        'aol.com': 'AOL'
    }
    
    return providers.get(domain.lower(), 'other')


def analyze_email(email):
    """
    Comprehensive email analysis
    
    Args:
        email: Email address
    
    Returns:
        dict: Analysis results
    """
    validation = validate_email(email)
    
    if not validation['valid']:
        return {
            'email': email,
            'valid': False,
            'error': 'Invalid email format'
        }
    
    domain = validation['domain']
    local_part = validation['local_part']
    
    return {
        'email': email,
        'valid': True,
        'local_part': local_part,
        'domain': domain,
        'tld': validation['tld'],
        'is_disposable': check_disposable_domain(domain),
        'provider': check_common_provider(domain),
        'local_length': len(local_part),
        'has_plus_sign': '+' in local_part,
        'has_dot': '.' in local_part
    }


def handle(event, context):
    """
    OpenFaaS handler for email parsing and validation
    
    Request body for validation:
    {
        "operation": "validate",
        "email": "user@example.com"
    }
    
    Request body for parsing:
    {
        "operation": "parse",
        "email_string": "John Doe <john@example.com>"
    }
    
    Request body for extraction:
    {
        "operation": "extract",
        "text": "Contact us at support@example.com or sales@example.com"
    }
    
    Request body for analysis:
    {
        "operation": "analyze",
        "email": "user@example.com"
    }
    
    Request body for batch:
    {
        "operation": "batch_validate",
        "emails": ["email1@example.com", "email2@example.com", ...]
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received email parsing request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'validate')
        
        if operation == 'validate':
            email = payload.get('email', '')
            if not email:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'email' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = validate_email(email)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "Validation complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'parse':
            email_string = payload.get('email_string', '')
            if not email_string:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'email_string' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = parse_email_address(email_string)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "Parsing complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'extract':
            text = payload.get('text', '')
            if not text:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'text' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            results = extract_emails(text)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "count": len(results),
                    "message": "Extraction complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'analyze':
            email = payload.get('email', '')
            if not email:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'email' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = analyze_email(email)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "message": "Analysis complete"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'batch_validate':
            emails = payload.get('emails', [])
            if not emails:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'emails' field"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            results = []
            for email in emails:
                results.append(validate_email(email))
            
            valid_count = sum(1 for r in results if r['valid'])
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "statistics": {
                        "total": len(results),
                        "valid": valid_count,
                        "invalid": len(results) - valid_count
                    },
                    "message": "Batch validation complete"
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
        logger.error(f"Error in email processing: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
