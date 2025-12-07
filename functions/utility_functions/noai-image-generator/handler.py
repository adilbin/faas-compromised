#!/usr/bin/env python3
"""
Image Processing Utility
Resize, crop, filter, and manipulate images
"""

import json
import logging
import base64
import io
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def decode_image(image_data):
    """Decode base64 image data"""
    image_bytes = base64.b64decode(image_data)
    return Image.open(io.BytesIO(image_bytes))


def encode_image(image, format='PNG'):
    """Encode image to base64"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def resize_image(image, width=None, height=None, maintain_aspect=True):
    """Resize image"""
    orig_width, orig_height = image.size
    
    if maintain_aspect:
        if width and not height:
            ratio = width / orig_width
            height = int(orig_height * ratio)
        elif height and not width:
            ratio = height / orig_height
            width = int(orig_width * ratio)
        elif width and height:
            # Use the smaller ratio to fit within bounds
            ratio = min(width / orig_width, height / orig_height)
            width = int(orig_width * ratio)
            height = int(orig_height * ratio)
    
    return image.resize((width, height), Image.Resampling.LANCZOS)


def crop_image(image, x, y, width, height):
    """Crop image"""
    return image.crop((x, y, x + width, y + height))


def apply_filter(image, filter_name):
    """Apply filter to image"""
    filters = {
        'blur': ImageFilter.BLUR,
        'contour': ImageFilter.CONTOUR,
        'detail': ImageFilter.DETAIL,
        'edge_enhance': ImageFilter.EDGE_ENHANCE,
        'emboss': ImageFilter.EMBOSS,
        'sharpen': ImageFilter.SHARPEN,
        'smooth': ImageFilter.SMOOTH
    }
    
    if filter_name not in filters:
        raise ValueError(f"Unknown filter: {filter_name}")
    
    return image.filter(filters[filter_name])


def adjust_brightness(image, factor):
    """Adjust brightness (factor: 0.0 to 2.0)"""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image, factor):
    """Adjust contrast (factor: 0.0 to 2.0)"""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def rotate_image(image, angle):
    """Rotate image by angle"""
    return image.rotate(angle, expand=True)


def flip_image(image, direction):
    """Flip image horizontally or vertically"""
    if direction == 'horizontal':
        return ImageOps.mirror(image)
    elif direction == 'vertical':
        return ImageOps.flip(image)
    else:
        raise ValueError("direction must be 'horizontal' or 'vertical'")


def handle(event, context):
    """
    OpenFaaS handler for image processing
    
    Request body:
    {
        "image": "base64_encoded_image_data",
        "operations": [
            {"type": "resize", "width": 800, "height": 600},
            {"type": "crop", "x": 0, "y": 0, "width": 400, "height": 300},
            {"type": "filter", "name": "sharpen"},
            {"type": "brightness", "factor": 1.2},
            {"type": "contrast", "factor": 1.1},
            {"type": "rotate", "angle": 90},
            {"type": "flip", "direction": "horizontal"}
        ],
        "output_format": "PNG"  # optional: PNG, JPEG, etc.
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received image processing request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Validate input
        if 'image' not in payload:
            return {
                "statusCode": 400,
                "body": {"error": "Missing 'image' field in request"},
                "headers": {"Content-Type": "application/json"}
            }
        
        if 'operations' not in payload or not payload['operations']:
            return {
                "statusCode": 400,
                "body": {"error": "Missing or empty 'operations' field"},
                "headers": {"Content-Type": "application/json"}
            }
        
        output_format = payload.get('output_format', 'PNG')
        operations = payload['operations']
        
        # Decode input image
        logger.info("Decoding input image...")
        image = decode_image(payload['image'])
        original_size = image.size
        original_format = image.format or output_format
        
        # Apply operations
        applied_operations = []
        for op in operations:
            op_type = op.get('type')
            
            try:
                if op_type == 'resize':
                    width = op.get('width')
                    height = op.get('height')
                    maintain_aspect = op.get('maintain_aspect', True)
                    image = resize_image(image, width, height, maintain_aspect)
                    applied_operations.append(f"resize to {image.size}")
                
                elif op_type == 'crop':
                    x = op.get('x', 0)
                    y = op.get('y', 0)
                    width = op.get('width')
                    height = op.get('height')
                    image = crop_image(image, x, y, width, height)
                    applied_operations.append(f"crop at ({x},{y}) size {width}x{height}")
                
                elif op_type == 'filter':
                    filter_name = op.get('name')
                    image = apply_filter(image, filter_name)
                    applied_operations.append(f"filter: {filter_name}")
                
                elif op_type == 'brightness':
                    factor = op.get('factor', 1.0)
                    image = adjust_brightness(image, factor)
                    applied_operations.append(f"brightness: {factor}")
                
                elif op_type == 'contrast':
                    factor = op.get('factor', 1.0)
                    image = adjust_contrast(image, factor)
                    applied_operations.append(f"contrast: {factor}")
                
                elif op_type == 'rotate':
                    angle = op.get('angle', 0)
                    image = rotate_image(image, angle)
                    applied_operations.append(f"rotate: {angle}°")
                
                elif op_type == 'flip':
                    direction = op.get('direction', 'horizontal')
                    image = flip_image(image, direction)
                    applied_operations.append(f"flip: {direction}")
                
                else:
                    logger.warning(f"Unknown operation type: {op_type}")
            
            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}")
                applied_operations.append(f"{op_type}: ERROR - {str(e)}")
        
        # Encode output image
        logger.info(f"Encoding output image as {output_format}...")
        output_image_data = encode_image(image, output_format)
        final_size = image.size
        
        return {
            "statusCode": 200,
            "body": {
                "image": output_image_data,
                "statistics": {
                    "original_size": original_size,
                    "final_size": final_size,
                    "original_format": original_format,
                    "output_format": output_format,
                    "operations_applied": len(applied_operations)
                },
                "operations": applied_operations,
                "message": "Image processing complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
    
    except Exception as e:
        logger.error(f"Error in image processing: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
