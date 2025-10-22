"""
Lorica API router for OHTTP encryption and confidential computing attestation.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from open_webui.config import (
    ENABLE_LORICA_API,
    LORICA_API_BASE_URLS,
    LORICA_API_KEYS,
    LORICA_API_CONFIGS
)
from open_webui.utils.lorica_client import (
    AsyncLoricaSession,
    get_lorica_session,
    test_lorica_connection
)
from open_webui.models.users import UserModel
from open_webui.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lorica", tags=["lorica"])


class LoricaConfigResponse(BaseModel):
    enabled: bool
    base_urls: List[str]
    api_keys: List[str]
    configs: Dict[str, Any]


class LoricaAttestationResponse(BaseModel):
    verified: bool
    trust_level: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
    service_url: str


class LoricaModel(BaseModel):
    id: str
    name: str
    description: str
    context_length: int
    provider: str
    enabled: bool
    lorica_encrypted: bool


class LoricaModelsResponse(BaseModel):
    models: List[LoricaModel]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = True


@router.get("/config")
async def get_lorica_config(user: UserModel = Depends(get_current_user)) -> LoricaConfigResponse:
    """Get Lorica configuration."""
    # Allow reading config even when disabled, so frontend can show current state
    
    return LoricaConfigResponse(
        enabled=ENABLE_LORICA_API.value,
        base_urls=LORICA_API_BASE_URLS.value,
        api_keys=["*" * 8 + key[-4:] if len(key) > 8 else "*" * len(key) for key in LORICA_API_KEYS.value],
        configs=LORICA_API_CONFIGS.value
    )


@router.post("/config/update")
async def update_lorica_config(
    config_data: dict,
    user: UserModel = Depends(get_current_user)
):
    """Update Lorica configuration."""
    # Allow updates even when disabled, as user might be trying to enable it
    
    try:
        # Update configuration values
        if "ENABLE_LORICA_API" in config_data:
            ENABLE_LORICA_API.value = config_data["ENABLE_LORICA_API"]
            ENABLE_LORICA_API.save()
        
        if "LORICA_API_BASE_URLS" in config_data:
            LORICA_API_BASE_URLS.value = config_data["LORICA_API_BASE_URLS"]
            LORICA_API_BASE_URLS.save()
        
        if "LORICA_API_KEYS" in config_data:
            LORICA_API_KEYS.value = config_data["LORICA_API_KEYS"]
            LORICA_API_KEYS.save()
        
        if "LORICA_API_CONFIGS" in config_data:
            LORICA_API_CONFIGS.value = config_data["LORICA_API_CONFIGS"]
            LORICA_API_CONFIGS.save()
        
        return {"message": "Lorica configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating Lorica configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {e}")


@router.post("/verify/{url_idx}")
async def verify_lorica_attestation(
    url_idx: int,
    user: UserModel = Depends(get_current_user)
) -> LoricaAttestationResponse:
    """Verify Lorica service attestation."""
    if not ENABLE_LORICA_API:
        raise HTTPException(status_code=403, detail="Lorica API is disabled")
    
    if url_idx >= len(LORICA_API_BASE_URLS.value) or url_idx < 0:
        raise HTTPException(status_code=400, detail="Invalid URL index")
    
    base_url = LORICA_API_BASE_URLS.value[url_idx]
    api_key = LORICA_API_KEYS.value[url_idx] if url_idx < len(LORICA_API_KEYS.value) else ""
    
    if not base_url or not api_key:
        raise HTTPException(status_code=400, detail="Invalid Lorica configuration")
    
    try:
        # Test connection and get attestation
        connection_result = await test_lorica_connection(base_url, api_key)
        
        if connection_result["connected"]:
            attestation = connection_result.get("attestation", {})
            return LoricaAttestationResponse(
                verified=attestation.get("verified", False),
                trust_level=attestation.get("trust_level"),
                timestamp=attestation.get("timestamp"),
                error=attestation.get("error"),
                service_url=base_url
            )
        else:
            return LoricaAttestationResponse(
                verified=False,
                error=connection_result.get("error", "Connection failed"),
                service_url=base_url
            )
            
    except Exception as e:
        logger.error(f"Attestation verification failed: {e}")
        return LoricaAttestationResponse(
            verified=False,
            error=str(e),
            service_url=base_url
        )


@router.get("/models/{url_idx}")
async def get_lorica_models(
    url_idx: int,
    user: UserModel = Depends(get_current_user)
) -> LoricaModelsResponse:
    """Get available Lorica models."""
    if not ENABLE_LORICA_API:
        raise HTTPException(status_code=403, detail="Lorica API is disabled")
    
    if url_idx >= len(LORICA_API_BASE_URLS.value) or url_idx < 0:
        raise HTTPException(status_code=400, detail="Invalid URL index")
    
    base_url = LORICA_API_BASE_URLS.value[url_idx]
    api_key = LORICA_API_KEYS.value[url_idx] if url_idx < len(LORICA_API_KEYS.value) else ""
    
    if not base_url or not api_key:
        raise HTTPException(status_code=400, detail="Invalid Lorica configuration")
    
    try:
        async with AsyncLoricaSession(base_url, api_key) as session:
            models = await session.get_models()
            
            formatted_models = []
            for model in models:
                formatted_models.append(LoricaModel(
                    id=model["id"],
                    name=model["name"],
                    description=model["description"],
                    context_length=model["context_length"],
                    provider=model["provider"],
                    enabled=model["enabled"],
                    lorica_encrypted=model["lorica_encrypted"]
                ))
            
            return LoricaModelsResponse(models=formatted_models)
            
    except Exception as e:
        logger.error(f"Failed to get Lorica models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.post("/chat/completions/{url_idx}")
async def lorica_chat_completion(
    url_idx: int,
    request: ChatCompletionRequest,
    user: UserModel = Depends(get_current_user)
):
    """Send chat completion request with OHTTP encryption."""
    if not ENABLE_LORICA_API:
        raise HTTPException(status_code=403, detail="Lorica API is disabled")
    
    if url_idx >= len(LORICA_API_BASE_URLS.value) or url_idx < 0:
        raise HTTPException(status_code=400, detail="Invalid URL index")
    
    base_url = LORICA_API_BASE_URLS.value[url_idx]
    api_key = LORICA_API_KEYS.value[url_idx] if url_idx < len(LORICA_API_KEYS.value) else ""
    
    if not base_url or not api_key:
        raise HTTPException(status_code=400, detail="Invalid Lorica configuration")
    
    try:
        async def generate_response():
            async with AsyncLoricaSession(base_url, api_key) as session:
                async for chunk in session.chat_completion(
                    messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=request.stream
                ):
                    if request.stream:
                        yield f"data: {json.dumps(chunk)}\n\n"
                    else:
                        yield json.dumps(chunk)
        
        if request.stream:
            return StreamingResponse(
                generate_response(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # For non-streaming, collect all chunks
            response_data = None
            async for chunk in generate_response():
                response_data = json.loads(chunk)
            return response_data
            
    except Exception as e:
        logger.error(f"Lorica chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.get("/health")
async def lorica_health():
    """Health check for Lorica integration."""
    return {
        "status": "healthy",
        "lorica_enabled": ENABLE_LORICA_API.value,
        "endpoints_configured": len(LORICA_API_BASE_URLS.value) if LORICA_API_BASE_URLS.value else 0
    }
