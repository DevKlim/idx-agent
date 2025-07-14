
from fastapi import APIRouter, HTTPException, Body, UploadFile, File
import httpx
import json

from models.schemas import Incident, CorrelationRequest, CorrelationResponse
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["Incidents", "EIDO"])

EIDO_AGENT_URL = settings.eido_agent_url

# Store "claimed" incidents in memory for simplicity
claimed_incidents = set()

@router.get("/incidents", response_model=list[Incident])
async def get_incidents():
    """
    Get all incidents from the EIDO Agent.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EIDO_AGENT_URL}/api/v1/incidents")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from EIDO Agent: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to EIDO Agent: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching incidents: {e}")


@router.post("/incidents/{incident_id}/claim")
async def claim_incident(incident_id: str):
    """
    Claim an incident for the IDX Agent.
    """
    claimed_incidents.add(incident_id)
    return {"message": f"Incident {incident_id} claimed."}

@router.get("/incidents/claimed", response_model=list[str])
async def get_claimed_incidents():
    """
    Get all claimed incidents.
    """
    return list(claimed_incidents)

@router.post("/eido/upload", response_model=dict)
async def upload_eido(file: UploadFile = File(...)):
    """
    Upload an EIDO JSON file to the EIDO Agent.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .json files are accepted.")

    content = await file.read()
    try:
        eido_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in uploaded file.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{EIDO_AGENT_URL}/api/v1/ingest", json=eido_data)
            response.raise_for_status()
            # It's possible the EIDO agent returns a success status but non-JSON body
            return response.json()
    except httpx.HTTPStatusError as e:
        # Re-raise the error from the downstream service with more context
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from EIDO Agent: {e.response.text}")
    except httpx.RequestError as e:
        # Network-level error
        raise HTTPException(status_code=502, detail=f"Could not connect to EIDO Agent: {e}")
    except json.JSONDecodeError:
        # The EIDO agent returned a success status but the response body was not valid JSON
        raise HTTPException(status_code=502, detail="Received an invalid response from the EIDO Agent.")
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.post("/incidents/correlate", response_model=CorrelationResponse)
async def correlate_incident(request: CorrelationRequest):
    """
    Correlate a new incident with existing incidents.
    """
    # This is a placeholder for the actual correlation logic.
    # In a real implementation, this would involve some form of AI/ML model.
    return {"status": "new", "correlation_id": None}
