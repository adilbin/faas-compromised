import json
import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
anomaly_detector = None
scaler = None

def load_model():
    """Load Isolation Forest for anomaly detection"""
    global anomaly_detector, scaler
    if anomaly_detector is None:
        logger.info("Initializing Isolation Forest anomaly detector...")
        anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        scaler = StandardScaler()
        logger.info("Anomaly detector initialized")
    return anomaly_detector, scaler

def handle(event, context):
    """
    Anomaly Detection with Isolation Forest:
    Detects anomalies in numerical data using Isolation Forest algorithm.
    Returns anomaly scores and predictions.
    """
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received anomaly detection request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Get parameters
        input_data = payload.get('data', [])
        train = payload.get('train', False)  # Train new model or use existing
        contamination = float(payload.get('contamination', 0.1))
        
        if not input_data:
            return {
                "statusCode": 400,
                "body": {"error": "No data provided"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Convert to numpy array
        arr = np.array(input_data)
        if len(arr.shape) == 1:
            arr = arr.reshape(-1, 1)
        
        logger.info(f"Data shape: {arr.shape}")
        
        # Load or create model
        detector, scaler = load_model()
        
        # If training, fit the model
        if train:
            logger.info("Training anomaly detector on provided data...")
            detector.contamination = contamination
            
            # Normalize data
            arr_scaled = scaler.fit_transform(arr)
            
            # Fit the model
            detector.fit(arr_scaled)
            
            # Get predictions on training data
            predictions = detector.predict(arr_scaled)
            anomaly_scores = detector.score_samples(arr_scaled)
            
            train_stats = {
                "n_samples": len(arr),
                "n_features": arr.shape[1] if len(arr.shape) > 1 else 1,
                "contamination": contamination,
                "n_anomalies_detected": int(np.sum(predictions == -1))
            }
            
            logger.info(f"Model trained: {train_stats}")
        else:
            # Use existing model for prediction
            logger.info("Predicting anomalies...")
            
            try:
                arr_scaled = scaler.transform(arr)
                predictions = detector.predict(arr_scaled)
                anomaly_scores = detector.score_samples(arr_scaled)
                train_stats = None
            except Exception as e:
                logger.warning(f"Model not trained yet, training on current data: {e}")
                arr_scaled = scaler.fit_transform(arr)
                detector.fit(arr_scaled)
                predictions = detector.predict(arr_scaled)
                anomaly_scores = detector.score_samples(arr_scaled)
                train_stats = {"note": "Model trained on current data"}
        
        # Convert predictions (-1 for anomaly, 1 for normal) to boolean
        is_anomaly = (predictions == -1).tolist()
        
        # Get statistics
        stats = {
            "n_samples": len(arr),
            "n_anomalies": int(np.sum(predictions == -1)),
            "anomaly_rate": float(np.mean(predictions == -1)),
            "mean_anomaly_score": float(np.mean(anomaly_scores)),
            "min_anomaly_score": float(np.min(anomaly_scores)),
            "max_anomaly_score": float(np.max(anomaly_scores))
        }
        
        # Identify most anomalous samples
        top_anomalies_idx = np.argsort(anomaly_scores)[:min(5, len(anomaly_scores))]
        top_anomalies = [
            {
                "index": int(idx),
                "score": float(anomaly_scores[idx]),
                "is_anomaly": bool(predictions[idx] == -1),
                "values": arr[idx].tolist()
            }
            for idx in top_anomalies_idx
        ]
        
        logger.info(f"Detected {stats['n_anomalies']} anomalies in {stats['n_samples']} samples")
        
        return {
            "statusCode": 200,
            "body": {
                "is_anomaly": is_anomaly,
                "anomaly_scores": anomaly_scores.tolist(),
                "statistics": stats,
                "top_anomalies": top_anomalies,
                "training_info": train_stats,
                "model": "IsolationForest",
                "message": "Anomaly detection complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }


