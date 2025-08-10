#!/usr/bin/env python3
"""
Manual testing guide for CineScope Backend
"""

print("🎬 CineScope Backend Manual Testing Guide")
print("=" * 60)

print("\n📋 STEP 1: Start the Backend Server")
print("-" * 30)
print("Choose ONE of these commands:")
print("   Option A: python start_test_server.py")
print("   Option B: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
print("   Option C: python startup.py")

print("\n📋 STEP 2: Wait for Server Initialization")
print("-" * 30)
print("Look for these messages:")
print("   ✅ 'OMDB Service initialized'")
print("   ✅ 'Application startup complete'")
print("   ✅ 'Uvicorn running on http://0.0.0.0:8000'")

print("\n📋 STEP 3: Test Endpoints in Browser")
print("-" * 30)
print("Open these URLs in your browser:")
print("   🏥 Health Check:    http://localhost:8000/api/movies/health")
print("   🌟 Popular Movies:  http://localhost:8000/api/movies/popular")
print("   📅 Recent Movies:   http://localhost:8000/api/movies/recent")
print("   ⭐ Top Rated:       http://localhost:8000/api/movies/top-rated")
print("   💡 Suggestions:     http://localhost:8000/api/movies/suggestions")

print("\n📋 STEP 4: Alternative - Use Test Client")
print("-" * 30)
print("In a NEW terminal window, run:")
print("   python test_client.py")

print("\n📋 STEP 5: Expected Results")
print("-" * 30)
print("✅ /health should return: {\"status\": \"healthy\", \"service\": \"movies\", ...}")
print("✅ /popular should return: Array of movie objects with id, title, year, poster")
print("✅ Other endpoints should return similar movie arrays")

print("\n📋 STEP 6: Troubleshooting")
print("-" * 30)
print("If you see 405 Method Not Allowed:")
print("   • Check server startup logs for import errors")
print("   • Verify routes are registered properly")
print("   • Make sure you're using the correct HTTP method (GET)")

print("\nIf you see 500 Internal Server Error:")
print("   • Check if OMDB service is working (should show mock data if not)")
print("   • Look at server console for detailed error messages")
print("   • Verify all dependencies are installed")

print("\n🎯 SUCCESS CRITERIA")
print("-" * 30)
print("✅ Server starts without import errors")
print("✅ All 5 new endpoints return 200 status")
print("✅ Endpoints return movie data (real or mock)")
print("✅ No 405 Method Not Allowed errors")

print("\n" + "=" * 60)
print("🚀 Ready to test! Start with STEP 1 above.")
