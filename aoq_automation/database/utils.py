from functools import wraps
from datetime import datetime


def raises_only(exception):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise exception(*e.args)

        return wrapper

    return decorator


def parse_time_as_seconds(timestamp: str) -> float:
    possible_formats = [
        "%H:%M:%S.%f",
        "%M:%S.%f",
        "%S.%f",
        "%H:%M:%S",
        "%M:%S",
        "%S",
    ]
    seconds = None
    for format in possible_formats:
        try:
            t = datetime.strptime(timestamp, format).time()
            seconds = (
                t.microsecond / 1000000 + t.second + 60 * (t.minute + 60 * (t.hour))
            )
            break
        except ValueError:
            continue
    if seconds is not None:
        return seconds
    raise ValueError()
