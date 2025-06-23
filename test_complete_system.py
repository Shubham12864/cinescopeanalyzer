#!/usr/bin/env python3
"""
Complete System Test for CineScopeAnalyzer Enhanced Edition
Tests all components: API, Frontend, Enhanced Analysis, and Integration
"""

import asyncio
import json
import time
import requests
from datetime import datetime
import sys
import os

# Test Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_MOVIE = "Inception"

class SystemTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.frontend_url = FRONTEND_URL
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'backend_tests': {},
            'frontend_tests': {},
            'integration_tests': {},
            'enhanced_features': {},
            'overall_status': 'UNKNOWN'
        }

    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "ℹ️"
        print(f"[{timestamp}] {icon} {message}")

    def test_backend_health(self):
        """Test backend server health and basic endpoints"""
        self.log("Testing Backend Health...")
        
        try:
            # Test basic health
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("Backend health check passed", "SUCCESS")
                self.results['backend_tests']['health'] = True
            else:
                self.log(f"Backend health check failed: {response.status_code}", "ERROR")
                self.results['backend_tests']['health'] = False
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Backend server not accessible: {e}", "ERROR")
            self.results['backend_tests']['health'] = False
            return False
            
        # Test API documentation
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("API documentation accessible", "SUCCESS")
                self.results['backend_tests']['docs'] = True            else:
                self.log("API documentation not accessible", "ERROR")
                self.results['backend_tests']['docs'] = False
        except Exception as e:
            self.log(f"API docs test failed: {e}", "ERROR")
            self.results['backend_tests']['docs'] = False
            
        return True

    def test_movie_search(self):
        """Test basic movie search functionality"""
        self.log(f"Testing movie search for '{TEST_MOVIE}'...")
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/movies/search",
                params={"q": TEST_MOVIE, "limit": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    self.log(f"Movie search returned {len(data)} results", "SUCCESS")
                    self.results['backend_tests']['movie_search'] = True
                    self.log(f"First result: {data[0].get('title', 'Unknown')}")
                else:
                    self.log("Movie search returned no results", "ERROR")
                    self.results['backend_tests']['movie_search'] = False
            else:
                self.log(f"Movie search failed: {response.status_code}", "ERROR")
                self.results['backend_tests']['movie_search'] = False
                
        except Exception as e:
            self.log(f"Movie search test failed: {e}", "ERROR")
            self.results['backend_tests']['movie_search'] = False

    def test_enhanced_features(self):
        """Test enhanced analysis features"""
        self.log("Testing Enhanced Features...")
        
        # Test enhanced info endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/v1/enhanced/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log("Enhanced info endpoint working", "SUCCESS")
                self.log(f"Enhanced Edition: {data.get('enhanced_edition', 'Unknown')}")
                self.log(f"Version: {data.get('version', 'Unknown')}")
                self.log(f"Status: {data.get('status', 'Unknown')}")
                self.results['enhanced_features']['info_endpoint'] = True
            else:
                self.log("Enhanced info endpoint failed", "ERROR")
                self.results['enhanced_features']['info_endpoint'] = False
        except Exception as e:
            self.log(f"Enhanced info test failed: {e}", "ERROR")
            self.results['enhanced_features']['info_endpoint'] = False

        # Test comprehensive analysis endpoint
        try:
            analysis_payload = {
                "movie_title": TEST_MOVIE,
                "include_reddit": True,
                "include_scraping": True,
                "reddit_limit": 50,
                "scraping_platforms": ["imdb", "rotten_tomatoes"]
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/movies/analyze/comprehensive",
                json=analysis_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis_id = data.get('analysis_id')
                self.log(f"Comprehensive analysis started: {analysis_id}", "SUCCESS")
                self.results['enhanced_features']['comprehensive_analysis'] = True
                
                # Test status endpoint
                if analysis_id:
                    time.sleep(2)  # Wait a bit
                    status_response = requests.get(
                        f"{self.backend_url}/api/v1/movies/analyze/{analysis_id}/status",
                        timeout=5
                    )
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        self.log(f"Analysis status: {status_data.get('status', 'Unknown')}", "SUCCESS")
                        self.results['enhanced_features']['status_tracking'] = True
                    else:
                        self.log("Analysis status endpoint failed", "ERROR")
                        self.results['enhanced_features']['status_tracking'] = False
                        
            else:
                self.log(f"Comprehensive analysis failed: {response.status_code}", "ERROR")
                self.results['enhanced_features']['comprehensive_analysis'] = False
                
        except Exception as e:
            self.log(f"Comprehensive analysis test failed: {e}", "ERROR")
            self.results['enhanced_features']['comprehensive_analysis'] = False

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        self.log("Testing Frontend Accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log("Frontend is accessible", "SUCCESS")
                self.results['frontend_tests']['accessibility'] = True
            else:
                self.log(f"Frontend not accessible: {response.status_code}", "ERROR")
                self.results['frontend_tests']['accessibility'] = False
        except requests.exceptions.RequestException as e:
            self.log(f"Frontend not running: {e}", "ERROR")
            self.results['frontend_tests']['accessibility'] = False

    def test_integration(self):
        """Test integration between backend and frontend"""
        self.log("Testing Backend-Frontend Integration...")
        
        # This would typically test API calls from frontend to backend
        # For now, we'll test if both are running on expected ports
        backend_running = self.results['backend_tests'].get('health', False)
        frontend_running = self.results['frontend_tests'].get('accessibility', False)
        
        if backend_running and frontend_running:
            self.log("Both backend and frontend are running", "SUCCESS")
            self.results['integration_tests']['both_running'] = True
        else:
            self.log("Integration test failed - services not running", "ERROR")
            self.results['integration_tests']['both_running'] = False

    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("\n" + "="*60)
        self.log("CINESCOPE ANALYZER - SYSTEM TEST REPORT")
        self.log("="*60)
        
        # Calculate overall status
        all_tests = []
        for category in ['backend_tests', 'frontend_tests', 'enhanced_features', 'integration_tests']:
            if category in self.results:
                all_tests.extend(self.results[category].values())
        
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 80:
            self.results['overall_status'] = 'EXCELLENT'
            status_icon = "🚀"
        elif success_rate >= 60:
            self.results['overall_status'] = 'GOOD'
            status_icon = "✅"
        elif success_rate >= 40:
            self.results['overall_status'] = 'FAIR'
            status_icon = "⚠️"
        else:
            self.results['overall_status'] = 'NEEDS_WORK'
            status_icon = "❌"
        
        self.log(f"\n{status_icon} OVERALL STATUS: {self.results['overall_status']}")
        self.log(f"📊 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Detailed results
        self.log("\n📋 DETAILED RESULTS:")
        
        self.log("\n🔧 Backend Tests:")
        for test, result in self.results['backend_tests'].items():
            icon = "✅" if result else "❌"
            self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        if self.results['frontend_tests']:
            self.log("\n🎨 Frontend Tests:")
            for test, result in self.results['frontend_tests'].items():
                icon = "✅" if result else "❌"
                self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        self.log("\n🚀 Enhanced Features:")
        for test, result in self.results['enhanced_features'].items():
            icon = "✅" if result else "❌"
            self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        if self.results['integration_tests']:
            self.log("\n🔗 Integration Tests:")
            for test, result in self.results['integration_tests'].items():
                icon = "✅" if result else "❌"
                self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        # Recommendations
        self.log("\n💡 RECOMMENDATIONS:")
        if not self.results['backend_tests'].get('health', False):
            self.log("  • Start the backend server: cd backend && python -m app.main")
        if not self.results['frontend_tests'].get('accessibility', False):
            self.log("  • Start the frontend server: cd frontend && npm run dev")
        if not self.results['enhanced_features'].get('comprehensive_analysis', False):
            self.log("  • Install enhanced dependencies: pip install praw nltk textblob")
        
        self.log(f"\n📅 Test completed at: {self.results['timestamp']}")
        self.log("="*60)
        
        return self.results

    def run_all_tests(self):
        """Run all system tests"""
        self.log("🚀 Starting CineScopeAnalyzer System Tests...")
        self.log(f"Backend URL: {self.backend_url}")
        self.log(f"Frontend URL: {self.frontend_url}")
        self.log(f"Test Movie: {TEST_MOVIE}")
        
        # Run tests in order
        if self.test_backend_health():
            self.test_movie_search()
            self.test_enhanced_features()
        
        self.test_frontend_accessibility()
        self.test_integration()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test function"""
    print("🎬 CineScopeAnalyzer Enhanced Edition - System Test")
    print("=" * 60)
    
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: test_results.json")
    
    # Exit with appropriate code
    if results['overall_status'] in ['EXCELLENT', 'GOOD']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
