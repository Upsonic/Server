import os
import random

import redis

from upsonic_on_prem.api.utils.configs import redis_host, redis_port, redis_password
from upsonic_on_prem.api.utils.db.serialization import *


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
        conf = "/lib/systemd/system/redis-server.service"
        with open(conf, "w") as f:
            f.write("""
[Unit]
Description=Advanced key-value store
After=network.target
Documentation=http://redis.io/documentation, man:redis-server(1)

[Service]
ReadWriteDirectories=-/db
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf --supervised systemd --daemonize no
PIDFile=/run/redis/redis-server.pid
TimeoutStopSec=0
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=2755

UMask=007
PrivateTmp=yes
LimitNOFILE=65535
PrivateDevices=yes
ProtectHome=yes
ReadOnlyDirectories=/
ReadWritePaths=-/var/lib/redis
ReadWritePaths=-/var/log/redis
ReadWritePaths=-/var/run/redis

NoNewPrivileges=true
CapabilityBoundingSet=CAP_SETGID CAP_SETUID CAP_SYS_RESOURCE
MemoryDenyWriteExecute=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

# redis-server can write to its own config file when in cluster mode so we
# permit writing there by default. If you are not using this feature, it is
# recommended that you replace the following lines with "ProtectSystem=full".
ProtectSystem=true
ReadWriteDirectories=-/etc/redis

[Install]
WantedBy=multi-user.target
Alias=redis.service
""")
            

        os.system("systemctl daemon-reload")

        conf = "/etc/redis/redis.conf"
        with open(conf, "w") as f:

                    f.write(f"bind {self.host}\n")
          
                    f.write(f"port {self.port}\n")
                
                    f.write(f"dbfilename storage.rdb\n")

                    f.write(f"dir /db/\n")
      
                    f.write(f"requirepass {self.password}\n")
                    
                    f.write(f"appendonly yes\n")
                    f.write(f"save 60 1000\n")


