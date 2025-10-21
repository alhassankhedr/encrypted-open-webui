"""
Lorica proxy router
Provides proxy endpoints for Lorica backend communication to avoid CORS issues
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/lorica", tags=["lorica"])

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working"""
    return {"message": "Lorica proxy router is working"}

@router.get("/discover")
async def proxy_discover(backend_url: str, request: Request):
    """
    Proxy the /discover endpoint from a Lorica backend
    """
    try:
        # Ensure the backend_url starts with https://
        if not backend_url.startswith(('http://', 'https://')):
            backend_url = f"https://{backend_url}"
        
        discover_url = f"{backend_url}/discover"
        logger.info(f"Proxying discover request to: {discover_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(discover_url)
            logger.info(f"Received response: {response.status_code}, content-type: {response.headers.get('content-type')}, content-length: {len(response.content)}")
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("content-type", "application/octet-stream"),
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except Exception as e:
        logger.error(f"Error proxying discover request to {backend_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Lorica backend: {str(e)}")

@router.get("/token/{backend_url:path}")
async def proxy_token(backend_url: str, request: Request):
    """
    Proxy the /token endpoint from a Lorica backend
    """
    try:
        # Ensure the backend_url starts with https://
        if not backend_url.startswith(('http://', 'https://')):
            backend_url = f"https://{backend_url}"
        
        token_url = f"{backend_url}/token"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(token_url)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("content-type", "text/plain"),
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except Exception as e:
        logger.error(f"Error proxying token request to {backend_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Lorica backend: {str(e)}")

@router.get("/trustee/{trustee_url:path}")
async def proxy_trustee(trustee_url: str, request: Request):
    """
    Proxy requests to the Trustee service
    """
    try:
        # Ensure the trustee_url starts with https://
        if not trustee_url.startswith(('http://', 'https://')):
            trustee_url = f"https://{trustee_url}"
        
        # Get the full path from the request
        path = request.url.path.replace(f"/api/v1/lorica/trustee/{trustee_url}", "")
        trustee_request_url = f"{trustee_url}{path}"
        
        # Forward query parameters
        if request.url.query:
            trustee_request_url += f"?{request.url.query}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                trustee_request_url,
                headers={
                    "Authorization": request.headers.get("authorization", ""),
                    "Content-Type": request.headers.get("content-type", "application/json")
                }
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("content-type", "application/json"),
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except Exception as e:
        logger.error(f"Error proxying trustee request to {trustee_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Trustee service: {str(e)}")

@router.options("/{path:path}")
async def handle_options(path: str):
    """
    Handle CORS preflight requests
    """
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )
