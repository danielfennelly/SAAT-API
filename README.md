# SAAT-API

This repository contains code for a [Flask](http://flask.pocoo.org/docs/0.11/) API server for persisting and fetching heartbeat and subjective psychological data from a Postgres database via the Psycopg2 and Pandas Python packages.

## Running the server locally

You'll first need [Postgres 9.6](https://www.postgresql.org/) installed on your machine. If you are on OSX and use Homebrew, just do `brew update` then `brew install postgres`.

Next create a postgres database and load the schema:
```sh
# Connect to management database to enter the psql prompt
psql postgres
# Create the database
create database saatdb01;
# Disconnect to leave psql
\q
# Load the schema
psql -d "postgresql://@localhost:5432/saatdb01" < schema.sql
```

Then you'll want to [install virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to manage Python dependencies. Create a Python 3.6 virtual environment named `venv` and then use the new environment's `pip` to install dependencies like so:

    venv/bin/pip install -r requirements.txt
    
With Flask installed, the following commands can be used to start up a reloading server in debug mode. 

    export FLASK_APP=app.py
    export FLASK_DEBUG=true
    export PG_USER=$(whoami)
    flask run

You will need to create a local instances folder with a configuration like so:

    mkdir instances
    cp config.py instances
    
Edit the values in config.py to reflect your local database credentials.

## Interacting with the server

The `curl` commands below demonstrate basic interaction with the API. RR interval data can be created or fetched with `POST` and `GET` requests respectively. See the below referenced JSON files for examples.

	curl -i -X POST localhost:5000/users/watson/measurements/rr_intervals -H "Content-Type: application/json" --data-binary "@sample_post_single_rri.json"

	curl -i -X GET localhost:5000/users/watson/measurements/rr_intervals -H "Content-Type: application/json" --data-binary "@sample_get_rri.json"

## Troubleshooting Dependencies

If you're getting cryptic "Reason: image not found" errors when trying to import `psycopg2`, you might need the following fix.

    export DYLD_FALLBACK_LIBRARY_PATH=$HOME/anaconda3/lib/:$DYLD_FALLBACK_LIBRARY_PATH

See this [stack overflow question](http://stackoverflow.com/questions/27264574/import-psycopg2-library-not-loaded-libssl-1-0-0-dylib) for details.

## Connecting to the prod DB

The app loads postgres connection params from environment variables.
If you'd like to connect to the prod database, find the credentials in
the file `saat-api.sh` in the SAAT-Internal repo.

Pre load them into your shell:

```sh
source saat-api.sh
```

then run the app:

```sh
python app.py
```

You can also run it like this:

```sh
PG_HOST=bla.bla.us-west-2.rds.amazonaws.com PG_DB=YourSweetDB PG_USER=YourCoolUser PG_PASS=Blabla python app.py
```
