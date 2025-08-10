#!/usr/bin/env python3

try:
    from app.services.image_cache_service import ImageCacheService
    print("✅ ImageCacheService imported successfully")
    
    service = ImageCacheService()
    print("✅ ImageCacheService instantiated successfully")
    
    # Check if get_or_cache_image method exists and is callable
    if hasattr(service, 'get_or_cache_image') and callable(getattr(service, 'get_or_cache_image')):
        print("✅ get_or_cache_image method exists and is callable")
    else:
        print("❌ get_or_cache_image method missing or not callable")
    
    # List all available methods
    methods = [m for m in dir(service) if not m.startswith('_') and callable(getattr(service, m))]
    print(f"Available methods: {methods}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
