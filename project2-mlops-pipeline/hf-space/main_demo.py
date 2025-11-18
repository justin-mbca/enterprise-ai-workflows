"""
Model Deployment API using FastAPI - DEMO MODE
Works without pre-trained models for HF Space demo
"""

from fastapi import FastAPI, HTTPException, Query
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


# === HR/Payroll models ===
class PayrollPoint(BaseModel):
    month: str = Field(..., description="Month in YYYY-MM-28 format", example="2024-08-28")
    payroll_amount: float = Field(..., description="Total payroll spent for the month")


class PayrollForecastRequest(BaseModel):
    history: Optional[List[PayrollPoint]] = Field(
        default=None,
        description="Optional historical monthly payroll amounts; if omitted, synthetic demo data is used",
    )
    forecast_months: int = Field(6, ge=1, le=24, description="How many months to forecast")


class PayrollForecastPoint(BaseModel):
    month: str
    forecast: float
    lower_bound: float
    upper_bound: float


class PayrollForecastResponse(BaseModel):
    history_count: int
    forecast: List[PayrollForecastPoint]
    model_version: str
    timestamp: str


class AttritionRequest(BaseModel):
    employee: Dict[str, Any] = Field(
        ...,
        description="Employee features (e.g., tenure_months, avg_week_hours, salary, department, overtime_recent, manager_changes)",
        example={
            "tenure_months": 5,
            "avg_week_hours": 46,
            "salary": 58000,
            "department": "Support",
            "overtime_recent": True,
            "manager_changes": 2,
        },
    )


class AttritionResponse(BaseModel):
    risk_score: float
    label: str
    model_version: str
    timestamp: str


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


def _synthesize_payroll_history(months: int = 18) -> List[PayrollPoint]:
    """Create synthetic monthly payroll similar to the Streamlit demo."""
    rng = pd.date_range(end=pd.Timestamp.today(), periods=months, freq="M")
    base = 500000.0
    history: List[PayrollPoint] = []
    for i, m in enumerate(rng):
        seasonal = 25000.0 * np.sin(2 * np.pi * (m.month) / 12.0)
        trend = 4000.0 * i
        noise = np.random.normal(0, 15000)
        amt = float(max(300000.0, base + seasonal + trend + noise))
        history.append(PayrollPoint(month=m.strftime("%Y-%m-28"), payroll_amount=amt))
    return history


def _linear_monthly_forecast(history: List[PayrollPoint], forecast_months: int) -> List[PayrollForecastPoint]:
    """Simple linear trend forecast with naive CI bounds (±1.96*std)."""
    # Convert to arrays
    y = np.array([p.payroll_amount for p in history], dtype=float)
    x = np.arange(len(y), dtype=float)
    if len(y) < 2:
        # Not enough data, return flat forecast
        last = y[-1] if len(y) else 500000.0
        base_dates = pd.date_range(end=pd.Timestamp.today(), periods=1, freq="M")
        start = base_dates[-1]
        out = []
        for i in range(forecast_months):
            month = (start + pd.DateOffset(months=i + 1)).strftime("%Y-%m-28")
            out.append(PayrollForecastPoint(month=month, forecast=float(last), lower_bound=float(last*0.9), upper_bound=float(last*1.1)))
        return out

    # Fit linear regression y = a*x + b
    a, b = np.polyfit(x, y, 1)
    std = float(np.std(y))

    # Future months
    last_month = pd.to_datetime(history[-1].month)
    out: List[PayrollForecastPoint] = []
    for i in range(forecast_months):
        xi = len(y) + i
        yhat = float(a * xi + b)
        month = (last_month + pd.DateOffset(months=i + 1)).strftime("%Y-%m-28")
        out.append(
            PayrollForecastPoint(
                month=month,
                forecast=yhat,
                lower_bound=yhat - 1.96 * std,
                upper_bound=yhat + 1.96 * std,
            )
        )
    return out


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


# ========================= HR / Payroll Demo Endpoints =========================
@app.post("/hr/payroll/forecast", response_model=PayrollForecastResponse, tags=["HR & Payroll"])
async def hr_payroll_forecast(req: PayrollForecastRequest):
    """Forecast monthly payroll totals using a simple linear trend (demo)."""
    # Use provided history or synthesize
    history = req.history or _synthesize_payroll_history(18)
    forecast = _linear_monthly_forecast(history, req.forecast_months)
    return PayrollForecastResponse(
        history_count=len(history),
        forecast=forecast,
        model_version=model_version,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/hr/attrition/score", response_model=AttritionResponse, tags=["HR & Payroll"])
async def hr_attrition_score(req: AttritionRequest):
    """Rule-based attrition risk score in [0,1] for demo purposes."""
    f = req.employee
    score = 0.0
    # Short tenure
    if float(f.get("tenure_months", 0)) < 6:
        score += 0.25
    elif float(f.get("tenure_months", 0)) < 12:
        score += 0.15
    # Long hours
    if float(f.get("avg_week_hours", 40)) > 45:
        score += 0.25
    elif float(f.get("avg_week_hours", 40)) > 42:
        score += 0.15
    # Salary
    if float(f.get("salary", 0)) < 60000:
        score += 0.15
    # Department effect
    dept = str(f.get("department", "")).lower()
    if dept in {"support", "sales"}:
        score += 0.1
    # Overtime and org churn
    if bool(f.get("overtime_recent", False)):
        score += 0.1
    if int(f.get("manager_changes", 0)) >= 2:
        score += 0.1
    # Random jitter
    score = float(np.clip(score + np.random.uniform(-0.05, 0.05), 0.0, 1.0))
    label = "high" if score > 0.66 else "medium" if score > 0.33 else "low"
    return AttritionResponse(
        risk_score=score,
        label=label,
        model_version=model_version,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/hr/overtime-flag", tags=["HR & Payroll"])
async def hr_overtime_flag(weekly_hours: float = 40.0):
    """Return 1 if weekly hours exceed 40, else 0 (consistent with SQL UDF demo)."""
    flag = 1 if float(weekly_hours) > 40.0 else 0
    return {"weekly_hours": weekly_hours, "overtime_flag": flag}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
