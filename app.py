#! /usr/local/bin/python3
from flask import Flask, jsonify, make_response, abort, request
import json
import time
from datetime import datetime
import boto3
import psycopg2
from flask import Flask, request, render_template
#from utils import json_response, parse_datetime, unix_time_millis
import uuid

# Global app constant (for REST API definition)
app = Flask(__name__)
PG_PORT = 8000

class User:
#    def __init__(self):
#        self.aws = {}
    @staticmethod
    def post(data):
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = data
        except TypeError:
            json_data = data
        try:
            execute = getattr(User, json_data["exec"])
            return execute(json_data)
        except KeyError:
            return json_response("Malformatted body.  Please only use JSON.", 400)

    @staticmethod
    def register(json_data):
        try:
            user_id = json_data["id"]
        except KeyError:
            abort(400, "ID must be included in register request.")
        conn = psycopg2.connect(user="saat", password="CHANGEME",
                host="tf-201611180437251236751897ul.chhanozbpeca.us-west-2.rds.amazonaws.com", dbname="saatdb01")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Users (id varchar PRIMARY KEY, apiKey uuid);")
        conn.commit()
        cur.execute("SELECT id FROM Users WHERE id='{}';".format(user_id))
        if cur.fetchone() is not None:
            abort(409, "User with selected ID already exists!")
        api_key = uuid.uuid4()
        cur.execute("SELECT id FROM Users WHERE apiKey='{}';".format(api_key))
        while cur.fetchone() is not None:
            api_key = uuid.uuid4()
            cur.execute("SELECT id FROM Users WHERE apiKey='{}';".format(api_key))
        cur.execute("INSERT INTO Users (id, apiKey) VALUES ('{}', '{}');".format(user_id, api_key))
        conn.commit()
        res = {
            "message": "User successfully created!",
            "id": user_id
        }
        return make_response(jsonify(res), 201)

#    @staticmethod
#    def authenticate(api_key):
#        conn = psycopg2.connect(user="saat", password="CHANGEME",
#                host="tf-201611180437251236751897ul.chhanozbpeca.us-west-2.rds.amazonaws.com", dbname="saatdb01")
#        cur = conn.cursor()
#        cur.execute("SELECT id FROM Users WHERE apiKey = {}".format(api_key))
#        if cur.fetchone() is not None:
#            abort(401, "Incorrect API key, please try again with a different one!")

class HeartBeat:
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
        conn = psycopg2.connect(user="saat", password="CHANGEME",
                host="tf-201611180437251236751897ul.chhanozbpeca.us-west-2.rds.amazonaws.com", dbname="saatdb01")
        cur = conn.cursor()
        cur.execute("SELECT id FROM Users WHERE apiKey={};".format(api_key))
        if cur.fetchone() is not None:
            abort(401, "Incorrect API key, please try again with a different one!")

    @staticmethod
    def post(data):
        #try:
        #    self.aws["rds"]
        #except KeyError:
        #    self.aws["rds"] = boto3.client('rds')
        #res = self.aws["rds"].describe_db_instances()
        #for db in res["DBInstances"]:
        #    if db["Engine"].lower == "postgres" and db["DBName"] == "testdb":
        #        self.aws["pg_endpoint"] = db["Endpoint"]
        conn = psycopg2.connect(user="saat", password="CHANGEME",
                host="tf-201611180437251236751897ul.chhanozbpeca.us-west-2.rds.amazonaws.com", dbname="saatdb01")
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
executors["user"] = User()

def execute(method, event_type, data=None):
    print("method: {}, event_type: {}, data: {}".format(method, event_type, data))
    try:
        req = getattr(executors[event_type.lower()], method.lower())
        if data is None:
            return req()
        else:
            return req(data)
    except KeyError:
        return {}

@app.route('/events/<event_type>', methods=['POST', "PUT", "DELETE"])
def event_insert(event_type):
    validate = getattr(executors[event_type], "validate_{}".format(request.method))
    if validate():
        return execute(request.method, event_type, request.json)
    else:
        return json_response("Bad Request", 400)

@app.route('/user/<exec_>', methods=['POST'])
@app.route('/user', methods=['POST'])
def user(exec_=None):
    json_request = request.json
    if exec_ is not None:
        json_request["exec"] = exec_
    return execute(request.method, "user", json_request)

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



# ERROR HANDLERS
@app.errorhandler(400)
def client_error(error):
    json_error = {
        "error": "Client error.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 400)

@app.errorhandler(404)
def not_found(error):
    json_error = {
        "error": "Resource not found.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 404)

@app.errorhandler(405)
def not_found(error):
    json_error = {
        "error": "Invalid HTTP method.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 405)

@app.errorhandler(409)
def resource_conflict(error):
    json_error = {
        "error": "Resource conflict.",
        "message": error.description,
    }
    return make_response(jsonify(json_error), 409)

@app.errorhandler(500)
def unknown_error(error):
    return make_response(jsonify({"message": "Unknown internal server error."}), 500)



if __name__ == "__main__":
    app.run(debug=True)
