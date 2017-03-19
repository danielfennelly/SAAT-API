import psycopg2
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

try:
    PG_HOST = os.environ["PG_HOST"]
except KeyError:
    PG_HOST = "tf-201611180437251236751897ul.chhanozbpeca.us-west-2.rds.amazonaws.com"
try:
    PG_DB = os.environ["PG_DB"]
except KeyError:
    PG_DB = "saatdb01"
try:
    PG_USER = os.environ["PG_USER"]
except KeyError:
    PG_USER = "saat"
try:
    PG_PASS = os.environ["PG_PASS"]
except KeyError:
    PG_PASS = "CHANGEME"


def connect_saat():
    # print(f"Connecting to Postgres database: {PG_USER}@{PG_HOST}/{PG_DB}")
    return psycopg2.connect(user=PG_USER, password=PG_PASS,
                            host=PG_HOST, dbname=PG_DB)


def user_walker(initial=100, chunk=3):
    conn = connect_saat()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT mobile_time, value from rr_intervals WHERE user_id = 'watson' ORDER BY mobile_time ASC")
        yield cur.fetchmany(initial)
        out = cur.fetchmany(chunk)
        while out is not None:
            yield out
            out = cur.fetchmany(chunk)


def user_walker_date_interval(initial=5, increment=5):
    conn = connect_saat()
    with conn.cursor() as cur:
        cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                    "ORDER BY mobile_time ASC LIMIT %s", (initial,))
        out = cur.fetchall()
        yield out
        while out is not None: # This will stop as soon as it doesn't get a return
            last_dt = out[-1][0]
            cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                        "mobile_time > %s ORDER BY mobile_time ASC " +
                        "LIMIT %s", (last_dt, 2))
            out = cur.fetchall()
            yield out

# def retrieve_initial(limit=100):
#     with db_cur() as cur:
#         cur.execute("SELECT mobile_time, value from rr_intervals WHERE user_id = 'watson' ORDER BY mobile_time ASC LIMIT %s",
#             (limit,))
#         out = cur.fetchall()
#     return out

# def retrieve_next(from_time, num=3):
#     with db_cur() as cur:
#         cur.execute("SELECT mobile_time, value from rr_intervals WHERE user_id = 'watson' AND mobile_time > %s ORDER BY mobile_time ASC LIMIT %s",
#             (from_time, num,))
#         out = cur.fetchall()
#     return out
