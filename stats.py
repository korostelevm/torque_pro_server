from pymongo import MongoClient
from geopy.distance import vincenty
host = "localhost:27017";
mongo_client = MongoClient(host)
logs_db = mongo_client.torque
import numpy as np
import time
def reject_outliers(data, m = 20.):
    data = np.asarray(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    if not np.sum(s):
        return data
    return data[s<m]



def calc_stats():
    
    session_ids = []
    sessions_meta = {}
#     sessions = logs_db.Trip.find({},{'_id':0}).sort('session')
    sessions = logs_db.Trip.find({'car': { "$exists" : False }},{'_id':0}).sort('session')

        
    for a in sessions:
        print time.gmtime(float(a['session'])/1000.),a['session']

        print ''
        print ''
#         continue
        if 'time' in a:
            if a['time'] < 10:
                logs_db.TripData.delete_many({'session':a['session']})
                logs_db.Trip.delete_many({'session':a['session']})
                continue
            sessions_meta[a['session']] = a
            sessions_meta[a['session']]['start_from_home'] =  vincenty(a['start'], [40.117357, -75.037635]).miles
            print a
            data = list(logs_db.TripData.find({"session":a['session']}))
                
            available_sensors = list(set([i for s in [d.keys() for d in data] for i in s]))
            sensors = list(logs_db.Sensors.find({'id':{'$in':available_sensors}}))
#              print [(s['name'],s['id']) for s in sensors]
            sensors_update = {}
            sensors_update['car'] = 'liberty'
            for s in sensors:
                s_data = [float(d[s['id']]) for d in data if s['id'] in d]
#                 s_data = reject_outliers(s_data)
                sensors_update[s['id']+'_mean'] = np.mean(s_data)
                sensors_update[s['id']+'_var'] = np.var(s_data)
                sensors_update[s['id']+'_std'] = np.std(s_data)
                if(s['id'] == 'k49'):
                    if sensors_update[s['id']+'_mean']:
                        sensors_update['car'] = 'wrangler'
    #                 
            logs_db.Trip.update_one(
                            {"session": a["session"]},
                            {
    #                             "$setOnInsert": trip,
                                "$set": sensors_update,
                            },
                            upsert=True,
                        )
    return 0

# calc_stats(sessions) 
                            
