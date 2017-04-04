import tornado.ioloop
import tornado.web
from bson import json_util
import json
import os
from pip._vendor.requests.sessions import session
os.environ['TZ'] = 'US/Eastern'


from pymongo import MongoClient
from geopy.distance import vincenty
host = "localhost:27017";
mongo_client = MongoClient(host)
logs_db = mongo_client.torque



import json
import time
import datetime



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
                sensor_id = 'k' + key[len('userFullName'):].strip("0")
                if sensor_id not in sensors:
                    sensors[sensor_id] = {'id':sensor_id}
                sensors[sensor_id]['name'] = value
                
            if 'userShortName' in key:
                sensor_id = 'k' + key[len('userShortName'):].strip("0")
                if sensor_id not in sensors:
                    sensors[sensor_id] = {'id':sensor_id}
                sensors[sensor_id]['short_name'] = value
                
            if 'userUnit' in key:
                sensor_id = 'k' + key[len('userUnit'):].strip("0")
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
# reference https://reminiscential.wordpress.com/2012/04/07/realtime-notification-delivery-using-rabbitmq-tornado-and-websocket/
#             print vincenty(b_loc, a_loc).miles, tdelta  tdelta.total_seconds()
class SessionHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        sessions = logs_db.TripData.find({'kff1204':{'$ne':None},'kff1266':{'$ne':None}}).sort('time',-1)
        session_ids = []
        sessions_meta = {}
        for a in sessions:
            if a['session'] in session_ids:
                continue;
            distance =  float(a['kff1204']) 
            duration =  float(a['kff1266'])
            email = a['email'] if 'email' in a else 'anon'
            sessions_meta[a['session']] = {'distance': distance, 'time': duration, 'email':email}
            session_ids.append(a['session'])
        sessions = {'sessions':session_ids, 'meta':sessions_meta}
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
        
        
        data = list(logs_db.TripData.find({"session":session_id}))
        
        available_sensors = list(set([i for s in [d.keys() for d in data] for i in s]))
        sensors = list(logs_db.Sensors.find({'id':{'$in':available_sensors}}))
#         
#         for i, sample in enumerate(data):
#             for j, m in sample.iteritems():
#                 if j in sensors:
#                     data[i][j] = float(m)
                
        res = {'data':data, 'sensors':sensors}
        
        
        self.write(json.dumps(res,default=json_util.default))
        

class UpdateHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        session_id = self.get_argument("delete_session")
        
        
        data = logs_db.TripData.remove({"session":session_id})
        
        
        res = {'data':data}
        
        self.write(json.dumps(res,default=json_util.default))
        
        
import tornado.websocket as websocket
class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
     
    def open(self, *args, **kwargs):
        self.write_message(u"You said: " + message)
        print 'socket open'
         
  
    def on_close(self):
#         pika.log.info("WebSocket closed")
        print 'socket close'
        self.application.pc.remove_event_listener(self)
     
    def on_message(self, message):
        print 'cleint said: ', message
        self.write_message(u"You said: " + message)

def make_app():
    return tornado.web.Application([
#         (r'/', tornado.web.StaticFileHandler,  {'path':'public/index.html'}),
        (r"/push/*", MainHandler),
        (r"/sessions", SessionHandler),
        (r"/data*", DataHandler),
        (r"/update*", UpdateHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './public'}),
        (r'/ws', SocketHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()