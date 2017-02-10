#! /usr/local/bin/python3
from flask import Flask, jsonify, make_response, abort, request
import os
import psycopg2
import pandas as pd
import json
import uuid

# Global app constant (for REST API definition)
app = Flask(__name__)

try:
    PG_HOST = os.environ["PG_HOST"]
except KeyError:
    PG_HOST = "localhost"
try:
    DB_NAME = os.environ["DB_NAME"]
except KeyError:
    DB_NAME = "saatdb01"
try:
    PG_USER = os.environ["PG_USER"]
except KeyError:
    PG_USER = "saat"
try:
    PG_PASS = os.environ["PG_PASS"]
except KeyError:
    PG_PASS = "CHANGEME"

print(f"Connecting to postgres database: {PG_USER}@{PG_HOST}/{DB_NAME}")

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
            "INSERT INTO rr_intervals (user_id,mobile_time,batch_index,value) VALUES ('{}','{}',{},{})".format(
                user_id,payload['mobile_time'],payload['batch_index'],payload['value']))
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

    REQUIRED_KEYS = ('start_time','end_time')
    payload = request.get_json()

    conn = connect_saat()
    cur = conn.cursor()

    #*** LAST HERE 3/7: GET is working! make it use ISO datetime format for output. then Then multi value upload (with different sample.json file)

    if event_type == "rr_intervals":
        for k in REQUIRED_KEYS:
            if k not in payload:
                abort(400,'missing required key in request JSON: ' + k)
        conn = connect_saat()
        query = "SELECT * FROM rr_intervals WHERE (user_id = '{}' AND mobile_time BETWEEN '{}' and '{}')".format(
                user_id, payload['start_time'],payload['end_time'])
        query_df = pd.read_sql_query(query, conn, index_col=['user_id','mobile_time'])#,parse_dates=['mobile_time'])
#        query_df.set_index('mobile_time',drop=False,inplace=True)
        print('query_df:')
        print(query_df)
    else:
        abort(400,"unknown event type: " + str(event_type))

    json_response = {
        "method": request.method,
        "user_id": user_id,
        "event_type": event_type,
        "request json": request.json,
        "output json": query_df.to_json(orient='split')#orient="records")
    }
    print(json_response)
    return make_response(jsonify(json_response), 200)

def connect_saat():
    return psycopg2.connect(user=PG_USER, password=PG_PASS,
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
