from flask import Flask, render_template
import requests
import json
from bs4 import BeautifulSoup as Soup
from math import radians, sin, cos, acos, pi, copysign
from heapq import heappush, heappop
import ast
import middleware

def f64_acos(x):
    n = 40 # precision
    if (x < -1.0) or (x > +1.0):
        return 0
    y = 0.0
    b = 0.5 * pi
    i = 0
    while (i < n):
        y0 = y
        y += b
        if (cos(y) < x): # if overshot, go back to prev y and try with smaller b
            y = y0
        i += 1
        b *= 0.5
    return y

def lldist(pt_1,pt_2):
    lat_1 = radians(float(pt_1[0]))
    lon_1 = radians(float(pt_1[1]))
    lat_2 = radians(float(pt_2[0]))
    lon_2 = radians(float(pt_2[1]))
    dist = 6371.01 *\
        f64_acos( sin(lat_1)*sin(lat_2) + cos(lat_1)*cos(lat_2)*cos(lon_1-lon_2) )

    return dist

def find_closest_parking_spot_to(destination_coords):
    url = 'http://api.sfpark.org/sfpark/rest/availabilityservice'

    # page_text = requests.get(url).text
    page_text = open('parking.xml').read()

    soup = Soup(page_text, 'html.parser')
    parking_spot_coords_list = []
    for message in soup.findAll('avl')[1:]:
        box = [float(num) for num in message.find('loc').contents[0][1:-1].split(',')]
        lats = box[1:2]#[1::2]
        lons = box[0:1]#[::2]
        parking_spot_coords = (sum(lats)/len(lats),sum(lons)/len(lons))
        dist = lldist(destination_coords, parking_spot_coords)
        heappush(parking_spot_coords_list, (dist, parking_spot_coords))

    closest_parking_spot_coords = heappop(parking_spot_coords_list)[1]
    return closest_parking_spot_coords

# def get_jump_bikes():
#     url = 'https://sf.jumpbikes.com/opendata/free_bike_status.json'
#     try:
#         data = requests.get(url).json()
#         raw_bikes = data['data']['bikes']
#         bikes = []
#         for raw_bike in raw_bikes:
#             bike = {
#                 'company': 'Jump',
#                 'bike_id': raw_bike['bike_id'],
#                 'latitude': raw_bike['lat'],
#                 'longitude': raw_bike['lon']
#             }
#             bikes.append(bike)
#     except:
#         bikes = []
#     return bikes

def get_ford_bikes():
    url = 'https://gbfs.fordgobike.com/gbfs/en/station_information.json'
    try:
        data = requests.get(url).json()
        raw_bikes = data['data']['stations']
        bikes = []
        for raw_bike in raw_bikes:
            bike = {
                'company': 'Ford',
                'bike_id': raw_bike['external_id'],
                'latitude': raw_bike['lat'],
                'longitude': raw_bike['lon']
            }
            bikes.append(bike)
    except:
        bikes = []
    return bikes

def get_bike_data():
	bike_data = get_ford_bikes()
	return bike_data

app = Flask(__name__)

app.wsgi_app = middleware.SimpleMiddleWare(app.wsgi_app)

@app.route('/park/<destination_coords>')
def park(destination_coords):
    parking_spot_lat, parking_spot_lon = find_closest_parking_spot_to(ast.literal_eval(destination_coords))
    return f'{parking_spot_lat}, {parking_spot_lon}'

# @app.route('/gas/<coords>')
# def gas(coords):
    
#     return render_template('gas.html', bikes=bike_data)

@app.route('/bikes')
def bikes():
    bike_data = get_bike_data()
    return json.dumps(bike_data)

# if __name__ == '__main__':
#     app.run()
