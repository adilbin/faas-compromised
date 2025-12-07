#!/usr/bin/env python3
"""
JSON/XML Converter
Convert between JSON and XML formats
"""

import json
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dict_to_xml(data, root_name='root'):
    """
    Convert dictionary to XML
    
    Args:
        data: Dictionary to convert
        root_name: Name of root element
    
    Returns:
        str: XML string
    """
    root = ET.Element(root_name)
    
    def build_xml(parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                # Clean key name (remove invalid XML characters)
                key = str(key).replace(' ', '_')
                child = ET.SubElement(parent, key)
                build_xml(child, value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, 'item')
                build_xml(child, item)
        else:
            parent.text = str(data)
    
    build_xml(root, data)
    
    # Convert to string with formatting
    xml_str = ET.tostring(root, encoding='unicode')
    
    # Pretty print
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')


def xml_to_dict(xml_string):
    """
    Convert XML to dictionary
    
    Args:
        xml_string: XML string to convert
    
    Returns:
        dict: Converted dictionary
    """
    root = ET.fromstring(xml_string)
    
    def parse_element(element):
        # Get element data
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Process children
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = parse_element(child)
                
                if child.tag in child_dict:
                    # Handle multiple children with same tag
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_data)
                else:
                    child_dict[child.tag] = child_data
            
            result.update(child_dict)
        
        # Add text content
        if element.text and element.text.strip():
            if result:
                result['#text'] = element.text.strip()
            else:
                return element.text.strip()
        
        return result if result else None
    
    return {root.tag: parse_element(root)}


def json_to_xml(json_string, root_name='root'):
    """
    Convert JSON to XML
    
    Args:
        json_string: JSON string
        root_name: Name of root element
    
    Returns:
        str: XML string
    """
    data = json.loads(json_string)
    return dict_to_xml(data, root_name)


def xml_to_json(xml_string):
    """
    Convert XML to JSON
    
    Args:
        xml_string: XML string
    
    Returns:
        str: JSON string
    """
    data = xml_to_dict(xml_string)
    return json.dumps(data, indent=2)


def handle(event, context):
    """
    OpenFaaS handler for JSON/XML conversion
    
    Request body for JSON to XML:
    {
        "operation": "json_to_xml",
        "data": {"key": "value", ...},  # or JSON string
        "root_name": "root"  # optional
    }
    
    Request body for XML to JSON:
    {
        "operation": "xml_to_json",
        "data": "<root><key>value</key></root>"
    }
    
    Request body for dict to XML:
    {
        "operation": "dict_to_xml",
        "data": {"key": "value", ...},
        "root_name": "root"  # optional
    }
    
    Request body for XML to dict:
    {
        "operation": "xml_to_dict",
        "data": "<root><key>value</key></root>"
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received JSON/XML conversion request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'json_to_xml')
        data = payload.get('data')
        
        if data is None:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'data' field"},
                "headers": {"Content-Type": "application/json"}
            }
        
        if operation == 'json_to_xml':
            root_name = payload.get('root_name', 'root')
            
            # Handle both JSON string and dict
            if isinstance(data, str):
                xml_result = json_to_xml(data, root_name)
            else:
                xml_result = dict_to_xml(data, root_name)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": xml_result,
                    "operation": operation,
                    "message": "Conversion successful"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'xml_to_json':
            json_result = xml_to_json(data)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": json.loads(json_result),  # Return as dict
                    "operation": operation,
                    "message": "Conversion successful"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'dict_to_xml':
            root_name = payload.get('root_name', 'root')
            xml_result = dict_to_xml(data, root_name)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": xml_result,
                    "operation": operation,
                    "message": "Conversion successful"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'xml_to_dict':
            dict_result = xml_to_dict(data)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": dict_result,
                    "operation": operation,
                    "message": "Conversion successful"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
    
    except ET.ParseError as e:
        return {
            "statusCode": 400,
            "body": {"error": f"Invalid XML: {str(e)}"},
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        logger.error(f"Error in JSON/XML conversion: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }

