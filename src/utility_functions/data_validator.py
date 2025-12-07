#!/usr/bin/env python3
"""
Data Validation Utility
Validate data against schemas and rules
"""

import json
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone, country='US'):
    """Validate phone number"""
    # Simple US format validation
    phone = re.sub(r'\D', '', phone)
    if country == 'US':
        return len(phone) == 10 or len(phone) == 11
    return len(phone) >= 10


def validate_url(url):
    """Validate URL format"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_date(date_str, format='%Y-%m-%d'):
    """Validate date format"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_range(value, min_val=None, max_val=None):
    """Validate value is within range"""
    try:
        val = float(value)
        if min_val is not None and val < min_val:
            return False
        if max_val is not None and val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_length(value, min_length=None, max_length=None):
    """Validate string length"""
    length = len(str(value))
    if min_length is not None and length < min_length:
        return False
    if max_length is not None and length > max_length:
        return False
    return True


def validate_pattern(value, pattern):
    """Validate against regex pattern"""
    return re.match(pattern, str(value)) is not None


def validate_type(value, expected_type):
    """Validate value type"""
    type_map = {
        'string': str,
        'number': (int, float),
        'integer': int,
        'float': float,
        'boolean': bool,
        'list': list,
        'dict': dict
    }
    
    if expected_type not in type_map:
        return False
    
    return isinstance(value, type_map[expected_type])


def validate_enum(value, allowed_values):
    """Validate value is in allowed list"""
    return value in allowed_values


def validate_field(field_name, value, rules):
    """
    Validate a single field against rules
    
    Args:
        field_name: Name of the field
        value: Value to validate
        rules: Dictionary of validation rules
    
    Returns:
        dict: Validation result
    """
    errors = []
    
    # Required check
    if rules.get('required', False):
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"Field '{field_name}' is required")
            return {'valid': False, 'errors': errors}
    
    # Skip other checks if value is None and not required
    if value is None:
        return {'valid': True, 'errors': []}
    
    # Type check
    if 'type' in rules:
        if not validate_type(value, rules['type']):
            errors.append(f"Field '{field_name}' must be of type {rules['type']}")
    
    # Email check
    if rules.get('format') == 'email':
        if not validate_email(value):
            errors.append(f"Field '{field_name}' must be a valid email")
    
    # Phone check
    if rules.get('format') == 'phone':
        if not validate_phone(value):
            errors.append(f"Field '{field_name}' must be a valid phone number")
    
    # URL check
    if rules.get('format') == 'url':
        if not validate_url(value):
            errors.append(f"Field '{field_name}' must be a valid URL")
    
    # Date check
    if rules.get('format') == 'date':
        date_format = rules.get('date_format', '%Y-%m-%d')
        if not validate_date(value, date_format):
            errors.append(f"Field '{field_name}' must be a valid date ({date_format})")
    
    # Range check
    if 'min' in rules or 'max' in rules:
        if not validate_range(value, rules.get('min'), rules.get('max')):
            errors.append(f"Field '{field_name}' must be between {rules.get('min')} and {rules.get('max')}")
    
    # Length check
    if 'min_length' in rules or 'max_length' in rules:
        if not validate_length(value, rules.get('min_length'), rules.get('max_length')):
            errors.append(f"Field '{field_name}' length must be between {rules.get('min_length')} and {rules.get('max_length')}")
    
    # Pattern check
    if 'pattern' in rules:
        if not validate_pattern(value, rules['pattern']):
            errors.append(f"Field '{field_name}' does not match required pattern")
    
    # Enum check
    if 'enum' in rules:
        if not validate_enum(value, rules['enum']):
            errors.append(f"Field '{field_name}' must be one of {rules['enum']}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_data(data, schema):
    """
    Validate data against schema
    
    Args:
        data: Dictionary of data to validate
        schema: Dictionary of field rules
    
    Returns:
        dict: Validation results
    """
    results = {}
    all_valid = True
    
    for field_name, rules in schema.items():
        value = data.get(field_name)
        result = validate_field(field_name, value, rules)
        results[field_name] = result
        if not result['valid']:
            all_valid = False
    
    return {
        'valid': all_valid,
        'fields': results
    }


def handle(event, context):
    """
    OpenFaaS handler for data validation
    
    Request body:
    {
        "data": {
            "email": "test@example.com",
            "age": 25,
            "phone": "1234567890",
            "website": "https://example.com"
        },
        "schema": {
            "email": {
                "required": true,
                "type": "string",
                "format": "email"
            },
            "age": {
                "required": true,
                "type": "integer",
                "min": 0,
                "max": 150
            },
            "phone": {
                "required": false,
                "type": "string",
                "format": "phone"
            },
            "website": {
                "required": false,
                "type": "string",
                "format": "url"
            }
        }
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received data validation request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Validate input
        if 'data' not in payload:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'data' field in request"},
                "headers": {"Content-Type": "application/json"}
            }
        
        if 'schema' not in payload:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'schema' field in request"},
                "headers": {"Content-Type": "application/json"}
            }
        
        data = payload['data']
        schema = payload['schema']
        
        logger.info(f"Validating {len(data)} fields against schema...")
        validation_result = validate_data(data, schema)
        
        # Count errors
        total_errors = sum(len(field['errors']) for field in validation_result['fields'].values())
        
        return {
            "statusCode": 200,
            "body": {
                "validation": validation_result,
                "statistics": {
                    "total_fields": len(schema),
                    "valid_fields": sum(1 for f in validation_result['fields'].values() if f['valid']),
                    "invalid_fields": sum(1 for f in validation_result['fields'].values() if not f['valid']),
                    "total_errors": total_errors
                },
                "message": "Validation complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
    
    except Exception as e:
        logger.error(f"Error in data validation: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }

