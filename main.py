from flask import Flask, render_template, jsonify, request
import pprint as pprint
import requests

app = Flask(__name__)

SEPTA_LOCATIONS_ENDPOINT = "http://www3.septa.org/api/locations/get_locations.php"
SEPTA_SCHEDULES_ENDPOINT = "https://www3.septa.org/api/BusSchedules/index.php"
SEPTA_TRANSITVIEW_ENDPOINT = "https://www3.septa.org/api/TransitView/index.php"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_nearby_transit', methods=['GET'])
def get_nearby_transit():
    # lat = request.args.get('lat')
    lat = "39.951689"
    # lon = request.args.get('lon')
    lon = "-75.171225"
    # radius = request.args.get('radius', default=0.1)
    radius = "0.1"
    # Fetch nearby stops
    response = requests.get(SEPTA_LOCATIONS_ENDPOINT,
                            params={"lon": lon, "lat": lat, "type": "bus_stops", "radius": radius})
    stops = response.json()

    transit_data = []

    # Fetch transit data for each stop
    for stop in stops:
        stop_id = stop['location_id']
        response = requests.get(SEPTA_SCHEDULES_ENDPOINT, params={"stop_id": stop_id})

        # so I can get nearby stops, and then use those stop ids to get the bus/trolley schedules for those stops,
        # and using those schedules I can get route numbers, but I can also highlight the routes on the map
        data = response.json()
        transit_data.append(data)

    return jsonify(transit_data)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
