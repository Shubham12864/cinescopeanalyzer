"""
Image proxy endpoint to resolve CORS issues with external images
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from typing import Optional

router = APIRouter(prefix="/api/images", tags=["images"])

@router.get("/proxy")
async def proxy_image(url: str = Query(..., description="Image URL to proxy")):
    """Proxy external images to avoid CORS issues"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                return StreamingResponse(
                    iter([response.content]),
                    media_type=response.headers.get("content-type", "image/jpeg"),
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="Image not found")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error proxying image: {str(e)}")
