import logging
from app import db
from models import POI, Category
import trafilatura
import re
import random
from bs4 import BeautifulSoup
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_family_trails():
    """Scrape family-friendly hiking trails from several dedicated sources"""
    trails = []
    
    # Sources focused on family hiking in the Italian Alps
    sources = [
        {
            "url": "https://www.livigno.eu/en/hiking-with-children",
            "region": "Livigno",
            "base_lat": 46.5384, 
            "base_lng": 10.1357
        },
        {
            "url": "https://www.val-gardena.org/en/activities/summer/hiking-trekking/hiking-with-children/",
            "region": "Val Gardena",
            "base_lat": 46.5572, 
            "base_lng": 11.6669
        },
        {
            "url": "https://www.dolomiti.it/en/activities/with-children",
            "region": "Dolomites",
            "base_lat": 46.4102, 
            "base_lng": 11.8449
        },
        {
            "url": "https://www.trentino.com/en/highlights/trekking-and-hiking/trekking-with-children/",
            "region": "Trentino",
            "base_lat": 46.0664, 
            "base_lng": 11.1242
        }
    ]
    
    for source in sources:
        try:
            logger.info(f"Scraping family trails from {source['url']}")
            
            # Download the content
            response = requests.get(source['url'], timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup for better extraction of trail elements
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main text content with trafilatura for description
            downloaded = trafilatura.extract(response.content)
            
            # Look for trail sections
            trail_sections = []
            
            # Different websites have different structures - try various selectors
            for section in soup.select('article, .trail-item, .hike-item, .card, .excursion-item, .content-block'):
                trail_name = None
                trail_desc = None
                trail_url = None
                
                # Try to find the trail name from headers or strong texts
                name_elem = section.select_one('h2, h3, h4, strong.title, .card-title')
                if name_elem and 'family' in name_elem.text.lower() or 'child' in name_elem.text.lower() or 'kid' in name_elem.text.lower():
                    trail_name = name_elem.text.strip()
                    
                    # Look for description
                    desc_elem = section.select_one('p, .description, .card-text')
                    if desc_elem:
                        trail_desc = desc_elem.text.strip()
                    
                    # Look for URL
                    url_elem = section.select_one('a')
                    if url_elem and url_elem.has_attr('href'):
                        href = url_elem['href']
                        if href.startswith('/'):
                            # Convert relative URL to absolute
                            base_url = '/'.join(source['url'].split('/')[:3])
                            trail_url = f"{base_url}{href}"
                        elif href.startswith('http'):
                            trail_url = href
                            
                    if trail_name:
                        trail_sections.append({
                            'name': f"{trail_name} - {source['region']}",
                            'description': trail_desc or f"Family-friendly hiking trail in {source['region']}",
                            'url': trail_url or source['url'],
                            'region': source['region'],
                            'base_lat': source['base_lat'],
                            'base_lng': source['base_lng']
                        })
            
            # If no structured elements were found, extract from the general text
            if len(trail_sections) == 0:
                # Look for "family" or "children" keywords in paragraphs
                for para in soup.select('p'):
                    text = para.text.strip().lower()
                    if ('family' in text or 'children' in text or 'kid' in text) and len(text) > 100:
                        # This might be a trail description
                        # Look for potential trail names in nearby headings
                        prev_heading = para.find_previous(['h1', 'h2', 'h3', 'h4'])
                        if prev_heading:
                            trail_name = prev_heading.text.strip()
                            trail_desc = para.text.strip()
                            
                            trail_sections.append({
                                'name': f"{trail_name} - {source['region']}",
                                'description': trail_desc,
                                'url': source['url'],
                                'region': source['region'],
                                'base_lat': source['base_lat'],
                                'base_lng': source['base_lng']
                            })
            
            # Add the scraped trail sections
            for trail in trail_sections:
                # Generate a random path around the base coordinates
                path = create_family_trail_path(trail['base_lat'], trail['base_lng'])
                
                trails.append({
                    'name': trail['name'],
                    'description': trail['description'],
                    'url': trail['url'],
                    'lat': path[0]['lat'],  # Start point latitude
                    'lng': path[0]['lng'],  # Start point longitude
                    'path': path
                })
                
            # Ensure we don't hammer the servers
            time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error scraping {source['url']}: {str(e)}")
            continue
            
    logger.info(f"Scraped {len(trails)} family-friendly trails")
    return trails

def create_family_trail_path(base_lat, base_lng):
    """Create a family-friendly trail path based on base coordinates
    
    For family trails, we'll create shorter paths with less elevation
    change to represent easier, family-friendly trails.
    """
    path_length = random.randint(5, 10)  # Family trails are shorter
    path = []
    
    # Start point - near the base coordinates
    start_lat = base_lat + random.uniform(-0.01, 0.01)
    start_lng = base_lng + random.uniform(-0.01, 0.01)
    
    path.append({'lat': start_lat, 'lng': start_lng})
    
    current_lat = start_lat
    current_lng = start_lng
    
    # Generate a path with smaller elevation changes
    for i in range(path_length):
        # Family trails tend to be more circular and return to starting point
        direction_to_start = 0
        if i > path_length / 2:
            # Start heading back to the beginning
            direction_to_start = 0.7
            
        # Calculate next point with small variations to simulate gentle slopes
        # These smaller changes create easier "family-friendly" paths
        lat_change = random.uniform(-0.003, 0.003) + direction_to_start * (start_lat - current_lat) * 0.2
        lng_change = random.uniform(-0.003, 0.003) + direction_to_start * (start_lng - current_lng) * 0.2
        
        current_lat += lat_change
        current_lng += lng_change
        
        path.append({'lat': current_lat, 'lng': current_lng})
    
    # For family trails, ensure we return close to start point
    path.append({'lat': start_lat + random.uniform(-0.001, 0.001), 
                'lng': start_lng + random.uniform(-0.001, 0.001)})
    
    return path

def add_family_trails_to_database():
    """Add family-friendly trails to the database"""
    logger.info("Adding scraped family-friendly trails to database")
    
    # Get the trails category
    category = Category.query.filter_by(name='trails').first()
    if not category:
        logger.error("Trails category not found!")
        return
    
    # Scrape family trails
    trails = scrape_family_trails()
    
    # Count only new trails added
    count_added = 0
    
    # Add each trail to the database
    for trail in trails:
        # Check if a trail with this name already exists
        existing_trail = POI.query.filter_by(name=trail['name'], category_id=category.id).first()
        
        if not existing_trail:
            # Create new trail
            new_trail = POI(
                name=trail['name'],
                lat=trail['lat'],
                lng=trail['lng'],
                description=trail['description'],
                url=trail['url'],
                category_id=category.id,
                path=trail['path'],
                difficulty_rating=1.5  # Family trails are easier
            )
            
            db.session.add(new_trail)
            count_added += 1
    
    # Commit changes
    db.session.commit()
    
    logger.info(f"Added {count_added} new family-friendly trails to database")
    return count_added

if __name__ == "__main__":
    # When run as a script, add the trails to the database
    from app import app
    with app.app_context():
        add_family_trails_to_database()