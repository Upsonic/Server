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
        for i in self.version_history:
            storage_3.delete(i)            
        self.the_storage.delete(self.key + ":dump_history")
        self.the_storage.delete(self.key + ":documentation")
        self.the_storage.delete(self.key + ":time_complexity")
        self.the_storage.delete(self.key + ":mistakes")
        self.the_storage.delete(self.key + ":required_test_types")
        self.the_storage.delete(self.key + ":tags")
        self.the_storage.delete(self.key + ":security_analysis")
        self.the_storage.delete(self.key + ":code")
        self.the_storage.delete(self.key + ":requirements")
        self.the_storage.delete(self.key + ":version_history")
        self.the_storage.delete(self.key + ":python_version")

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


    @property
    def time_complexity(self):
        return self.the_storage.get(self.key + ":time_complexity")


    @property
    def mistakes(self):
        return self.the_storage.get(self.key + ":mistakes")
    @property
    def required_test_types(self):
        return self.the_storage.get(self.key + ":required_test_types")

    @property
    def tags(self):
        return self.the_storage.get(self.key + ":tags")


    @property
    def security_analysis(self):
        return self.the_storage.get(self.key + ":security_analysis")

    def create_documentation(self):
        document = AI.code_to_documentation(self.code)
        self.the_storage.set(self.key + ":documentation", document)


    def create_time_complexity(self):
        document = AI.code_to_time_complexity(self.code)
        self.the_storage.set(self.key + ":time_complexity", document)

    def create_mistakes(self):
        document = AI.code_to_mistakes(self.code)
        self.the_storage.set(self.key + ":mistakes", document)


    def create_required_test_types(self):
        document = AI.code_to_required_test_types(self.code)
        self.the_storage.set(self.key + ":required_test_types", document)


    def create_tags(self):
        document = AI.code_to_tags(self.code)
        self.the_storage.set(self.key + ":tags", document)


    def create_security_analysis(self):
        document = AI.code_to_security_analysis(self.code)
        self.the_storage.set(self.key + ":security_analysis", document)

    def create_documentation_old(self):
        document = AI.code_to_documentation(self.code_old)
        self.the_storage.set(self.key + ":documentation", document)



    @property
    def source(self):
        the_resource = self.the_storage.get(self.key)
        if the_resource is None:
            return None
        return self.the_storage.get(self.key)["data"]

    @property
    def type(self):
        return self.the_storage.get(self.key + ":type")

    def set_type(self, type):
        return self.the_storage.set(self.key + ":type", type)

    @property
    def python(self):
        if self.source is None:
            return None
        decrypt = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).decrypt(self.source)
        return cloudpickle.loads(decrypt)

    @property
    def code_old(self):
        the_python = self.python
        if the_python is None:
            return None
        return textwrap.dedent(dill.source.getsource(self.python))


    @property
    def code(self):
        return self.the_storage.get(self.key + ":code")

    def set_code(self, code):
        return self.the_storage.set(self.key + ":code", code)

    @property
    def requirements(self):
        return self.the_storage.get(self.key + ":requirements")

    def set_requirements(self, requirements):
        return self.the_storage.set(self.key + ":requirements", requirements)


    @property
    def python_version(self):
        return self.the_storage.get(self.key + ":python_version")

    def set_python_version(self, python_version):
        return self.the_storage.set(self.key + ":python_version", python_version)


    def dump(self, data, user: AccessKey, pass_str=False):
        if not pass_str:
            data = data.decode()
        current_time = time.time()
        the_time = str(current_time) + "_" + str(random.randint(0, 100000))
        sha256 = hashlib.sha256(the_time.encode()).hexdigest()
        key = self.key + ":" + sha256

        data = {"data": data, "user": user.key, "time": current_time,}

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
            if not ":" in i and i != "":
                scopes.append(i)

        scopes.sort()
        return scopes

    @staticmethod
    def get_all_scopes_name(user: AccessKey):
        all_scopes = Scope.get_all_scopes()

        custom_scopes_read = user.scopes_read
        result = []

        for i in all_scopes:
            if user.can_access_read(i, custom_scopes_read=custom_scopes_read) or user.is_admin:
                result.append(i)

        return result

    @staticmethod
    def get_all_scopes_name_prefix(user, prefix):
        all_scopes = Scope.get_all_scopes_name(user)

        return [i for i in all_scopes if i.startswith(prefix)]





    @staticmethod
    def get_all_scopes_with_documentation():
        all_scopes = Scope.get_all_scopes()

        result = []
        for i in all_scopes:
            the_scope = Scope(i)
            element = {"name": i, "documentation": str(the_scope.documentation) + " " + str(the_scope.tags)}
            result.append(element)

        return result
