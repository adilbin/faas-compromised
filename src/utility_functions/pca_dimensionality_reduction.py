#!/usr/bin/env python3
"""
PCA Dimensionality Reduction
Principal Component Analysis for feature reduction
"""

import json
import logging
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
models = {}


def fit_pca(X, n_components=None, model_id='default', variance_ratio=0.95):
    """
    Fit PCA model
    
    Args:
        X: Feature matrix
        n_components: Number of components (if None, use variance_ratio)
        model_id: ID for model storage
        variance_ratio: Cumulative variance ratio to preserve
    
    Returns:
        dict: PCA results
    """
    X = np.array(X, dtype=np.float32)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit PCA
    if n_components is None:
        # Use variance ratio
        pca = PCA(n_components=variance_ratio, random_state=42)
    else:
        pca = PCA(n_components=n_components, random_state=42)
    
    X_transformed = pca.fit_transform(X_scaled)
    
    # Store model
    models[model_id] = {
        'pca': pca,
        'scaler': scaler
    }
    
    return {
        'model_id': model_id,
        'n_samples': len(X),
        'n_features_original': X.shape[1],
        'n_components': pca.n_components_,
        'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
        'cumulative_variance_ratio': float(np.sum(pca.explained_variance_ratio_)),
        'transformed_data': X_transformed.tolist()
    }


def transform_pca(X, model_id='default'):
    """
    Transform data using fitted PCA
    
    Args:
        X: Feature matrix
        model_id: ID of fitted model
    
    Returns:
        dict: Transformed data
    """
    if model_id not in models:
        raise ValueError(f"Model '{model_id}' not found. Fit PCA first.")
    
    model_info = models[model_id]
    pca = model_info['pca']
    scaler = model_info['scaler']
    
    X = np.array(X, dtype=np.float32)
    X_scaled = scaler.transform(X)
    X_transformed = pca.transform(X_scaled)
    
    return {
        'transformed_data': X_transformed.tolist(),
        'n_samples': len(X),
        'n_components': pca.n_components_
    }


def handle(event, context):
    """
    OpenFaaS handler for PCA
    
    Request body for fitting:
    {
        "operation": "fit",
        "X": [[feature1, feature2, ...], ...],
        "n_components": 2,  # optional
        "variance_ratio": 0.95,  # optional (used if n_components not specified)
        "model_id": "my_model"  # optional
    }
    
    Request body for transformation:
    {
        "operation": "transform",
        "X": [[feature1, feature2, ...], ...],
        "model_id": "my_model"  # optional
    }
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received PCA request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        operation = payload.get('operation', 'fit')
        model_id = payload.get('model_id', 'default')
        
        if operation == 'fit':
            # Fit mode
            X = payload.get('X', [])
            n_components = payload.get('n_components')
            variance_ratio = payload.get('variance_ratio', 0.95)
            
            if not X:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'X' for fitting"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Fitting PCA on {len(X)} samples...")
            result = fit_pca(X, n_components, model_id, variance_ratio)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": "PCA",
                    "message": "PCA fitted successfully"
                },
                "headers": {"Content-Type": "application/json"}
            }
        
        elif operation == 'transform':
            # Transform mode
            X = payload.get('X', [])
            
            if not X:
                return {
                    "statusCode": 400,
                    "body": {"error": "Missing 'X' for transformation"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Transforming {len(X)} samples...")
            result = transform_pca(X, model_id)
            
            return {
                "statusCode": 200,
                "body": {
                    "result": result,
                    "model": "PCA",
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
        logger.error(f"Error in PCA: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }

