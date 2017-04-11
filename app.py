#! /usr/local/bin/python3
import flask
from flask import Flask, jsonify, make_response, abort, request
from flask_cors import CORS, cross_origin
import os
import pandas as pd
import json
import uuid
import pprint  # for debugging
from datetime import datetime, timedelta
from push import push_link
from apscheduler.schedulers.background import BackgroundScheduler
from models import connect_saat, payload_to_sql_post_rrinterval, payload_to_sql_post_subjective, run_sql


# Global app constant (for REST API definition)
app = Flask(__name__, instance_relative_config = True)
# Other app config stuff
#
# Seeeekrit stuff here
app.config.from_object('config')
app.config.from_pyfile('config.py')
# app.secret_key = app.config['SECRET_KEY']
scheduler = BackgroundScheduler()

CORS(app)  # TODO: proabably turn this off for production

db_conn = None

##### Temporary ######
# Only for the hackthon weekend :)
h_users = [{'name': 'watson', 'token': None},
           {'name': 'daniel', 'token': 'o.Gl5W5Vj15Vrki1PlhsTispABgfVPrBnB'},
           {'name': 'logan', 'token': None},
           {'name': 'efrem', 'token': None},
           {'name': 'kaan', 'token': None},
           {'name': 'jean', 'token': 'o.y54hitGOHeS8u96cpOWz9tUwxDS1SKwo'}]


@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')


@app.route('/mood', methods=['GET', 'POST'])
def mood():
    if request.method == 'POST':
        return handle_mood_post()
    else:
        return present_mood_form()


def notification():
    current_hour = int(datetime.utcnow().strftime('%H'))
    appropriate_time = (current_hour > 16) or (current_hour < 4)

    if appropriate_time:
        print('apscheduler running')
        for user in h_users:
            token = user.get('token')
            name = user.get('name')[0].upper() + user.get('name')[1:]
            title = 'Hello ' + name + ','
            body = 'How are you feeling?'
            url = 'http://35.167.145.159:5000/mood'  # !! replace with link to survey
            if token:
                push_link(title, body, url, token)


scheduler.add_job(notification, 'interval', minutes=15)
scheduler.start()


@app.route('/start', methods=['POST'])  # !! needs a UI
def resume():
    scheduler.resume()
    return flask.redirect('/')


@app.route('/pause', methods=['POST'])  # !! needs a UI
def pause():
    scheduler.pause()
    return flask.redirect('/')


def present_mood_form():
    return flask.render_template('mood.html')

def handle_mood_post():
    activation = parseToInt(request.form.get('activation'))
    pleasantness = parseToInt(request.form.get('pleasantness'))
    username = request.form.get('username')
    if (not username):
        return flask.redirect(flask.url_for('mood'))
    else:
        now = datetime.utcnow()
        cur = db_conn.cursor()
        cur.execute("INSERT INTO subjective (user_id, mobile_time, event_type, value) VALUES (%s, %s, %s, %s)", (username, str(now), "pleasantness", pleasantness))
        cur.execute("INSERT INTO subjective (user_id, mobile_time, event_type, value) VALUES (%s, %s, %s, %s)", (username, str(now + timedelta(milliseconds=1)), "activation", activation))
        db_conn.commit()
        print(f"(user, activation, pleasantness) = ({username}, {activation}, {pleasantness})")
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


#TODO: This does not make sense
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
    db_conn = connect_saat(app.config)
    app.run(host="0.0.0.0")
