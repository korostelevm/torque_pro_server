import tornado.ioloop
import tornado.web
from bson import json_util
import json
import os
os.environ['TZ'] = 'US/Eastern'


from pymongo import MongoClient

host = "localhost:27017";
mongo_client = MongoClient(host)
logs_db = mongo_client.torque



import json
import time
import datetime


# ubuntu@ip-172-31-32-235:/var/www/api.lawatlas.org/Symfony$ sudo  composer self-update
# Updating to version 0d5ff633b5da378df379fc462877282633736a17.
#     Downloading: 100%         
# Use composer self-update --rollback to return to version 4d134ce8a2aacb9566fee8deb8c514248fd2a983
sensors = {
#                 'kff1005':{  
#                     'id':'kff1005',
#                     'name':'Longitude',
#                     'short_name': 'lon',
#                     'unit':'',
#                  },
#                 'kff1006':{  
#                     'id':'kff1006',
#                     'name':'Latitude',
#                     'short_name': 'lat',
#                     'unit':'',
#                  },
#                 'kff1001':{
#                     'id':'kff1001',
#                     'name':'Speed (GPS)',
#                     'short_name': 'gps_speed',
#                     'unit':'mph',
#                  },
#                 'kff1007':{
#                     'id':'kff1007',
#                     'name':'GPS Bearing',
#                     'short_name': 'gps_bearing',
#                     'unit':'deg',
#                  },
            }
for sensor in logs_db.Sensors.find({}):
    sensors[sensor['id']] = sensor
class MainHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        global sensors
#         print self.request
#         print self.request.body
#         print self.request.arguments
#         data = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })

        data = { k: self.get_argument(k) for k in self.request.arguments }
#         print data.keys()
#         print data
        # meta
        email = data['eml']
        session = data['session']
        t = data['time']
        
        timestamp = datetime.datetime.fromtimestamp(float(t)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for key, value in data.iteritems():
            if 'userFullName' in key:
                sensor_id = 'k' + key[len('userFullName'):]
                if sensor_id not in sensors:
                    sensors[sensor_id] = {'id':sensor_id}
                sensors[sensor_id]['name'] = value
                
            if 'userShortName' in key:
                sensor_id = 'k' + key[len('userShortName'):]
                if sensor_id not in sensors:
                    sensors[sensor_id] = {'id':sensor_id}
                sensors[sensor_id]['short_name'] = value
                
            if 'userUnit' in key:
                sensor_id = 'k' + key[len('userUnit'):]
                if sensor_id not in sensors:
                    sensors[sensor_id] = {'id':sensor_id}
                sensors[sensor_id]['unit'] = value
        
        if 'userUnitff1007' in self.request.arguments:
            for key, value in sensors.iteritems():
#                 print key
                if not logs_db.Sensors.find_one({'id':key}):
#                     print 'inserting'
                    a = logs_db.Sensors.insert_one(value)
#                     print a
            
            
        
        sensor_data = [sensors[key]['short_name'] + ' ' + data[key] for key in sensors if key in data]
#         print timestamp, session, sensor_data
        
        
        if len(sensor_data) > 0:
            sample = {
                    'time': datetime.datetime.fromtimestamp(float(t)/1000),
                    'session': session,
                    'email': email,
                    }
            for key in sensors:
                if key in data:
                    sample[sensors[key]['id']] = data[key] 
            logs_db.TripData.insert_one(sample)
        
        
        
#         print timestamp
        self.write("OK!")










    def post(self):
        print self.request
        # data = json.loads(self.request.body)
        print self.request.body
        print 'post'
        self.write("OK!")

class SessionHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        sessions = logs_db.TripData.distinct("session")
        self.write(json.dumps(sessions))

class DataHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        session_id = self.get_argument("session")
        
        sensors = list(logs_db.Sensors.find({}))
        data = list(logs_db.TripData.find({"session":session_id}))
        res = {'data':data, 'sensors':sensors}
        self.write(json.dumps(res,default=json_util.default))


def make_app():
    return tornado.web.Application([
#         (r'/', tornado.web.StaticFileHandler,  {'path':'public/index.html'}),
        (r"/push/*", MainHandler),
        (r"/sessions", SessionHandler),
        (r"/data*", DataHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './public'}),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()