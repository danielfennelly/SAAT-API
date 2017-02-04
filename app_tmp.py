#! /usr/local/bin/python3
from flask import Flask, jsonify, make_response, abort, request
import json
import uuid

# Global app constant (for REST API definition)
app = Flask(__name__)
# PG_PORT = 8000

PG_HOST = "localhost"
DB_NAME = "saatdb01"

#**** LAST HERE 2/3. Next todo: Make the rr_intervals table as specified below. Try this out! 
#after that try to implement the GET. Then multi value upload (with different sample.json file)

@app.route('/users/<user_id>/measurements/<event_type>',methods=['POST'])
def measurement_post_temp(user_id,event_type):

    REQUIRED_KEYS = ('mobile_time','batch_index','value')
    payload = request.get_json() 

    if event_type == "rr_intervals":
        for k in REQUIRED_KEYS:
            if k not in payload:
                abort(400,'missing required key in posted JSON: ' + k)
        conn = connect_saat()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO rr_intervals ('user_id,mobile_time,batch_index,value') VALUES ('{},{},{},{}')".format(
                user_id,mobile_time,batch_index,value))
        conn.commit()
    else:
        abort(400,"unknown event type: " + str(event_type))

    json_output = {
        "method": request.method,
        "user_id": user_id,
        "event_type": event_type,
        "payload": payload
    }
    print(json_output)
    return make_response(jsonify(json_output), 201)

@app.route('/users/<user_id>/measurements/<event_type>',methods=['GET'])
def measurement_get_temp(user_id,event_type):
    conn = connect_saat()
    cur = conn.cursor()

    json_output = {
        "method": request.method,
        "user_id": user_id,
        "event_type": event_type,
        "json": request.json
    }
    print(json_output)
    return make_response(jsonify(json_output), 200)

def connect_saat():
    return psycopg2.connect(user="saat", password="CHANGEME",
                        host=PG_HOST, dbname=DB_NAME)


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
