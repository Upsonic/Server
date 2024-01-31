import os
import random

import redis

from upsonic_on_prem.utils.configs import redis_host, redis_port
from upsonic_on_prem.utils.db.serialization import *


class redis_client_():
    def __init__(self):
        self.host = redis_host
        self.port = redis_port
        self.password = redis_password
        self.redis = redis.Redis(host=self.host, port=self.port, password=self.password)
    

    def status(self):
        condition_1 =  self.redis.ping()

        condition_2 = False
        self.set("test", "test")

        if self.get("test") == "test":
            condition_2 = True

        return condition_1 and condition_2


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

        
    def password_override(self):
        global redis_password
        redis_password = self.password


    def service_restart(self):
        os.system("service redis-server restart")           

    def config_dump(self):
        system_conf = "/etc/systemd/system/redis.service.d/override.conf"
        # if not create a file
        if not os.path.exists(system_conf):
            os.makedirs(os.path.dirname(system_conf), exist_ok=True)
            open(system_conf, "w").close()

        with open(system_conf, "w") as f:
            f.write(f"[Service]\n")
            f.write(f"ReadWriteDirectories=-/data/\n")

        os.system("systemctl daemon-reload")

        conf = "/etc/redis/redis.conf"
        with open(conf, "w") as f:

                    f.write(f"bind {self.host}\n")
          
                    f.write(f"port {self.port}\n")
                
                    f.write(f"dbfilename storage.rdb\n")
              
                    f.write(f"dir /data/\n")
      
                    f.write(f"requirepass {self.password}\n")
                    
                    f.write(f"appendonly yes\n")
                    f.write(f"save 60 1000\n")


