import psycopg2
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
from itertools import cycle

try:
    PG_HOST = os.environ["PG_HOST"]
except KeyError:
    PG_HOST = ""
try:
    PG_DB = os.environ["PG_DB"]
except KeyError:
    PG_DB = ""
try:
    PG_USER = os.environ["PG_USER"]
except KeyError:
    PG_USER = ""
try:
    PG_PASS = os.environ["PG_PASS"]
except KeyError:
    PG_PASS = ""


def connect_saat():
    # print(f"Connecting to Postgres database: {PG_USER}@{PG_HOST}/{PG_DB}")
    return psycopg2.connect(user=PG_USER, password=PG_PASS,
                            host=PG_HOST, dbname=PG_DB)


def user_walker(initial=100, chunk=10, skip=0):
    conn = connect_saat()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT mobile_time, value, user_id from rr_intervals ORDER BY mobile_time ASC")
        if skip > 0:
            cur.fetchmany(skip)
        yield cur.fetchmany(initial)
        out = cur.fetchmany(chunk)
        while out is not None:
            yield out
            out = cur.fetchmany(chunk)


def user_walker_date_interval(initial=200, increment=10):
    conn = connect_saat()
    with conn.cursor() as cur:
        cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                    "ORDER BY mobile_time ASC LIMIT %s", (initial,))
        out = cur.fetchall()
        yield out
        while out is not None: # This will stop as soon as it doesn't get a return
            last_dt = out[-1][0]
            cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                        "WHERE mobile_time > %s ORDER BY mobile_time ASC " +
                        "LIMIT %s", (last_dt, 2))
            out = cur.fetchall()
            yield out


user_colors = {
    'jean': "DarkCyan",
    'daniel': "LimeGreen",
    'watson': "Red",
    'logan': "RoyalBlue",
    'efrem': "DarkOrchid",
    'kaan': "DarkOrange",
}

def user_walker_realtime_mode(initial=2000):
    conn = connect_saat()
    with conn.cursor() as cur:
        cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                    "ORDER BY mobile_time DESC LIMIT %s", (initial,))
        out = cur.fetchall()
        yield reversed(out)
        last_dt = out[0][0]
        user_cycler = cycle(user_colors.keys())
        user_last_times = {}
        for user in user_colors.keys():
            user_last_times[user] = last_dt
        for user in user_cycler:
            cur.execute("SELECT mobile_time, value, user_id from rr_intervals " +
                        "WHERE user_id = %s AND " +
                        "mobile_time > %s ORDER BY mobile_time ASC ", 
                        (user, user_last_times[user]))
            out = cur.fetchall()
            if not out:
                yield None
            else:
                yield out
                user_last_times[user] = out[-1][0]

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
