from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# League configurations
LEAGUES = {
    "premier-league": {
        "id": "premier-league",
        "name": "الدوري الإنجليزي",
        "name_en": "Premier League",
        "tour_id": 93,
        "comp_id": 2968,
        "country": "إنجلترا",
        "logo": "https://mediayk.gemini.media/img/yallakora/tourlogo/Premier-League-Symbol%20(1)28-01-2025-12-24-46.webp"
    },
    "la-liga": {
        "id": "la-liga",
        "name": "الدوري الإسباني",
        "name_en": "La Liga",
        "tour_id": 95,
        "comp_id": 2978,
        "country": "إسبانيا",
        "logo": "https://mediayk.gemini.media/img/yallakora/tourlogo/LaLiga_logo_202328-01-2025-12-28-56.webp"
    },
    "serie-a": {
        "id": "serie-a",
        "name": "الدوري الإيطالي",
        "name_en": "Serie A",
        "tour_id": 94,
        "comp_id": 2981,
        "country": "إيطاليا",
        "logo": "https://mediayk.gemini.media/img/yallakora/tourlogo/Serie_A_logo_202228-01-2025-12-27-48.webp"
    },
    "bundesliga": {
        "id": "bundesliga",
        "name": "الدوري الألماني",
        "name_en": "Bundesliga",
        "tour_id": 92,
        "comp_id": 2980,
        "country": "ألمانيا",
        "logo": "https://mediayk.gemini.media/img/yallakora/tourlogo/Bundesliga_logo_(2017)28-01-2025-12-30-44.webp"
    },
    "ligue-1": {
        "id": "ligue-1",
        "name": "الدوري الفرنسي",
        "name_en": "Ligue 1",
        "tour_id": 96,
        "comp_id": 2979,
        "country": "فرنسا",
        "logo": "https://mediayk.gemini.media/img/yallakora/tourlogo/Ligue_128-01-2025-12-29-48.webp"
    }
}

# Models
class League(BaseModel):
    id: str
    name: str
    name_en: str
    tour_id: int
    comp_id: int
    country: str
    logo: str

class NewsItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    link: str
    league_id: str
    date: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StandingItem(BaseModel):
    position: int
    team_name: str
    team_logo: Optional[str] = None
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    points: int

class MatchItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    home_team: str
    away_team: str
    home_logo: Optional[str] = None
    away_logo: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    match_time: str
    match_date: str
    status: str  # upcoming, live, finished
    league_id: str

async def fetch_page(url: str) -> Optional[str]:
    """Fetch HTML content from URL"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en;q=0.9'
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            if response.status_code == 200:
                return response.text
            logger.error(f"Failed to fetch {url}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

async def scrape_news(league_id: str) -> List[dict]:
    """Scrape news from YallaKora for a specific league"""
    league = LEAGUES.get(league_id)
    if not league:
        return []
    
    # Try multiple URL formats
    urls_to_try = [
        f"https://www.yallakora.com/tour-news/{league['tour_id']}/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1",
        f"https://www.yallakora.com/tour/{league['tour_id']}",
    ]
    
    html = None
    for url in urls_to_try:
        html = await fetch_page(url)
        if html:
            break
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []
    seen_titles = set()
    
    # Find news list items with postid attribute (main news listing)
    news_list_items = soup.find_all('li', attrs={'postid': True})
    
    for item in news_list_items:
        try:
            # Find the image
            img = item.find('img')
            image_url = None
            if img:
                image_url = img.get('src', '') or img.get('data-src', '')
                if image_url:
                    # Fix backslashes in URL
                    image_url = image_url.replace('\\', '/')
                    if not image_url.startswith('http'):
                        image_url = 'https:' + image_url if image_url.startswith('//') else 'https://www.yallakora.com' + image_url
            
            # Find title in p tag
            title_elem = item.find('p')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            
            if not title or len(title) < 10 or title in seen_titles:
                continue
            
            seen_titles.add(title)
            
            # Find link
            link_elem = item.find('a', href=True)
            if not link_elem:
                continue
            
            href = link_elem.get('href', '')
            if '/news/' not in href:
                continue
            
            link = href if href.startswith('http') else 'https://www.yallakora.com' + href
            
            # Find date from time div
            date_str = None
            time_div = item.find('div', class_='time')
            if time_div:
                spans = time_div.find_all('span')
                if spans:
                    date_str = spans[0].get_text(strip=True)
            
            news_items.append({
                "id": str(uuid.uuid4()),
                "title": title,
                "summary": None,
                "image_url": image_url,
                "link": link,
                "league_id": league_id,
                "date": date_str,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            if len(news_items) >= 20:
                break
                
        except Exception as e:
            logger.error(f"Error parsing news item: {e}")
            continue
    
    # If no items found with postid, try alternative parsing
    if not news_items:
        # Fallback: look for news links with images
        containers = soup.find_all(['li', 'div'], class_=lambda x: x and 'link' in str(x).lower())
        for container in containers:
            try:
                link_elem = container.find('a', href=True)
                if not link_elem or '/news/' not in link_elem.get('href', ''):
                    continue
                
                img = container.find('img')
                image_url = None
                if img:
                    image_url = img.get('src', '') or img.get('data-src', '')
                    if image_url:
                        # Fix backslashes in URL
                        image_url = image_url.replace('\\', '/')
                        if not image_url.startswith('http'):
                            image_url = 'https:' + image_url if image_url.startswith('//') else 'https://www.yallakora.com' + image_url
                
                title_elem = container.find('p')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                if not title or len(title) < 10 or title in seen_titles:
                    continue
                
                seen_titles.add(title)
                href = link_elem.get('href', '')
                link = href if href.startswith('http') else 'https://www.yallakora.com' + href
                
                news_items.append({
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "summary": None,
                    "image_url": image_url,
                    "link": link,
                    "league_id": league_id,
                    "date": None,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if len(news_items) >= 20:
                    break
                    
            except Exception as e:
                logger.error(f"Error in fallback parsing: {e}")
                continue
    
    return news_items

async def scrape_standings(league_id: str) -> List[dict]:
    """Scrape standings from YallaKora for a specific league"""
    league = LEAGUES.get(league_id)
    if not league:
        return []
    
    url = f"https://www.yallakora.com/tour-standing/{league['tour_id']}/ترتيب-الفرق"
    html = await fetch_page(url)
    if not html:
        url = f"https://www.yallakora.com/tour/{league['tour_id']}"
        html = await fetch_page(url)
        if not html:
            return []
    
    soup = BeautifulSoup(html, 'html.parser')
    standings = []
    
    # Find standings table rows
    rows = soup.find_all('tr')
    
    for row in rows:
        try:
            cells = row.find_all('td')
            if len(cells) < 8:
                continue
            
            # Extract position
            pos_text = cells[0].get_text(strip=True)
            if not pos_text.isdigit():
                continue
            position = int(pos_text)
            
            # Extract team name and logo
            team_cell = cells[1]
            team_name = team_cell.get_text(strip=True)
            team_img = team_cell.find('img')
            team_logo = team_img.get('src', '') if team_img else None
            
            # Extract stats
            played = int(cells[2].get_text(strip=True) or 0)
            won = int(cells[3].get_text(strip=True) or 0)
            drawn = int(cells[4].get_text(strip=True) or 0)
            lost = int(cells[5].get_text(strip=True) or 0)
            goals_for = int(cells[6].get_text(strip=True) or 0)
            goals_against = int(cells[7].get_text(strip=True) or 0)
            points = int(cells[-1].get_text(strip=True) or 0)
            
            standings.append({
                "position": position,
                "team_name": team_name,
                "team_logo": team_logo,
                "played": played,
                "won": won,
                "drawn": drawn,
                "lost": lost,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "points": points
            })
            
        except Exception as e:
            logger.error(f"Error parsing standing row: {e}")
            continue
    
    return standings

async def scrape_matches(league_id: str) -> List[dict]:
    """Scrape matches from YallaKora for a specific league"""
    league = LEAGUES.get(league_id)
    if not league:
        return []
    
    url = f"https://www.yallakora.com/tour-fixtures/{league['tour_id']}/نتائج-المباريات"
    html = await fetch_page(url)
    if not html:
        url = f"https://www.yallakora.com/tour/{league['tour_id']}"
        html = await fetch_page(url)
        if not html:
            return []
    
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    
    # Find match elements
    match_elements = soup.find_all(['div', 'a'], class_=lambda x: x and ('match' in str(x).lower() or 'game' in str(x).lower()))
    
    for match_elem in match_elements:
        try:
            # Try to extract team names
            teams = match_elem.find_all(['span', 'div'], class_=lambda x: x and 'team' in str(x).lower())
            if len(teams) < 2:
                continue
            
            home_team = teams[0].get_text(strip=True)
            away_team = teams[1].get_text(strip=True)
            
            # Get scores if available
            scores = match_elem.find_all(['span', 'div'], class_=lambda x: x and 'score' in str(x).lower())
            home_score = None
            away_score = None
            if len(scores) >= 2:
                try:
                    home_score = int(scores[0].get_text(strip=True))
                    away_score = int(scores[1].get_text(strip=True))
                except:
                    pass
            
            # Get team logos
            imgs = match_elem.find_all('img')
            home_logo = imgs[0].get('src', '') if len(imgs) > 0 else None
            away_logo = imgs[1].get('src', '') if len(imgs) > 1 else None
            
            # Get time/date
            time_elem = match_elem.find(['span', 'div'], class_=lambda x: x and ('time' in str(x).lower() or 'date' in str(x).lower()))
            match_time = time_elem.get_text(strip=True) if time_elem else "TBD"
            
            status = "finished" if home_score is not None else "upcoming"
            
            matches.append({
                "id": str(uuid.uuid4()),
                "home_team": home_team,
                "away_team": away_team,
                "home_logo": home_logo,
                "away_logo": away_logo,
                "home_score": home_score,
                "away_score": away_score,
                "match_time": match_time,
                "match_date": datetime.now().strftime("%Y-%m-%d"),
                "status": status,
                "league_id": league_id
            })
            
            if len(matches) >= 10:
                break
                
        except Exception as e:
            logger.error(f"Error parsing match: {e}")
            continue
    
    return matches

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Arabic Football News API - أخبار الكرة الأوروبية"}

@api_router.get("/leagues", response_model=List[League])
async def get_leagues():
    """Get all available leagues"""
    return list(LEAGUES.values())

@api_router.get("/news/{league_id}")
async def get_news(league_id: str):
    """Get news for a specific league"""
    if league_id not in LEAGUES:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Try to get cached news first
    cached = await db.news_cache.find_one({"league_id": league_id})
    if cached and (datetime.utcnow() - cached.get('updated_at', datetime.min)).total_seconds() < 300:  # 5 min cache
        return {"news": cached.get('items', []), "cached": True}
    
    # Scrape fresh news
    news_items = await scrape_news(league_id)
    
    # Cache the results
    if news_items:
        await db.news_cache.update_one(
            {"league_id": league_id},
            {"$set": {"items": news_items, "updated_at": datetime.utcnow()}},
            upsert=True
        )
    
    return {"news": news_items, "cached": False}

@api_router.get("/standings/{league_id}")
async def get_standings(league_id: str):
    """Get standings for a specific league"""
    if league_id not in LEAGUES:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Try to get cached standings first
    cached = await db.standings_cache.find_one({"league_id": league_id})
    if cached and (datetime.utcnow() - cached.get('updated_at', datetime.min)).total_seconds() < 3600:  # 1 hour cache
        return {"standings": cached.get('items', []), "cached": True}
    
    # Scrape fresh standings
    standings = await scrape_standings(league_id)
    
    # Cache the results
    if standings:
        await db.standings_cache.update_one(
            {"league_id": league_id},
            {"$set": {"items": standings, "updated_at": datetime.utcnow()}},
            upsert=True
        )
    
    return {"standings": standings, "cached": False}

@api_router.get("/matches/{league_id}")
async def get_matches(league_id: str):
    """Get matches for a specific league"""
    if league_id not in LEAGUES:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Try to get cached matches first
    cached = await db.matches_cache.find_one({"league_id": league_id})
    if cached and (datetime.utcnow() - cached.get('updated_at', datetime.min)).total_seconds() < 600:  # 10 min cache
        return {"matches": cached.get('items', []), "cached": True}
    
    # Scrape fresh matches
    matches = await scrape_matches(league_id)
    
    # Cache the results
    if matches:
        await db.matches_cache.update_one(
            {"league_id": league_id},
            {"$set": {"items": matches, "updated_at": datetime.utcnow()}},
            upsert=True
        )
    
    return {"matches": matches, "cached": False}

@api_router.get("/all-news")
async def get_all_news():
    """Get news from all leagues"""
    all_news = []
    for league_id in LEAGUES.keys():
        try:
            news_items = await scrape_news(league_id)
            all_news.extend(news_items[:5])  # Get top 5 from each league
        except Exception as e:
            logger.error(f"Error getting news for {league_id}: {e}")
    
    # Sort by date/timestamp
    all_news.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return {"news": all_news[:25]}  # Return top 25

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
