#!/usr/bin/env python3
"""
Minimal mock backend for Open WebUI to test Lorica integration
This provides the basic API endpoints that the frontend needs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import uvicorn

app = FastAPI(title="Open WebUI Mock Backend", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data models
class User(BaseModel):
    id: str = "mock-user-id"
    name: str = "Test User"
    email: str = "test@example.com"
    role: str = "admin"

class Model(BaseModel):
    id: str
    name: str
    provider: str = "openai"
    api_base: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None

# Mock data
mock_models = [
    Model(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", provider="openai"),
    Model(id="gpt-4", name="GPT-4", provider="openai"),
    Model(id="llama2", name="Llama 2", provider="ollama"),
]

@app.get("/")
async def root():
    return {"message": "Open WebUI Mock Backend", "status": "running"}

@app.get("/api/v1/users")
async def get_users():
    return [User()]

@app.get("/api/v1/models")
async def get_models():
    return mock_models

@app.get("/api/v1/configs")
async def get_configs():
    return {
        "version": "0.6.34",
        "features": {
            "lorica_encryption": True
        }
    }

@app.post("/api/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Mock chat completions endpoint"""
    
    if request.stream:
        # Return streaming response
        async def generate_stream():
            # Simulate streaming response
            response_data = {
                "id": "chatcmpl-mock-123",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": "This is a mock response from the backend. "},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            
            await asyncio.sleep(0.1)
            
            response_data = {
                "id": "chatcmpl-mock-123",
                "object": "chat.completion.chunk", 
                "created": 1234567890,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": "The Lorica encryption integration is working!"},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            
            await asyncio.sleep(0.1)
            
            # Final chunk
            response_data = {
                "id": "chatcmpl-mock-123",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    else:
        # Return non-streaming response
        return {
            "id": "chatcmpl-mock-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a mock response from the backend. The Lorica encryption integration is working!"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

@app.post("/api/v1/chat/completions/stream")
async def chat_completions_stream(request: ChatCompletionRequest):
    """Alternative streaming endpoint"""
    return await chat_completions(request)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "lorica_integration": "enabled"}

@app.get("/api/v1/lorica/status")
async def lorica_status():
    """Mock Lorica status endpoint"""
    return {
        "enabled": True,
        "backend_detected": False,
        "attestation_status": "not_configured",
        "trustee_url": "https://trustee.lorica.ai"
    }

if __name__ == "__main__":
    print("Starting Open WebUI Mock Backend...")
    print("Frontend should be available at: http://localhost:5173")
    print("Backend API available at: http://localhost:8080")
    print("API docs available at: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
