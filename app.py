from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, flash
import os
import logging
import uuid
import json
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "italian_alps_vacation")

# Configure the database - ensure DATABASE_URL is properly set
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
logging.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Create the database base class
class Base(DeclarativeBase):
    pass

# Create the database instance
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension
db.init_app(app)

@app.route('/')
def index():
    """Render the main map page."""
    return render_template('index.html')

@app.route('/airbnbs')
def airbnb_list():
    """Render the Airbnb listings page."""
    from models import Airbnb
    airbnbs = Airbnb.query.all()
    return render_template('airbnb_list.html', airbnbs=airbnbs)

@app.route('/api/pois')
def get_pois():
    """Get all POIs from the database."""
    from models import POI, Category
    categories = Category.query.all()
    result = {}
    
    for category in categories:
        result[category.name] = [poi.to_dict() for poi in POI.query.filter_by(category_id=category.id).all()]
    
    return jsonify(result)

@app.route('/api/airbnbs')
def get_airbnbs():
    """Get all Airbnbs from the database."""
    from models import Airbnb
    airbnbs = Airbnb.query.all()
    return jsonify([airbnb.to_dict() for airbnb in airbnbs])

@app.route('/api/airbnbs/<int:airbnb_id>')
def get_airbnb(airbnb_id):
    """Get a specific Airbnb by ID."""
    from models import Airbnb
    airbnb = Airbnb.query.get(airbnb_id)
    if not airbnb:
        return jsonify({"error": "Airbnb not found"}), 404
    return jsonify(airbnb.to_dict())

@app.route('/api/trails/<int:trail_id>/ratings', methods=['GET'])
def get_trail_ratings(trail_id):
    """Get all ratings for a specific trail."""
    from models import TrailRating, POI, Category
    
    # Verify that the POI exists and is a trail
    poi = POI.query.join(Category).filter(POI.id == trail_id, Category.name == 'trails').first()
    if not poi:
        return jsonify({"error": "Trail not found"}), 404
    
    # Get all ratings for this trail
    ratings = TrailRating.query.filter_by(poi_id=trail_id).all()
    return jsonify({
        "trail": poi.to_dict(),
        "ratings": [rating.to_dict() for rating in ratings]
    })

@app.route('/api/trails/<int:trail_id>/rate', methods=['POST'])
def rate_trail(trail_id):
    """Rate a trail's difficulty."""
    from models import TrailRating, POI, Category
    
    # Verify that the POI exists and is a trail
    poi = POI.query.join(Category).filter(POI.id == trail_id, Category.name == 'trails').first()
    if not poi:
        return jsonify({"error": "Trail not found"}), 404
    
    # Get the rating data
    data = request.json
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # Generate a unique user identifier or use the one provided
    user_identifier = data.get('user_identifier', str(uuid.uuid4()))
    
    # Validate the rating
    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid rating value"}), 400
    
    # Check if this user has already rated this trail
    existing_rating = TrailRating.query.filter_by(
        poi_id=trail_id,
        user_identifier=user_identifier
    ).first()
    
    if existing_rating:
        # Update the existing rating
        existing_rating.rating = rating
        existing_rating.comment = comment
    else:
        # Create a new rating
        new_rating = TrailRating(
            poi_id=trail_id,
            rating=rating,
            comment=comment,
            user_identifier=user_identifier
        )
        db.session.add(new_rating)
    
    # Update the trail's average rating
    all_ratings = TrailRating.query.filter_by(poi_id=trail_id).all()
    total_ratings = len(all_ratings) + (0 if existing_rating else 1)
    avg_rating = sum([r.rating for r in all_ratings] + ([rating] if not existing_rating else [])) / total_ratings
    
    poi.difficulty_rating = round(avg_rating, 1)
    poi.rating_count = total_ratings
    
    # Commit changes
    db.session.commit()
    
    return jsonify({
        "success": True,
        "trail": poi.to_dict(),
        "user_identifier": user_identifier
    })

@app.route('/rate-trail/<int:trail_id>', methods=['GET'])
def rate_trail_page(trail_id):
    """Show the trail rating page."""
    from models import POI
    poi = POI.query.get_or_404(trail_id)
    return render_template('rate_trail.html', trail=poi)

@app.route('/add-airbnb', methods=['GET', 'POST'])
def add_airbnb():
    """Add a new Airbnb to the database."""
    if request.method == 'POST':
        from models import Airbnb
        
        # Get form data
        name = request.form.get('name')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        price = request.form.get('price')
        description = request.form.get('description')
        url = request.form.get('url')
        bedrooms = request.form.get('bedrooms')
        image_url = request.form.get('image_url')
        
        # Validate required fields
        if not name or not lat or not lng:
            flash('Name, latitude, and longitude are required fields.', 'error')
            return redirect(url_for('add_airbnb'))
        
        try:
            # Convert numeric fields
            lat = float(lat)
            lng = float(lng)
            price = int(price) if price else None
            bedrooms = int(bedrooms) if bedrooms else None
            
            # Create new Airbnb
            new_airbnb = Airbnb(
                name=name,
                lat=lat,
                lng=lng,
                price=price,
                description=description,
                url=url,
                bedrooms=bedrooms,
                image_url=image_url
            )
            
            # Add to database
            db.session.add(new_airbnb)
            db.session.commit()
            
            flash('Airbnb added successfully!', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(f'Error adding Airbnb: {str(e)}', 'error')
            return redirect(url_for('add_airbnb'))
    
    # GET request - show the form
    return render_template('add_airbnb.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logging.error(f"Server error: {e}")
    return render_template('index.html'), 500

# API routes for trekking integration
@app.route('/admin/trekking-api')
def admin_trekking_api():
    """Admin page for managing the trekking API integration."""
    # Get the API key from environment variable
    api_key = os.environ.get('TREKKING_API_KEY', '')
    return render_template('admin/trekking_api.html', api_key=api_key)
    
@app.route('/recommend-trails')
def recommend_trails_page():
    """Show the trail recommendation page."""
    from models import Airbnb
    airbnbs = Airbnb.query.all()
    return render_template('recommend_trails.html', airbnbs=airbnbs)

@app.route('/api/trails/update-from-api', methods=['POST'])
def update_trails_from_api():
    """Update trails from external trekking API."""
    try:
        # Get parameters from request
        data = request.json or {}
        region = data.get('region', 'trentino-alto-adige')
        limit = int(data.get('limit', 25))
        
        from trekking_api import fetch_trails_from_api, import_trails_to_database
        
        # Fetch trails
        trails_data = fetch_trails_from_api(region=region, limit=limit)
        
        # Import to database
        imported_count = import_trails_to_database(trails_data)
        
        # Save sync history
        save_sync_history("success", f"Successfully imported {imported_count} new trails from API")
        
        return jsonify({
            "status": "success" if imported_count > 0 else "no_changes",
            "imported_count": imported_count,
            "timestamp": time.time()
        })
    except Exception as e:
        logging.error(f"Error updating trails from API: {str(e)}")
        save_sync_history("error", f"Error: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/trails/external-sources')
def get_external_trail_sources():
    """Get information about external trail data sources."""
    sources = [
        {
            "name": "External Trekking API",
            "description": "Official hiking trails data from our partner trekking application",
            "url": "https://hiking-trails-api.example.com/",
            "last_update": "2025-04-06T12:00:00Z",
            "trail_count": 25
        }
    ]
    return jsonify(sources)

@app.route('/api/admin/save-api-key', methods=['POST'])
def save_api_key():
    """Save the trekking API key."""
    try:
        data = request.json
        api_key = data.get('api_key', '')
        
        # In a production environment, you would save this to a secure storage
        # For this demo, we'll just print it to the console
        logging.info(f"Saving API key: {api_key[:4]}{'*' * (len(api_key) - 4)}")
        
        # For a real implementation, you might set an environment variable
        os.environ['TREKKING_API_KEY'] = api_key
        
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Error saving API key: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/test-connection')
def test_api_connection():
    """Test the connection to the trekking API."""
    try:
        from trekking_api import fetch_trails_from_api
        
        # Try to fetch just one trail to test the connection
        trails = fetch_trails_from_api(limit=1)
        
        if trails and len(trails) > 0:
            return jsonify({"connected": True})
        else:
            return jsonify({"connected": False, "error": "API returned no data"})
    except Exception as e:
        logging.error(f"API connection test failed: {str(e)}")
        return jsonify({"connected": False, "error": str(e)})

@app.route('/api/admin/connection-status')
def api_connection_status():
    """Check the status of the trekking API connection."""
    api_key = os.environ.get('TREKKING_API_KEY', '')
    
    if not api_key:
        return jsonify({"connected": False, "error": "No API key set"})
    
    try:
        from trekking_api import fetch_trails_from_api
        
        # Try to fetch just one trail to test the connection
        trails = fetch_trails_from_api(limit=1)
        
        if trails and len(trails) > 0:
            return jsonify({"connected": True})
        else:
            return jsonify({"connected": False, "error": "API returned no data"})
    except Exception as e:
        logging.error(f"API connection check failed: {str(e)}")
        return jsonify({"connected": False, "error": str(e)})

@app.route('/api/admin/save-settings', methods=['POST'])
def save_api_settings():
    """Save the trekking API settings."""
    try:
        data = request.json
        
        # In a production app, you would save these settings to a database
        # For this demo, we'll just log them
        logging.info(f"Saving API settings: {data}")
        
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Error saving API settings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/sync-history')
def get_sync_history():
    """Get the synchronization history."""
    # In a production app, you would store this in a database
    # For this demo, we'll return some sample data
    history = [
        {
            "timestamp": "2025-04-06 12:30:15",
            "status": "success",
            "message": "Successfully imported 8 new trails from API"
        },
        {
            "timestamp": "2025-04-05 08:15:22",
            "status": "warning",
            "message": "API rate limit reached, only 5 trails imported"
        },
        {
            "timestamp": "2025-04-04 09:45:10",
            "status": "error",
            "message": "Connection failed: API key invalid"
        }
    ]
    
    # Try to read from history file if it exists
    try:
        if os.path.exists('sync_history.json'):
            with open('sync_history.json', 'r') as f:
                saved_history = json.load(f)
                # Merge with our static data
                if saved_history:
                    # Add the most recent entries at the top
                    history = saved_history + history
    except Exception as e:
        logging.error(f"Error reading sync history: {str(e)}")
    
    return jsonify({"history": history})

# Helper function to save sync history
def save_sync_history(status, message):
    """Save a sync history entry."""
    try:
        # Create a new history entry
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "status": status,
            "message": message
        }
        
        # Read existing history
        history = []
        if os.path.exists('sync_history.json'):
            try:
                with open('sync_history.json', 'r') as f:
                    history = json.load(f)
            except:
                # If file exists but can't be read, start with empty history
                history = []
        
        # Add new entry at the beginning
        history.insert(0, entry)
        
        # Keep only the last 50 entries
        if len(history) > 50:
            history = history[:50]
        
        # Save back to file
        with open('sync_history.json', 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logging.error(f"Error saving sync history: {str(e)}")

# Trail recommendation endpoints
@app.route('/api/recommend/trails', methods=['POST'])
def recommend_trails_api():
    """Recommend trails based on user preferences."""
    try:
        user_preferences = request.json
        # Validate input
        if not user_preferences:
            return jsonify({"error": "Invalid request, preferences required"}), 400
        
        # Import the recommendation engine
        from trail_recommendation import recommend_trails
        
        # Get recommendations
        recommendations = recommend_trails(user_preferences)
        
        # Format the response
        response = {
            "recommendations": {
                "by_difficulty": [t.to_dict() for t in recommendations.get('by_difficulty', [])],
                "popular_trails": [t.to_dict() for t in recommendations.get('popular_trails', [])]
            }
        }
        
        # Add family-friendly trails if requested
        if 'family_friendly' in recommendations:
            response["recommendations"]["family_friendly"] = [
                t.to_dict() for t in recommendations.get('family_friendly', [])
            ]
        
        # Add nearby trails if an Airbnb was specified
        if 'nearby_trails' in recommendations:
            response["recommendations"]["nearby_trails"] = [
                {
                    "trail": item['trail'].to_dict(),
                    "distance_km": round(item['distance'], 1)
                }
                for item in recommendations.get('nearby_trails', [])
            ]
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error generating trail recommendations: {str(e)}")
        return jsonify({"error": "Failed to generate recommendations"}), 500

@app.route('/api/trails/difficulty/<int:difficulty>', methods=['GET'])
def get_trails_by_difficulty(difficulty):
    """Get trails filtered by difficulty level."""
    try:
        # Validate difficulty level
        if difficulty < 1 or difficulty > 5:
            return jsonify({"error": "Difficulty must be between 1 and 5"}), 400
        
        # Import the function
        from trail_recommendation import get_trails_with_ratings
        
        # Get trails
        trails = get_trails_with_ratings(difficulty_level=difficulty)
        
        # Format the response
        response = {
            "trails": [t.to_dict() for t in trails]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error getting trails by difficulty: {str(e)}")
        return jsonify({"error": "Failed to get trails"}), 500

@app.route('/api/trails/family-friendly', methods=['GET'])
def get_family_trails_api():
    """Get family-friendly trails."""
    try:
        # Import the function
        from trail_recommendation import get_family_friendly_trails
        
        # Get trails
        trails = get_family_friendly_trails()
        
        # Format the response
        response = {
            "trails": [t.to_dict() for t in trails]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error getting family-friendly trails: {str(e)}")
        return jsonify({"error": "Failed to get family-friendly trails"}), 500

@app.route('/api/trails/near-airbnb/<int:airbnb_id>', methods=['GET'])
def get_trails_near_airbnb_api(airbnb_id):
    """Get trails near a specific Airbnb."""
    try:
        # Get optional parameters
        max_distance = request.args.get('max_distance', default=10, type=float)
        
        # Import the function
        from trail_recommendation import get_trails_near_airbnb
        
        # Get trails
        nearby_trails = get_trails_near_airbnb(airbnb_id, max_distance=max_distance)
        
        # Format the response
        response = {
            "trails": [
                {
                    "trail": item['trail'].to_dict(),
                    "distance_km": round(item['distance'], 1)
                }
                for item in nearby_trails
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error getting trails near Airbnb: {str(e)}")
        return jsonify({"error": "Failed to get nearby trails"}), 500

@app.route('/api/trails/popular', methods=['GET'])
def get_popular_trails_api():
    """Get the most popular trails."""
    try:
        # Import the function
        from trail_recommendation import get_popular_trails
        
        # Get trails
        trails = get_popular_trails()
        
        # Format the response
        response = {
            "trails": [t.to_dict() for t in trails]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error getting popular trails: {str(e)}")
        return jsonify({"error": "Failed to get popular trails"}), 500

# Create tables
with app.app_context():
    # Import models here to avoid circular imports
    import models  # noqa: F401
    db.create_all()
    # Initialize the database with default categories if empty
    from models import Category, POI
    if Category.query.count() == 0:
        from initialize_db import populate_database
        populate_database()
        db.session.commit()
        logging.info("Database initialized with default data")
    
    # Check if we need to add family trails
    trails_category = Category.query.filter_by(name='trails').first()
    if trails_category:
        # See if we already have at least 5 trails that include 'family' in the name or description
        family_trail_count = POI.query.filter(
            POI.category_id == trails_category.id,
            (POI.name.ilike('%family%') | POI.description.ilike('%family%') | 
             POI.name.ilike('%child%') | POI.description.ilike('%child%') |
             POI.name.ilike('%kid%') | POI.description.ilike('%kid%'))
        ).count()
        
        if family_trail_count < 5:
            # Not enough family trails, add more
            try:
                from family_trails import add_family_trails_to_database
                added = add_family_trails_to_database()
                logging.info(f"Added {added} new family-friendly trails to database")
            except Exception as e:
                logging.error(f"Error adding family trails: {str(e)}")
    else:
        logging.warning("Trails category not found, can't add family trails")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Trail Enrichment Routes
@app.route('/enrich-trails', methods=['GET', 'POST'])
def enrich_trails_page():
    """Show the trail enrichment page."""
    from models import POI, Category
    from trail_enrichment import get_trails_without_descriptions
    
    trails = get_trails_without_descriptions()
    
    # Get stats for all trails
    trails_category = Category.query.filter_by(name="trails").first()
    stats = None
    
    if trails_category:
        total_trails = POI.query.filter_by(category_id=trails_category.id).count()
        trails_with_descriptions = POI.query.filter_by(category_id=trails_category.id).filter(
            POI.description.isnot(None), 
            POI.description != '',
            db.func.length(POI.description) >= 50
        ).count()
        
        stats = {
            "total": total_trails,
            "with_descriptions": trails_with_descriptions,
            "needs_descriptions": total_trails - trails_with_descriptions
        }
    
    # If POST request, process trails
    result = None
    if request.method == 'POST':
        try:
            from trail_enrichment import batch_enrich_trails
            
            limit = int(request.form.get('limit', 3))
            result = batch_enrich_trails(limit=limit)
            
            # Refresh the trails list after processing
            trails = get_trails_without_descriptions()
            
            flash('Trail data enrichment completed successfully!', 'success')
        except Exception as e:
            flash(f'Error enriching trail data: {str(e)}', 'error')
    
    return render_template('enrich_trails.html', trails=trails, stats=stats, result=result)

@app.route('/enrich-trail/<int:trail_id>', methods=['POST'])
def enrich_single_trail(trail_id):
    """Enrich a single trail's data."""
    try:
        from models import POI
        from trail_enrichment import enrich_trail_data
        
        # Get the trail
        trail = POI.query.get_or_404(trail_id)
        
        # Enrich the trail data
        success = enrich_trail_data(trail)
        
        if success:
            flash(f'Successfully enriched data for trail: {trail.name}', 'success')
        else:
            flash(f'Could not enrich data for trail: {trail.name}', 'error')
        
        return redirect(url_for('enrich_trails_page'))
    except Exception as e:
        flash(f'Error enriching trail data: {str(e)}', 'error')
        return redirect(url_for('enrich_trails_page'))
