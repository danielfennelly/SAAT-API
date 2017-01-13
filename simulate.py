from utils import unix_time_millis
from datetime import datetime as dt, timedelta as td, timezone


def generate_heartbeats(start_datetime, end_datetime, bpm):
    """
    Generates an array containing epoch milliseconds for a constant heart rate.
    """
    start_millis = int(unix_time_millis(start_datetime))
    end_millis = int(unix_time_millis(end_datetime))
    heartbeats = [start_millis]
    delta = (1000 * 60) / bpm
    beat = start_millis
    while beat < end_millis:
        beat = int(beat + delta)
        heartbeats.append(beat)
    return heartbeats


if __name__ == "__main__":
    start = dt.now(timezone.utc)
    end = start + td(seconds=60)
    bpm = 80
    print(start)
    print(end)
    print(generate_heartbeats(start, end, bpm))
