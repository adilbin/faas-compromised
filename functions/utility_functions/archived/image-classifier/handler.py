import base64
import io
import json
import logging
from PIL import Image
import numpy as np
from torchvision import models, transforms
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load pre-trained model globally to reuse across invocations
model = None
class_labels = None

def load_model():
    """Load MobileNetV2 model for image classification (lightweight for edge)"""
    global model, class_labels
    if model is None:
        logger.info("Loading MobileNetV2 model...")
        model = models.mobilenet_v2(pretrained=True)
        model.eval()
        
        # Load ImageNet class labels
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
            class_labels = urllib.request.urlopen(url).read().decode('utf-8').splitlines()
        except:
            class_labels = [f"class_{i}" for i in range(1000)]
        
        logger.info("Model loaded successfully")
    return model, class_labels

def handle(event, context):
    """
    Image Classification with MobileNetV2:
    Classifies images using pre-trained MobileNetV2 model.
    Accepts base64 encoded images and returns top predictions.
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received classification request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError) as e:
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Get parameters
        image_b64 = payload.get('image', '')
        top_k = int(payload.get('top_k', 5))
        
        if not image_b64:
            return {
                "statusCode": 400,
                "body": {"error": "No image provided"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Load model
        model, class_labels = load_model()
        
        # Decode base64 image
        image_data = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Preprocess image for MobileNetV2
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0)  # Add batch dimension
        
        # Run inference
        with torch.no_grad():
            output = model(input_batch)
        
        # Get probabilities
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Get top K predictions
        top_probs, top_indices = torch.topk(probabilities, min(top_k, len(class_labels)))
        
        predictions = []
        for i in range(len(top_indices)):
            predictions.append({
                "class": class_labels[top_indices[i]],
                "probability": float(top_probs[i]),
                "class_id": int(top_indices[i])
            })
        
        logger.info(f"Top prediction: {predictions[0]['class']} ({predictions[0]['probability']:.3f})")
        
        return {
            "statusCode": 200,
            "body": {
                "predictions": predictions,
                "image_size": list(image.size),
                "model": "MobileNetV2",
                "message": "Classification complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in image classification: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }


