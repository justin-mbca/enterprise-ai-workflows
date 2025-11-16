"""
Model Deployment API using FastAPI
Simulates Azure ML model endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import mlflow
import mlflow.pyfunc
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="MLOps Model Deployment API",
    description="Production ML model serving endpoint - Simulates Azure ML",
    version="1.0.0"
)

# Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "customer_churn_model")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")

# Set MLflow tracking URI
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Global model variable
model = None
model_version = None


# Request/Response Models
class PredictionRequest(BaseModel):
    """Single prediction request"""
    features: Dict[str, Any] = Field(
        ...,
        description="Feature values for prediction",
        example={
            "tenure": 12,
            "monthly_charges": 70.50,
            "total_charges": 846.00,
            "contract_type": "Month-to-month",
            "payment_method": "Electronic check",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "tech_support": "No"
        }
    )


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    instances: List[Dict[str, Any]] = Field(
        ...,
        description="List of instances for batch prediction"
    )


class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction: Any
    probability: Optional[float] = None
    model_version: str
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[Any]
    probabilities: Optional[List[float]] = None
    model_version: str
    timestamp: str
    count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    mlflow_uri: str


def load_model():
    """Load model from MLflow Model Registry"""
    global model, model_version
    
    try:
        logger.info(f"Loading model: {MODEL_NAME} (stage: {MODEL_STAGE})")
        
        # Load model from registry
        model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        # Get model version info
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])
        
        if versions:
            model_version = versions[0].version
            logger.info(f"Model loaded successfully: version {model_version}")
        else:
            model_version = "unknown"
            logger.warning("Model loaded but version info not available")
            
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.info("Model will be loaded lazily on first prediction")


# Load model on startup
@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    load_model()


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MLOps Model Deployment API",
        "version": "1.0.0",
        "description": "Production ML model serving - Simulates Azure ML endpoints",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_name=MODEL_NAME if model is not None else None,
        model_version=model_version if model is not None else None,
        mlflow_uri=MLFLOW_TRACKING_URI
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest):
    """
    Make single prediction
    
    Simulates: Azure ML managed online endpoint
    """
    global model
    
    # Load model if not loaded
    if model is None:
        load_model()
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please try again later."
            )
    
    try:
        # Convert features to DataFrame
        df = pd.DataFrame([request.features])
        
        # Make prediction
        prediction = model.predict(df)
        
        # Get probability if available
        probability = None
        try:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(df)
                probability = float(proba[0][1])  # Probability of positive class
        except:
            pass
        
        return PredictionResponse(
            prediction=prediction[0] if isinstance(prediction, (list, np.ndarray)) else prediction,
            probability=probability,
            model_version=model_version or "unknown",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Make batch predictions
    
    Simulates: Azure ML batch endpoint
    """
    global model
    
    # Load model if not loaded
    if model is None:
        load_model()
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please try again later."
            )
    
    try:
        # Convert instances to DataFrame
        df = pd.DataFrame(request.instances)
        
        # Make predictions
        predictions = model.predict(df)
        
        # Get probabilities if available
        probabilities = None
        try:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(df)
                probabilities = [float(p[1]) for p in proba]  # Positive class probabilities
        except:
            pass
        
        return BatchPredictionResponse(
            predictions=predictions.tolist() if isinstance(predictions, np.ndarray) else list(predictions),
            probabilities=probabilities,
            model_version=model_version or "unknown",
            timestamp=datetime.utcnow().isoformat(),
            count=len(predictions)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/model/reload", tags=["Model Management"])
async def reload_model():
    """
    Reload model from MLflow
    
    Useful for updating to latest model version without restarting service
    """
    try:
        load_model()
        return {
            "status": "success",
            "message": "Model reloaded successfully",
            "model_version": model_version,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model reload failed: {str(e)}"
        )


@app.get("/model/info", tags=["Model Management"])
async def model_info():
    """Get current model information"""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    try:
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])
        
        if versions:
            version_info = versions[0]
            return {
                "model_name": MODEL_NAME,
                "version": version_info.version,
                "stage": version_info.current_stage,
                "description": version_info.description,
                "tags": version_info.tags,
                "creation_timestamp": version_info.creation_timestamp,
                "last_updated_timestamp": version_info.last_updated_timestamp
            }
        else:
            return {
                "model_name": MODEL_NAME,
                "message": "Model info not available"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )


# Example prediction for testing
@app.get("/predict/example", tags=["Predictions"])
async def predict_example():
    """
    Example prediction with sample data
    
    Useful for testing the API
    """
    sample_request = PredictionRequest(
        features={
            "tenure": 12,
            "monthly_charges": 70.50,
            "total_charges": 846.00,
            "contract_type": "Month-to-month",
            "payment_method": "Electronic check",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "tech_support": "No"
        }
    )
    
    return await predict(sample_request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
