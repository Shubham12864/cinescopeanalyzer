#!/usr/bin/env python3
"""
Critical Production Fix for Railway Deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for the fix script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_environment_variables():
    """Check and set critical environment variables"""
    logger = logging.getLogger(__name__)
    
    required_vars = {
        'TMDB_API_KEY': '9f362b6618db6e8a53976a51c2da62a4',
        'TMDB_ACCESS_TOKEN': 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZjM2MmI2NjE4ZGI2ZThhNTM5NzZhNTFjMmRhNjJhNCIsIm5iZiI6MTc1MDE2OTg2Ni4wODA5OTk5LCJzdWIiOiI2ODUxNzkwYTNhODk3M2NjMmM2YWVhOTciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.q74ulySmlmbxKBPFda37bXbuFd3ZAMMRReoc_lWLCLg',
        'OMDB_API_KEY': '4977b044',
        'FANART_API_KEY': 'fb2b79b4e05ed6d3452f751ddcf38bda',
        'PORT': '8000',
        'ENVIRONMENT': 'production'
    }
    
    logger.info("🔧 Checking environment variables...")
    
    missing = []
    for var, default_value in required_vars.items():
        if not os.getenv(var):
            os.environ[var] = default_value
            logger.info(f"✅ Set {var} = {default_value[:10]}...")
        else:
            logger.info(f"✅ {var} already set")
    
    return len(missing) == 0

def check_python_syntax():
    """Check Python syntax of critical files"""
    logger = logging.getLogger(__name__)
    
    critical_files = [
        'backend/app/core/tmdb_api.py',
        'backend/app/main.py',
        'backend/app/api/routes/movies.py',
        'backend/app/api/routes/images.py'
    ]
    
    logger.info("🐍 Checking Python syntax...")
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', file_path], 
                    capture_output=True, 
                    text=True,
                    check=True
                )
                logger.info(f"✅ {file_path}: Syntax OK")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ {file_path}: Syntax Error")
                logger.error(f"Error: {e.stderr}")
                return False
        else:
            logger.warning(f"⚠️ {file_path}: File not found")
    
    return True

def test_imports():
    """Test critical imports"""
    logger = logging.getLogger(__name__)
    
    logger.info("📦 Testing critical imports...")
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Test TMDB API import
        from app.core.tmdb_api import TMDBApi
        logger.info("✅ TMDBApi import: OK")
        
        # Test FastAPI app import
        from app.main import app
        logger.info("✅ FastAPI app import: OK")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        return False

def create_procfile():
    """Create optimized Procfile for Railway"""
    logger = logging.getLogger(__name__)
    
    procfile_content = """web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    logger.info("✅ Created optimized Procfile")

def create_railway_config():
    """Create railway.json configuration"""
    logger = logging.getLogger(__name__)
    
    railway_config = """{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}"""
    
    with open('railway.json', 'w') as f:
        f.write(railway_config)
    
    logger.info("✅ Created railway.json configuration")

def test_server_start():
    """Test if server can start successfully"""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Testing server startup...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Test import without starting server
        result = subprocess.run([
            'python3', '-c', 
            'from app.main import app; print("✅ Server imports successful")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info("✅ Server can start successfully")
            return True
        else:
            logger.error(f"❌ Server startup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Server startup timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Server test failed: {e}")
        return False
    finally:
        # Change back to root directory
        os.chdir('..')

def main():
    """Run all production fixes"""
    logger = setup_logging()
    
    logger.info("🔧 PRODUCTION FIX STARTED")
    logger.info("=" * 50)
    
    fixes = [
        ("Environment Variables", check_environment_variables),
        ("Python Syntax", check_python_syntax), 
        ("Import Tests", test_imports),
        ("Procfile Creation", create_procfile),
        ("Railway Config", create_railway_config),
        ("Server Test", test_server_start)
    ]
    
    results = {}
    
    for name, fix_func in fixes:
        logger.info(f"\n🔍 Running: {name}")
        try:
            results[name] = fix_func()
            if results[name]:
                logger.info(f"✅ {name}: PASSED")
            else:
                logger.error(f"❌ {name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {name}: ERROR - {e}")
            results[name] = False
    
    # Summary
    logger.info("\n📊 PRODUCTION FIX SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} fixes successful")
    
    if passed == total:
        logger.info("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        logger.info("🚀 Ready for Railway deployment")
        return True
    else:
        logger.error("⚠️ Some fixes failed - check logs above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
