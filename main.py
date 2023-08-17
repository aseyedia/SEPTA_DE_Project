from flask import Flask, render_template, jsonify, request
from pprint import pprint
import requests

app = Flask(__name__)

SEPTA_LOCATIONS_ENDPOINT = "http://www3.septa.org/api/locations/get_locations.php"
SEPTA_SCHEDULE_ENDPOINT = "https://www3.septa.org/api/BusSchedules/index.php"
SEPTA_TRANSITVIEW_ENDPOINT = "https://www3.septa.org/api/TransitView/index.php"


@app.route('/')
def index():
    return render_template('index.html')


# lat = "39.951689"
# lon = "-75.171225"

@app.route('/get_transit_info', methods=['GET'])
def get_transit_info():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    # Fetch nearby stops
    stops_response = requests.get(SEPTA_LOCATIONS_ENDPOINT, params={"lon": lon, "lat": lat, "type": "bus_stops"})
    stops = stops_response.json()

    route_ids = []
    for stop in stops:
        # Fetch schedule for each stop
        schedule_response = requests.get(SEPTA_SCHEDULE_ENDPOINT, params={"stop_id": stop['location_id']})
        schedule = schedule_response.json()
        route_ids = list(schedule.keys())

    vehicles_data = []
    for route_id in route_ids:
        # Fetch real-time vehicle locations for each route
        transit_response = requests.get(SEPTA_TRANSITVIEW_ENDPOINT, params={"route": route_id})
        vehicles = transit_response.json()
        vehicles_data.extend(vehicles)

    # You can then return this data to be displayed on the frontend.
    return jsonify({
        "stops": stops,
        "vehicles": vehicles_data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
