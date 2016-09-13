import json
from flask import make_response
import iso8601
from datetime import datetime as dt, timezone

epoch = dt.fromtimestamp(0, timezone.utc)


def unix_time_millis(dt):
	return (dt - epoch).total_seconds() * 1000.0

def parse_datetime(datetime_string):
	try:
		return iso8601.parse_date(datetime_string)
	except:
		# TODO: Log Parse Failures?
		return None


def json_response(message, status_code=200):
    response = make_response(json.dumps(message), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response
