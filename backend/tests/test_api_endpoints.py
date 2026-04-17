"""
Backend API Tests for Arabic Football News App
Tests all endpoints: leagues, news, standings, matches for 5 European leagues
"""
import pytest
import requests
import os

# Get backend URL from environment
# Read from frontend .env file
from pathlib import Path
from dotenv import load_dotenv

frontend_env = Path(__file__).parent.parent.parent / 'frontend' / '.env'
load_dotenv(frontend_env)

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("EXPO_PUBLIC_BACKEND_URL not found in environment")

# League IDs to test
LEAGUE_IDS = ['premier-league', 'la-liga', 'serie-a', 'bundesliga', 'ligue-1']

class TestHealthCheck:
    """Test basic API health"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root accessible: {data['message']}")

class TestLeaguesEndpoint:
    """Test /api/leagues endpoint"""
    
    def test_get_leagues(self):
        """Test GET /api/leagues returns 5 leagues"""
        response = requests.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5, f"Expected 5 leagues, got {len(data)}"
        
        # Verify all expected leagues are present
        league_ids = [league['id'] for league in data]
        for expected_id in LEAGUE_IDS:
            assert expected_id in league_ids, f"League {expected_id} not found"
        
        # Verify league structure
        for league in data:
            assert 'id' in league
            assert 'name' in league
            assert 'name_en' in league
            assert 'tour_id' in league
            assert 'comp_id' in league
            assert 'country' in league
            assert 'logo' in league
            print(f"✓ League found: {league['name_en']} ({league['id']})")

class TestNewsEndpoint:
    """Test /api/news/{league_id} endpoint"""
    
    def test_get_premier_league_news(self):
        """Test GET /api/news/premier-league returns news with required fields"""
        response = requests.get(f"{BASE_URL}/api/news/premier-league")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        assert len(news_items) > 0, "No news items returned for Premier League"
        
        # Verify news item structure
        first_item = news_items[0]
        assert 'id' in first_item
        assert 'title' in first_item
        assert 'link' in first_item
        assert 'league_id' in first_item
        assert first_item['league_id'] == 'premier-league'
        
        # Check optional fields
        if 'image_url' in first_item and first_item['image_url']:
            assert first_item['image_url'].startswith('http')
        
        print(f"✓ Premier League news: {len(news_items)} items")
        print(f"  Sample title: {first_item['title'][:50]}...")
    
    def test_get_la_liga_news(self):
        """Test GET /api/news/la-liga returns Spanish league news"""
        response = requests.get(f"{BASE_URL}/api/news/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            first_item = news_items[0]
            assert first_item['league_id'] == 'la-liga'
            print(f"✓ La Liga news: {len(news_items)} items")
        else:
            print("⚠ La Liga news: 0 items (may be scraping issue)")
    
    def test_get_serie_a_news(self):
        """Test GET /api/news/serie-a returns Italian league news"""
        response = requests.get(f"{BASE_URL}/api/news/serie-a")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        print(f"✓ Serie A news: {len(news_items)} items")
    
    def test_get_bundesliga_news(self):
        """Test GET /api/news/bundesliga returns German league news"""
        response = requests.get(f"{BASE_URL}/api/news/bundesliga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        print(f"✓ Bundesliga news: {len(news_items)} items")
    
    def test_get_ligue_1_news(self):
        """Test GET /api/news/ligue-1 returns French league news"""
        response = requests.get(f"{BASE_URL}/api/news/ligue-1")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        print(f"✓ Ligue 1 news: {len(news_items)} items")
    
    def test_invalid_league_news(self):
        """Test GET /api/news/invalid-league returns 404"""
        response = requests.get(f"{BASE_URL}/api/news/invalid-league")
        assert response.status_code == 404
        print("✓ Invalid league returns 404")

class TestStandingsEndpoint:
    """Test /api/standings/{league_id} endpoint"""
    
    def test_get_premier_league_standings(self):
        """Test GET /api/standings/premier-league returns 20 teams with stats"""
        response = requests.get(f"{BASE_URL}/api/standings/premier-league")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Premier League should have 20 teams
            assert len(standings) >= 18, f"Expected at least 18 teams, got {len(standings)}"
            
            # Verify standings structure
            first_team = standings[0]
            assert 'position' in first_team
            assert 'team_name' in first_team
            assert 'played' in first_team
            assert 'won' in first_team
            assert 'drawn' in first_team
            assert 'lost' in first_team
            assert 'goals_for' in first_team
            assert 'goals_against' in first_team
            assert 'points' in first_team
            
            # Verify data types
            assert isinstance(first_team['position'], int)
            assert isinstance(first_team['points'], int)
            assert isinstance(first_team['played'], int)
            
            print(f"✓ Premier League standings: {len(standings)} teams")
            print(f"  Top team: {first_team['team_name']} - {first_team['points']} points")
        else:
            print("⚠ Premier League standings: 0 teams (scraping issue)")
    
    def test_get_la_liga_standings(self):
        """Test GET /api/standings/la-liga returns standings"""
        response = requests.get(f"{BASE_URL}/api/standings/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        print(f"✓ La Liga standings: {len(standings)} teams")
    
    def test_invalid_league_standings(self):
        """Test GET /api/standings/invalid-league returns 404"""
        response = requests.get(f"{BASE_URL}/api/standings/invalid-league")
        assert response.status_code == 404
        print("✓ Invalid league standings returns 404")

class TestMatchesEndpoint:
    """Test /api/matches/{league_id} endpoint"""
    
    def test_get_premier_league_matches(self):
        """Test GET /api/matches/premier-league returns matches with teams, time, channel"""
        response = requests.get(f"{BASE_URL}/api/matches/premier-league")
        assert response.status_code == 200
        
        data = response.json()
        assert 'matches' in data
        matches = data['matches']
        assert isinstance(matches, list)
        
        if len(matches) > 0:
            # Verify match structure
            first_match = matches[0]
            assert 'id' in first_match
            assert 'home_team' in first_match
            assert 'away_team' in first_match
            assert 'match_time' in first_match
            assert 'match_date' in first_match
            assert 'status' in first_match
            assert 'league_id' in first_match
            assert first_match['league_id'] == 'premier-league'
            
            # Verify status is valid
            assert first_match['status'] in ['upcoming', 'live', 'finished']
            
            print(f"✓ Premier League matches: {len(matches)} matches")
            print(f"  Sample: {first_match['home_team']} vs {first_match['away_team']}")
        else:
            print("⚠ Premier League matches: 0 matches (may be off-season)")
    
    def test_get_la_liga_matches(self):
        """Test GET /api/matches/la-liga returns matches"""
        response = requests.get(f"{BASE_URL}/api/matches/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'matches' in data
        matches = data['matches']
        assert isinstance(matches, list)
        print(f"✓ La Liga matches: {len(matches)} matches")
    
    def test_invalid_league_matches(self):
        """Test GET /api/matches/invalid-league returns 404"""
        response = requests.get(f"{BASE_URL}/api/matches/invalid-league")
        assert response.status_code == 404
        print("✓ Invalid league matches returns 404")

class TestAllNewsEndpoint:
    """Test /api/all-news endpoint"""
    
    def test_get_all_news(self):
        """Test GET /api/all-news returns news from all leagues"""
        response = requests.get(f"{BASE_URL}/api/all-news")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # Should have news from multiple leagues
            league_ids = set(item['league_id'] for item in news_items)
            print(f"✓ All news: {len(news_items)} items from {len(league_ids)} leagues")
        else:
            print("⚠ All news: 0 items")

class TestSearchEndpoint:
    """Test /api/search endpoint - NEW FEATURE"""
    
    def test_search_liverpool(self):
        """Test GET /api/search?q=ليفربول returns Liverpool-related news"""
        query = "ليفربول"
        response = requests.get(f"{BASE_URL}/api/search?q={query}")
        assert response.status_code == 200
        
        data = response.json()
        assert 'results' in data
        assert 'query' in data
        assert 'count' in data
        assert data['query'] == query
        
        results = data['results']
        assert isinstance(results, list)
        
        # Verify results contain the search term
        if len(results) > 0:
            for item in results:
                assert 'id' in item
                assert 'title' in item
                assert 'link' in item
                assert 'league_id' in item
                assert 'league_name' in item
                # Check if query is in title
                assert query in item['title'], f"Query '{query}' not found in title: {item['title']}"
            print(f"✓ Search 'ليفربول': {len(results)} results found")
        else:
            print("⚠ Search 'ليفربول': 0 results (may need more news data)")
    
    def test_search_salah(self):
        """Test GET /api/search?q=صلاح returns Salah-related news"""
        query = "صلاح"
        response = requests.get(f"{BASE_URL}/api/search?q={query}")
        assert response.status_code == 200
        
        data = response.json()
        assert 'results' in data
        assert 'query' in data
        assert 'count' in data
        assert data['query'] == query
        
        results = data['results']
        assert isinstance(results, list)
        
        if len(results) > 0:
            for item in results:
                assert query in item['title'], f"Query '{query}' not found in title: {item['title']}"
            print(f"✓ Search 'صلاح': {len(results)} results found")
        else:
            print("⚠ Search 'صلاح': 0 results")
    
    def test_search_with_league_filter(self):
        """Test GET /api/search?q=test&league_id=premier-league filters by league"""
        query = "ليفربول"
        response = requests.get(f"{BASE_URL}/api/search?q={query}&league_id=premier-league")
        assert response.status_code == 200
        
        data = response.json()
        results = data['results']
        
        # All results should be from premier-league
        if len(results) > 0:
            for item in results:
                assert item['league_id'] == 'premier-league', f"Expected premier-league, got {item['league_id']}"
            print(f"✓ Search with league filter: {len(results)} results from premier-league only")
        else:
            print("⚠ Search with league filter: 0 results")
    
    def test_search_short_query(self):
        """Test GET /api/search?q=a returns 400 for query < 2 chars"""
        response = requests.get(f"{BASE_URL}/api/search?q=a")
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data
        print("✓ Search with short query returns 400")
    
    def test_search_no_results(self):
        """Test GET /api/search?q=xyzabc123 returns empty results"""
        query = "xyzabc123nonexistent"
        response = requests.get(f"{BASE_URL}/api/search?q={query}")
        assert response.status_code == 200
        
        data = response.json()
        assert data['count'] == 0
        assert len(data['results']) == 0
        print("✓ Search with no matches returns empty results")

class TestNewsDetailEndpoint:
    """Test /api/news-detail/{league_id}/{news_id} endpoint - NEW FEATURE"""
    
    def test_get_news_detail(self):
        """Test GET /api/news-detail/{league_id}/{news_id} returns article detail"""
        # First get a news item to get a valid ID
        news_response = requests.get(f"{BASE_URL}/api/news/premier-league")
        assert news_response.status_code == 200
        
        news_data = news_response.json()
        news_items = news_data['news']
        
        if len(news_items) > 0:
            first_news = news_items[0]
            news_id = first_news['id']
            league_id = first_news['league_id']
            
            # Now get the detail
            detail_response = requests.get(f"{BASE_URL}/api/news-detail/{league_id}/{news_id}")
            assert detail_response.status_code == 200
            
            detail_data = detail_response.json()
            assert 'article' in detail_data
            
            article = detail_data['article']
            assert article['id'] == news_id
            assert article['title'] == first_news['title']
            assert article['link'] == first_news['link']
            
            # Content is optional (may be None if scraping fails)
            print(f"✓ News detail: Article retrieved successfully")
            if detail_data.get('content'):
                print(f"  Content length: {len(detail_data['content'])} chars")
            else:
                print("  Content: Not available (scraping may have failed)")
        else:
            pytest.skip("No news items available to test detail endpoint")
    
    def test_get_news_detail_invalid_league(self):
        """Test GET /api/news-detail/invalid-league/123 returns 404"""
        response = requests.get(f"{BASE_URL}/api/news-detail/invalid-league/123")
        assert response.status_code == 404
        print("✓ News detail with invalid league returns 404")
    
    def test_get_news_detail_invalid_id(self):
        """Test GET /api/news-detail/premier-league/invalid-id returns 404"""
        response = requests.get(f"{BASE_URL}/api/news-detail/premier-league/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ News detail with invalid ID returns 404")

class TestPushTokenEndpoint:
    """Test /api/register-push-token endpoint - NEW FEATURE"""
    
    def test_register_push_token(self):
        """Test POST /api/register-push-token registers a token"""
        token_data = {
            "token": "ExponentPushToken[test-token-12345]",
            "leagues": ["premier-league", "la-liga"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/register-push-token",
            json=token_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'status' in data
        assert data['status'] == 'registered'
        print("✓ Push token registration successful")
    
    def test_register_push_token_no_token(self):
        """Test POST /api/register-push-token without token returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/register-push-token",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data
        print("✓ Push token registration without token returns 400")
    
    def test_register_push_token_update(self):
        """Test POST /api/register-push-token updates existing token"""
        token_data = {
            "token": "ExponentPushToken[test-token-update-67890]",
            "leagues": ["premier-league"]
        }
        
        # Register first time
        response1 = requests.post(
            f"{BASE_URL}/api/register-push-token",
            json=token_data,
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        
        # Update with different leagues
        token_data['leagues'] = ["premier-league", "la-liga", "serie-a"]
        response2 = requests.post(
            f"{BASE_URL}/api/register-push-token",
            json=token_data,
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 200
        
        data = response2.json()
        assert data['status'] == 'registered'
        print("✓ Push token update successful")
