#!/usr/bin/env python3
"""
QR Code Generator
Generate QR codes from text, URLs, and other data
"""

import json
import logging
import base64
import io
import qrcode
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_qr_code(data, error_correction='M', box_size=10, border=4, 
                     fill_color='black', back_color='white'):
    """
    Generate QR code
    
    Args:
        data: Data to encode
        error_correction: Error correction level (L, M, Q, H)
        box_size: Size of each box in pixels
        border: Border size in boxes
        fill_color: Foreground color
        back_color: Background color
    
    Returns:
        PIL Image: QR code image
    """
    # Map error correction levels
    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    ec_level = error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version
        error_correction=ec_level,
        box_size=box_size,
        border=border
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    return img


def generate_qr_with_logo(data, logo_base64, error_correction='H', 
                          box_size=10, border=4):
    """
    Generate QR code with embedded logo
    
    Args:
        data: Data to encode
        logo_base64: Base64 encoded logo image
        error_correction: Error correction level (should be H for logo)
        box_size: Size of each box in pixels
        border: Border size in boxes
    
    Returns:
        PIL Image: QR code image with logo
    """
    # Generate base QR code
    qr_img = generate_qr_code(data, error_correction, box_size, border)
    
    # Load and resize logo
    logo_bytes = base64.b64decode(logo_base64)
    logo = Image.open(io.BytesIO(logo_bytes))
    
    # Calculate logo size (max 30% of QR code)
    qr_width, qr_height = qr_img.size
    logo_size = int(min(qr_width, qr_height) * 0.3)
    
    # Resize logo
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Convert QR to RGBA if needed
    if qr_img.mode != 'RGBA':
        qr_img = qr_img.convert('RGBA')
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')
    
    # Calculate position (center)
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    
    # Paste logo
    qr_img.paste(logo, logo_pos, logo)
    
    return qr_img


def encode_image(image):
    """Encode PIL image to base64"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def handle(event, context):
    """
    OpenFaaS handler for QR code generation
    
    Request body:
    {
        "data": "text or URL to encode",
        "error_correction": "M",  # optional: L, M, Q, H
        "box_size": 10,  # optional
        "border": 4,  # optional
        "fill_color": "black",  # optional
        "back_color": "white",  # optional
        "logo": "base64_encoded_logo",  # optional
        "format": "base64"  # optional: base64 or file
    }
    
    For batch:
    {
        "batch": [
            {"data": "text1", "error_correction": "M"},
            {"data": "text2", "error_correction": "H"}
        ]
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received QR code generation request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Batch mode
        if 'batch' in payload:
            batch_items = payload['batch']
            results = []
            
            for item in batch_items:
                try:
                    data = item.get('data', '')
                    if not data:
                        results.append({"error": "Missing data"})
                        continue
                    
                    error_correction = item.get('error_correction', 'M')
                    box_size = item.get('box_size', 10)
                    border = item.get('border', 4)
                    fill_color = item.get('fill_color', 'black')
                    back_color = item.get('back_color', 'white')
                    logo = item.get('logo')
                    
                    if logo:
                        qr_img = generate_qr_with_logo(data, logo, error_correction, box_size, border)
                    else:
                        qr_img = generate_qr_code(data, error_correction, box_size, 
                                                  border, fill_color, back_color)
                    
                    qr_base64 = encode_image(qr_img)
                    
                    results.append({
                        "data_preview": data[:50] + '...' if len(data) > 50 else data,
                        "qr_code": qr_base64,
                        "size": qr_img.size
                    })
                except Exception as e:
                    results.append({"error": str(e)})
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "total_items": len(results),
                    "successful": sum(1 for r in results if "error" not in r)
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        # Single QR code mode
        data = payload.get('data', '')
        if not data:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'data' field"},
                "headers": {"Content-Type": "application/json"}
            }
        
        error_correction = payload.get('error_correction', 'M')
        box_size = payload.get('box_size', 10)
        border = payload.get('border', 4)
        fill_color = payload.get('fill_color', 'black')
        back_color = payload.get('back_color', 'white')
        logo = payload.get('logo')
        
        logger.info(f"Generating QR code for data (length: {len(data)})...")
        
        if logo:
            qr_img = generate_qr_with_logo(data, logo, error_correction, box_size, border)
        else:
            qr_img = generate_qr_code(data, error_correction, box_size, border, 
                                     fill_color, back_color)
        
        qr_base64 = encode_image(qr_img)
        
        return {
            "statusCode": 200,
            "body": {
                "qr_code": qr_base64,
                "data_length": len(data),
                "image_size": qr_img.size,
                "error_correction": error_correction,
                "message": "QR code generated successfully"
            },
            "headers": {"Content-Type": "application/json"}
        }
    
    except Exception as e:
        logger.error(f"Error in QR code generation: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }

