#! /usr/local/bin/python3
from flask import Flask, jsonify, make_response, abort, request
import json
import time
from datetime import datetime
import boto3
import psycopg2

# Global app constant (for REST API definition)
app = Flask(__name__)
PG_PORT = 8000

class HeartBeat:
    def __init__(self):
        self.aws = {}

    @staticmethod
    def validate_post(data):
        VALID_KEYS = ["mobile_time", "rr_interval", "batch_idx"]
        key_count = 0
        for key in data.keys():
            if key in VALID_KEYS:
                key_count += 1
            else:
                return False
        if key_count == len(VALID_KEYS):
            return True
        else:
            return False

    def post(self, data):
        try:
            self.aws["rds"]
        except KeyError:
            self.aws["rds"] = boto3.client('rds')
        res = self.aws["rds"].describe_db_instances()
        for db in res["DBInstances"]:
            if db["Engine"].lower == "postgres" and db["DBName"] == "testdb":
                self.aws["pg_endpoint"] = db["Endpoint"]
        conn = psycopg2.connect(database="testdb", user="SAATpg",
                                    password="SAATpassw0rd", port=PG_PORT)
        cur = conn.cursor()
        # This should be threadsafe as opposed to relying on data.keys() and data.values()
        keys, values = zip(*data.items())
        cur.execute("INSERT INTO HeartRate ({}) VALUES ({})".format(",".join(keys), ",".join(values)))
	return json_response('Posted heartbeats', 201)

## TODO: Implement PUT
#    def put(self, data):
#	posted_json = request.get_json(force=True)
#	start = parse_datetime(posted_json['start'])
#	end = parse_datetime(posted_json['end'])
#	beats = posted_json['beats']
#	self.heartbeat_array.extend(beats)
#	return json_response('Posted heartbeats')

## TODO: Implement DELETE
#    def delete_heartbeats(self, data):
#        start = parse_datetime(request.args.get('start'))
#        end = parse_datetime(request.args.get('end'))
#        if start and end:
#            start_millis = unix_time_millis(start)
#            end_millis = unix_time_millis(end)
#            compare = lambda t: not (t > start_millis and t < end_millis)
#            self.heartbeat_array = list(filter(compare, self.heartbeat_array))
#        else:
#            return json_response('Bad Request', 400)

executors = {}
executors["heart_beat"] = HeartBeat()

def execute(method, event_type, data=None):
    try:
        req = getattr(executors[event_type.lower()], method.lower())
        if data is None:
            req()
        else:
            req(data)
    except KeyError:
        return {}

@app.route('/events/<event_type>', methods=['POST', "PUT", "DELETE"])
def event_insert(event_type):
    validate = getattr(executors[event_type], "validate_{}".format(request.method))
    if validate():
        return execute(request.method, event_type, request.json)
    else:
        return json_response("Bad Request", 400)

@app.route('/heartbeats', methods=['GET', 'POST', 'DELETE'])
def heartbeats():
    if request.method == 'GET':
        return get_heartbeats()
    elif request.method == 'POST':
        return post_heartbeats()
    elif request.method == 'DELETE':
        return delete_heartbeats()
    else:
        return json_response('Bad Request', 400)

if __name__ == "__main__":
    app.run(debug=True)
