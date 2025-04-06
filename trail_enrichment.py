"""
Trail Enrichment Module for Italian Alps Vacation Planner

This module provides functions to enrich trail data with additional information
from external sources and AI-powered analysis.
"""

import os
import re
import logging
import json
import trafilatura
from models import POI, Category, TrailRating, db
from sqlalchemy import desc

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_website_text_content(url):
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        else:
            logger.error(f"Failed to download content from {url}")
            return None
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None

def get_trails_without_descriptions():
    """
    Get all trails that don't have descriptions or have minimal descriptions
    """
    # Get the trails category ID
    trails_category = Category.query.filter_by(name="trails").first()
    if not trails_category:
        logger.error("Trails category not found")
        return []
    
    # Get trails with no description or short descriptions
    trails = POI.query.filter_by(category_id=trails_category.id).filter(
        (POI.description.is_(None)) | 
        (POI.description == '') | 
        (db.func.length(POI.description) < 50)
    ).all()
    
    return trails

def update_trail_description(trail_id, new_description):
    """
    Update a trail's description
    """
    trail = POI.query.get(trail_id)
    if not trail:
        logger.error(f"Trail with ID {trail_id} not found")
        return False
    
    try:
        trail.description = new_description
        db.session.commit()
        logger.info(f"Updated description for trail {trail.name}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating trail description: {str(e)}")
        return False

def extract_clean_description(content, trail_name):
    """
    Extract a clean, useful description from raw content
    """
    # Remove extra whitespace
    clean_content = re.sub(r'\s+', ' ', content).strip()
    
    # Try to find a good paragraph to use (looking for keywords)
    keywords = ['hiking', 'trail', 'path', 'route', 'trek', 'mountain', 'hike', 
                'difficulty', 'scenic', 'panoramic', 'family', 'children', 
                'distance', 'elevation', 'duration', 'alpine']
    
    # Try to find paragraphs containing trail info
    paragraphs = clean_content.split('. ')
    relevant_paragraphs = []
    
    for paragraph in paragraphs:
        # Skip very short paragraphs
        if len(paragraph.strip()) < 40:
            continue
            
        paragraph = paragraph.strip() + '.'
        score = 0
        
        # Score the paragraph based on keywords
        for keyword in keywords:
            if keyword.lower() in paragraph.lower():
                score += 1
                
        # If trail name is in paragraph, boost score
        if trail_name.lower() in paragraph.lower():
            score += 3
            
        if score > 1:  # Only include if it has some relevance
            relevant_paragraphs.append((paragraph, score))
    
    # Sort by relevance score
    relevant_paragraphs.sort(key=lambda x: x[1], reverse=True)
    
    # Take top paragraphs up to ~500 chars
    description = ""
    char_count = 0
    
    for paragraph, _ in relevant_paragraphs:
        if char_count + len(paragraph) > 600:
            break
        description += " " + paragraph
        char_count += len(paragraph)
    
    # If no relevant paragraphs found, just take the first 500 characters
    if not description:
        description = clean_content[:500] + "..."
    
    return description.strip()

def enrich_trail_data(trail):
    """
    Enrich a trail's data with information scraped from its URL
    """
    if not trail.url:
        logger.info(f"Trail {trail.name} has no URL")
        return False
    
    # Get text content from the trail's URL
    content = get_website_text_content(trail.url)
    if not content:
        logger.info(f"Could not get content for trail {trail.name}")
        return False
    
    # Extract a clean, useful description
    description = extract_clean_description(content, trail.name)
    
    # Update the trail's description
    return update_trail_description(trail.id, description)

def batch_enrich_trails(limit=5):
    """
    Enrich multiple trails with scraped data
    """
    trails = get_trails_without_descriptions()
    enriched_count = 0
    
    for trail in trails[:limit]:
        if enrich_trail_data(trail):
            enriched_count += 1
    
    return {
        "processed": min(limit, len(trails)),
        "enriched": enriched_count,
        "remaining": max(0, len(trails) - limit)
    }

# If you have an OpenAI API key, you could use this function to generate better descriptions
def generate_ai_description(trail_name, raw_content):
    """
    Use OpenAI to generate a more engaging and informative trail description
    """
    # This would require the OpenAI API key to be configured
    # For now, just return a placeholder
    
    # In a production environment with the API key, you would use:
    # response = openai.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a hiking expert in the Italian Alps. Create an engaging"
    #             + " and informative description of a hiking trail based on the raw text"
    #             + " extracted from a website. Focus on difficulty, scenery, key features,"
    #             + " and whether it's suitable for families or experienced hikers. Limit"
    #             + " to 200-300 words."
    #         },
    #         {
    #             "role": "user",
    #             "content": f"Trail name: {trail_name}\nRaw content: {raw_content[:2000]}"
    #         }
    #     ],
    #     max_tokens=500
    # )
    # return response.choices[0].message.content
    
    return f"Enhanced description for {trail_name} would be generated with OpenAI API if configured."

if __name__ == "__main__":
    # This code will run when the script is executed directly
    result = batch_enrich_trails(limit=5)
    print(f"Processed {result['processed']} trails")
    print(f"Enriched {result['enriched']} trails")
    print(f"Remaining {result['remaining']} trails to process")