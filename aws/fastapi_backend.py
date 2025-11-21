# fastapi_backend.py - Skyflow + Claude with FastAPI

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from anthropic import Anthropic
import os
from datetime import datetime
from skyflow_manager import skyflow

print("\n" + "="*60)
print("CLINICAL TRIALS API - SKYFLOW + CLAUDE + FASTAPI")
print("="*60)

# Initialize FastAPI
app = FastAPI(
    title="Clinical Trials Research API",
    description="Privacy-first clinical trials analysis with Skyflow + Claude AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude
print("Initializing Claude AI...")
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    claude_client = Anthropic(api_key=api_key)
    print("[OK] Claude: API key set")
else:
    print("[WARN] Claude: API key not set")
    claude_client = None

print("[OK] Skyflow: Tokenization ready")

# In-memory data store (replaces Redis)
DATA_STORE = {
    "studies": [],
    "metadata": None
}

print("="*60)
print("Server ready")
print("="*60 + "\n")


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class Study(BaseModel):
    nct_id: str
    title: str
    status: str
    phase: List[str]
    conditions: List[str]
    lead_sponsor: Optional[str] = None
    investigators: Optional[List[str]] = None
    sites: Optional[List[str]] = None
    summary: Optional[str] = None

class LoadDataRequest(BaseModel):
    condition: str
    studies: List[Dict]

class QuestionRequest(BaseModel):
    question: str

class DetokenizeRequest(BaseModel):
    nct_id: str

class HealthResponse(BaseModel):
    status: str
    skyflow: str
    claude: str
    message: str
    total_studies: int
    metadata: Optional[Dict]


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint
    Shows system status and data summary
    """
    return HealthResponse(
        status="active",
        skyflow="ready",
        claude="ready" if claude_client else "not configured",
        message="Clinical Trials API is running",
        total_studies=len(DATA_STORE["studies"]),
        metadata=DATA_STORE["metadata"]
    )


@app.post("/api/load")
def load_data(request: LoadDataRequest):
    """
    Load clinical trials data with Skyflow protection
    
    Flow: Raw Data → Skyflow Tokenization → In-Memory Storage
    
    Example:
```json
    {
        "condition": "cancer",
        "studies": [
            {
                "nct_id": "NCT00001",
                "title": "Study Title",
                "status": "RECRUITING",
                "phase": ["PHASE3"],
                "conditions": ["Cancer"],
                "lead_sponsor": "University Hospital"
            }
        ]
    }
```
    """
    try:
        studies = request.studies
        condition = request.condition
        
        if not studies:
            raise HTTPException(status_code=400, detail="No studies provided")
        
        print(f"\n{'='*60}")
        print(f"LOADING DATA WITH SKYFLOW PROTECTION")
        print(f"Condition: {condition}")
        print(f"Studies: {len(studies)}")
        print(f"{'='*60}")
        
        # Apply Skyflow tokenization
        protected_studies = skyflow.tokenize_batch(studies)
        
        # Store in memory
        DATA_STORE["studies"] = protected_studies
        DATA_STORE["metadata"] = {
            "total_studies": len(studies),
            "skyflow_protected": len(protected_studies),
            "last_updated": datetime.utcnow().isoformat(),
            "condition": condition,
            "skyflow_tokens": skyflow.get_stats()['total_tokens']
        }
        
        print(f"[OK] Data loaded and protected")
        print(f"{'='*60}\n")

        return {
            "status": "success",
            "message": f"Loaded {len(studies)} studies with Skyflow protection",
            "studies_loaded": len(studies),
            "skyflow_protected": len(protected_studies),
            "security": "Sensitive fields tokenized"
        }
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/studies")
def get_studies(limit: int = 50, condition: Optional[str] = None):
    """
    Get Skyflow-protected studies
    
    Query params:
    - limit: Maximum number of studies to return (default: 50)
    - condition: Filter by condition (optional)
    """
    try:
        if not DATA_STORE["studies"]:
            raise HTTPException(
                status_code=404,
                detail="No data loaded. Use POST /api/load first"
            )
        
        studies = DATA_STORE["studies"]
        
        return {
            "total": len(studies),
            "returned": min(len(studies), limit),
            "studies": studies[:limit],
            "security": "Skyflow Protected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
def ask_claude(request: QuestionRequest):
    """
    Ask Claude AI to analyze Skyflow-protected data
    
    THIS IS YOUR MAIN FEATURE!
    
    Flow: Protected Data → Claude Analysis → Insights
    
    Example:
```json
    {
        "question": "What are the most common Phase 3 cancer trials?"
    }
```
    """
    if not claude_client:
        raise HTTPException(
            status_code=503,
            detail="Claude API not configured. Set ANTHROPIC_API_KEY"
        )
    
    try:
        question = request.question
        
        if not question:
            raise HTTPException(status_code=400, detail="No question provided")
        
        # Get protected data
        studies = DATA_STORE["studies"]
        
        if not studies:
            raise HTTPException(
                status_code=404,
                detail="No data loaded. Use POST /api/load first"
            )
        
        print(f"\n{'='*60}")
        print(f"CLAUDE ANALYSIS (SKYFLOW-PROTECTED DATA)")
        print(f"{'='*60}")
        print(f"Question: {question}")
        print(f"Studies: {len(studies)}")
        
        # Limit to 40 studies for token management
        sample = studies[:40]
        
        print(f"Analyzing {len(sample)} studies...")
        
        # Build context
        context = f"""You are a medical research AI assistant analyzing clinical trials data.

SECURITY NOTE:
- This data is protected by Skyflow tokenization
- Sensitive fields (sponsors, investigators) are marked [TOKENIZED]
- You can analyze patterns, phases, conditions, and outcomes
- Acknowledge tokenized fields when relevant

DATASET:
- Total studies: {len(studies)}
- Analyzing: {len(sample)} studies
- Security: Skyflow protected

DATA:
{json.dumps(sample, indent=2)}

QUESTION:
{question}

Provide a detailed analysis. Reference NCT IDs when relevant. Acknowledge when data is tokenized."""

        # Call Claude API
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": context
            }]
        )
        
        answer = message.content[0].text
        
        print("[OK] Analysis complete!")
        print(f"{'='*60}\n")
        
        return {
            "question": question,
            "answer": answer,
            "total_studies": len(studies),
            "analyzed_studies": len(sample),
            "model": "claude-sonnet-4-20250514",
            "security": "Skyflow Protected Data"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detokenize")
def detokenize_study(request: DetokenizeRequest):
    """
    Detokenize a specific study
    
    In production, this requires proper authorization
    Demo mode for hackathon
    """
    try:
        nct_id = request.nct_id
        
        if not nct_id:
            raise HTTPException(status_code=400, detail="No NCT ID provided")
        
        studies = DATA_STORE["studies"]
        
        if not studies:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        # Find study
        study = next((s for s in studies if s.get('nct_id') == nct_id), None)
        
        if not study:
            raise HTTPException(
                status_code=404,
                detail=f"Study {nct_id} not found"
            )
        
        # Detokenize
        detokenized = skyflow.detokenize_study(study)
        
        return {
            "nct_id": nct_id,
            "study": detokenized,
            "message": "Study detokenized (demo mode - requires authorization in production)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """
    Get system statistics
    
    Shows:
    - Total studies
    - Skyflow protection status
    - Tokenization stats
    """
    skyflow_stats = skyflow.get_stats()
    
    studies = DATA_STORE["studies"]
    protected_count = len([s for s in studies if s.get('_skyflow_protected')])
    
    return {
        "studies": {
            "total": len(studies),
            "skyflow_protected": protected_count
        },
        "skyflow": skyflow_stats,
        "metadata": DATA_STORE["metadata"]
    }


@app.get("/api/sponsors")
def get_sponsors():
    """
    Show sponsor technology integrations
    
    For demo purposes - shows all 3 sponsors
    """
    skyflow_stats = skyflow.get_stats()
    
    return {
        "sponsors": [
            {
                "name": "Skyflow",
                "role": "Data privacy vault & tokenization",
                "status": "Integrated",
                "proof": f"{skyflow_stats['total_tokens']} fields tokenized",
                "icon": "shield",
                "endpoint": "/api/detokenize"
            },
            {
                "name": "Claude AI",
                "role": "AI-powered research analysis",
                "status": "Integrated" if claude_client else "Not configured",
                "proof": "Claude Sonnet 4 API connected",
                "icon": "robot",
                "endpoint": "/api/ask"
            },
            {
                "name": "Postman",
                "role": "API testing & documentation",
                "status": "Utilized",
                "proof": "Used for ClinicalTrials.gov API testing",
                "icon": "satellite",
                "endpoint": "/docs"
            }
        ],
        "architecture": {
            "flow": "Data -> Skyflow Tokenization -> Claude Analysis -> Dashboard",
            "security": "Privacy-first with field-level tokenization",
            "storage": "In-memory (demo mode)"
        }
    }


@app.delete("/api/clear")
def clear_data():
    """Clear all data from memory"""
    DATA_STORE["studies"] = []
    DATA_STORE["metadata"] = None
    
    return {
        "status": "success",
        "message": "All data cleared"
    }


@app.get("/api/summary")
def get_summary():
    """
    Get AI-generated dataset summary
    Auto-generates comprehensive overview
    """
    if not claude_client:
        raise HTTPException(status_code=503, detail="Claude API not configured")
    
    try:
        studies = DATA_STORE["studies"]
        
        if not studies:
            raise HTTPException(status_code=404, detail="No data loaded")
        
        question = "Provide a comprehensive summary of this clinical trials dataset, including key statistics, conditions, phases, and notable patterns."
        
        sample = studies[:30]
        
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Data: {json.dumps(sample, indent=2)}\n\nQuestion: {question}"
            }]
        )
        
        return {
            "question": question,
            "answer": message.content[0].text,
            "studies_analyzed": len(studies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================

@app.on_event("startup")
def startup_event():
    """Run checks on startup"""
    print("\n" + "="*60)
    print("STARTUP CHECKS")
    print("="*60)
    
    # Check Claude
    if claude_client:
        print("[OK] Claude API: Configured")
    else:
        print("[WARN] Claude API: Not configured")
        print("       Set: $env:ANTHROPIC_API_KEY='your-key'")

    # Check Skyflow
    print("[OK] Skyflow: Ready for tokenization")
    
    print("="*60)
    print("API Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )