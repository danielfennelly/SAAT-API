# SAAT-API

This repository contains code for a [Flask](http://flask.pocoo.org/docs/0.11/) API server for persisting and fetching heartbeat data. At the present time, this is just stored in an in-memory Python list.

## Running the server locally

You'll want to [install virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to manage dependencies. Create a Python 3 virtual environment named `venv` and then use the new environment's `pip` to install dependencies like so:

    venv/bin/pip install -r requirements.txt
    
With Flask installed, the following commands can be used to start up a reloading server in debug mode. Note that if changes are made to the app while running, the memory of previously posted heartbeat data will be lost.

    export FLASK_APP=app.py
    export FLASK_DEBUG=true
    flask run

## Interacting with the server

The `curl` commands below demonstrate basic interaction with the API. The only API endpoint is at `/heartbeats` and data can be created or fetched with `POST` and `GET` requests respectively. See the `sample_post.json` file for an example.

    curl -i -X POST localhost:5000/heartbeats -H "Content-Type: application/json" --data-binary "@sample_post.json"

    curl -i -X GET 'localhost:5000/heartbeats?start=2016-09-13T13:09:28Z&end=2016-09-13T13:10:28Z' -H "Content-Type: application/json"

## Troubleshooting Dependencies

If you're getting cryptic "Reason: image not found" errors when trying to import `psycopg2`, you might need the following fix.

    export DYLD_FALLBACK_LIBRARY_PATH=$HOME/anaconda3/lib/:$DYLD_FALLBACK_LIBRARY_PATH
    
See this [stack overflow question](http://stackoverflow.com/questions/27264574/import-psycopg2-library-not-loaded-libssl-1-0-0-dylib) for details.
