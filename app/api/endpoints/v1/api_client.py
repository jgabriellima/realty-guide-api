from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.api.endpoints.mock_data import mock_client_profiles, mock_client_preferences
from app.schemas.tools import ClientProfileLookupResponse, ClientProfileLookupRequest, \
    SaveClientPreferencesResponse, SaveClientPreferencesRequest, GetCustomizedRecommendationsResponse, \
    GetCustomizedRecommendationsRequest

client_router = APIRouter()


@client_router.post("/lookup", response_model=ClientProfileLookupResponse)
def client_profile_lookup(request: ClientProfileLookupRequest):
    if request.client_id in mock_client_profiles:
        return ClientProfileLookupResponse(client_id=request.client_id, profile=mock_client_profiles[request.client_id])
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@client_router.post("/save_preferences", response_model=SaveClientPreferencesResponse)
def save_client_preferences(request: SaveClientPreferencesRequest):
    client_id = request.client_id
    preferences = request.preferences
    if client_id in mock_client_profiles:
        mock_client_profiles[client_id]['preferences'] = preferences
        mock_client_preferences[client_id] = preferences
        return SaveClientPreferencesResponse(status="Preferences saved successfully")
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@client_router.post("/get_recommendations", response_model=GetCustomizedRecommendationsResponse)
def get_customized_recommendations(request: GetCustomizedRecommendationsRequest):
    recommendations = ["Great school nearby", "Low traffic area"]
    return GetCustomizedRecommendationsResponse(recommendations=recommendations)


@client_router.post("/save_metadata", response_model=SaveClientPreferencesResponse)
def save_client_metadata(client_id: int, preference_key: str, preference_value: Any):
    if client_id in mock_client_profiles:
        if client_id not in mock_client_preferences:
            mock_client_preferences[client_id] = {}
        mock_client_preferences[client_id][preference_key] = preference_value
        return SaveClientPreferencesResponse(status="Client metadata saved successfully")
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@client_router.get("/get_preferences/{client_id}", response_model=Dict[str, Any])
def get_client_preferences(client_id: int):
    if client_id in mock_client_preferences:
        return mock_client_preferences[client_id]
    else:
        raise HTTPException(status_code=404, detail="Client preferences not found")
