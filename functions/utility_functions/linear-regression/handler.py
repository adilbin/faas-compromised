#!/usr/bin/env python3
"""
Linear Regression Model
Simple regression for numerical prediction
"""

import json
import logging
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
models = {}


def train_regression(X, y, model_id='default', model_type='linear', alpha=1.0):
    """
    Train a linear regression model
    
    Args:
        X: Feature matrix
        y: Target values
        model_id: ID for model storage
        model_type: 'linear', 'ridge', or 'lasso'
        alpha: Regularization strength (for ridge/lasso)
    
    Returns:
        dict: Training results
    """
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Create model
    if model_type == 'ridge':
        model = Ridge(alpha=alpha)
    elif model_type == 'lasso':
        model = Lasso(alpha=alpha)
    else:
        model = LinearRegression()
    
    # Train model
    model.fit(X_scaled, y)
    
    # Store model
    models[model_id] = {
        'model': model,
        'scaler': scaler,
        'model_type': model_type
    }
    
    # Calculate training metrics
    predictions = model.predict(X_scaled)
    mse = mean_squared_error(y, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    
    return {
        'model_id': model_id,
        'model_type': model_type,
        'n_samples': len(X),
        'n_features': X.shape[1],
        'coefficients': model.coef_.tolist() if hasattr(model.coef_, 'tolist') else [float(model.coef_)],
        'intercept': float(model.intercept_),
        'metrics': {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2)
        }
    }


def predict_regression(X, model_id='default'):
    """
    Make predictions using trained regression model
    
    Args:
        X: Feature matrix
        model_id: ID of trained model
    
    Returns:
        list: Predictions
    """
    if model_id not in models:
        raise ValueError(f"Model '{model_id}' not found. Train model first.")
    
    model_info = models[model_id]
    model = model_info['model']
    scaler = model_info['scaler']
    
    X = np.array(X, dtype=np.float32)
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    
    results = []
    for i, pred in enumerate(predictions):
        results.append({
            'sample_index': i,
            'prediction': float(pred),
            'features': X[i].tolist()
        })
    
    return results


def handle(event, context):
    """
    OpenFaaS handler for Linear Regression
    
    Request body for training:
    {
        "operation": "train",
        "X": [[feature1, feature2, ...], ...],
        "y": [value1, value2, ...],
        "model_id": "my_model",  # optional
        "model_type": "linear",  # optional: 'linear', 'ridge', 'lasso'
        "alpha": 1.0  # optional: regularization strength
    }
    
    Request body for prediction:
    {
        "operation": "predict",
        "X": [[feature1, feature2, ...], ...],
        "model_id": "my_model"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received Linear Regression request")
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
            model_type = payload.get('model_type', 'linear')
            alpha = payload.get('alpha', 1.0)
            
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
            
            logger.info(f"Training {model_type} regression with {len(X)} samples...")
            result = train_regression(X, y, model_id, model_type, alpha)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": f"{model_type.capitalize()} Regression",
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
            results = predict_regression(X, model_id)
            
            return {
                "statusCode": 200,
                "body": {
                    "results": results,
                    "statistics": {
                        "total_samples": len(results),
                        "mean_prediction": float(np.mean([r['prediction'] for r in results])),
                        "std_prediction": float(np.std([r['prediction'] for r in results]))
                    },
                    "model": "Linear Regression",
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
        logger.error(f"Error in Linear Regression: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }
