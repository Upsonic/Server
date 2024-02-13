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

    def delete(self):
        self.the_storage.delete(self.key)
        for i in self.dump_history:
            storage_3.delete(i)
        self.the_storage.delete(self.key + ":dump_history")
        self.the_storage.delete(self.key + ":documentation")


    @property
    def dump_history(self):
        return self.the_storage.get(self.key + ":dump_history") or []

    @property
    def version_history(self):
        return self.the_storage.get(self.key + ":version_history") or []

    def create_version(self, version, user: AccessKey):
        current_time = time.time()
        current = self.version_history

        key = self.key + ":" + str(version)

        data = {"data": self.source, "user": user.key, "time": current_time}

        storage_3.set(key, data)

        current.append(key)

        self.the_storage.set(self.key + ":version_history", current)

    @staticmethod
    def get_version(version_id):
        the_scope = Scope(version_id)
        the_scope.the_storage = storage_3
        return the_scope

    @property
    def documentation(self):
        return self.the_storage.get(self.key + ":documentation")

    def create_documentation(self):
        document = AI.code_to_documentation(self.code)
        self.the_storage.set(self.key + ":documentation", document)


    @property
    def source(self):
        the_resource = self.the_storage.get(self.key)
        if the_resource is None:
            return None
        return self.the_storage.get(self.key)["data"]

    @property
    def type(self):
        if self.python is None:
            return None
        the_type = type(self.python).__name__
        if the_type == "type":
            the_type = "class"
        return the_type

    @property
    def code(self):
        the_python = self.python
        if the_python is None:
            return None
        return textwrap.dedent(dill.source.getsource(self.python))

    @property
    def python(self):
        if self.source is None:
            return None
        decrypt = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).decrypt(self.source)
        return cloudpickle.loads(decrypt)

    def dump(self, data, user: AccessKey):
        current_time = time.time()
        the_time = str(current_time) + "_" + str(random.randint(0, 100000))
        sha256 = hashlib.sha256(the_time.encode()).hexdigest()
        key = self.key + ":" + sha256

        data = {"data": data, "user": user.key, "time": current_time}

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


    @staticmethod
    def get_all_scopes_name(user: AccessKey):
        all_scopes = Scope.get_all_scopes()

        custom_scops_read = user.scopes_read
        result = []

        for i in all_scopes:
            if user.can_access_read(i, custom_scopes_read=custom_scops_read):
                result.append(i)

        return result

    @staticmethod
    def get_all_scopes_name_prefix(user, prefix):
        all_scopes = Scope.get_all_scopes()

        return [i for i in all_scopes if i.startswith(prefix)]

