document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map
    const map = L.map('map', {
        center: [46.4, 11.9], // Centered on Trentino/Friuli
        zoom: 10,
        zoomControl: false // We'll add it to the top-right later
    });

    // Add zoom control to the top right
    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    // Add basemap layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Create layer groups - add all to the map by default
    const layerGroups = {
        airbnbs: L.layerGroup().addTo(map),
        huts: L.layerGroup().addTo(map),
        trails: L.layerGroup().addTo(map),
        cableCars: L.layerGroup().addTo(map),
        playgrounds: L.layerGroup().addTo(map),
        adventureParks: L.layerGroup().addTo(map),
        bikeRentals: L.layerGroup().addTo(map),
        restaurants: L.layerGroup().addTo(map),
        nature: L.layerGroup().addTo(map),
        museums: L.layerGroup().addTo(map),
        userLocation: L.layerGroup().addTo(map) // New layer for user location
    };

    // Custom icons for markers
    const createCustomIcon = (iconClass, color, size = [25, 25]) => {
        return L.divIcon({
            className: `custom-marker ${color}`,
            html: `<i class="${iconClass}"></i>`,
            iconSize: size,
            iconAnchor: [size[0]/2, size[0]/2],
            popupAnchor: [0, -size[0]/2]
        });
    };

    // Icon definitions
    const icons = {
        airbnb: createCustomIcon('fas fa-home', 'airbnb-marker', [35, 35]),
        hut: createCustomIcon('fas fa-mountain', 'hut-marker'),
        trail: createCustomIcon('fas fa-hiking', 'trail-marker'),
        cableCar: createCustomIcon('fas fa-tram', 'cable-marker'),
        playground: createCustomIcon('fas fa-child', 'playground-marker'),
        adventurePark: createCustomIcon('fas fa-tree', 'adventure-marker'),
        bikeRental: createCustomIcon('fas fa-bicycle', 'bike-marker'),
        restaurant: createCustomIcon('fas fa-utensils', 'restaurant-marker'),
        nature: createCustomIcon('fas fa-binoculars', 'nature-marker'),
        museum: createCustomIcon('fas fa-landmark', 'museum-marker'),
        userLocation: createCustomIcon('fas fa-map-marker-alt', 'user-location-marker', [35, 35])
    };

    // Map category names to icon types
    const categoryToIconType = {
        'huts': 'hut',
        'trails': 'trail',
        'cableCars': 'cableCar',
        'playgrounds': 'playground',
        'adventureParks': 'adventurePark',
        'bikeRentals': 'bikeRental',
        'restaurants': 'restaurant',
        'nature': 'nature',
        'museums': 'museum'
    };

    // Map category names to marker types for popup text
    const categoryToMarkerType = {
        'huts': 'hut',
        'trails': 'trail',
        'cableCars': 'cableCar',
        'playgrounds': 'playground',
        'adventureParks': 'adventurePark',
        'bikeRentals': 'bikeRental',
        'restaurants': 'restaurant',
        'nature': 'nature',
        'museums': 'museum'
    };

    // Create popups for markers
    const createPopup = (item, type) => {
        let popupContent = `<div class="popup-content">
            <div class="popup-title">${item.name}</div>`;
        
        if (item.description) {
            popupContent += `<div class="popup-info">${item.description}</div>`;
        }
        
        // Add difficulty rating for trails
        if (type === 'trail') {
            let difficultyStars = '';
            const ratingValue = item.difficulty_rating || 0;
            const fullStars = Math.floor(ratingValue);
            
            // Create hiking boot icons for ratings
            for (let i = 0; i < 5; i++) {
                if (i < fullStars) {
                    difficultyStars += '<i class="fas fa-hiking"></i>'; // Full hiking boot
                } else {
                    difficultyStars += '<i class="far fa-hiking"></i>'; // Empty hiking boot
                }
            }
            
            const ratingText = item.rating_count 
                ? `${ratingValue} / 5 difficulty (${item.rating_count} ratings)` 
                : 'Not rated yet';
            
            popupContent += `
            <div class="trail-difficulty">
                <div class="difficulty-rating">
                    <span class="difficulty-label">Difficulty: </span>
                    <span class="difficulty-stars">${difficultyStars}</span>
                    <span class="rating-value">${ratingText}</span>
                </div>
                <a href="/rate-trail/${item.id}" class="rate-trail-btn">Rate This Trail</a>
            </div>`;
        }
        
        // Add source information based on type
        let sourceText = '';
        if (type === 'trail') {
            sourceText = 'Hiking information source: ';
        } else if (type === 'hut') {
            sourceText = 'Mountain hut information: ';
        } else if (type === 'cableCar') {
            sourceText = 'Cable car information: ';
        } else if (type === 'nature') {
            sourceText = 'Natural attraction information: ';
        } else if (type === 'museum') {
            sourceText = 'Museum information: ';
        } else if (type === 'restaurant') {
            sourceText = 'Restaurant information: ';
        } else if (type === 'adventurePark') {
            sourceText = 'Adventure park information: ';
        } else if (type === 'playground') {
            sourceText = 'Playground information: ';
        } else if (type === 'bikeRental') {
            sourceText = 'Bike rental information: ';
        } else if (type === 'airbnb') {
            sourceText = 'Find similar accommodations: ';
        }
        
        if (item.url) {
            popupContent += `<div class="popup-source">${sourceText}</div>
            <a href="${item.url}" target="_blank" class="popup-link"><i class="fas fa-external-link-alt"></i> ${type === 'airbnb' ? 'Search Airbnb in this area' : 'Visit Official Website'}</a>`;
        }
        
        popupContent += `</div>`;
        
        return popupContent;
    };

    // Add markers to layers with hover effect
    const addMarkers = (data, layerGroup, icon, type) => {
        data.forEach(item => {
            const marker = L.marker([item.lat, item.lng], { icon: icon })
                .bindPopup(createPopup(item, type));
            
            // Add hover effects
            marker.on('mouseover', function() {
                this._icon.classList.add('highlight-marker');
                this.openPopup();
            });
            
            marker.on('mouseout', function() {
                this._icon.classList.remove('highlight-marker');
            });
            
            marker.addTo(layerGroup);
        });
    };

    // Handle layer toggles
    document.querySelectorAll('.layer-toggle input[type="checkbox"]').forEach(checkbox => {
        // Set all checkboxes to checked by default
        checkbox.checked = true;
        
        checkbox.addEventListener('change', function() {
            const layerName = this.getAttribute('data-layer');
            if (this.checked) {
                layerGroups[layerName].addTo(map);
            } else {
                map.removeLayer(layerGroups[layerName]);
            }
        });
    });

    // Reset view button
    document.getElementById('reset-view').addEventListener('click', function() {
        map.setView([46.4, 11.9], 10);
    });

    // User location variables
    let userLocationMarker = null;
    let userLocationCircle = null;
    let isLocating = false;
    let followingLocation = false;

    // Create geolocation control
    const createLocationControl = () => {
        const locationControl = L.Control.extend({
            options: {
                position: 'topright'
            },
            onAdd: function() {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                const locationButton = L.DomUtil.create('a', 'location-button', container);
                locationButton.href = '#';
                locationButton.title = 'Show my location';
                locationButton.innerHTML = '<i class="fas fa-location-arrow"></i>';
                locationButton.id = 'location-button';
                
                L.DomEvent.on(locationButton, 'click', function(e) {
                    L.DomEvent.preventDefault(e);
                    toggleLocationTracking();
                });
                
                return container;
            }
        });
        
        return new locationControl();
    };

    // Add location control to map
    const locationControl = createLocationControl();
    locationControl.addTo(map);

    // Toggle location tracking
    const toggleLocationTracking = () => {
        const locationButton = document.getElementById('location-button');
        
        if (!isLocating) {
            // Start locating
            isLocating = true;
            followingLocation = true;
            locationButton.classList.add('active');
            map.locate({
                watch: true,
                setView: true,
                maxZoom: 16,
                enableHighAccuracy: true
            });
            showLocationSearchingIndicator();
        } else {
            // Stop locating
            isLocating = false;
            followingLocation = false;
            locationButton.classList.remove('active');
            map.stopLocate();
            hideLocationMarker();
            hideLocationSearchingIndicator();
        }
    };

    // Show location "searching" indicator
    const showLocationSearchingIndicator = () => {
        const locationButton = document.getElementById('location-button');
        locationButton.classList.add('searching');
    };

    // Hide location "searching" indicator
    const hideLocationSearchingIndicator = () => {
        const locationButton = document.getElementById('location-button');
        locationButton.classList.remove('searching');
    };

    // Update user location marker
    const updateLocationMarker = (e) => {
        const radius = e.accuracy / 2;
        
        // If first-time location found or marker doesn't exist
        if (!userLocationMarker) {
            // Create marker
            userLocationMarker = L.marker(e.latlng, {
                icon: L.divIcon({
                    className: 'user-location-marker',
                    html: '<div class="user-location-icon"></div>',
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                })
            }).addTo(layerGroups.userLocation);
            
            // Create accuracy circle
            userLocationCircle = L.circle(e.latlng, {
                radius: radius,
                weight: 2,
                color: '#4285F4',
                fillColor: '#4285F4',
                fillOpacity: 0.15
            }).addTo(layerGroups.userLocation);
            
            // Bind popup
            userLocationMarker.bindPopup('You are within ' + Math.round(radius) + ' meters from this point');
        } else {
            // Update existing marker and circle
            userLocationMarker.setLatLng(e.latlng);
            userLocationCircle.setLatLng(e.latlng);
            userLocationCircle.setRadius(radius);
            userLocationMarker.setPopupContent('You are within ' + Math.round(radius) + ' meters from this point');
        }
        
        // Hide searching indicator once location is found
        hideLocationSearchingIndicator();
    };

    // Hide user location marker and circle
    const hideLocationMarker = () => {
        if (userLocationMarker) {
            layerGroups.userLocation.clearLayers();
            userLocationMarker = null;
            userLocationCircle = null;
        }
    };

    // Location found event handler
    map.on('locationfound', function(e) {
        updateLocationMarker(e);
        
        // Set view to user's location if following
        if (followingLocation) {
            map.setView(e.latlng);
        }
    });

    // Location error event handler
    map.on('locationerror', function(e) {
        console.error('Location error:', e.message);
        hideLocationSearchingIndicator();
        isLocating = false;
        followingLocation = false;
        
        const locationButton = document.getElementById('location-button');
        locationButton.classList.remove('active');
        
        alert('Unable to find your location. Please check if location services are enabled in your browser and device.');
    });

    // Stop following user location when map is manually panned
    map.on('dragstart', function() {
        if (isLocating) {
            followingLocation = false;
        }
    });

    // Fetch Airbnbs data from API
    fetch('/api/airbnbs')
        .then(response => response.json())
        .then(airbnbsData => {
            // Add Airbnb markers
            addMarkers(airbnbsData, layerGroups.airbnbs, icons.airbnb, 'airbnb');
        })
        .catch(error => {
            console.error('Error fetching Airbnbs data:', error);
        });

    // Fetch POIs data from API
    fetch('/api/pois')
        .then(response => response.json())
        .then(poisData => {
            // Add POI markers for each category
            Object.entries(poisData).forEach(([category, items]) => {
                if (layerGroups[category] && items.length > 0) {
                    const iconType = categoryToIconType[category] || category;
                    const markerType = categoryToMarkerType[category] || category;
                    addMarkers(items, layerGroups[category], icons[iconType], markerType);
                    
                    // Add trail lines for hiking trails
                    if (category === 'trails') {
                        items.forEach(trail => {
                            if (trail.path && trail.path.length > 0) {
                                const pathLatLngs = trail.path.map(point => [point.lat, point.lng]);
                                const pathLine = L.polyline(pathLatLngs, {
                                    color: '#228B22',
                                    weight: 5,
                                    opacity: 0.85,
                                    lineJoin: 'round',
                                    lineCap: 'round',
                                    dashArray: null
                                }).addTo(layerGroups.trails);
                                
                                // Add hover effects for trail lines
                                pathLine.on('mouseover', function() {
                                    this.setStyle({
                                        weight: 8,
                                        opacity: 1,
                                        color: '#1E8449'
                                    });
                                    
                                    this.openPopup();
                                });
                                
                                pathLine.on('mouseout', function() {
                                    this.setStyle({
                                        weight: 5,
                                        opacity: 0.85,
                                        color: '#228B22'
                                    });
                                });
                                
                                // Create difficulty rating HTML for trails
                                let difficultyHTML = '';
                                if (trail.difficulty_rating || trail.difficulty_rating === 0) {
                                    let difficultyStars = '';
                                    const ratingValue = trail.difficulty_rating || 0;
                                    const fullStars = Math.floor(ratingValue);
                                    
                                    // Create hiking boot icons for ratings
                                    for (let i = 0; i < 5; i++) {
                                        if (i < fullStars) {
                                            difficultyStars += '<i class="fas fa-hiking"></i>'; // Full hiking boot
                                        } else {
                                            difficultyStars += '<i class="far fa-hiking"></i>'; // Empty hiking boot
                                        }
                                    }
                                    
                                    const ratingText = trail.rating_count 
                                        ? `${ratingValue} / 5 difficulty (${trail.rating_count} ratings)` 
                                        : 'Not rated yet';
                                    
                                    difficultyHTML = `
                                    <div class="trail-difficulty">
                                        <div class="difficulty-rating">
                                            <span class="difficulty-label">Difficulty: </span>
                                            <span class="difficulty-stars">${difficultyStars}</span>
                                            <span class="rating-value">${ratingText}</span>
                                        </div>
                                        <a href="/rate-trail/${trail.id}" class="rate-trail-btn">Rate This Trail</a>
                                    </div>`;
                                }
                                
                                pathLine.bindPopup(`<div class="popup-content">
                                    <div class="popup-title">${trail.name}</div>
                                    <div class="popup-info">${trail.description || ''}</div>
                                    ${difficultyHTML}
                                    <div class="popup-source">Trail information source:</div>
                                    ${trail.url ? `<a href="${trail.url}" target="_blank" class="popup-link"><i class="fas fa-external-link-alt"></i> Visit Official Trail Website</a>` : ''}
                                </div>`);
                            }
                        });
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching POIs data:', error);
        });

    // Check if URL has focus parameters and handle accordingly
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('focus') && urlParams.has('id')) {
        const focusType = urlParams.get('focus');
        const focusId = urlParams.get('id');
        
        if (focusType === 'airbnb') {
            // Focus on specific Airbnb
            fetch(`/api/airbnbs/${focusId}`)
                .then(response => response.json())
                .then(airbnb => {
                    if (airbnb) {
                        map.setView([airbnb.lat, airbnb.lng], 15);
                        // Create a temporary highlighted marker
                        const highlightMarker = L.marker([airbnb.lat, airbnb.lng], { 
                            icon: icons.airbnb
                        }).addTo(map);
                        highlightMarker.bindPopup(createPopup(airbnb, 'airbnb')).openPopup();
                    }
                })
                .catch(error => {
                    console.error('Error fetching focused Airbnb:', error);
                });
        }
    }
});
