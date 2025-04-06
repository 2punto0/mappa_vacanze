from app import app, db
from models import POI, Category
import json

def add_additional_trails():
    """Add additional trekking trails to the database"""
    with app.app_context():
        # Get the trails category
        trails_category = Category.query.filter_by(name='trails').first()
        if not trails_category:
            print("Trails category not found!")
            return
        
        # Additional trails to add
        additional_trails = [
            {
                "name": "Alta Via dell'Adamello",
                "lat": 46.1687,
                "lng": 10.7248,
                "description": "Epic long-distance trekking route across the Adamello mountain range. Can be split into shorter day hikes for families.",
                "url": "https://www.visittrentino.info/en/experience/alta-via-dell-adamello",
                "path": [
                    {"lat": 46.1687, "lng": 10.7248},
                    {"lat": 46.1703, "lng": 10.7279},
                    {"lat": 46.1732, "lng": 10.7312},
                    {"lat": 46.1763, "lng": 10.7341},
                    {"lat": 46.1796, "lng": 10.7386},
                    {"lat": 46.1821, "lng": 10.7412}
                ]
            },
            {
                "name": "Giro del Sassolungo",
                "lat": 46.5152,
                "lng": 11.7391,
                "description": "Spectacular circular trek around the Sassolungo massif with stunning Dolomites views. Moderate difficulty, suitable for families with older children.",
                "url": "https://www.valgardena.it/en/summer-holidays/hiking-climbing/hiking-tours/detail/giro-del-sassolungo/",
                "path": [
                    {"lat": 46.5152, "lng": 11.7391},
                    {"lat": 46.5177, "lng": 11.7425},
                    {"lat": 46.5209, "lng": 11.7467},
                    {"lat": 46.5238, "lng": 11.7489},
                    {"lat": 46.5271, "lng": 11.7473},
                    {"lat": 46.5302, "lng": 11.7453},
                    {"lat": 46.5329, "lng": 11.7408},
                    {"lat": 46.5317, "lng": 11.7363},
                    {"lat": 46.5285, "lng": 11.7321},
                    {"lat": 46.5248, "lng": 11.7306},
                    {"lat": 46.5209, "lng": 11.7328},
                    {"lat": 46.5171, "lng": 11.7359},
                    {"lat": 46.5152, "lng": 11.7391}
                ]
            },
            {
                "name": "Alpe di Siusi Family Trail",
                "lat": 46.5505,
                "lng": 11.6279,
                "description": "Easy trail across Europe's largest alpine plateau. Perfect for families with young children, with multiple playgrounds and rest areas.",
                "url": "https://www.seiseralm.it/en/summer/hiking/hiking-with-children.html",
                "path": [
                    {"lat": 46.5505, "lng": 11.6279},
                    {"lat": 46.5519, "lng": 11.6317},
                    {"lat": 46.5538, "lng": 11.6358},
                    {"lat": 46.5563, "lng": 11.6391},
                    {"lat": 46.5583, "lng": 11.6426},
                    {"lat": 46.5597, "lng": 11.6468},
                    {"lat": 46.5589, "lng": 11.6511},
                    {"lat": 46.5567, "lng": 11.6534},
                    {"lat": 46.5541, "lng": 11.6517},
                    {"lat": 46.5523, "lng": 11.6485},
                    {"lat": 46.5506, "lng": 11.6443},
                    {"lat": 46.5499, "lng": 11.6392},
                    {"lat": 46.5497, "lng": 11.6338},
                    {"lat": 46.5505, "lng": 11.6279}
                ]
            },
            {
                "name": "Tre Cime di Lavaredo Circuit",
                "lat": 46.6153,
                "lng": 12.3026,
                "description": "Iconic circular hike around the famous three peaks of the Dolomites. Moderate route with spectacular views, suitable for families with children who are regular hikers.",
                "url": "https://www.dolomiti.org/en/cortina/summer/trekking/tre-cime-di-lavaredo/",
                "path": [
                    {"lat": 46.6153, "lng": 12.3026},
                    {"lat": 46.6179, "lng": 12.3053},
                    {"lat": 46.6211, "lng": 12.3089},
                    {"lat": 46.6243, "lng": 12.3103},
                    {"lat": 46.6276, "lng": 12.3074},
                    {"lat": 46.6295, "lng": 12.3028},
                    {"lat": 46.6312, "lng": 12.2979},
                    {"lat": 46.6325, "lng": 12.2921},
                    {"lat": 46.6305, "lng": 12.2871},
                    {"lat": 46.6276, "lng": 12.2836},
                    {"lat": 46.6241, "lng": 12.2814},
                    {"lat": 46.6209, "lng": 12.2843},
                    {"lat": 46.6183, "lng": 12.2889},
                    {"lat": 46.6164, "lng": 12.2943},
                    {"lat": 46.6153, "lng": 12.3026}
                ]
            },
            {
                "name": "Val Venegia Family Path",
                "lat": 46.3357,
                "lng": 11.8173,
                "description": "Easy panoramic trail through beautiful alpine meadows at the base of the Pale di San Martino. Perfect for families with young children.",
                "url": "https://www.visittrentino.info/en/experience/val-venegia",
                "path": [
                    {"lat": 46.3357, "lng": 11.8173},
                    {"lat": 46.3375, "lng": 11.8201},
                    {"lat": 46.3392, "lng": 11.8234},
                    {"lat": 46.3416, "lng": 11.8267},
                    {"lat": 46.3435, "lng": 11.8301},
                    {"lat": 46.3458, "lng": 11.8328},
                    {"lat": 46.3483, "lng": 11.8349}
                ]
            },
            {
                "name": "Lago di Carezza Trail",
                "lat": 46.4116,
                "lng": 11.5755,
                "description": "Easy family walk around the magical rainbow lake with stunning Latemar mountain views. Wooden walkways make it accessible even for strollers.",
                "url": "https://www.suedtirol.info/en/experiences/lake-carezza",
                "path": [
                    {"lat": 46.4116, "lng": 11.5755},
                    {"lat": 46.4125, "lng": 11.5767},
                    {"lat": 46.4132, "lng": 11.5786},
                    {"lat": 46.4137, "lng": 11.5812},
                    {"lat": 46.4133, "lng": 11.5836},
                    {"lat": 46.4126, "lng": 11.5852},
                    {"lat": 46.4116, "lng": 11.5857},
                    {"lat": 46.4106, "lng": 11.5845},
                    {"lat": 46.4101, "lng": 11.5824},
                    {"lat": 46.4102, "lng": 11.5796},
                    {"lat": 46.4109, "lng": 11.5773},
                    {"lat": 46.4116, "lng": 11.5755}
                ]
            }
        ]
        
        # Add trails to database
        for trail_data in additional_trails:
            trail = POI(
                name=trail_data["name"],
                lat=trail_data["lat"],
                lng=trail_data["lng"],
                description=trail_data["description"],
                url=trail_data["url"],
                category_id=trails_category.id,
                path=trail_data["path"]
            )
            db.session.add(trail)
        
        # Update existing trail URLs
        update_urls = {
            "Vallesinella Waterfall Trail": "https://www.campigliodolomiti.it/en/article/detail/vallesinella-waterfalls",
            "Lago Nambino Family Trail": "https://www.campigliodolomiti.it/en/article/detail/lake-nambino",
            "Cinque Laghi Trail": "https://www.campigliodolomiti.it/en/excursion/five-lakes-hike",
            "Ritort Valley Family Trail": "https://www.campigliodolomiti.it/en/activity/val-ritort-family-hike",
            "Sentiero dei Fiori": "https://www.pontedilegnotonale.com/en/hiking-path-sentiero-dei-fiori/",
            "Val di Sole Family Walk": "https://www.valdisole.net/en/Family-hikes.html",
            "Lago dei Caprioli Trail": "https://www.valdisole.net/en/Lakes-in-Val-di-Sole.html",
            "Lago Fedaia Circuit": "https://www.dolomiti.it/en/destinations/marmolada/lake-fedaia",
            "Serrai di Sottoguda Trail": "https://www.dolomiti.it/en/destinations/marmolada/serrai-di-sottoguda",
            "Arabba Alpine Meadows Trail": "https://www.dolomiti.it/en/destinations/arabba/summer-hiking",
            "Mulini di Sappada Trail": "https://www.sappada.info/en/summer/hiking/ancient-mills-path/",
            "Piani del Cristo Family Loop": "https://www.sappada.info/en/summer/hiking/piani-del-cristo/",
            "Sorgenti del Piave Path": "https://www.sappada.info/en/summer/hiking/source-of-the-piave-river/"
        }
        
        for trail_name, new_url in update_urls.items():
            trail = POI.query.filter_by(name=trail_name).first()
            if trail:
                trail.url = new_url
        
        # Commit changes
        db.session.commit()
        print("Added additional trails and updated URLs successfully!")

if __name__ == "__main__":
    add_additional_trails()
