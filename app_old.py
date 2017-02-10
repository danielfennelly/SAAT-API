#! /usr/local/bin/python3
from flask import Flask, jsonify, make_response, abort, request
import json
import psycopg2
from utils import json_response
import uuid

# Global app constant (for REST API definition)
app = Flask(__name__)
# PG_PORT = 8000

PG_HOST = (
    "tf-201611180437251236751897ul"
    ".chhanozbpeca.us-west-2.rds.amazonaws.com")

class User:

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
            return json_response(
                "Malformatted body. Please only use JSON.",
                400)

    @staticmethod
    def register(json_data):
        try:
            user_id = json_data["id"]
        except KeyError:
            abort(400, "ID must be included in register request.")
        conn = psycopg2.connect(
            user="saat",
            password="CHANGEME",
            host=PG_HOST,
            dbname="saatdb01")
        cur = conn.cursor()
        create_statement = ("CREATE TABLE IF NOT EXISTS Users "
                            "(id varchar PRIMARY KEY, apiKey uuid);")

        cur.execute(create_statement)
        conn.commit()
        #TODO: something seems funky with below logic. some ID variable is misnamed
        cur.execute("SELECT id FROM Users WHERE id='{}';".format(user_id))
        if cur.fetchone() is not None:
            abort(409, "User with selected ID already exists!")
        api_key = uuid.uuid4()
        cur.execute("SELECT id FROM Users WHERE apiKey='{}';".format(api_key))
        while cur.fetchone() is not None:
            api_key = uuid.uuid4()
            cur.execute(
                "SELECT id FROM Users WHERE apiKey='{}';".format(api_key))

        insert_statement = ("INSERT INTO Users (id, apiKey) "
                            "VALUES ('{}', '{}');").format(user_id, api_key)
        cur.execute(insert_statement)
        conn.commit()
        res = {
            "message": "User successfully created!",
            "id": user_id,
            "apiToken": api_key
        }
        return make_response(jsonify(res), 201)


class HeartBeat:

    @staticmethod
    def validate_post(data):
        VALID_KEYS = ["mobile_time", "rr_interval", "batch_idx", "api_key"]
        key_count = 0
        for key in data.keys():
            if key in VALID_KEYS:
                key_count += 1
            else:
                return False
        if key_count == len(VALID_KEYS):
            return True #TODO: eventually this should just pass to get to the below user lookup logic
        else:
            return False
        conn = psycopg2.connect(user="saat", password="CHANGEME",
                                host=PG_HOST, dbname="saatdb01")
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM Users WHERE apiKey='{}';".format(data["api_key"]))
        result = cur.fetchone()
        if result is None:
            abort(401,
                  "Incorrect API key, please try again with a different one!")
        else:
            return result

    @staticmethod
    def post(data):
        conn = psycopg2.connect(user="saat", password="CHANGEME",
                                host=PG_HOST, dbname="saatdb01")
        cur = conn.cursor()
        # This should be threadsafe as opposed to relying on data.keys() and
        # data.values()
        keys, values = zip(*data.items())
        # TODO: make sure HeartRate table and schema is already created
        # TODO: validate the below SQL call
        # TODO: Add bulk upload (list of heart rate values
        #       instead of single value)
        # TODO: Add user ID value into heartrate data (Do a user lookup)
        cur.execute("INSERT INTO HeartRate ('{}') VALUES ('{}')".format(
            ",".join(keys), ",".join(values)))
        conn.commit()
        return json_response('Posted heartbeats', 201)

# TODO: Implement PUT

# TODO: Implement DELETE


executors = {}
executors["heart_beat"] = HeartBeat()
executors["user"] = User()


def execute(method, event_type, data=None):
    message = "method: {}, event_type: {}, data: {}".format(
        method, event_type, data)
    print(message)
    try:
        req = getattr(executors[event_type.lower()], method.lower())
        if data is None:
            return req()
        else:
            return req(data)
    except KeyError:
        return {}

@app.route('/measurements/rr_intervals',methods=['POST'])
def measurement_post_temp():
    print("method: {}".format(request.method)) 
    print("json: {}".format(request.json))
    return json_response('Posted RRIs', 201)


@app.route('/events/<event_type>', methods=['POST', "PUT", "DELETE"])
def event_insert(event_type):
    validate = getattr(executors[event_type],
                       "validate_{}".format(request.method))
    # TODO: Adjust validate comparison here (it's not a bool anymore)
    if validate(request.json):
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


# ERROR HANDLERS
@app.errorhandler(400)
def client_error(error):
    json_error = {
        "error": "Client error.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 400)


@app.errorhandler(401)
def unauthorized_error(error):
    json_error = {
        "error": "Unauthorized.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 401)


@app.errorhandler(404)
def not_found(error):
    json_error = {
        "error": "Resource not found.",
        "message": error.description
    }
    return make_response(jsonify(json_error), 404)


@app.errorhandler(405)
def invalid_method(error):
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
    return make_response(
        jsonify({"message": "Unknown internal server error."}),
        500)


if __name__ == "__main__":
    app.run(debug=True)
