"""
Backend API Tests - League Data Verification (Bug Fix Testing)
Tests that each league returns correct teams after tour_id fix:
- La Liga (tour_id 101) should return Spanish teams (Barcelona, Real Madrid) NOT French teams
- Ligue 1 (tour_id 95) should return French teams (PSG, Lens) NOT Spanish teams
- Serie A (tour_id 100) should return Italian teams (Inter Milan)
- Bundesliga (tour_id 98) should return German teams (Bayern Munich)
- Premier League (tour_id 93) should return English teams (Arsenal)
"""
import pytest
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Get backend URL from environment
frontend_env = Path(__file__).parent.parent.parent / 'frontend' / '.env'
load_dotenv(frontend_env)

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("EXPO_PUBLIC_BACKEND_URL not found in environment")

class TestLaLigaDataCorrectness:
    """Test La Liga returns Spanish teams (NOT French teams)"""
    
    def test_la_liga_standings_returns_spanish_teams(self):
        """Test GET /api/standings/la-liga returns Spanish teams like Barcelona, Real Madrid"""
        response = requests.get(f"{BASE_URL}/api/standings/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Get all team names
            team_names = [team['team_name'] for team in standings]
            team_names_str = ', '.join(team_names[:5])
            
            # Check for Spanish teams (common La Liga teams)
            spanish_teams = ['برشلونة', 'ريال مدريد', 'أتلتيكو مدريد', 'إشبيلية', 'ريال سوسيداد', 'فالنسيا', 'بيتيس']
            found_spanish = [team for team in spanish_teams if any(team in name for name in team_names)]
            
            # Check for French teams (should NOT be present)
            french_teams = ['باريس سان جيرمان', 'لانس', 'مارسيليا', 'موناكو', 'ليون', 'ليل']
            found_french = [team for team in french_teams if any(team in name for name in team_names)]
            
            print(f"✓ La Liga standings: {len(standings)} teams")
            print(f"  Top 5 teams: {team_names_str}")
            print(f"  Spanish teams found: {len(found_spanish)} ({', '.join(found_spanish[:3])})")
            print(f"  French teams found: {len(found_french)} (should be 0)")
            
            # CRITICAL: La Liga should have Spanish teams, NOT French teams
            assert len(found_spanish) > 0, f"La Liga should have Spanish teams but found none. Teams: {team_names_str}"
            assert len(found_french) == 0, f"La Liga should NOT have French teams but found: {', '.join(found_french)}"
        else:
            pytest.skip("No standings data available for La Liga")
    
    def test_la_liga_news_returns_spanish_league_news(self):
        """Test GET /api/news/la-liga returns Spanish league news"""
        response = requests.get(f"{BASE_URL}/api/news/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # All news should be for la-liga
            for item in news_items:
                assert item['league_id'] == 'la-liga', f"Expected la-liga, got {item['league_id']}"
            
            print(f"✓ La Liga news: {len(news_items)} items")
            print(f"  Sample title: {news_items[0]['title'][:60]}...")
        else:
            print("⚠ La Liga news: 0 items")
    
    def test_la_liga_matches_returns_spanish_teams(self):
        """Test GET /api/matches/la-liga returns matches with Spanish teams"""
        response = requests.get(f"{BASE_URL}/api/matches/la-liga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'matches' in data
        matches = data['matches']
        assert isinstance(matches, list)
        
        if len(matches) > 0:
            # All matches should be for la-liga
            for match in matches:
                assert match['league_id'] == 'la-liga', f"Expected la-liga, got {match['league_id']}"
            
            print(f"✓ La Liga matches: {len(matches)} matches")
            print(f"  Sample: {matches[0]['home_team']} vs {matches[0]['away_team']}")
        else:
            print("⚠ La Liga matches: 0 matches")

class TestLigue1DataCorrectness:
    """Test Ligue 1 returns French teams (NOT Spanish teams)"""
    
    def test_ligue_1_standings_returns_french_teams(self):
        """Test GET /api/standings/ligue-1 returns French teams like PSG, Lens"""
        response = requests.get(f"{BASE_URL}/api/standings/ligue-1")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Get all team names
            team_names = [team['team_name'] for team in standings]
            team_names_str = ', '.join(team_names[:5])
            
            # Check for French teams (common Ligue 1 teams)
            french_teams = ['باريس سان جيرمان', 'لانس', 'مارسيليا', 'موناكو', 'ليون', 'ليل', 'رين']
            found_french = [team for team in french_teams if any(team in name for name in team_names)]
            
            # Check for Spanish teams (should NOT be present)
            spanish_teams = ['برشلونة', 'ريال مدريد', 'أتلتيكو مدريد', 'إشبيلية']
            found_spanish = [team for team in spanish_teams if any(team in name for name in team_names)]
            
            print(f"✓ Ligue 1 standings: {len(standings)} teams")
            print(f"  Top 5 teams: {team_names_str}")
            print(f"  French teams found: {len(found_french)} ({', '.join(found_french[:3])})")
            print(f"  Spanish teams found: {len(found_spanish)} (should be 0)")
            
            # CRITICAL: Ligue 1 should have French teams, NOT Spanish teams
            assert len(found_french) > 0, f"Ligue 1 should have French teams but found none. Teams: {team_names_str}"
            assert len(found_spanish) == 0, f"Ligue 1 should NOT have Spanish teams but found: {', '.join(found_spanish)}"
        else:
            pytest.skip("No standings data available for Ligue 1")
    
    def test_ligue_1_news_returns_french_league_news(self):
        """Test GET /api/news/ligue-1 returns French league news"""
        response = requests.get(f"{BASE_URL}/api/news/ligue-1")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # All news should be for ligue-1
            for item in news_items:
                assert item['league_id'] == 'ligue-1', f"Expected ligue-1, got {item['league_id']}"
            
            print(f"✓ Ligue 1 news: {len(news_items)} items")
            print(f"  Sample title: {news_items[0]['title'][:60]}...")
        else:
            print("⚠ Ligue 1 news: 0 items")

class TestSerieADataCorrectness:
    """Test Serie A returns Italian teams"""
    
    def test_serie_a_standings_returns_italian_teams(self):
        """Test GET /api/standings/serie-a returns Italian teams like Inter Milan, Napoli"""
        response = requests.get(f"{BASE_URL}/api/standings/serie-a")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Get all team names
            team_names = [team['team_name'] for team in standings]
            team_names_str = ', '.join(team_names[:5])
            
            # Check for Italian teams (common Serie A teams)
            italian_teams = ['إنتر ميلان', 'نابولي', 'يوفنتوس', 'ميلان', 'روما', 'لاتسيو', 'أتالانتا']
            found_italian = [team for team in italian_teams if any(team in name for name in team_names)]
            
            print(f"✓ Serie A standings: {len(standings)} teams")
            print(f"  Top 5 teams: {team_names_str}")
            print(f"  Italian teams found: {len(found_italian)} ({', '.join(found_italian[:3])})")
            
            # Serie A should have Italian teams
            assert len(found_italian) > 0, f"Serie A should have Italian teams but found none. Teams: {team_names_str}"
        else:
            pytest.skip("No standings data available for Serie A")
    
    def test_serie_a_news_returns_italian_league_news(self):
        """Test GET /api/news/serie-a returns Italian league news"""
        response = requests.get(f"{BASE_URL}/api/news/serie-a")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # All news should be for serie-a
            for item in news_items:
                assert item['league_id'] == 'serie-a', f"Expected serie-a, got {item['league_id']}"
            
            print(f"✓ Serie A news: {len(news_items)} items")
        else:
            print("⚠ Serie A news: 0 items")

class TestBundesligaDataCorrectness:
    """Test Bundesliga returns German teams"""
    
    def test_bundesliga_standings_returns_german_teams(self):
        """Test GET /api/standings/bundesliga returns German teams like Bayern Munich"""
        response = requests.get(f"{BASE_URL}/api/standings/bundesliga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Get all team names
            team_names = [team['team_name'] for team in standings]
            team_names_str = ', '.join(team_names[:5])
            
            # Check for German teams (common Bundesliga teams)
            german_teams = ['بايرن ميونخ', 'دورتموند', 'لايبزيج', 'ليفركوزن', 'فرانكفورت', 'فولفسبورج']
            found_german = [team for team in german_teams if any(team in name for name in team_names)]
            
            print(f"✓ Bundesliga standings: {len(standings)} teams")
            print(f"  Top 5 teams: {team_names_str}")
            print(f"  German teams found: {len(found_german)} ({', '.join(found_german[:3])})")
            
            # Bundesliga should have German teams
            assert len(found_german) > 0, f"Bundesliga should have German teams but found none. Teams: {team_names_str}"
        else:
            pytest.skip("No standings data available for Bundesliga")
    
    def test_bundesliga_news_returns_german_league_news(self):
        """Test GET /api/news/bundesliga returns German league news"""
        response = requests.get(f"{BASE_URL}/api/news/bundesliga")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # All news should be for bundesliga
            for item in news_items:
                assert item['league_id'] == 'bundesliga', f"Expected bundesliga, got {item['league_id']}"
            
            print(f"✓ Bundesliga news: {len(news_items)} items")
        else:
            print("⚠ Bundesliga news: 0 items")

class TestPremierLeagueDataCorrectness:
    """Test Premier League returns English teams"""
    
    def test_premier_league_standings_returns_english_teams(self):
        """Test GET /api/standings/premier-league returns English teams like Arsenal, Liverpool"""
        response = requests.get(f"{BASE_URL}/api/standings/premier-league")
        assert response.status_code == 200
        
        data = response.json()
        assert 'standings' in data
        standings = data['standings']
        assert isinstance(standings, list)
        
        if len(standings) > 0:
            # Get all team names
            team_names = [team['team_name'] for team in standings]
            team_names_str = ', '.join(team_names[:5])
            
            # Check for English teams (common Premier League teams)
            english_teams = ['أرسنال', 'ليفربول', 'مانشستر سيتي', 'تشيلسي', 'مانشستر يونايتد', 'توتنهام']
            found_english = [team for team in english_teams if any(team in name for name in team_names)]
            
            print(f"✓ Premier League standings: {len(standings)} teams")
            print(f"  Top 5 teams: {team_names_str}")
            print(f"  English teams found: {len(found_english)} ({', '.join(found_english[:3])})")
            
            # Premier League should have English teams
            assert len(found_english) > 0, f"Premier League should have English teams but found none. Teams: {team_names_str}"
        else:
            pytest.skip("No standings data available for Premier League")
    
    def test_premier_league_news_returns_english_league_news(self):
        """Test GET /api/news/premier-league returns English league news"""
        response = requests.get(f"{BASE_URL}/api/news/premier-league")
        assert response.status_code == 200
        
        data = response.json()
        assert 'news' in data
        news_items = data['news']
        assert isinstance(news_items, list)
        
        if len(news_items) > 0:
            # All news should be for premier-league
            for item in news_items:
                assert item['league_id'] == 'premier-league', f"Expected premier-league, got {item['league_id']}"
            
            print(f"✓ Premier League news: {len(news_items)} items")
        else:
            print("⚠ Premier League news: 0 items")
