"""
Trekking API integration for the Italian Alps Vacation Planner
This module provides functions to fetch data from external trekking APIs
and integrate it with our database.
"""
import requests
import logging
import json
import os
import random
import time
from models import POI, Category, db
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for the API
API_BASE_URL = "https://hiking-trails-api.example.com/api/v1"  # Replace with actual API URL
DEFAULT_REGION = "trentino-alto-adige"  # Default region in Italy for our search


def fetch_trails_from_api(region=DEFAULT_REGION, limit=10):
    """
    Fetch trail data from the external trekking API
    
    Args:
        region (str): The region to search for trails
        limit (int): Maximum number of trails to fetch
        
    Returns:
        list: List of trail objects
    """
    try:
        # If we need an API key, check for it
        api_key = os.environ.get('TREKKING_API_KEY')
        if not api_key:
            logger.warning("No TREKKING_API_KEY found in environment variables")
            return []
            
        # Sample API endpoint
        endpoint = f"{API_BASE_URL}/trails"
        
        # Request parameters - adjust based on the actual API
        params = {
            "region": region,
            "limit": limit,
            "api_key": api_key
        }
        
        # Make the API request
        response = requests.get(endpoint, params=params, timeout=10)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully fetched {len(data['trails'])} trails from API")
            return data['trails']
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"Error fetching data from trekking API: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in fetch_trails_from_api: {str(e)}")
        return []


def import_trails_to_database(trails_data, category_name="trails"):
    """
    Import trail data from the API into our database
    
    Args:
        trails_data (list): List of trail objects from the API
        category_name (str): Name of the category to assign the trails to
        
    Returns:
        int: Number of trails successfully imported
    """
    if not trails_data:
        return 0
        
    # Get the trails category
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        logger.error(f"Category '{category_name}' not found in database")
        return 0
    
    imported_count = 0
    
    # Process each trail from the API
    for trail in trails_data:
        try:
            # Check if we already have this trail (by name or other identifier)
            existing_trail = POI.query.filter_by(
                name=trail.get('name'),
                category_id=category.id
            ).first()
            
            if existing_trail:
                logger.info(f"Trail '{trail.get('name')}' already exists in database (ID: {existing_trail.id})")
                continue
                
            # Extract trail data - adjust these field names based on the actual API response
            name = trail.get('name')
            lat = trail.get('lat') or trail.get('latitude')
            lng = trail.get('lng') or trail.get('longitude')
            description = trail.get('description', '')
            url = trail.get('url', '')
            
            # Extract the path data if available
            path = trail.get('path') or trail.get('coordinates') or []
            
            # Create a new POI for this trail
            new_trail = POI(
                name=name,
                lat=lat,
                lng=lng,
                description=description,
                url=url,
                category_id=category.id,
                path=path,
                difficulty_rating=trail.get('difficulty', 0),
                rating_count=trail.get('rating_count', 0)
            )
            
            # Add to database
            db.session.add(new_trail)
            imported_count += 1
            
            # Commit every few trails to avoid large transactions
            if imported_count % 10 == 0:
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error importing trail '{trail.get('name')}': {str(e)}")
            # Continue with the next trail rather than failing the whole import
            continue
    
    # Final commit
    if imported_count > 0:
        db.session.commit()
        
    logger.info(f"Successfully imported {imported_count} new trails to database")
    return imported_count


def update_trails_from_api():
    """
    Main function to fetch new trails from the API and update our database
    
    Returns:
        dict: Summary of the update operation
    """
    with current_app.app_context():
        # Fetch trails from API
        trails_data = fetch_trails_from_api()
        
        # Import to database
        imported_count = import_trails_to_database(trails_data)
        
        return {
            "status": "success" if imported_count > 0 else "no_changes",
            "imported_count": imported_count,
            "timestamp": time.time()
        }


def create_api_trail_path(lat, lng, length=5):
    """
    Create a simulated trail path for testing when API doesn't provide path data
    
    Args:
        lat (float): Center latitude
        lng (float): Center longitude
        length (int): Approximate length of the trail in km
        
    Returns:
        list: List of [lat, lng] coordinates forming a path
    """
    path = []
    # Starting point
    path.append([lat, lng])
    
    # Generate a somewhat realistic trail path
    steps = 20  # Number of points in the path
    for i in range(steps):
        # Add some randomness to create a winding path
        # Scale the randomness based on desired length
        scale = length / 50.0
        lat_change = random.uniform(-0.01, 0.01) * scale
        lng_change = random.uniform(-0.01, 0.01) * scale
        
        # Get the previous point
        prev_lat, prev_lng = path[-1]
        
        # Add new point
        path.append([prev_lat + lat_change, prev_lng + lng_change])
    
    return path