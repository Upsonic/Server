import time

import redis
import random
import os
import traceback

from upsonic_on_prem.utils import storage_2

from upsonic_on_prem.utils.configs import admin_key

import cloudpickle
import dill

from cryptography.fernet import Fernet
import base64
import hashlib

import textwrap


class Scope:
    def __init__(self, key):
        self.key = key

    @property
    def source(self):
        return storage_2.get(self.key)

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

    def dump(self, data):
        storage_2.set(self.key, data)
