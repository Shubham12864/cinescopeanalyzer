#!/usr/bin/env python3
"""
PIL Import Test - Verify Pillow installation
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    print("✅ PIL import successful!")
    print(f"PIL version: {Image.__version__}")
    
    # Test creating a simple image
    img = Image.new('RGB', (100, 100), color='red')
    print("✅ Image creation successful!")
    
    # Test if we can import the image processing service
    try:
        from app.services.image_processing_service import image_processing_service
        print("✅ Image processing service import successful!")
    except Exception as e:
        print(f"❌ Image processing service import failed: {e}")
        
    # Test main app import
    try:
        import app.main
        print("✅ Main app import successful!")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        
except ImportError as e:
    print(f"❌ PIL import failed: {e}")
    print("Run: pip install Pillow")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
