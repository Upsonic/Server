from .redis import *


import traceback


from upsonic_on_prem.api.utils.configs import redis_password, redis_host, redis_port
from upsonic_on_prem.api.utils.logs import *

import threading

import time



info("Connecting to Redis")


def can_access_to_config():
    try:
        os.listdir("/etc/redis/")
        return True
    except:
        return False

if can_access_to_config():
    threading.Thread(target=redis_config).start()
    time.sleep(2)

succed = False

while not succed:
    try:
        info("Redis configured")
        storage = redis_client_()
        storage_2 = redis_client_(db=1)
        storage_3 = redis_client_(db=2)
        storage_4 = redis_client_(db=2)
        storage_5 = redis_client_(db=2)
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

