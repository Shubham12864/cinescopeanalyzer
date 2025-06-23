import sys
import os
import subprocess
import importlib.util

def check_python_version():
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version should be 3.8+")
        return False

def check_dependencies():
    required = [
        'fastapi', 'uvicorn', 'pydantic', 'python-dotenv', 
        'httpx', 'aiofiles', 'python-multipart'
    ]
    
    missing = []
    for dep in required:
        try:
            __import__(dep)
            print(f"✅ {dep} is installed")
        except ImportError:
            print(f"❌ {dep} is missing")
            missing.append(dep)
    
    return len(missing) == 0, missing

def check_app_structure():
    # Change to backend directory first
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(backend_dir)
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/api/__init__.py',
        'app/api/routes/__init__.py',
        'app/api/routes/movies.py',
        'app/services/__init__.py',
        'app/services/movie_service.py',
        'app/core/__init__.py',
        'app/models/__init__.py',
        'app/models/movie.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def test_import():
    try:
        # Add backend to path
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, backend_dir)
        
        from app.main import app
        print("✅ Main app imports successfully")
        return True, None
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False, str(e)

def test_movie_service():
    try:
        from app.services.movie_service import MovieService
        service = MovieService()
        print("✅ MovieService imports and initializes successfully")
        return True, None
    except Exception as e:
        print(f"❌ MovieService failed: {e}")
        return False, str(e)

def main():
    print("🔍 CineScope Analyzer Backend Diagnostic")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("App Structure", check_app_structure),
        ("Import Test", test_import),
        ("Movie Service Test", test_movie_service)
    ]
    
    results = []
    errors = []
    
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        try:
            result = check_func()
            if isinstance(result, tuple):
                success, error = result
                results.append((name, success))
                if error:
                    errors.append(f"{name}: {error}")
            else:
                results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results.append((name, False))
            errors.append(f"{name}: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY:")
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    if errors:
        print("\n🚨 ERRORS FOUND:")
        for error in errors:
            print(f"   • {error}")
    
    if all_passed:
        print("\n🎉 All checks passed! Backend should work.")
        print("Try starting with: python -m uvicorn app.main:app --reload")
    else:
        print("\n🚨 Some checks failed. See errors above.")
        
        # Provide fix suggestions
        print("\n💡 SUGGESTED FIXES:")
        if any("missing" in str(error).lower() for error in errors):
            print("   • Install missing dependencies: pip install -r requirements.txt")
        if any("import" in str(error).lower() for error in errors):
            print("   • Check file paths and __init__.py files")
        if any("file" in str(error).lower() for error in errors):
            print("   • Create missing files or fix file structure")

if __name__ == "__main__":
    main()
