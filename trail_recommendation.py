"""
Trail Recommendation Engine for Italian Alps Vacation Planner

This module provides functions to recommend hiking trails based on user preferences,
including difficulty level, proximity to accommodation, and family friendliness.
"""

from flask import current_app
from models import POI, TrailRating, Category, Airbnb
from sqlalchemy import desc, func
import logging
import math

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lng1: Coordinates of point 1
        lat2, lng2: Coordinates of point 2
        
    Returns:
        float: Distance in kilometers
    """
    # Radius of the Earth in km
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def get_trails_category_id():
    """Get the category ID for hiking trails"""
    trails_category = Category.query.filter_by(name='trails').first()
    if not trails_category:
        logger.error("Trails category not found in the database")
        return None
    return trails_category.id

def get_trails_with_ratings(difficulty_level=None, limit=10):
    """
    Get trails with their ratings, optionally filtered by difficulty level
    
    Args:
        difficulty_level (int, optional): Filter by difficulty level (1-5)
        limit (int, optional): Maximum number of trails to return
        
    Returns:
        list: List of trails with their ratings
    """
    category_id = get_trails_category_id()
    if not category_id:
        return []
    
    query = POI.query.filter_by(category_id=category_id)
    
    # Filter by difficulty level if specified
    if difficulty_level:
        # Allow for a small range around the requested difficulty
        query = query.filter(
            POI.difficulty_rating >= difficulty_level - 0.5,
            POI.difficulty_rating <= difficulty_level + 0.5
        )
    
    # Get trails with at least some ratings
    trails = query.filter(POI.rating_count > 0).order_by(desc(POI.rating_count)).limit(limit).all()
    
    return trails

def get_family_friendly_trails(limit=5):
    """
    Get family-friendly trails (those with lower difficulty ratings or 
    family-friendly keywords in the name or description)
    
    Args:
        limit (int, optional): Maximum number of trails to return
        
    Returns:
        list: List of family-friendly trails
    """
    category_id = get_trails_category_id()
    if not category_id:
        return []
    
    # Start with trails that mention family, kids, children, etc. in their name or description
    from sqlalchemy import or_
    family_keywords = POI.query.filter_by(category_id=category_id).filter(
        or_(
            POI.name.ilike('%family%'),
            POI.description.ilike('%family%'),
            POI.name.ilike('%kid%'),
            POI.description.ilike('%kid%'),
            POI.name.ilike('%child%'),
            POI.description.ilike('%child%'),
            POI.name.ilike('%easy%'),
            POI.description.ilike('%easy%'),
            POI.name.ilike('%beginner%'),
            POI.description.ilike('%beginner%')
        )
    ).limit(limit).all()
    
    # If we didn't get enough trails with keywords, add trails with low difficulty
    if len(family_keywords) < limit:
        remaining_limit = limit - len(family_keywords)
        # Find IDs of trails we already have to avoid duplicates
        existing_ids = [trail.id for trail in family_keywords]
        
        # Add trails with low difficulty ratings
        if existing_ids:
            easy_trails = POI.query.filter_by(category_id=category_id).filter(
                ~POI.id.in_(existing_ids),
                POI.difficulty_rating > 0,  # Must have a rating
                POI.difficulty_rating <= 2.5  # Easy to moderate difficulty
            ).order_by(POI.difficulty_rating).limit(remaining_limit).all()
        else:
            easy_trails = POI.query.filter_by(category_id=category_id).filter(
                POI.difficulty_rating > 0,  # Must have a rating
                POI.difficulty_rating <= 2.5  # Easy to moderate difficulty
            ).order_by(POI.difficulty_rating).limit(remaining_limit).all()
        
        family_keywords.extend(easy_trails)
    
    return family_keywords

def get_trails_near_airbnb(airbnb_id, max_distance=10, limit=5):
    """
    Get trails near a specific Airbnb accommodation
    
    Args:
        airbnb_id (int): ID of the Airbnb
        max_distance (float, optional): Maximum distance in kilometers
        limit (int, optional): Maximum number of trails to return
        
    Returns:
        list: List of trails sorted by distance
    """
    # Get the Airbnb coordinates
    airbnb = Airbnb.query.get(airbnb_id)
    if not airbnb:
        logger.error(f"Airbnb with ID {airbnb_id} not found")
        return []
    
    airbnb_lat, airbnb_lng = airbnb.lat, airbnb.lng
    
    # Get the trails category ID
    category_id = get_trails_category_id()
    if not category_id:
        return []
    
    # Get all trails
    trails = POI.query.filter_by(category_id=category_id).all()
    
    # Calculate distance to each trail and filter
    nearby_trails = []
    for trail in trails:
        distance = calculate_distance(airbnb_lat, airbnb_lng, trail.lat, trail.lng)
        if distance <= max_distance:
            nearby_trails.append({
                'trail': trail,
                'distance': distance
            })
    
    # Sort by distance and limit results
    nearby_trails.sort(key=lambda x: x['distance'])
    return nearby_trails[:limit]

def get_popular_trails(limit=5):
    """
    Get the most popular trails based on rating count
    
    Args:
        limit (int, optional): Maximum number of trails to return
        
    Returns:
        list: List of popular trails
    """
    category_id = get_trails_category_id()
    if not category_id:
        return []
    
    popular_trails = POI.query.filter_by(category_id=category_id).order_by(
        desc(POI.rating_count),
        desc(POI.difficulty_rating)
    ).limit(limit).all()
    
    return popular_trails

def recommend_trails(user_preferences):
    """
    Recommend trails based on user preferences
    
    Args:
        user_preferences (dict): User preferences including:
            - difficulty_level (int): Preferred difficulty level (1-5)
            - family_friendly (bool): Whether to prioritize family-friendly trails
            - airbnb_id (int, optional): ID of the Airbnb to find nearby trails
        
    Returns:
        dict: Recommended trails in different categories
    """
    difficulty_level = user_preferences.get('difficulty_level', 3)
    family_friendly = user_preferences.get('family_friendly', False)
    airbnb_id = user_preferences.get('airbnb_id')
    
    recommendations = {
        'by_difficulty': get_trails_with_ratings(difficulty_level, limit=5),
        'popular_trails': get_popular_trails(limit=5)
    }
    
    if family_friendly:
        recommendations['family_friendly'] = get_family_friendly_trails(limit=5)
    
    if airbnb_id:
        nearby_trails = get_trails_near_airbnb(airbnb_id, limit=5)
        recommendations['nearby_trails'] = nearby_trails
    
    return recommendations