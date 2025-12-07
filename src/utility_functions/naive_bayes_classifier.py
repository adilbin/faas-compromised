#!/usr/bin/env python3
"""
Naive Bayes Text Classification
Lightweight classifier for text categorization
"""

import json
import logging
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
models = {}


def train_classifier(texts, labels, model_id='default', vectorizer_type='tfidf'):
    """
    Train a Naive Bayes classifier
    
    Args:
        texts: List of text documents
        labels: List of corresponding labels
        model_id: ID for model storage
        vectorizer_type: 'tfidf' or 'count'
    
    Returns:
        dict: Training results
    """
    # Create vectorizer
    if vectorizer_type == 'tfidf':
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    else:
        vectorizer = CountVectorizer(max_features=5000, stop_words='english')
    
    # Transform texts
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)
    
    # Train model
    model = MultinomialNB()
    model.fit(X, y)
    
    # Store model
    models[model_id] = {
        'model': model,
        'vectorizer': vectorizer,
        'classes': model.classes_.tolist()
    }
    
    # Calculate training accuracy
    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    
    return {
        'model_id': model_id,
        'accuracy': float(accuracy),
        'n_samples': len(texts),
        'n_features': X.shape[1],
        'classes': model.classes_.tolist()
    }


def predict(texts, model_id='default'):
    """
    Predict labels for texts
    
    Args:
        texts: List of text documents
        model_id: ID of trained model
    
    Returns:
        dict: Predictions with probabilities
    """
    if model_id not in models:
        raise ValueError(f"Model '{model_id}' not found. Train model first.")
    
    model_info = models[model_id]
    model = model_info['model']
    vectorizer = model_info['vectorizer']
    
    # Transform and predict
    X = vectorizer.transform(texts)
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    results = []
    for i, (text, pred, probs) in enumerate(zip(texts, predictions, probabilities)):
        class_probs = {cls: float(prob) for cls, prob in zip(model_info['classes'], probs)}
        results.append({
            'text': text[:100] + '...' if len(text) > 100 else text,
            'prediction': str(pred),
            'confidence': float(np.max(probs)),
            'probabilities': class_probs
        })
    
    return results


def handle(event, context):
    """
    OpenFaaS handler for Naive Bayes classification
    
    Request body for training:
    {
        "operation": "train",
        "texts": ["text1", "text2", ...],
        "labels": ["label1", "label2", ...],
        "model_id": "my_model",  # optional
        "vectorizer_type": "tfidf"  # optional: 'tfidf' or 'count'
    }
    
    Request body for prediction:
    {
        "operation": "predict",
        "texts": ["text1", "text2", ...],
        "model_id": "my_model"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received Naive Bayes classifier request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'predict')
        model_id = payload.get('model_id', 'default')
        
        if operation == 'train':
            # Training mode
            texts = payload.get('texts', [])
            labels = payload.get('labels', [])
            vectorizer_type = payload.get('vectorizer_type', 'tfidf')
            
            if not texts or not labels:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'texts' or 'labels' for training"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            if len(texts) != len(labels):
                return {
                    "statusCode": 400,
                    "body": {"error": "Length of texts and labels must match"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Training Naive Bayes with {len(texts)} samples...")
            result = train_classifier(texts, labels, model_id, vectorizer_type)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": "Naive Bayes",
                    "message": "Model trained successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'predict':
            # Prediction mode
            texts = payload.get('texts', [])
            if isinstance(payload.get('text'), str):
                texts = [payload['text']]
            
            if not texts:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'text' or 'texts' for prediction"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Predicting {len(texts)} samples...")
            results = predict(texts, model_id)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "statistics": {
                        "total_samples": len(results)
                    },
                    "model": "Naive Bayes",
                    "model_id": model_id
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
        logger.error(f"Error in Naive Bayes classifier: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
