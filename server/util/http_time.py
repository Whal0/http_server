from datetime import datetime, timezone


def datetime_to_string(date: datetime) -> str:
    return date.strftime('%a, %d %b %Y %H:%M:%S GMT')

def string_to_datetime(sdate: str) -> datetime:
    return datetime.strptime(sdate, '%a, %d %b %Y %H:%M:%S GMT')

# FORMAT: Sun, 06 Nov 1994 08:49:37 GMT; RFC 822, updated by RFC 1123
def get_date_from_timestamp(ts: int) -> datetime:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

# used on dates we have not generated
def format_date(dt: datetime) -> datetime:
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

