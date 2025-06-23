#!/usr/bin/env python3
"""
🎬 CineScopeAnalyzer Enhanced Edition - System Test
============================================================
Comprehensive system test for backend and frontend integration
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
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
        except Exception as e:
            self.log(f"Backend health test failed: {e}", "ERROR")
            self.results['backend_tests']['health'] = False

        # Test API documentation
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("API documentation accessible", "SUCCESS")
                self.results['backend_tests']['docs'] = True
            else:
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

    def test_movie_suggestions(self):
        """Test movie suggestions endpoint"""
        self.log("Testing movie suggestions...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/movies/suggestions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    self.log(f"Movie suggestions returned {len(data)} results", "SUCCESS")
                    self.results['backend_tests']['suggestions'] = True
                else:
                    self.log("Movie suggestions returned no results", "ERROR")
                    self.results['backend_tests']['suggestions'] = False
            else:
                self.log(f"Movie suggestions failed: {response.status_code}", "ERROR")
                self.results['backend_tests']['suggestions'] = False
                
        except Exception as e:
            self.log(f"Movie suggestions test failed: {e}", "ERROR")
            self.results['backend_tests']['suggestions'] = False

    def test_movie_details(self):
        """Test movie details endpoint"""
        self.log("Testing movie details...")
        
        try:
            # First get a movie ID from search
            search_response = requests.get(
                f"{self.backend_url}/api/movies/search",
                params={"q": TEST_MOVIE, "limit": 1},
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data and len(search_data) > 0:
                    movie_id = search_data[0].get('id')
                    if movie_id:
                        # Test details endpoint
                        details_response = requests.get(
                            f"{self.backend_url}/api/movies/{movie_id}",
                            timeout=10
                        )
                        
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            self.log("Movie details endpoint working", "SUCCESS")
                            self.results['backend_tests']['details'] = True
                        else:
                            self.log(f"Movie details failed: {details_response.status_code}", "ERROR")
                            self.results['backend_tests']['details'] = False
                    else:
                        self.log("No movie ID found in search results", "ERROR")
                        self.results['backend_tests']['details'] = False
                else:
                    self.log("No search results for details test", "ERROR")
                    self.results['backend_tests']['details'] = False
            else:
                self.log("Search failed for details test", "ERROR")
                self.results['backend_tests']['details'] = False
                
        except Exception as e:
            self.log(f"Movie details test failed: {e}", "ERROR")
            self.results['backend_tests']['details'] = False

    def test_frontend_accessibility(self):
        """Test frontend server accessibility"""
        self.log("Testing Frontend Accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log("Frontend is accessible", "SUCCESS")
                self.results['frontend_tests']['accessibility'] = True
            else:
                self.log(f"Frontend not accessible: {response.status_code}", "ERROR")
                self.results['frontend_tests']['accessibility'] = False
        except Exception as e:
            self.log(f"Frontend accessibility test failed: {e}", "ERROR")
            self.results['frontend_tests']['accessibility'] = False

    def test_integration(self):
        """Test backend-frontend integration"""
        self.log("Testing Backend-Frontend Integration...")
        
        backend_healthy = self.results['backend_tests'].get('health', False)
        frontend_accessible = self.results['frontend_tests'].get('accessibility', False)
        
        if backend_healthy and frontend_accessible:
            self.log("Both backend and frontend are running", "SUCCESS")
            self.results['integration_tests']['both_running'] = True
        else:
            self.log("Backend or frontend not properly running", "ERROR")
            self.results['integration_tests']['both_running'] = False

    def calculate_overall_status(self):
        """Calculate overall system status"""
        all_tests = {}
        all_tests.update(self.results['backend_tests'])
        all_tests.update(self.results['frontend_tests'])
        all_tests.update(self.results['integration_tests'])
        
        total_tests = len(all_tests)
        passed_tests = sum(1 for result in all_tests.values() if result)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate >= 90:
            status = "EXCELLENT"
        elif success_rate >= 75:
            status = "GOOD"
        elif success_rate >= 50:
            status = "FAIR"
        else:
            status = "POOR"
            
        self.results['overall_status'] = status
        self.results['success_rate'] = success_rate
        self.results['passed_tests'] = passed_tests
        self.results['total_tests'] = total_tests

    def run_all_tests(self):
        """Run comprehensive system tests"""
        print("🎬 CineScopeAnalyzer Enhanced Edition - System Test")
        print("=" * 60)
        self.log("🚀 Starting CineScopeAnalyzer System Tests...")
        self.log(f"Backend URL: {self.backend_url}")
        self.log(f"Frontend URL: {self.frontend_url}")
        self.log(f"Test Movie: {TEST_MOVIE}")
        
        # Run all tests
        self.test_backend_health()
        self.test_movie_search()
        self.test_movie_suggestions()
        self.test_movie_details()
        self.test_frontend_accessibility()
        self.test_integration()
        
        # Calculate overall status
        self.calculate_overall_status()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()

    def print_summary(self):
        """Print test summary"""
        self.log("")
        print("=" * 60)
        self.log("CINESCOPE ANALYZER - SYSTEM TEST REPORT")
        self.log("=" * 60)
        self.log("")
        
        status_icons = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡", 
            "FAIR": "⚠️",
            "POOR": "🔴"
        }
        
        icon = status_icons.get(self.results['overall_status'], "❓")
        self.log(f"{icon} OVERALL STATUS: {self.results['overall_status']}")
        self.log(f"📊 Success Rate: {self.results['success_rate']:.1f}% ({self.results['passed_tests']}/{self.results['total_tests']})")
        self.log("")
        
        self.log("📋 DETAILED RESULTS:")
        self.log("")
        
        # Backend tests
        self.log("🔧 Backend Tests:")
        for test, result in self.results['backend_tests'].items():
            icon = "✅" if result else "❌"
            self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        # Frontend tests
        self.log("")
        self.log("🎨 Frontend Tests:")
        for test, result in self.results['frontend_tests'].items():
            icon = "✅" if result else "❌"
            self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        # Integration tests
        self.log("")
        self.log("🔗 Integration Tests:")
        for test, result in self.results['integration_tests'].items():
            icon = "✅" if result else "❌"
            self.log(f"  {icon} {test.replace('_', ' ').title()}")
        
        self.log("")
        self.log(f"📅 Test completed at: {self.results['timestamp']}")
        self.log("=" * 60)

    def save_results(self):
        """Save test results to JSON file"""
        filename = "test_results_fixed.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed results saved to: {filename}")

def main():
    """Main test execution"""
    tester = SystemTester()
    tester.run_all_tests()
    
    # Exit with appropriate code
    if tester.results['overall_status'] in ['EXCELLENT', 'GOOD']:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
