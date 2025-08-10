#!/usr/bin/env python3
"""
Simple connection string validation test
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import socket

load_dotenv()

def test_connection_string():
    """Test and validate the connection string"""
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment")
        return False
    
    print(f"🔧 Connection String: {mongodb_uri[:80]}...")
    
    # Parse the connection string
    try:
        parsed = urlparse(mongodb_uri)
        print(f"📋 Scheme: {parsed.scheme}")
        print(f"📋 Hostname: {parsed.hostname}")
        print(f"📋 Port: {parsed.port}")
        print(f"📋 Username: {parsed.username}")
        print(f"📋 Database: {parsed.path.lstrip('/')}")
        
        # Test DNS resolution
        print(f"\n🔍 Testing DNS resolution for: {parsed.hostname}")
        try:
            ip = socket.gethostbyname(parsed.hostname)
            print(f"✅ DNS resolved to: {ip}")
        except socket.gaierror as e:
            print(f"❌ DNS resolution failed: {e}")
            print("\n🔧 Possible solutions:")
            print("1. Check if the Azure Cosmos DB account is created and running")
            print("2. Verify the account name in Azure Portal")
            print("3. Check if there are network restrictions or firewall rules")
            print("4. Try accessing the Cosmos DB from Azure Portal to confirm it exists")
            return False
        
        # Test port connectivity
        print(f"\n🔍 Testing port connectivity to: {parsed.hostname}:{parsed.port}")
        try:
            with socket.create_connection((parsed.hostname, parsed.port), timeout=10):
                print(f"✅ Port {parsed.port} is accessible")
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"❌ Port connectivity failed: {e}")
            print("\n🔧 Possible solutions:")
            print("1. Check Azure Cosmos DB firewall settings")
            print("2. Add your IP address to allowed IPs in Azure Portal")
            print("3. Check if 'Allow access from Azure services' is enabled")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection string parsing failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection_string()
    if success:
        print("\n✅ Connection string validation passed")
    else:
        print("\n❌ Connection string validation failed")
        print("\n📋 Next steps:")
        print("1. Go to Azure Portal (portal.azure.com)")
        print("2. Navigate to your Cosmos DB account")
        print("3. Check if the account exists and is running")
        print("4. Go to 'Keys' section and verify the connection string")
        print("5. Check 'Firewall and virtual networks' settings")
