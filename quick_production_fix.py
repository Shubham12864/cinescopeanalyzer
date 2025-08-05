#!/usr/bin/env python3
"""
Quick fix for production deployment issues
"""

import os
import sys
import logging

def fix_image_url_validation():
    """Fix image URL validation to handle fallback cases properly"""
    
    # Read the current image routes file
    images_file = "/workspaces/cinescopeanalyzer/backend/app/api/routes/images.py"
    
    if not os.path.exists(images_file):
        print("❌ Images route file not found")
        return False
    
    with open(images_file, 'r') as f:
        content = f.read()
    
    # Check if the fix is already applied
    if "# Production fix for fallback URL handling" in content:
        print("✅ Image URL fallback fix already applied")
        return True
    
    # Add fix for fallback URL handling
    fix_code = '''
    # Production fix for fallback URL handling
    if url == "fallback" or url.lower() in ["fallback", "n/a", "null", "none"]:
        raise error_handler.handle_validation_error(
            "Invalid image URL: fallback or placeholder value not allowed", "url", url
        )
    '''
    
    # Insert fix after URL validation
    insert_point = 'if len(url) > 2000:'
    if insert_point in content:
        content = content.replace(
            insert_point,
            fix_code + "\n    " + insert_point
        )
        
        with open(images_file, 'w') as f:
            f.write(content)
        
        print("✅ Applied image URL fallback fix")
        return True
    else:
        print("⚠️ Could not apply image URL fix - insertion point not found")
        return False

def create_production_env():
    """Create production environment file for Railway"""
    
    env_content = """# Production Environment Variables for Railway
TMDB_API_KEY=9f362b6618db6e8a53976a51c2da62a4
TMDB_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZjM2MmI2NjE4ZGI2ZThhNTM5NzZhNTFjMmRhNjJhNCIsIm5iZiI6MTc1MDE2OTg2Ni4wODA5OTk5LCJzdWIiOiI2ODUxNzkwYTNhODk3M2NjMmM2YWVhOTciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.q74ulySmlmbxKBPFda37bXbuFd3ZAMMRReoc_lWLCLg
OMDB_API_KEY=4977b044
FANART_API_KEY=fb2b79b4e05ed6d3452f751ddcf38bda
ENVIRONMENT=production
DEBUG=false
PORT=8000
"""
    
    with open(".env.production", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env.production file")
    return True

def main():
    print("🔧 QUICK PRODUCTION FIX")
    print("=" * 40)
    
    fixes = [
        ("Image URL Validation Fix", fix_image_url_validation),
        ("Production Environment", create_production_env)
    ]
    
    success_count = 0
    
    for name, fix_func in fixes:
        print(f"\n🔍 Applying: {name}")
        try:
            if fix_func():
                print(f"✅ {name}: SUCCESS")
                success_count += 1
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
    
    print(f"\n📊 Applied {success_count}/{len(fixes)} fixes")
    
    if success_count == len(fixes):
        print("🎉 ALL FIXES APPLIED!")
        print("🚀 Ready to redeploy to Railway")
        return True
    else:
        print("⚠️ Some fixes failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
