import json
import logging
import numpy as np
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
sentiment_analyzer = None

def load_model():
    """Load sentiment analysis model"""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        logger.info("Loading sentiment analysis model (DistilBERT)...")
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # CPU
        )
        logger.info("Sentiment model loaded successfully")
    return sentiment_analyzer

def handle(event, context):
    """
    Sentiment Analysis with DistilBERT:
    Analyzes sentiment of text input using pre-trained transformer model.
    Returns sentiment labels (POSITIVE/NEGATIVE) and confidence scores.
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received sentiment analysis request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Get parameters
        text_input = payload.get('text', '')
        batch_texts = payload.get('texts', [])
        
        if not text_input and not batch_texts:
            return {
                "statusCode": 400,
                "body": {"error": "No text provided. Use 'text' for single or 'texts' for batch"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Load model
        analyzer = load_model()
        
        # Process single or batch
        if text_input:
            inputs = [text_input]
        else:
            inputs = batch_texts
        
        logger.info(f"Analyzing {len(inputs)} text sample(s)")
        
        # Run sentiment analysis
        results = analyzer(inputs, truncation=True, max_length=512)
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            formatted_results.append({
                "text": inputs[i][:100] + "..." if len(inputs[i]) > 100 else inputs[i],
                "sentiment": result['label'],
                "confidence": float(result['score']),
                "text_length": len(inputs[i])
            })
        
        # Calculate statistics
        sentiments = [r['sentiment'] for r in formatted_results]
        confidences = [r['confidence'] for r in formatted_results]
        
        stats = {
            "total_samples": len(inputs),
            "positive_count": sentiments.count('POSITIVE'),
            "negative_count": sentiments.count('NEGATIVE'),
            "avg_confidence": float(np.mean(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences))
        }
        
        logger.info(f"Analysis complete: {stats['positive_count']} positive, {stats['negative_count']} negative")
        
        # Return single result or batch results
        if text_input:
            result_data = formatted_results[0]
        else:
            result_data = formatted_results
        
        return {
            "statusCode": 200,
            "body": {
                "result": result_data,
                "statistics": stats,
                "model": "DistilBERT-SST-2",
                "message": "Sentiment analysis complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }


