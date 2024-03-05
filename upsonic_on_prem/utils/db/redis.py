import os
import random

import redis

from upsonic_on_prem.utils.configs import redis_host, redis_port, redis_password
from upsonic_on_prem.utils.db.serialization import *


class redis_client_():
    def __init__(self, db=0):
        self.host = redis_host
        self.port = redis_port
        self.password = redis_password
        self.redis = redis.Redis(host=self.host, port=self.port, password=self.password, db=db)
    

    def status(self):
        condition_1 =  self.redis.ping()

        condition_2 = False
        random_key = random.randint(100000, 999999)
        self.set("test", random_key)

        if self.get("test") == random_key:
            condition_2 = True

        return condition_1 and condition_2

    def total_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk("/db/"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        total_size = total_size / 1000000
        return total_size

    def get(self, key):
        result = self.redis.get(key)
        return deserialize(result) if result else None
    

    
    def set(self, key, value):

        return self.redis.set(key, serialize(value))



    def pop(self):
        return self.redis.flushdb()

    def delete(self, key):
        return self.redis.delete(key)

    def keys(self):
        the_keys= self.redis.keys()
        return [i.decode() for i in the_keys] if the_keys else []
   


class redis_config:
    def __init__(self):
        one_time_password = random.randint(100000, 999999)
        self.host = redis_host
        self.port = redis_port
        self.password = redis_password+str(one_time_password)
        self.password_override()
    
        self.config_dump()
        self.service_restart()
        self.service_status()

    def service_status(self):
        os.system("service redis-server status")

        
    def password_override(self):
        global redis_password
        redis_password = self.password


    def service_restart(self):
        os.system("service redis-server restart")           

    def config_dump(self):

        conf = "/etc/redis/redis.conf"
        with open(conf, "w") as f:

                    f.write(f"bind {self.host}\n")
          
                    f.write(f"port {self.port}\n")
                
                    f.write(f"dbfilename storage.rdb\n")

                    f.write(f"dir /db/\n")
      
                    f.write(f"requirepass {self.password}\n")
                    
                    f.write(f"appendonly yes\n")
                    f.write(f"save 60 1000\n")


