from .redis import *


import traceback


from upsonic_on_prem.utils.configs import redis_password, redis_host, redis_port
from upsonic_on_prem.utils.logs import *







redis_config()
storage = redis_client_()
if storage.status():
    successfully("Redis connection established")
else:
    failed("Redis connection failed")
    traceback.print_exc()
    exit(1)

