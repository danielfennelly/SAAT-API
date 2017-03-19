#! /usr/local/bin/python3
import flask
from flask import Flask, jsonify, make_response, abort, request
from flask_cors import CORS, cross_origin
import os
import psycopg2
import pandas as pd
import json
import uuid
import pprint  # for debugging

# Global app constant (for REST API definition)
app = Flask(__name__)

CORS(app)  # TODO: proabably turn this off for production

PG_HOST = os.environ.get("PG_HOST") or "localhost"
PG_DB = os.environ.get("PG_DB") or "saatdb01"
PG_USER = os.environ.get("PG_USER") or "saat"
PG_PASS = os.environ.get("PG_PASS") or "CHANGEME"

db_conn = None

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')


@app.route('/mood', methods=['GET', 'POST'])
def mood():
    if request.method == 'POST':
        return handle_mood_post()
    else:
        return present_mood_form()

def present_mood_form():
    return flask.render_template('mood.html')

def handle_mood_post():
    activation = parseToInt(request.form.get('activation'))
    valence = parseToInt(request.form.get('valence'))
    print(f"(activation, valence) = ({activation}, {valence})")
    return flask.redirect(flask.url_for('index'))

def parseToInt(arg):
    try:
        return int(arg) if arg is not None else None
    except ValueError:
        return None

# util to test that the server is being reached and getting data etc
@app.route('/test/<path>', methods=['GET', 'POST'])
def test(path):
    print(f'You want path: /test/{path}')
    print(f'Request.data: {request.data}')
    response = make_response(jsonify({"test": "successful"}), 201)
    return response


@app.route('/users/<user_id>/measurements/<event_type>', methods=['POST'])
def measurement_post(user_id, event_type):

    print("request.__dict__: \n" + pprint.pformat(request.__dict__, depth=5))

    # if not request.is_json:
    #     print('request posted to /users/<user_id>/measurements/<event_type> is not JSON. request data: ' + str(request.data))
    #     abort(400,f'request posted to /users/<user_id>/measurements/<event_type> is not JSON. request data: {request.data}')
    payload = request.get_json(force=True)
    if type(payload) != dict:
        print("received payload is not JSON: {}".format(payload))
        abort(400, "received payload is not JSON: {}".format(payload))

    print('post request: ' + str(request))
    print('payload: ' + str(payload))

    payload['user_id'] = user_id
    payload['event_type'] = event_type

    if event_type == "rr_intervals":
        sql_text = payload_to_sql_post_rrinterval(payload)
    elif event_type in ("activation", "pleasantness"):
        sql_text = payload_to_sql_post_subjective(payload)
    else:
        abort(400, "unknown event type: " + str(event_type))

    run_sql(sql_text)

    json_output = {
        "method": request.method,
        "user_id": user_id,
        "event_type": event_type,
        "payload": payload
    }
    print('json output:' + str(json_output))
    response = make_response(jsonify(json_output), 201)
    return response


def payload_to_sql_post_rrinterval(payload):
    REQUIRED_KEYS = ('mobile_time', 'batch_index', 'value')
    validate_payload_keys(payload, REQUIRED_KEYS)
    sql_text = (
        "INSERT INTO rr_intervals (user_id,mobile_time,batch_index,value) " +
        "VALUES ('{}','{}',{},{})"
        .format(payload['user_id'],
                payload['mobile_time'],
                payload['batch_index'],
                payload['value'])
    )
    return sql_text


def payload_to_sql_post_subjective(payload):
    REQUIRED_KEYS = ('mobile_time', 'value')
    validate_payload_keys(payload, REQUIRED_KEYS)
    # TODO: make sure below SQL complies with spec
    sql_text = (
        "INSERT INTO subjective (user_id,mobile_time,event_type,value) " +
        "VALUES ('{}','{}','{}','{}')"
        .format(payload['user_id'],
                payload['mobile_time'],
                payload['event_type'],
                payload['value'])
    )
    return sql_text


def payload_to_sql_get_rrinterval(payload):
    REQUIRED_KEYS = ('start_time', 'end_time')
    validate_payload_keys(payload, REQUIRED_KEYS)
    # TODO: create spec for this
    sql_text = (
        "SELECT * FROM rr_intervals " +
        "WHERE (user_id = '{}' AND mobile_time BETWEEN '{}' and '{}')"
        .format(payload['user_id'],
                payload['start_time'],
                payload['end_time'])
    )
    return sql_text


def validate_payload_keys(payload, required_keys):
    for k in required_keys:
        if k not in payload:
            abort(400, f"missing required key {k} in posted JSON: {payload}")


@app.route('/users/<user_id>/measurements/<event_type>', methods=['GET'])
def measurement_get(user_id, event_type):
    #*** LAST HERE 3/7: GET is working! make it use ISO datetime format for output. then Then multi value upload (with different sample.json file)

    payload = request.get_json(force=True)
    if type(payload) != dict:
        abort(400, "received payload is not JSON: {}".format(payload))

    payload['user_id'] = user_id
    payload['event_type'] = event_type

    if event_type == "rr_intervals":
        sql_text = payload_to_sql_get_rrinterval(payload)
    else:
        abort(400, "unknown event type: " + str(event_type))

    query_df = pd.read_sql_query(sql_text, db_conn, index_col=[
                                 'user_id', 'mobile_time'])  # ,parse_dates=['mobile_time'])
#        query_df.set_index('mobile_time',drop=False,inplace=True)
    print('query_df: \n' + str(query_df))

    json_response = {
        "method": request.method,
        "user_id": user_id,
        "event_type": event_type,
        "request json": request.json,
        "output json": query_df.to_json(orient='split')  # orient="records")
    }
    print(json_response)
    return make_response(jsonify(json_response), 200)


def connect_saat():
    print(f"Connecting to Postgres database: {PG_USER}@{PG_HOST}/{PG_DB}")
    return psycopg2.connect(user=PG_USER, password=PG_PASS,
                            host=PG_HOST, dbname=PG_DB)


def run_sql(sql_text):
    cur = db_conn.cursor()
    #print(f"executing SQL: {sql_text}")
    try:
        cur.execute(sql_text)
    except psycopg2.Error as e:
        db_conn.rollback()
        print(e.pgerror)
        abort(400,"SQL error: " + e.pgerror)
    db_conn.commit()

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
    db_conn = connect_saat()
    # app.run(debug=True)
    app.run(host="0.0.0.0", debug=True)
