PG_HOST = app.config["PG_HOST"]
PG_DB = app.config["PG_DB"]
PG_USER = app.config["PG_USER"]
PG_PASS = app.config["PG_PASS"]

def payload_to_sql_post_rrinterval(payload):
    REQUIRED_KEYS = ('mobile_time', 'batch_index', 'value')
    validate_payload_keys(payload, REQUIRED_KEYS)
    sql_text = (
        "INSERT INTO rr_intervals (user_id,mobile_time,batch_index,value) " +
        "VALUES (%s, %s, %s, %s)", (payload['user_id'],
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
        "VALUES (%s,%s,%s,%s)",
        (payload['user_id'],
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
        "WHERE (user_id = %s AND mobile_time BETWEEN %s and %s)",
        (payload['user_id'],
                payload['start_time'],
                payload['end_time'])
    )
    return sql_text


def validate_payload_keys(payload, required_keys):
    for k in required_keys:
        if k not in payload:
            abort(400, f"missing required key {k} in posted JSON: {payload}")

def connect_saat():
    print(f"Connecting to Postgres database: {PG_USER}@{PG_HOST}/{PG_DB}")
    return psycopg2.connect(user=PG_USER, password=PG_PASS,
                            host=PG_HOST, dbname=PG_DB)


def run_sql(sql_text):
    cur = db_conn.cursor()
    #print(f"executing SQL: {sql_text}")
    try:
        cur.execute(*sql_text)
    except psycopg2.Error as e:
        db_conn.rollback()
        print(e.pgerror)
        abort(400,"SQL error: " + e.pgerror)
    db_conn.commit()


schema_post_rri = {
    "type":"object",
    "properties": {
        "mobile_time":"date-time",
        "batch_index":"integer",
        "value":"integer",
    }
}