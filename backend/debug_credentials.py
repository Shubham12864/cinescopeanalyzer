#!/usr/bin/env python3
"""
Debug Reddit credentials
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging Reddit Credentials...")
print(f"REDDIT_CLIENT_ID: '{os.getenv('REDDIT_CLIENT_ID')}'")
print(f"REDDIT_CLIENT_SECRET: '{os.getenv('REDDIT_CLIENT_SECRET')}'")
print(f"REDDIT_USER_AGENT: '{os.getenv('REDDIT_USER_AGENT')}'")

# Check if credentials are valid
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')

print(f"\nValidation:")
print(f"client_id exists: {bool(client_id)}")
print(f"client_secret exists: {bool(client_secret)}")
print(f"client_id != placeholder: {client_id != 'your_reddit_client_id_here'}")

available = bool(client_id and client_secret and client_id != 'your_reddit_client_id_here')
print(f"Reddit available: {available}")
