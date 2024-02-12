import time

import redis
import random
import os
import traceback

from upsonic_on_prem.utils import storage_2, AI, storage_3, AccessKey

from upsonic_on_prem.utils.configs import admin_key

import cloudpickle
import dill

from cryptography.fernet import Fernet
import base64
import hashlib

import textwrap
import time


class Scope:
    def __init__(self, key):
        self.key = key
        self.the_storage = storage_2

    @property
    def dump_history(self):
        return self.the_storage.get(self.key + ":dump_history") or []

    @property
    def documentation(self):
        return self.the_storage.get(self.key + ":documentation") or "No documentation available."

    def create_documentation(self):
        document = AI.code_to_documentation(self.code)
        self.the_storage.set(self.key + ":documentation", document)


    @property
    def source(self):
        return self.the_storage.get(self.key)["data"]

    @property
    def type(self):
        the_type = type(self.python).__name__
        if the_type == "type":
            the_type = "class"
        return the_type

    @property
    def code(self):
        return textwrap.dedent(dill.source.getsource(self.python))

    @property
    def python(self):
        decrypt = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).decrypt(self.source)
        return cloudpickle.loads(decrypt)

    def dump(self, data, user: AccessKey):
        the_time = str(time.time()) + "_" + str(random.randint(0, 100000))
        sha256 = hashlib.sha256(the_time.encode()).hexdigest()
        key = self.key + ":" + sha256

        data = {"data": data, "user": user.key, "time": the_time}

        storage_3.set(key, data)

        current = self.dump_history
        current.append(key)
        self.the_storage.set(self.key + ":dump_history", current)

        self.the_storage.set(self.key, data)

    @staticmethod
    def get_dump(dump_id):
        the_scope = Scope(dump_id)
        the_scope.the_storage = storage_3
        return the_scope

    @staticmethod
    def get_all_scopes():
        keys = storage_2.keys()
        scopes = []
        for i in keys:
            if not ":" in i:
                scopes.append(i)

        scopes.sort()
        return scopes
