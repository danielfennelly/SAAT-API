from flask import Flask, request, render_template
from utils import json_response, parse_datetime, unix_time_millis

app = Flask(__name__)

heartbeat_array = []

def get_heartbeats():
	start = parse_datetime(request.args.get('start'))
	end = parse_datetime(request.args.get('end'))
	if start and end:
		start_millis = unix_time_millis(start)
		end_millis = unix_time_millis(end)
		compare = lambda t: t > start_millis and t < end_millis
		subset = list(filter(compare, heartbeat_array))
		return json_response(subset)
	else:
		return json_response('Bad Request', 400)

def post_heartbeats():
	posted_json = request.get_json(force=True)
	start = parse_datetime(posted_json['start'])
	end = parse_datetime(posted_json['end'])
	beats = posted_json['beats']
	heartbeat_array.extend(beats)
	return json_response('Posted heartbeats')

def delete_heartbeats():
	start = parse_datetime(request.args.get('start'))
	end = parse_datetime(request.args.get('end'))
	if start and end:
		start_millis = unix_time_millis(start)
		end_millis = unix_time_millis(end)
		compare = lambda t: not (t > start_millis and t < end_millis)
		heartbeat_array = list(filter(compare, heartbeat_array))
	else:
		return json_response('Bad Request', 400)

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

@app.route('/', methods=['GET'])
def show_heartbeats():
        return render_template('index.html')

