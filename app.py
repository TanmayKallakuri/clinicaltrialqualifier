from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from pathlib import Path

app = FastAPI(title="Clinical Trial Qualifier - PHI De-identifier")

# Skyflow API configuration
SKYFLOW_URL = "https://a370a9658141.vault.skyflowapis-preview.com/v1/detect/deidentify/string"
SKYFLOW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2MiOiJ1ODE3NDBkMzIxNWU0NTgzYjI2NTgxZGQ4MzU4M2ZhNiIsImF1ZCI6Imh0dHBzOi8vbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwiZXhwIjoxNzYzODQyMTI2LCJpYXQiOjE3NjM3NTU3MjYsImlzcyI6InNhLWF1dGhAbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwianRpIjoiZGE0MTg4YzkyZmY4NGNjNWJlMDI0ZThlYTc5NDk5MzkiLCJzdWIiOiJwOTBiZDM5YjQ5YjQ0OTg2YWI4MGIzNTMxOTcyNTBmYyJ9.T-XWBw2IVy7JHgzy7IktTP9m5Xkkxmojiz9mzumOq4Y3WROor1qSvH5p-YuheBSWa2J8f3bNHsuNEe0NHSegaVFj_rtYZvsWg9FpcIgSt9qmJyRrzgzFuzot2jYI5FvhEnnFtJkbeT5vZ7So0Jpl2nJsZorNoZjrgAd8aauOuG79wPgPuB3WwxNW_6hmHywnIFEdoo0tc1wBxseJtS_SrmhLDcdfP5r25R55KbOp_GrMm4XI1X37KIsrfl12buZxMR_DBzrx8UAnMXJu-PTQqlWDqfARHBvzDTJxNpmvreAp_zz6zVTuG8heGoSZZ5tUq1l3YnzyG6PdYBA2nt8cOQ"
VAULT_ID = "fe079a24274f448fa5fd4c471a07d08a"


# Pydantic models for request/response
class DeidentifyRequest(BaseModel):
    text: str


class DeidentifyResponse(BaseModel):
    text: str


class ErrorResponse(BaseModel):
    error: str
    details: str = None


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/deidentify", response_model=DeidentifyResponse)
async def deidentify(request: DeidentifyRequest):
    """De-identify medical information using Skyflow"""
    try:
        medical_text = request.text
        
        if not medical_text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Call Skyflow API
        response = requests.post(
            SKYFLOW_URL,
            headers={
                "Authorization": f"Bearer {SKYFLOW_TOKEN}"
            },
            json={
                "text": medical_text,
                "vault_id": VAULT_ID,
                "entity_types": [
                    "name",
                    "phone_number",
                    "account_number",
                    "ssn",
                    "dob",
                    "location_address_street",
                    "healthcare_number"
                ],
                "token_type": {
                    "default": "vault_token"
                }
            },
        )
        
        if response.status_code == 200:
            skyflow_response = response.json()
            # Extract only the de-identified text from the response
            deidentified_text = skyflow_response.get('text', '')
            return DeidentifyResponse(text=deidentified_text)
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Skyflow API error: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

