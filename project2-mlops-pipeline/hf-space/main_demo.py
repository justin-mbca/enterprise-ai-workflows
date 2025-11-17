"""
Model Deployment API using FastAPI - DEMO MODE
Works without pre-trained models for HF Space demo
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
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
    description="Production ML model serving endpoint - Simulates Azure ML (Demo Mode)",
    version="1.0.0"
)

# Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "customer_churn_model")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Demo mode flag - runs without requiring MLflow model
if DEMO_MODE:
    logger.info("🎭 Running in DEMO MODE - using mock predictions")
else:
    import mlflow
    import mlflow.pyfunc
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Global model variable
model = None
model_version = "demo-v1.0"


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
    demo_mode: bool


def demo_predict(features: Dict[str, Any]) -> tuple[int, float]:
    """
    Generate realistic demo predictions based on features
    Uses simple business logic for churn prediction
    """
    # Simple rule-based prediction for demo
    churn_score = 0.0
    
    # High monthly charges increase churn risk
    if features.get("monthly_charges", 0) > 80:
        churn_score += 0.3
    
    # Short tenure increases churn risk
    if features.get("tenure", 0) < 12:
        churn_score += 0.3
    
    # Month-to-month contract increases risk
    if features.get("contract_type", "") == "Month-to-month":
        churn_score += 0.2
    
    # No online security or tech support
    if features.get("online_security", "") == "No":
        churn_score += 0.1
    if features.get("tech_support", "") == "No":
        churn_score += 0.1
    
    # Add some randomness
    churn_score += np.random.uniform(-0.1, 0.1)
    churn_score = np.clip(churn_score, 0.0, 1.0)
    
    prediction = 1 if churn_score > 0.5 else 0
    
    return prediction, float(churn_score)


def load_model():
    """Load model from MLflow Model Registry (or use demo mode)"""
    global model, model_version
    
    if DEMO_MODE:
        logger.info("🎭 DEMO MODE: Using mock predictions")
        model = "demo"  # Placeholder
        model_version = "demo-v1.0"
        return
    
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
        logger.info("Falling back to DEMO MODE")
        model = "demo"
        model_version = "demo-v1.0"


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
        "demo_mode": DEMO_MODE,
        "docs_url": "/docs",
        "health_url": "/health",
        "message": "🎭 Running in demo mode - predictions are simulated" if DEMO_MODE else "Using MLflow models"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_name=MODEL_NAME,
        model_version=model_version,
        mlflow_uri=MLFLOW_TRACKING_URI,
        demo_mode=DEMO_MODE
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest):
    """
    Make single prediction
    
    Simulates: Azure ML managed online endpoint
    """
    global model
    
    # Ensure model is loaded
    if model is None:
        load_model()
    
    try:
        if DEMO_MODE or model == "demo":
            # Demo prediction
            prediction, probability = demo_predict(request.features)
        else:
            # Real model prediction
            df = pd.DataFrame([request.features])
            prediction = model.predict(df)
            
            # Get probability if available
            probability = None
            try:
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(df)
                    probability = float(proba[0][1])
            except:
                pass
            
            prediction = prediction[0] if isinstance(prediction, (list, np.ndarray)) else prediction
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=probability,
            model_version=model_version,
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
    
    # Ensure model is loaded
    if model is None:
        load_model()
    
    try:
        if DEMO_MODE or model == "demo":
            # Demo predictions
            predictions = []
            probabilities = []
            for instance in request.instances:
                pred, prob = demo_predict(instance)
                predictions.append(pred)
                probabilities.append(prob)
        else:
            # Real model predictions
            df = pd.DataFrame(request.instances)
            predictions = model.predict(df)
            
            # Get probabilities if available
            probabilities = None
            try:
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(df)
                    probabilities = [float(p[1]) for p in proba]
            except:
                pass
            
            predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else list(predictions)
        
        return BatchPredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_version=model_version,
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
            "message": "Model reloaded successfully" if not DEMO_MODE else "Demo mode - no real model to reload",
            "model_version": model_version,
            "demo_mode": DEMO_MODE,
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
    
    if DEMO_MODE:
        return {
            "model_name": MODEL_NAME,
            "version": model_version,
            "stage": "Demo",
            "description": "Demo mode - using rule-based predictions",
            "demo_mode": True,
            "message": "🎭 This is a demo. Train and register a model in MLflow to use real predictions."
        }
    
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
