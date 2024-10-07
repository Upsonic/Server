from .redis import *


import traceback


from upsonic_on_prem.api.utils.configs import redis_password, redis_host, redis_port
from upsonic_on_prem.api.utils.logs import *
from upsonic_on_prem.api.tracer import tracer
from opentelemetry.trace import Status, StatusCode
import threading

import time


with tracer.start_span("redis-startup") as span:
    info("Connecting to Redis")

    def can_access_to_config():
        try:
            os.listdir("/etc/redis/")
            return True
        except:
            return False

    if can_access_to_config() and redis_host == "localhost":
        threading.Thread(target=redis_config).start()
        time.sleep(2)

    succed = False
    the_exception = None
    while not succed:
        try:
            info("Redis configured")
            storage = redis_client_()
            storage_2 = redis_client_(db=1)
            storage_3 = redis_client_(db=2)
            storage_4 = redis_client_(db=2)
            storage_5 = redis_client_(db=2)
            storage_ai_history = redis_client_(db=3)
            succed = True
        except Exception as ex:
            the_exception = ex
            warning("Redis configuration failed retrying in 5 seconds")
            time.sleep(5)

    if storage.status():
        successfully("Redis connection established")
        span.set_status(Status(StatusCode.OK))
    else:
        failed("Redis connection failed")
        span.set_status(Status(StatusCode.ERROR))
        span.record_exception(the_exception)
        traceback.print_exc()
        exit(1)
