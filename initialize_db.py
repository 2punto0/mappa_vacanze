from app import db
from models import Category, POI, Airbnb
import json
import re

def js_to_json(js_content):
    """Convert JavaScript object to JSON format for parsing"""
    # Replace single quotes with double quotes
    json_content = js_content.replace("'", '"')
    # Fix unquoted keys
    json_content = re.sub(r'([{,])\s*(\w+):', r'\1"\2":', json_content)
    return json_content

def populate_database():
    """Populate the database with initial data"""
    # Create categories
    categories = {
        'huts': Category(name='huts', display_name='Mountain Huts'),
        'trails': Category(name='trails', display_name='Family Hiking Trails'),
        'cableCars': Category(name='cableCars', display_name='Cable Cars'),
        'playgrounds': Category(name='playgrounds', display_name='Playgrounds'),
        'adventureParks': Category(name='adventureParks', display_name='Adventure Parks'),
        'bikeRentals': Category(name='bikeRentals', display_name='Bike Rentals'),
        'restaurants': Category(name='restaurants', display_name='Restaurants'),
        'nature': Category(name='nature', display_name='Lakes & Waterfalls'),
        'museums': Category(name='museums', display_name='Children\'s Museums')
    }
    
    # Add categories to session
    for category in categories.values():
        db.session.add(category)
    
    # Commit to get category IDs
    db.session.commit()
    
    # Manually add POIs from our previous data
    # First, let's add all POIs for each category

    # Mountain Huts
    add_huts(categories)
    
    # Hiking Trails
    add_trails(categories)
    
    # Cable Cars
    add_cable_cars(categories)
    
    # Playgrounds
    add_playgrounds(categories)
    
    # Adventure Parks
    add_adventure_parks(categories)
    
    # Bike Rentals
    add_bike_rentals(categories)
    
    # Restaurants
    add_restaurants(categories)
    
    # Lakes and Waterfalls
    add_nature(categories)
    
    # Museums
    add_museums(categories)
    
    # Add Airbnbs
    add_airbnbs()

def add_huts(categories):
    """Add mountain huts to the database"""
    huts = [
        {
            "name": "Rifugio Brentei",
            "lat": 46.1937,
            "lng": 10.8758,
            "description": "Family-friendly mountain hut in the Brenta Dolomites at 2182m",
            "url": "https://www.rifugiobrentei.it"
        },
        {
            "name": "Rifugio Graffer",
            "lat": 46.2233,
            "lng": 10.8592,
            "description": "Easy access hut at 2261m, perfect for families with children",
            "url": "https://www.dossdelSabion.it/rifugio-graffer/"
        },
        {
            "name": "Rifugio Tuckett",
            "lat": 46.1925,
            "lng": 10.8691,
            "description": "Historic mountain hut with panoramic views of the Brenta Dolomites",
            "url": "https://www.rifugiotuckett.it"
        },
        {
            "name": "Rifugio Capanna Presena",
            "lat": 46.2286,
            "lng": 10.5800,
            "description": "Accessible by cable car, spectacular views at 2730m",
            "url": "https://www.pontedilegnotonale.com/en/capanna-presena/"
        },
        {
            "name": "Rifugio Denza",
            "lat": 46.2336,
            "lng": 10.6465,
            "description": "Beautiful hut in Val di Sole with family-friendly trails",
            "url": "https://www.rifugiodenza.it"
        },
        {
            "name": "Rifugio Pian dei Fiacconi",
            "lat": 46.4420,
            "lng": 11.8587,
            "description": "Perfect starting point for Marmolada glacier explorations",
            "url": "https://www.piandeifiacconi.it"
        },
        {
            "name": "Rifugio Contrin",
            "lat": 46.4242,
            "lng": 11.8008,
            "description": "Easy access mountain hut ideal for families, great food",
            "url": "https://www.rifugiocontrin.it"
        },
        {
            "name": "Rifugio Monte Ferro",
            "lat": 46.5839,
            "lng": 12.7437,
            "description": "Panoramic views with easy hiking access from Sappada",
            "url": "https://www.rifugiomontefero.it"
        },
        {
            "name": "Rifugio Sorgenti del Piave",
            "lat": 46.6233,
            "lng": 12.5697,
            "description": "Historic hut at the source of the Piave river, easy trail",
            "url": "https://www.sappada.info/rifugio-sorgenti-del-piave/"
        }
    ]
    
    for hut_data in huts:
        hut = POI(
            name=hut_data["name"],
            lat=hut_data["lat"],
            lng=hut_data["lng"],
            description=hut_data.get("description", ""),
            url=hut_data.get("url", ""),
            category_id=categories["huts"].id
        )
        db.session.add(hut)

def add_trails(categories):
    """Add hiking trails to the database"""
    trails = [
        {
            "name": "Vallesinella Waterfall Trail",
            "lat": 46.2247,
            "lng": 10.8414,
            "description": "Easy 2.5km trail with beautiful waterfalls, perfect for families. Dog-friendly path.",
            "url": "https://www.visittrentino.info/en/experience/vallesinella-waterfalls",
            "path": [
                {"lat": 46.2247, "lng": 10.8414},
                {"lat": 46.2233, "lng": 10.8426},
                {"lat": 46.2215, "lng": 10.8443},
                {"lat": 46.2207, "lng": 10.8464},
                {"lat": 46.2199, "lng": 10.8483},
                {"lat": 46.2185, "lng": 10.8497}
            ]
        },
        {
            "name": "Lago Nambino Family Trail",
            "lat": 46.2361,
            "lng": 10.8107,
            "description": "Easy 1-hour circular walk around beautiful alpine lake with a restaurant.",
            "url": "https://www.visittrentino.info/en/experience/lake-nambino",
            "path": [
                {"lat": 46.2361, "lng": 10.8107},
                {"lat": 46.2373, "lng": 10.8093},
                {"lat": 46.2385, "lng": 10.8081},
                {"lat": 46.2386, "lng": 10.8105},
                {"lat": 46.2372, "lng": 10.8125},
                {"lat": 46.2361, "lng": 10.8107}
            ]
        },
        {
            "name": "Cinque Laghi Trail",
            "lat": 46.2433,
            "lng": 10.8297,
            "description": "Moderate 11km trail passing five stunning alpine lakes. Family-friendly with resting points.",
            "url": "https://www.campigliodolomiti.it/en/experience/five-lakes-hike",
            "path": [
                {"lat": 46.2433, "lng": 10.8297},
                {"lat": 46.2456, "lng": 10.8334},
                {"lat": 46.2469, "lng": 10.8375},
                {"lat": 46.2487, "lng": 10.8398},
                {"lat": 46.2502, "lng": 10.8423},
                {"lat": 46.2518, "lng": 10.8455},
                {"lat": 46.2522, "lng": 10.8476}
            ]
        },
        {
            "name": "Ritort Valley Family Trail",
            "lat": 46.2337,
            "lng": 10.8362,
            "description": "Easy 3.5km path through meadows and forest with panoramic views, suitable for all ages.",
            "url": "https://www.campigliodolomiti.it/en/activity/val-ritort-family-hike",
            "path": [
                {"lat": 46.2337, "lng": 10.8362},
                {"lat": 46.2349, "lng": 10.8379},
                {"lat": 46.2367, "lng": 10.8394},
                {"lat": 46.2381, "lng": 10.8421},
                {"lat": 46.2395, "lng": 10.8445}
            ]
        },
        {
            "name": "Sentiero dei Fiori",
            "lat": 46.2352,
            "lng": 10.5719,
            "description": "Historic high-altitude path with WWI remains and stunning views, accessible via cable car.",
            "url": "https://www.pontedilegnotonale.com/en/sentiero-dei-fiori-path-of-flowers",
            "path": [
                {"lat": 46.2352, "lng": 10.5719},
                {"lat": 46.2371, "lng": 10.5734},
                {"lat": 46.2397, "lng": 10.5751},
                {"lat": 46.2412, "lng": 10.5778},
                {"lat": 46.2425, "lng": 10.5802},
                {"lat": 46.2439, "lng": 10.5823}
            ]
        },
        {
            "name": "Val di Sole Family Walk",
            "lat": 46.3197,
            "lng": 10.6891,
            "description": "Easy 4km path along the Noce River with playgrounds and picnic areas.",
            "url": "https://www.valdisole.net/en/Family-Trails.html",
            "path": [
                {"lat": 46.3197, "lng": 10.6891},
                {"lat": 46.3212, "lng": 10.6922},
                {"lat": 46.3225, "lng": 10.6955},
                {"lat": 46.3246, "lng": 10.6984},
                {"lat": 46.3267, "lng": 10.7012}
            ]
        },
        {
            "name": "Lago dei Caprioli Trail",
            "lat": 46.2903,
            "lng": 10.7614,
            "description": "Easy lakeside trail with mountain views and wildlife spotting opportunities.",
            "url": "https://www.valdisole.net/en/Lago-dei-Caprioli.html",
            "path": [
                {"lat": 46.2903, "lng": 10.7614},
                {"lat": 46.2918, "lng": 10.7638},
                {"lat": 46.2932, "lng": 10.7662},
                {"lat": 46.2941, "lng": 10.7687},
                {"lat": 46.2935, "lng": 10.7711},
                {"lat": 46.2920, "lng": 10.7698},
                {"lat": 46.2908, "lng": 10.7675},
                {"lat": 46.2903, "lng": 10.7643},
                {"lat": 46.2903, "lng": 10.7614}
            ]
        },
        {
            "name": "Lago Fedaia Circuit",
            "lat": 46.4567,
            "lng": 11.8660,
            "description": "Easy family walk around Lago Fedaia with Marmolada views and rest areas.",
            "url": "https://www.dolomiti.it/en/marmolada/fedaia-lake",
            "path": [
                {"lat": 46.4567, "lng": 11.8660},
                {"lat": 46.4580, "lng": 11.8695},
                {"lat": 46.4589, "lng": 11.8744},
                {"lat": 46.4578, "lng": 11.8787},
                {"lat": 46.4559, "lng": 11.8748},
                {"lat": 46.4567, "lng": 11.8660}
            ]
        },
        {
            "name": "Serrai di Sottoguda Trail",
            "lat": 46.4182,
            "lng": 11.9040,
            "description": "Easy scenic gorge walk with waterfalls, suitable for families and children.",
            "url": "https://www.dolomiti.it/en/marmolada/serrai-di-sottoguda",
            "path": [
                {"lat": 46.4182, "lng": 11.9040},
                {"lat": 46.4192, "lng": 11.9066},
                {"lat": 46.4203, "lng": 11.9084},
                {"lat": 46.4215, "lng": 11.9102},
                {"lat": 46.4230, "lng": 11.9118}
            ]
        },
        {
            "name": "Arabba Alpine Meadows Trail",
            "lat": 46.4982,
            "lng": 11.8662,
            "description": "Moderate 6km circular trail through meadows with spectacular Dolomites views.",
            "url": "https://www.dolomiti.it/en/arabba/summer-hiking",
            "path": [
                {"lat": 46.4982, "lng": 11.8662},
                {"lat": 46.4997, "lng": 11.8688},
                {"lat": 46.5014, "lng": 11.8713},
                {"lat": 46.5025, "lng": 11.8752},
                {"lat": 46.5015, "lng": 11.8788},
                {"lat": 46.4998, "lng": 11.8762},
                {"lat": 46.4984, "lng": 11.8722},
                {"lat": 46.4982, "lng": 11.8662}
            ]
        },
        {
            "name": "Mulini di Sappada Trail",
            "lat": 46.5690,
            "lng": 12.6915,
            "description": "Easy historical walk to discover Sappada's ancient mills, ideal for families with children.",
            "url": "https://www.sappada.info/en/activity/ancient-mills-trail",
            "path": [
                {"lat": 46.5690, "lng": 12.6915},
                {"lat": 46.5705, "lng": 12.6936},
                {"lat": 46.5721, "lng": 12.6962},
                {"lat": 46.5736, "lng": 12.7001},
                {"lat": 46.5751, "lng": 12.7032}
            ]
        },
        {
            "name": "Piani del Cristo Family Loop",
            "lat": 46.5826,
            "lng": 12.7065,
            "description": "Easy 3km circular trail through alpine meadows with playgrounds and picnic areas.",
            "url": "https://www.sappada.info/en/activity/piani-del-cristo-family-trail",
            "path": [
                {"lat": 46.5826, "lng": 12.7065},
                {"lat": 46.5842, "lng": 12.7089},
                {"lat": 46.5862, "lng": 12.7095},
                {"lat": 46.5878, "lng": 12.7082},
                {"lat": 46.5871, "lng": 12.7062},
                {"lat": 46.5853, "lng": 12.7055},
                {"lat": 46.5838, "lng": 12.7061},
                {"lat": 46.5826, "lng": 12.7065}
            ]
        },
        {
            "name": "Sorgenti del Piave Path",
            "lat": 46.6203,
            "lng": 12.5739,
            "description": "Easy 2km educational trail to the source of the Piave river with information boards.",
            "url": "https://www.sappada.info/en/activity/piave-river-source-trail",
            "path": [
                {"lat": 46.6203, "lng": 12.5739},
                {"lat": 46.6219, "lng": 12.5718},
                {"lat": 46.6233, "lng": 12.5697},
                {"lat": 46.6248, "lng": 12.5677},
                {"lat": 46.6259, "lng": 12.5653}
            ]
        }
    ]
    
    for trail_data in trails:
        trail = POI(
            name=trail_data["name"],
            lat=trail_data["lat"],
            lng=trail_data["lng"],
            description=trail_data.get("description", ""),
            url=trail_data.get("url", ""),
            category_id=categories["trails"].id,
            path=trail_data.get("path")
        )
        db.session.add(trail)

def add_cable_cars(categories):
    """Add cable cars to the database"""
    cable_cars = [
        {
            "name": "Cabinovia Grostè",
            "lat": 46.2313,
            "lng": 10.8371,
            "description": "Access to spectacular viewpoints and easy hiking trails",
            "url": "https://www.campigliodolomiti.it/en/article/detail/cabinovia-grosté"
        },
        {
            "name": "Cabinovia Spinale",
            "lat": 46.2306,
            "lng": 10.8261,
            "description": "Easy access to Rifugio Graffer and panoramic views",
            "url": "https://www.campigliodolomiti.it/en/article/detail/cabinovia-spinale"
        },
        {
            "name": "Funivia Paradiso",
            "lat": 46.2593,
            "lng": 10.5825,
            "description": "Access to Presena Glacier and family-friendly summer activities",
            "url": "https://www.pontedilegnotonale.com/en/paradiso-cable-car/"
        },
        {
            "name": "Funivia Marmolada",
            "lat": 46.4336,
            "lng": 11.8503,
            "description": "Italy's highest cable car to Punta Rocca (3265m), breathtaking views",
            "url": "https://www.funiviamarmolada.com"
        },
        {
            "name": "Seggiovia Sappada 2000",
            "lat": 46.5800,
            "lng": 12.6908,
            "description": "Access to alpine meadows and panoramic hiking trails",
            "url": "https://www.sappada.info/seggiovia-sappada-2000/"
        }
    ]
    
    for cable_car_data in cable_cars:
        cable_car = POI(
            name=cable_car_data["name"],
            lat=cable_car_data["lat"],
            lng=cable_car_data["lng"],
            description=cable_car_data.get("description", ""),
            url=cable_car_data.get("url", ""),
            category_id=categories["cableCars"].id
        )
        db.session.add(cable_car)

def add_playgrounds(categories):
    """Add playgrounds to the database"""
    playgrounds = [
        {
            "name": "Parco Giochi Campiglio",
            "lat": 46.2293,
            "lng": 10.8265,
            "description": "Central playground with swings, slides and climbing structures",
            "url": "https://www.campigliodolomiti.it"
        },
        {
            "name": "Family Park Spinale",
            "lat": 46.2366,
            "lng": 10.8217,
            "description": "High-altitude playground accessible via Spinale cable car",
            "url": "https://www.campigliodolomiti.it/en/family"
        },
        {
            "name": "Fantaski Summer Park",
            "lat": 46.2628,
            "lng": 10.5882,
            "description": "Summer activities for children including trampolines and games",
            "url": "https://www.pontedilegnotonale.com/en/fantaski-park/"
        },
        {
            "name": "Nevelandia Summer",
            "lat": 46.5781,
            "lng": 12.6925,
            "description": "Summer version of Nevelandia with tubing and activities for kids",
            "url": "https://www.sappada.info/nevelandia/"
        }
    ]
    
    for playground_data in playgrounds:
        playground = POI(
            name=playground_data["name"],
            lat=playground_data["lat"],
            lng=playground_data["lng"],
            description=playground_data.get("description", ""),
            url=playground_data.get("url", ""),
            category_id=categories["playgrounds"].id
        )
        db.session.add(playground)

def add_adventure_parks(categories):
    """Add adventure parks to the database"""
    adventure_parks = [
        {
            "name": "Flying Park",
            "lat": 46.2248,
            "lng": 10.8414,
            "description": "Treetop adventure park with ziplines and rope courses for all ages",
            "url": "https://www.campigliodolomiti.it/en/article/detail/flying-park-madonna-di-campiglio"
        },
        {
            "name": "Adventure Dolomiti",
            "lat": 46.4252,
            "lng": 11.7744,
            "description": "Family-friendly adventure park with courses for children 4+ years",
            "url": "https://www.adventuredolomiti.it"
        },
        {
            "name": "Sappada Adventure Park",
            "lat": 46.5697,
            "lng": 12.6978,
            "description": "Rope courses and ziplines for different ability levels",
            "url": "https://www.sappadaadventurepark.it"
        }
    ]
    
    for adventure_park_data in adventure_parks:
        adventure_park = POI(
            name=adventure_park_data["name"],
            lat=adventure_park_data["lat"],
            lng=adventure_park_data["lng"],
            description=adventure_park_data.get("description", ""),
            url=adventure_park_data.get("url", ""),
            category_id=categories["adventureParks"].id
        )
        db.session.add(adventure_park)

def add_bike_rentals(categories):
    """Add bike rentals to the database"""
    bike_rentals = [
        {
            "name": "Noleggio Bici Campiglio",
            "lat": 46.2314,
            "lng": 10.8264,
            "description": "Bike and e-bike rental in central Madonna di Campiglio",
            "url": "https://www.noleggiodicampiglio.it"
        },
        {
            "name": "Rent Bike Val di Sole",
            "lat": 46.3164,
            "lng": 10.8250,
            "description": "E-bikes and mountain bikes for family rides on cycling paths",
            "url": "https://www.rentbikevaldisole.it"
        },
        {
            "name": "Noleggio Mountain Bike Sappada",
            "lat": 46.5702,
            "lng": 12.7063,
            "description": "Bike rental with child seats and trailers available",
            "url": "https://www.sappadabike.it"
        }
    ]
    
    for bike_rental_data in bike_rentals:
        bike_rental = POI(
            name=bike_rental_data["name"],
            lat=bike_rental_data["lat"],
            lng=bike_rental_data["lng"],
            description=bike_rental_data.get("description", ""),
            url=bike_rental_data.get("url", ""),
            category_id=categories["bikeRentals"].id
        )
        db.session.add(bike_rental)

def add_restaurants(categories):
    """Add restaurants to the database"""
    restaurants = [
        {
            "name": "Malga Ritorto",
            "lat": 46.2271,
            "lng": 10.8132,
            "description": "Authentic mountain restaurant with panoramic terrace and local cuisine",
            "url": "https://www.malgaritorto.it"
        },
        {
            "name": "Chalet Fiat",
            "lat": 46.2375,
            "lng": 10.8216,
            "description": "Family-friendly restaurant with playground and stunning views",
            "url": "https://www.campigliodolomiti.it/en/article/detail/chalet-fiat"
        },
        {
            "name": "Ristorante Paradiso",
            "lat": 46.2294,
            "lng": 10.5801,
            "description": "High-altitude restaurant with kid's menu and glacier views",
            "url": "https://www.pontedilegnotonale.com/en/restaurant-paradiso/"
        },
        {
            "name": "Rifugio Padon",
            "lat": 46.4497,
            "lng": 11.8739,
            "description": "Family-friendly mountain restaurant with traditional cuisine",
            "url": "https://www.rifugiopadon.it"
        },
        {
            "name": "Baita Mondschein",
            "lat": 46.5852,
            "lng": 12.6976,
            "description": "Traditional Alpine cuisine with kids play area and mountain views",
            "url": "https://www.baitamondschein.it"
        }
    ]
    
    for restaurant_data in restaurants:
        restaurant = POI(
            name=restaurant_data["name"],
            lat=restaurant_data["lat"],
            lng=restaurant_data["lng"],
            description=restaurant_data.get("description", ""),
            url=restaurant_data.get("url", ""),
            category_id=categories["restaurants"].id
        )
        db.session.add(restaurant)

def add_nature(categories):
    """Add lakes and waterfalls to the database"""
    nature_spots = [
        {
            "name": "Cascata Nardis",
            "lat": 46.1875,
            "lng": 10.7779,
            "description": "Impressive 130m waterfall in Val Genova, easy access path",
            "url": "https://www.campigliodolomiti.it/en/article/detail/nardis-waterfall"
        },
        {
            "name": "Lago di Nambino",
            "lat": 46.2361,
            "lng": 10.8107,
            "description": "Picturesque alpine lake with easy walking trail and restaurant",
            "url": "https://www.campigliodolomiti.it/en/article/detail/lake-nambino"
        },
        {
            "name": "Lago di Fedaia",
            "lat": 46.4567,
            "lng": 11.8660,
            "description": "Beautiful lake at the foot of Marmolada with family-friendly path",
            "url": "https://www.marmolada.com/en/lake-fedaia/"
        },
        {
            "name": "Cascate del Saent",
            "lat": 46.3689,
            "lng": 10.6903,
            "description": "Series of beautiful waterfalls with observation platforms",
            "url": "https://www.valdisole.net/en/Waterfalls-Saent.html"
        },
        {
            "name": "Sorgenti del Piave",
            "lat": 46.6228,
            "lng": 12.5686,
            "description": "Source of the Piave river with educational trail and picnic area",
            "url": "https://www.sappada.info/sorgenti-del-piave/"
        }
    ]
    
    for nature_data in nature_spots:
        nature = POI(
            name=nature_data["name"],
            lat=nature_data["lat"],
            lng=nature_data["lng"],
            description=nature_data.get("description", ""),
            url=nature_data.get("url", ""),
            category_id=categories["nature"].id
        )
        db.session.add(nature)

def add_museums(categories):
    """Add museums to the database"""
    museums = [
        {
            "name": "MUSE Trento",
            "lat": 46.0618,
            "lng": 11.1166,
            "description": "Interactive science museum with special activities for children",
            "url": "https://www.muse.it/en/"
        },
        {
            "name": "Museo Ladino di Fassa",
            "lat": 46.4184,
            "lng": 11.7182,
            "description": "Cultural museum with exhibits on local traditions and folklore",
            "url": "https://www.istladin.net/en/museo-ladino-di-fassa"
        },
        {
            "name": "Museo Etnografico Sappada",
            "lat": 46.5694,
            "lng": 12.7076,
            "description": "Museum showcasing traditional mountain life with interactive exhibits",
            "url": "https://www.sappada.info/museo-etnografico/"
        },
        {
            "name": "Museo della Guerra Bianca",
            "lat": 46.3024,
            "lng": 10.5639,
            "description": "Museum about World War I in the Alps with kid-friendly exhibits",
            "url": "https://www.museoguerrabianca.it"
        }
    ]
    
    for museum_data in museums:
        museum = POI(
            name=museum_data["name"],
            lat=museum_data["lat"],
            lng=museum_data["lng"],
            description=museum_data.get("description", ""),
            url=museum_data.get("url", ""),
            category_id=categories["museums"].id
        )
        db.session.add(museum)

def add_airbnbs():
    """Add Airbnb listings to the database"""
    airbnbs = [
        {
            "name": "Mountain View Apartment",
            "lat": 46.2302,
            "lng": 10.8248,
            "price": 120,
            "description": "Cozy 2-bedroom apartment in the heart of Madonna di Campiglio",
            "url": "https://www.airbnb.com/rooms/12345",
            "bedrooms": 2,
            "image_url": "https://images.unsplash.com/photo-1568605114967-8130f3a36994"
        },
        {
            "name": "Alpine Family Chalet",
            "lat": 46.2328,
            "lng": 10.8294,
            "price": 180,
            "description": "Spacious 3-bedroom chalet with garden, perfect for families",
            "url": "https://www.airbnb.com/rooms/23456",
            "bedrooms": 3,
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750"
        },
        {
            "name": "Dolomites Panorama Loft",
            "lat": 46.2356,
            "lng": 10.8164,
            "price": 150,
            "description": "Modern 2-bedroom loft with breathtaking mountain views",
            "url": "https://www.airbnb.com/rooms/34567",
            "bedrooms": 2,
            "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9"
        },
        {
            "name": "Passo del Tonale Ski Apartment",
            "lat": 46.2632,
            "lng": 10.5841,
            "price": 95,
            "description": "Convenient 1-bedroom apartment near lifts and family activities",
            "url": "https://www.airbnb.com/rooms/45678",
            "bedrooms": 1,
            "image_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c"
        },
        {
            "name": "Tonale Family Lodge",
            "lat": 46.2653,
            "lng": 10.5903,
            "price": 140,
            "description": "Comfortable 2-bedroom apartment with children's play area",
            "url": "https://www.airbnb.com/rooms/56789",
            "bedrooms": 2,
            "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3"
        },
        {
            "name": "Marmolada View Suite",
            "lat": 46.4502,
            "lng": 11.8473,
            "price": 130,
            "description": "Elegant 2-bedroom apartment with stunning glacier views",
            "url": "https://www.airbnb.com/rooms/67890",
            "bedrooms": 2,
            "image_url": "https://images.unsplash.com/photo-1600210492493-0946911123ea"
        },
        {
            "name": "Arabba Mountain Retreat",
            "lat": 46.4962,
            "lng": 11.8724,
            "price": 165,
            "description": "Traditional 3-bedroom chalet with modern amenities, child-friendly",
            "url": "https://www.airbnb.com/rooms/78901",
            "bedrooms": 3,
            "image_url": "https://images.unsplash.com/photo-1575517111839-3a3843ee7f5d"
        },
        {
            "name": "Sappada Family House",
            "lat": 46.5701,
            "lng": 12.7089,
            "price": 120,
            "description": "Historic 2-bedroom Sappadino house in the village center",
            "url": "https://www.airbnb.com/rooms/89012",
            "bedrooms": 2,
            "image_url": "https://images.unsplash.com/photo-1518780664697-55e3ad937233"
        },
        {
            "name": "Alpine Meadows Cabin",
            "lat": 46.5769,
            "lng": 12.6945,
            "price": 110,
            "description": "Rustic 1-bedroom cabin with garden, ideal for families with children",
            "url": "https://www.airbnb.com/rooms/90123",
            "bedrooms": 1,
            "image_url": "https://images.unsplash.com/photo-1556912998-c57cc6b63cd7"
        },
        {
            "name": "Dolomites Family Penthouse",
            "lat": 46.3524,
            "lng": 11.7736,
            "price": 190,
            "description": "Luxury 3-bedroom penthouse in Val di Fassa with children's facilities",
            "url": "https://www.airbnb.com/rooms/01234",
            "bedrooms": 3,
            "image_url": "https://images.unsplash.com/photo-1480074568708-e7b720bb3f09"
        }
    ]
    
    for airbnb_data in airbnbs:
        airbnb = Airbnb(
            name=airbnb_data["name"],
            lat=airbnb_data["lat"],
            lng=airbnb_data["lng"],
            price=airbnb_data.get("price", 0),
            description=airbnb_data.get("description", ""),
            url=airbnb_data.get("url", ""),
            bedrooms=airbnb_data.get("bedrooms", 0),
            image_url=airbnb_data.get("image_url", "")
        )
        db.session.add(airbnb)

if __name__ == '__main__':
    # This can be run standalone to initialize the database
    from app import app
    with app.app_context():
        populate_database()
        db.session.commit()
        print("Database populated successfully!")
