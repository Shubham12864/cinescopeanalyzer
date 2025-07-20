"""
Image proxy endpoint to resolve CORS issues with external images
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
import httpx
import asyncio
import os
from pathlib import Path
from typing import Optional

router = APIRouter(prefix="/api/images", tags=["images"])

@router.get("/proxy")
@router.get("/image-proxy")  # Add compatibility route for frontend
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

@router.get("/cached/{filename}")
async def get_cached_image(filename: str):
    """Serve cached images"""
    try:
        # Define the cache directory
        cache_dir = Path("./cache/images")
        
        # Check different subdirectories
        possible_paths = [
            cache_dir / "posters" / filename,
            cache_dir / "backdrops" / filename,
            cache_dir / "thumbnails" / filename,
            cache_dir / filename
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    headers={
                        "Cache-Control": "public, max-age=86400",  # 24 hours
                        "Access-Control-Allow-Origin": "*"
                    }
                )
        
        raise HTTPException(status_code=404, detail="Cached image not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving cached image: {str(e)}")
