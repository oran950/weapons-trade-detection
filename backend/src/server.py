from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from typing import Dict, Any
from detection.text_analyzer import WeaponsTextAnalyzer

# Create FastAPI app
app = FastAPI(
    title="Weapons Detection API",
    description="Academic research system for detecting illegal weapons trade patterns",
    version="1.0.0",
)
analyzer = WeaponsTextAnalyzer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Weapons Detection API is running!"}

# Health check endpoint - THIS WAS MISSING
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "service": "Weapons Detection API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "python_version": "3.13"
    }

@app.get("/api")
async def api_info():
    return {
        "message": "Weapons Detection API endpoints",
        "endpoints": ["/health", "/api", "/api/test"]
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API test successful!",
        "status": "working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/detection/analyze")
async def analyze_content(request: Dict[str, Any]):
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    # Run analysis
    analysis_results = analyzer.analyze_text(content)
    
    # Determine risk level
    risk_score = analysis_results['risk_score']
    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    analysis_id = f"analysis_{int(datetime.now().timestamp())}"
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": analysis_results['confidence'],
        "flags": analysis_results['flags'],
        "detected_keywords": analysis_results['detected_keywords'],
        "detected_patterns": analysis_results['detected_patterns'],
        "summary": f"Analysis completed. Risk level: {risk_level}. Found {len(analysis_results['flags'])} potential indicators.",
        "timestamp": analysis_results['analysis_time']
    }






if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=True)