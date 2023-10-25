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
import traceback


import json
import time
import datetime
import stats

liveWebSockets = set()
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
        data = { k: self.get_argument(k) for k in self.request.arguments }
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
                if not logs_db.Sensors.find_one({'id':key}):
                    a = logs_db.Sensors.insert_one(value)
            
            
        
        sensor_data = [sensors[key]['short_name'] + ' ' + data[key] for key in sensors if key in data]
        
        
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
            try:
                trip = {
    #                 'distance': 
    #                 'time': float(sample['kff1266']),
                    'email':sample['email'],
                    'session': sample['session'], 
                    'start':[sample['kff1006'], sample['kff1005']],
    #                 'end':[sample['kff1006'], sample['kff1005']]
                 }
                logs_db.Trip.update_one(
                                        {"session": trip["session"]},
                                        {
                                            "$setOnInsert": trip,
                                            "$set": {'end':[sample['kff1006'], sample['kff1005']],'distance': float(sample['kff1204']) * 0.621371, 'time': float(sample['kff1266']) },
                                        },
                                        upsert=True,
                                    )
                server.add_callback(webSocketSendMessage, json.dumps(sample,default=json_util.default))
            except Exception, e:
                traceback.print_exc()
                print 'couldnt insert'
                pass
            

            
        
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
        print 'origin', origin
        return True
    
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
        
        stats.calc_stats()
        session_ids = []
        sessions_meta = {}
	
        sessions = logs_db.Trip.find({},{'_id':0}).sort('session')
        
        for a in sessions:
            try:
                if a['time'] < 10:
                    logs_db.TripData.delete_many({'session':a['session']})
                    logs_db.Trip.delete_many({'session':a['session']})
                    continue
                sessions_meta[a['session']] = a
                sessions_meta[a['session']]['start_from_home'] =  vincenty(a['start'], [40.117357, -75.037635]).miles
                session_ids.append(a['session'])
            except Exception, e:
                pass
          
#         sessions = logs_db.TripData.find({'kff1204':{'$ne':None},'kff1266':{'$ne':None}})
#         session_ids = []
#         sessions_meta = {}
#         for a in sessions:
#             distance =  float(a['kff1204']) * 0.621371
#             duration =  float(a['kff1266'])
# 	    email = a['email'] if 'email' in a else 'anon'
#             if a['session'] not in session_ids:
#                 sessions_meta[a['session']] = {'distance': distance,
#                                                 'time': duration,
#                                                 'email':email,
#                                                 'session': a['session'], 
#                                                 'start':[a['kff1006'], a['kff1005']],
#                                                 'end':[a['kff1006'], a['kff1005']]
#                                                  }
#                 session_ids.append(a['session'])
#             if sessions_meta[a['session']]['time'] < duration:
#                 sessions_meta[a['session']]['time'] = duration
#                 sessions_meta[a['session']]['distance'] = distance
#                 sessions_meta[a['session']]['end'] = [a['kff1006'], a['kff1005']]
#                 
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
#         sensors = list(logs_db.Sensors.find({}))
#         
#         for i, sample in enumerate(data):
#             for j, m in sample.iteritems():
#                 if j in sensors:
#                     data[i][j] = float(m)
                
        res = {'data':data, 'sensors':sensors}
        
#         server.add_callback(webSocketSendMessage, "build your data here")
        
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
#     self.user_session = ''
    def check_origin(self, origin):
        return True
       
#     def set_default_headers(self):
#         self.set_header("Access-Control-Allow-Origin", "*")
#         self.set_header("Access-Control-Allow-Headers", "x-requested-with")
#         self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
     
    def open(self):
        self.set_nodelay(True)
        liveWebSockets.add(self)
        pass
 
#     def on_message(self, message):
#         self.write_message(u"Your message was: " + message)
#  
#     def on_close(self):
#         pass
         
  
    def on_close(self):
#         pika.log.info("WebSocket closed")
        print 'socket close'
        
     
    def on_message(self, message):
        print 'cleint said: ', message
        self.user_session = message;
        
        
        
        self.write_message(u"You said: " + message)

def webSocketSendMessage(message):
    removable = set()
    for ws in liveWebSockets:
        if not ws.ws_connection or not ws.ws_connection.stream.socket:
            removable.add(ws)
        else:
            ws.write_message(message)
    for ws in removable:
        liveWebSockets.remove(ws)



class TestHandler(tornado.web.RequestHandler):
    
    
    
    def check_origin(self, origin):
        return True
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    #
    
    def get(self):
       
        
        res = {'data':'test'}
        
        self.write(json.dumps(res,default=json_util.default))
        

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("public/index.html")


def make_app():
    return tornado.web.Application([
        (r'/test', TestHandler),
        (r'/socket', SocketHandler),
        (r"/push/*", MainHandler),
        (r"/sessions", SessionHandler),
        (r"/data*", DataHandler),
        (r"/update*", UpdateHandler),
        (r"/", RootHandler),
        # (r'/', tornado.web.StaticFileHandler, {'path': './public/index.html'}),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './public'}),
        
    ],compress_response=True)

if __name__ == "__main__":
    print "hello"
    app = make_app()
    print "app made"
    app.listen(80)
    server = tornado.ioloop.IOLoop.instance()
    server.start()
#     tornado.ioloop.IOLoop.current().start()
