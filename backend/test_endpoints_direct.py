#!/usr/bin/env python3
"""
Start server and test endpoints directly
"""
import asyncio
import aiohttp
import time
import subprocess
import sys
import os

async def test_endpoints():
    """Test the API endpoints directly"""
    base_url = "http://localhost:8000/api/movies"
    
    endpoints_to_test = [
        "/health",
        "/popular", 
        "/recent",
        "/top-rated",
        "/suggestions"
    ]
    
    print("🔍 Testing API endpoints...")
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                print(f"Testing {url}...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    status = response.status
                    if status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint}: {status} - {len(data) if isinstance(data, list) else 'Object'}")
                    else:
                        text = await response.text()
                        print(f"❌ {endpoint}: {status} - {text[:100]}...")
                        
            except Exception as e:
                print(f"❌ {endpoint}: Connection failed - {e}")
                
def start_server():
    """Start the FastAPI server in the background"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different ways to start the server
    start_commands = [
        ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        ["python", "startup.py"],
        ["python", "start_server.py"]
    ]
    
    for cmd in start_commands:
        try:
            print(f"🚀 Trying to start server with: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd, 
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give server time to start
            time.sleep(5)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ Server started successfully with PID {process.pid}")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Server failed to start: {stderr.decode()}")
                
        except Exception as e:
            print(f"❌ Failed to start with {cmd}: {e}")
            
    return None

async def main():
    """Main test function"""
    print("🎬 CineScope Backend Endpoint Tester")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    
    if not server_process:
        print("❌ Could not start server - trying direct test without server")
        return
        
    try:
        # Wait a bit more for server to fully initialize
        time.sleep(10)
        
        # Test endpoints
        await test_endpoints()
        
    finally:
        # Clean up server
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    asyncio.run(main())
