from functools import wraps


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
