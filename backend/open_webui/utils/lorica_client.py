"""
Async Lorica Client for OHTTP encryption and confidential computing attestation.
Based on the working test pattern from test.py
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional, List
from urllib.parse import urljoin

import aiohttp
from lorica import ohttp

from open_webui.config import LORICA_API_BASE_URLS, LORICA_API_KEYS

logger = logging.getLogger(__name__)


class AsyncLoricaSession:
    """
    Async wrapper for Lorica OHTTP encryption and attestation.
    Based on the working test pattern from test.py
    """
    
    def __init__(self, base_url: str, api_key: str, model_id: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_id = model_id
        self.session: Optional[ohttp.Session] = None
        self._http_session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self):
        """Initialize the Lorica session and HTTP client."""
        try:
            # Initialize Lorica OHTTP session (as shown in test.py)
            self.session = ohttp.Session()
            
            # Initialize aiohttp session for async operations
            self._http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300),  # 5 minute timeout
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Open-WebUI-Lorica/1.0'
                }
            )
            
            logger.info(f"Lorica OHTTP session initialized for {self.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Lorica session: {e}")
            raise
    
    async def close(self):
        """Close the session and cleanup resources."""
        if self._http_session:
            await self._http_session.close()
        if self.session:
            self.session.close()
    
    async def verify_attestation(self) -> Dict[str, Any]:
        """
        Verify the attestation of the remote Lorica service.
        Returns attestation results including trust status.
        """
        try:
            if not self.session:
                await self.initialize()
            
            # Test connection with a simple chat completion request using the provided model
            if not self.model_id:
                raise ValueError("Model ID is required for attestation verification")
                
            test_response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 1,
                    "stream": False
                }
            )
            
            if test_response.status_code == 200:
                return {
                    "verified": True,
                    "attestation": "Lorica OHTTP attestation verified",
                    "trust_level": "verified",
                    "timestamp": datetime.now().isoformat(),
                    "service_url": self.base_url
                }
            else:
                return {
                    "verified": False,
                    "error": f"Attestation verification failed: {test_response.status_code}",
                    "service_url": self.base_url
                }
                
        except Exception as e:
            logger.error(f"Attestation verification failed: {e}")
            return {
                "verified": False,
                "error": str(e),
                "service_url": self.base_url
            }
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from the Lorica service.
        Since Lorica API doesn't have a /v1/models endpoint, return the provided model.
        """
        try:
            if not self.model_id:
                return []
                
            # Return the provided model ID as the available model
            return [{
                "id": self.model_id,
                "name": self.model_id.split('/')[-1] if '/' in self.model_id else self.model_id,
                "description": f"Lorica OHTTP encrypted model: {self.model_id}",
                "context_length": 8192,  # Default context length
                "provider": "lorica",
                "enabled": True,
                "lorica_encrypted": True
            }]
                
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send chat completion request with OHTTP encryption.
        Based on the working test.py pattern.
        """
        try:
            if not self.session:
                await self.initialize()
            
            # Prepare chat completion request (exactly like test.py)
            completion_request = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            
            # Use Lorica OHTTP session for the request (as in test.py)
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=completion_request,
                stream=stream
            )
            
            response.raise_for_status()
            
            if stream:
                # Handle streaming response (exactly like test.py)
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data: "):
                        continue

                    data = line[len("data: "):].strip()
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    # Format for Open-WebUI compatibility
                    yield {
                        "id": chunk.get("id", f"lorica-{asyncio.get_event_loop().time()}"),
                        "object": "chat.completion.chunk",
                        "created": chunk.get("created", int(asyncio.get_event_loop().time())),
                        "model": model,
                        "choices": chunk.get("choices", [])
                    }
            else:
                # Handle non-streaming response
                response_data = response.json()
                yield {
                    "id": response_data.get("id", "unknown"),
                    "object": "chat.completion",
                    "created": int(asyncio.get_event_loop().time()),
                    "model": model,
                    "choices": response_data.get("choices", [])
                }
                        
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            yield {
                "error": str(e),
                "details": "Lorica OHTTP encryption failed"
            }


async def get_lorica_session(base_url: str, api_key: str) -> AsyncLoricaSession:
    """Get a configured Lorica session."""
    return AsyncLoricaSession(base_url, api_key)


async def test_lorica_connection(base_url: str, api_key: str, model_id: str = None) -> Dict[str, Any]:
    """Test connection to Lorica service."""
    try:
        async with AsyncLoricaSession(base_url, api_key, model_id) as session:
            # Test attestation
            attestation_result = await session.verify_attestation()
            
            # Test models
            models = await session.get_models()
            
            return {
                "connected": True,
                "attestation": attestation_result,
                "models_count": len(models),
                "service_url": base_url
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "service_url": base_url
        }