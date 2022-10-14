import time

import redis
from flask import Flask, request, jsonify
from datetime import datetime,tzinfo,timedelta



app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
countries = [
    {"id": 1, "name": "Thailand", "capital": "Bangkok", "area": 513120},
    {"id": 2, "name": "Australia", "capital": "Canberra", "area": 7617930},
    {"id": 3, "name": "Egypt", "capital": "Cairo", "area": 1010408},
]

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

GMT = Zone(0,False,'GMT')
EST = Zone(-5,False,'EST')
CST = Zone(-5,False,'CST')
# print (datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S %Z'))
#print (datetime.now(GMT).strftime('%m/%d/%Y %H:%M:%S %Z'))
#print (datetime.now(EST).strftime('%m/%d/%Y %H:%M:%S %Z'))
#print (datetime.now(CST).strftime('%m/%d/%Y %H:%M:%S %Z'))

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/hello_world')
def helloworld():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

@app.route('/tiempo')
def tiempo():
    tz = request.args.get('tz')
    if tz == "CST":
        dateTimeObj = datetime.now(CST)
        fecha = str(dateTimeObj.year)  + '/' + str(dateTimeObj.month) + '/' + str(dateTimeObj.day)
        hora = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
        return 'Hello! It´s {} current date, and {} current CST time.\n'.format(fecha,hora)
    if tz == "UTC":
        dateTimeObj = datetime.utcnow()
        fecha = str(dateTimeObj.year)  + '/' + str(dateTimeObj.month) + '/' + str(dateTimeObj.day)
        hora = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
        return 'Hello! It´s {} current date, and {} current UTC time.\n'.format(fecha,hora)
    else:
        dateTimeObj = datetime.now()
        fecha = str(dateTimeObj.year)  + '/' + str(dateTimeObj.month) + '/' + str(dateTimeObj.day)
        hora = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
        return 'Hello! It´s {} current date, and {} current time.\n'.format(fecha,hora)


# Access the member variables of datetime object to print date & time information
#print(dateTimeObj.year, '/', dateTimeObj.month, '/', dateTimeObj.day)
#print(dateTimeObj.hour, ':', dateTimeObj.minute, ':', dateTimeObj.second, '.', dateTimeObj.microsecond)


def _find_next_id():
    return max(country["id"] for country in countries) + 1

@app.get("/countries")
def get_countries():
    return jsonify(countries)

@app.post("/countries")
def add_country():
    if request.is_json:
        country = request.get_json()
        country["id"] = _find_next_id()
        countries.append(country)
        return country, 201
    return {"error": "Request must be JSON"}, 415
