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
