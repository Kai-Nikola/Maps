import requests
import ujson
from flask import Flask, render_template, request

app = Flask(__name__)

API_KEY = "YOUR API KEY"

# Function to calculate route using HERE Routing API
def calculate_route(origin_lat, origin_lon, dest_lat, dest_lon):
    routing_url = f'https://router.hereapi.com/v8/routes'
    params = {
        'transportMode': 'car',
        'origin': f'{origin_lat},{origin_lon}',
        'destination': f'{dest_lat},{dest_lon}',
        'return': 'summary',
        'apiKey': API_KEY
    }
    response = requests.get(routing_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'routes' in data and len(data['routes']) > 0:
            summary = data['routes'][0]['sections'][0]['summary']
            distance_km = summary['length'] / 1000  # Convert meters to kilometerszz
            time_seconds = summary['baseDuration']  # Time in seconds
            time_minutes = time_seconds // 60  # Convert to minutes
            return distance_km, time_minutes
    return None, None

@app.route('/')
def index():
    # Define origin location (user's current location or a fixed point)
    origin_lat, origin_lon = 19.17231, 72.99214  # Airoli coordinates (fixed)

    # Query to search for ATMs in Airoli
    search_query = 'ATM Airoli'
    geocode_url = f'https://discover.search.hereapi.com/v1/discover?at={origin_lat},{origin_lon}&q={search_query}&apiKey=' + API_KEY

    # Fetch geocoding data
    response = requests.get(geocode_url)

    lat_lon_list = []

    if response.status_code == 200:
        data = ujson.loads(response.text)

        if 'items' in data and len(data['items']) > 0:
            places = data['items'][:10]  # Limit to 10 results
            for place in places:
                dest_lat = place['position']['lat']
                dest_lon = place['position']['lng']

                # Calculate route distance and time
                distance, time = calculate_route(origin_lat, origin_lon, dest_lat, dest_lon)

                # Add to lat/lon list with distance and time
                if distance is not None and time is not None:
                    lat_lon_list.append({
                        'title': place.get('title', 'Unknown'),
                        'address': place['address']['label'],
                        'lat': dest_lat,
                        'lon': dest_lon,
                        'distance': distance,
                        'time': time
                    })

    # Sort the lat_lon_list by distance (ascending order)
    lat_lon_list = sorted(lat_lon_list, key=lambda x: x['distance'])

    # Get the nearest location (first item in the sorted list)
    nearest_location = lat_lon_list[0] if lat_lon_list else None

    # Pass data to the front-end (locations and nearest location for routing)
    return render_template('map.html', api_key=API_KEY, locations=lat_lon_list, nearest_location=nearest_location, origin_lat=origin_lat, origin_lon=origin_lon)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
