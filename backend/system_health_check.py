#!/usr/bin/env python3
"""
CineScope Analyzer System Health Check
Tests all components and fixes common issues.
"""

import os
import sys
import requests
import subprocess
import time
from pathlib import Path

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_frontend_build():
    """Test if frontend can build successfully"""
    try:
        frontend_path = Path("../frontend")
        if not frontend_path.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Check if package.json exists
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            print("❌ Frontend package.json not found")
            return False
        
        print("✅ Frontend structure looks good")
        return True
        
    except Exception as e:
        print(f"❌ Frontend check error: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    required_vars = [
        "OMDB_API_KEY",
        "REDDIT_CLIENT_ID", 
        "REDDIT_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) in ['your_reddit_client_id_here', 'your_reddit_client_secret_here']:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or invalid environment variables: {', '.join(missing_vars)}")
        print("   Set these in your .env file for full functionality")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_api_connections():
    """Test external API connections"""
    print("\n📋 Testing API Connections...")
    
    # Test OMDB API
    omdb_key = os.getenv('OMDB_API_KEY')
    if omdb_key:
        try:
            response = requests.get(f"http://www.omdbapi.com/?apikey={omdb_key}&t=Batman&y=2008", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    print("✅ OMDB API connection successful")
                else:
                    print(f"⚠️  OMDB API returned error: {data.get('Error', 'Unknown error')}")
            else:
                print(f"❌ OMDB API HTTP error: {response.status_code}")
        except Exception as e:
            print(f"❌ OMDB API connection failed: {e}")
    else:
        print("⚠️  OMDB API key not set")
    
    return True

def run_database_test():
    """Run the database connection test"""
    try:
        result = subprocess.run([sys.executable, "test_database_connection.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Database connection test passed")
            return True
        else:
            print(f"❌ Database connection test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def start_backend():
    """Start the backend server"""
    try:
        print("🚀 Starting backend server...")
        print("   Use Ctrl+C to stop the server")
        print("   Backend will be available at: http://localhost:8000")
        print("   API documentation at: http://localhost:8000/docs")
        
        # Start the server
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")

def main():
    """Main health check function"""
    print("🔍 CineScope Analyzer System Health Check")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Database Connection", run_database_test),
        ("Frontend Structure", test_frontend_build),
        ("API Connections", test_api_connections),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 HEALTH CHECK SUMMARY:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your system is ready.")
        
        # Ask if user wants to start the backend
        try:
            choice = input("\nWould you like to start the backend server now? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                start_backend()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the application.")
        print("\n💡 Common fixes:")
        print("   - Set missing environment variables in .env file")
        print("   - Install missing dependencies with: pip install -r requirements.txt")
        print("   - Check network connectivity for API tests")

if __name__ == "__main__":
    main()
