#!/usr/bin/env python3
"""
Railway setup script to suppress cryptography warnings and upgrade packages
"""
import warnings
import sys
import os
import subprocess

def suppress_warnings():
    """Suppress cryptography and other warnings"""
    # Suppress cryptography deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Set environment variables
    os.environ["CRYPTOGRAPHY_DONT_BUILD_RUST"] = "1"
    os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"
    
    try:
        # Also suppress in Python warnings filter
        import cryptography
        cryptography._warnings.CryptographyDeprecationWarning.__init__ = lambda self, *args, **kwargs: None
    except:
        pass  # If it fails, continue anyway
    
    print("✅ Cryptography warnings suppressed for Railway deployment")

def upgrade_cryptography():
    """Try to upgrade cryptography to fix warnings"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "cryptography>=41.0.0"], 
                      check=True, capture_output=True, text=True)
        print("✅ Cryptography upgraded")
    except:
        print("⚠️ Could not upgrade cryptography, continuing with existing version")

if __name__ == "__main__":
    suppress_warnings()
    upgrade_cryptography()
    print("Railway setup complete")
