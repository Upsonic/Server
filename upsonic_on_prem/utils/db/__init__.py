from .redis import *


import traceback


from upsonic_on_prem.utils.configs import redis_password, redis_host, redis_port
from upsonic_on_prem.utils.logs import *

import threading

import time



info("Connecting to Redis")


threading.Thread(target=redis_config).start()

time.sleep(5)

succed = False

while not succed:
    try:
        info("Redis configured")
        storage = redis_client_()
        succed = True
    except:
        warning("Redis configuration failed retrying in 5 seconds")
        time.sleep(5)


if storage.status():
    successfully("Redis connection established")
else:
    failed("Redis connection failed")
    traceback.print_exc()
    exit(1)

