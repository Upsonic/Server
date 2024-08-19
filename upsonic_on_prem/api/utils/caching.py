# Create an decorator and this decarator will cache the response of the function for a given time.

import functools
import time
from typing import Any, Callable, Dict


cache = {}

def cache_response(seconds: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            global cache
            key = f"{func.__name__}"
            if key in cache and time.time() - cache[key]["time"] < seconds:
                return cache[key]["value"]
            value = func(*args, **kwargs)
            cache[key] = {"time": time.time(), "value": value}
            return value
        return wrapper
    return decorator


