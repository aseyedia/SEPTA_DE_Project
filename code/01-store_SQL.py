# http://www3.septa.org/#/Static%20Data/Locations
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///septa_data.db')


# Define the tables using SQLAlchemy ORM
class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    route_name = Column(String)


class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    direction = Column(String)
    destination = Column(String)
    late = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    route_id = Column(Integer, ForeignKey('routes.id'))


Base.metadata.create_all(engine)  # turns class definitions into SQL tables
Session = sessionmaker(bind=engine)
session = Session()

# Fetch data from API
endpoint = "http://www3.septa.org/api/TransitViewAll/index.php"
response = requests.get(endpoint)

if response.status_code == 200:
    data = response.json()

    # Looping through each route dictionary from the API response
    for route_dict in data['routes']:
        # Looping through each route within the route dictionary
        for route_name, vehicles in route_dict.items():

            # Check if the current route name already exists in the database
            route = session.query(Route).filter_by(route_name=route_name).first()

            # If the route doesn't exist, create a new route and add it to the database
            if not route:
                route = Route(route_name=route_name)
                session.add(route)
                session.commit()

            # For each vehicle related to the current route
            for vehicle_data in vehicles:
                # Check if the vehicle with this ID and timestamp already exists in the database
                existing_vehicle = session.query(Vehicle).filter_by(
                    vehicle_id=vehicle_data['VehicleID'],
                    timestamp=datetime.datetime.fromtimestamp(int(vehicle_data['timestamp']))
                ).first()

                # If the vehicle doesn't already exist, create a new vehicle record and add it to the database
                if not existing_vehicle:
                    vehicle = Vehicle(
                        vehicle_id=vehicle_data['VehicleID'],
                        lat=vehicle_data['lat'],
                        lng=vehicle_data['lng'],
                        direction=vehicle_data['Direction'],
                        destination=vehicle_data['destination'],
                        late=vehicle_data['late'],
                        timestamp=datetime.datetime.fromtimestamp(int(vehicle_data['timestamp'])),
                        route_id=route.id
                    )
                    session.add(vehicle)

    # Commit all the changes to the database
    session.commit()

else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

session.close()
