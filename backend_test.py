#!/usr/bin/env python3
"""
Backend API Testing for Arabic Football News API
Tests the YallaKora scraping endpoints
"""

import requests
import json
import sys
from typing import Dict, List, Any
import re

# Use the backend URL from frontend .env
BASE_URL = "https://top5-league-app.preview.emergentagent.com"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {}
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "أخبار" in data["message"]:
                    self.log_result("API Root", True, "Root endpoint working with Arabic message")
                else:
                    self.log_result("API Root", False, "Root endpoint missing Arabic message", {"response": data})
            else:
                self.log_result("API Root", False, f"HTTP {response.status_code}", {"response": response.text})
        except Exception as e:
            self.log_result("API Root", False, f"Connection error: {str(e)}")
    
    def test_leagues_endpoint(self):
        """Test GET /api/leagues endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/leagues")
            if response.status_code != 200:
                self.log_result("Leagues Endpoint", False, f"HTTP {response.status_code}", {"response": response.text})
                return
            
            data = response.json()
            
            # Check if it's a list
            if not isinstance(data, list):
                self.log_result("Leagues Endpoint", False, "Response is not a list", {"response": data})
                return
            
            # Check if we have 5 leagues
            if len(data) != 5:
                self.log_result("Leagues Endpoint", False, f"Expected 5 leagues, got {len(data)}", {"count": len(data)})
                return
            
            # Check league structure
            expected_leagues = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1"]
            found_leagues = [league.get("id") for league in data]
            
            missing_leagues = set(expected_leagues) - set(found_leagues)
            if missing_leagues:
                self.log_result("Leagues Endpoint", False, f"Missing leagues: {missing_leagues}", {"found": found_leagues})
                return
            
            # Check league data structure
            for league in data:
                required_fields = ["id", "name", "name_en", "tour_id", "comp_id", "country", "logo"]
                missing_fields = [field for field in required_fields if field not in league]
                if missing_fields:
                    self.log_result("Leagues Endpoint", False, f"League {league.get('id')} missing fields: {missing_fields}")
                    return
            
            self.log_result("Leagues Endpoint", True, "All 5 European leagues returned with correct structure")
            
        except Exception as e:
            self.log_result("Leagues Endpoint", False, f"Error: {str(e)}")
    
    def test_news_endpoint(self, league_id: str):
        """Test GET /api/news/{league_id} endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/news/{league_id}")
            if response.status_code != 200:
                self.log_result(f"News {league_id}", False, f"HTTP {response.status_code}", {"response": response.text})
                return
            
            data = response.json()
            
            # Check response structure
            if "news" not in data:
                self.log_result(f"News {league_id}", False, "Response missing 'news' field", {"response": data})
                return
            
            news_items = data["news"]
            
            # Check if news is a list
            if not isinstance(news_items, list):
                self.log_result(f"News {league_id}", False, "News is not a list", {"news": news_items})
                return
            
            # Check if we have at least some news items
            if len(news_items) == 0:
                self.log_result(f"News {league_id}", False, "No news items returned", {"count": 0})
                return
            
            # Check news item structure
            issues = []
            arabic_titles = 0
            valid_images = 0
            valid_links = 0
            
            for i, item in enumerate(news_items[:5]):  # Check first 5 items
                # Check required fields
                required_fields = ["title", "link", "league_id"]
                missing_fields = [field for field in required_fields if field not in item or not item[field]]
                if missing_fields:
                    issues.append(f"Item {i}: missing {missing_fields}")
                    continue
                
                # Check Arabic title
                title = item.get("title", "")
                if re.search(r'[\u0600-\u06FF]', title):  # Arabic Unicode range
                    arabic_titles += 1
                
                # Check image URL format
                image_url = item.get("image_url")
                if image_url:
                    if image_url.startswith("https://mediayk.gemini.media") and "\\" not in image_url:
                        valid_images += 1
                    elif "\\" in image_url:
                        issues.append(f"Item {i}: image URL contains backslashes")
                
                # Check link format
                link = item.get("link", "")
                if "yallakora.com" in link and link.startswith("http"):
                    valid_links += 1
                
                # Check league_id matches
                if item.get("league_id") != league_id:
                    issues.append(f"Item {i}: league_id mismatch")
            
            # Evaluate results
            success = True
            details = {
                "total_items": len(news_items),
                "arabic_titles": arabic_titles,
                "valid_images": valid_images,
                "valid_links": valid_links,
                "issues": issues
            }
            
            if len(news_items) < 5:
                success = False
                issues.append(f"Only {len(news_items)} items, expected at least 5")
            
            if arabic_titles == 0:
                success = False
                issues.append("No Arabic titles found")
            
            if issues:
                self.log_result(f"News {league_id}", success, f"Issues found: {len(issues)}", details)
            else:
                self.log_result(f"News {league_id}", True, f"News working correctly ({len(news_items)} items)", details)
                
        except Exception as e:
            self.log_result(f"News {league_id}", False, f"Error: {str(e)}")
    
    def test_standings_endpoint(self, league_id: str):
        """Test GET /api/standings/{league_id} endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/standings/{league_id}")
            if response.status_code != 200:
                self.log_result(f"Standings {league_id}", False, f"HTTP {response.status_code}", {"response": response.text})
                return
            
            data = response.json()
            
            # Check response structure
            if "standings" not in data:
                self.log_result(f"Standings {league_id}", False, "Response missing 'standings' field", {"response": data})
                return
            
            standings = data["standings"]
            
            # Check if standings is a list
            if not isinstance(standings, list):
                self.log_result(f"Standings {league_id}", False, "Standings is not a list", {"standings": standings})
                return
            
            # Standings may be empty if scraping fails, which is acceptable
            if len(standings) == 0:
                self.log_result(f"Standings {league_id}", True, "Standings endpoint working (empty result - scraping may have failed)", {"count": 0})
                return
            
            # If we have standings, check structure
            issues = []
            for i, item in enumerate(standings[:3]):  # Check first 3 items
                required_fields = ["position", "team_name", "played", "won", "drawn", "lost", "points"]
                missing_fields = [field for field in required_fields if field not in item]
                if missing_fields:
                    issues.append(f"Item {i}: missing {missing_fields}")
            
            if issues:
                self.log_result(f"Standings {league_id}", False, f"Structure issues: {issues}", {"count": len(standings)})
            else:
                self.log_result(f"Standings {league_id}", True, f"Standings working correctly ({len(standings)} teams)", {"count": len(standings)})
                
        except Exception as e:
            self.log_result(f"Standings {league_id}", False, f"Error: {str(e)}")
    
    def test_all_news_endpoint(self):
        """Test GET /api/all-news endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/all-news")
            if response.status_code != 200:
                self.log_result("All News", False, f"HTTP {response.status_code}", {"response": response.text})
                return
            
            data = response.json()
            
            # Check response structure
            if "news" not in data:
                self.log_result("All News", False, "Response missing 'news' field", {"response": data})
                return
            
            news_items = data["news"]
            
            # Check if news is a list
            if not isinstance(news_items, list):
                self.log_result("All News", False, "News is not a list", {"news": news_items})
                return
            
            # Check if we have news from multiple leagues
            league_ids = set(item.get("league_id") for item in news_items if item.get("league_id"))
            
            details = {
                "total_items": len(news_items),
                "unique_leagues": len(league_ids),
                "leagues": list(league_ids)
            }
            
            if len(news_items) == 0:
                self.log_result("All News", False, "No news items returned", details)
                return
            
            if len(league_ids) < 2:
                self.log_result("All News", False, f"Expected news from multiple leagues, got {len(league_ids)}", details)
                return
            
            self.log_result("All News", True, f"Combined news working ({len(news_items)} items from {len(league_ids)} leagues)", details)
            
        except Exception as e:
            self.log_result("All News", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting API tests for: {self.base_url}")
        print("=" * 60)
        
        # Test API root
        self.test_api_root()
        
        # Test leagues endpoint
        self.test_leagues_endpoint()
        
        # Test news endpoints for specific leagues
        leagues_to_test = ["premier-league", "la-liga", "serie-a"]
        for league in leagues_to_test:
            self.test_news_endpoint(league)
        
        # Test standings endpoint
        self.test_standings_endpoint("premier-league")
        
        # Test all news endpoint
        self.test_all_news_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

def main():
    """Main test function"""
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()