from unittest import TestCase, main
import psycopg2
import json
from datetime import datetime
import app


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# THESE TESTS WILL DELETE THE DB TABLES!
# DO NOT RUN ON PRODUCTION DB!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class AppApiTests(TestCase):

    def connectDB(self):
        return psycopg2.connect(dbname="vagrant")

    def resetDB(self):
        with open("schema.sql", 'r') as f:
            create_sql = f.read()
        with self.connectDB() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE rr_intervals")
                cur.execute("DROP TABLE subjective")
                cur.execute(create_sql)

    def setUp(self):
        # Manually set database config params to vagrant only DB
        app.app.config["DATABASE"] = 'vagrant'
        for item in ["PG_HOST", "PG_USER", "PG_PASS"]:
            app.app.config[item] = ""
        app.app.config["TESTING"] = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.get_db()
        self.resetDB()

    def tearDown(self):
        self.resetDB()

    def test_add_rr_interval(self):
        data = {
            "mobile_time": "2016-09-13T13:09:28Z",  # What's with the Z at the end????
            "batch_index": 1,
            "value": 667
        }
        url = "/users/watson/measurements/rr_intervals"
        rv = self.app.post(url, data=json.dumps(
            data), content_type="application/json")
        self.assertEqual(rv.status_code, 201)
        with self.connectDB() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, mobile_time, batch_index, value FROM rr_intervals")
                db = cur.fetchall()
        self.assertEqual(len(db), 1)
        db = db[0]
        self.assertEqual(db[0], "watson")
        db_dict = {"mobile_time": db[1], "batch_index": db[2], "value": db[3]}
        dt = db_dict["mobile_time"]
        # This extra timezone info makes it extremely hard to compare objects,
        # just removing it
        db_dict["mobile_time"] = datetime(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        db_dict["mobile_time"] = db_dict[
            "mobile_time"].isoformat(timespec="seconds")
        data["mobile_time"] = data["mobile_time"][:-1]
        self.assertDictEqual(db_dict, data)

    def test_add_mood(self):
        data = {
            "username": "me",
            "activation": "-1",
            "pleasantness": "1"
        }
        url = "/mood"
        rv = self.app.post(url, data=data)
        now = datetime.now()
        self.assertEqual(rv.status_code, 302)
        with self.connectDB() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, event_type, value FROM subjective")
                db = cur.fetchall()
                cur.execute("SELECT mobile_time FROM subjective")
                dates = cur.fetchall()
        self.assertEqual(len(db), 2)
        self.assertIn((data['username'], "pleasantness",
                       int(data['pleasantness'])), db)
        self.assertIn((data['username'], "activation", int(data['activation'])), db)
        # Check times only to the minute
        minute_now = datetime(now.year, now.month,
                              now.day, now.hour, now.minute)
        dates = [datetime(item[0].year, item[0].month, item[0].day,
                          item[0].hour, item[0].minute) for item in dates]
        self.assertTrue(all(minute_now == item for item in dates))


if __name__ == "__main__":
    main()
