#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast

from rich.console import Console

console = Console()

from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv(dotenv_path=".env")

admin_key = os.environ.get("admin_key")


class Upsonic_Cloud_Utils:
    def _log(self, message):
        console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def create_database(self, name):
        return (
                "DB_" + name + "_"
                + (((Fernet.generate_key()).decode()).replace("-", "").replace("_", "").replace("=", ""))[
                  :50
                  ]
        )  # pragma: no cover

    def create_access_key(self, ):
        return (
                "ACK_" + (((Fernet.generate_key()).decode()).replace("-", "").replace("_", "").replace("=", ""))[
                         :60
                         ]
        )  # pragma: no cover

    def create_read_only_access_key(self, ):
        return (
                "R-ACK_" + (((Fernet.generate_key()).decode()).replace("-", "").replace("_", "").replace("=", ""))[
                           :60
                           ]
        )  # pragma: no cover

    def __init__(self):
        import requests
        from requests.auth import HTTPBasicAuth

        self.verify = cloud_utils_ssl_verify

        from upsonic import console

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth

        self._log(
            f"[bold white]Upsonic Cloud Utils[bold white] initializing...",
        )

        from upsonic import encrypt, decrypt
        self.encrypt = encrypt
        self.decrypt = decrypt

        self.api_url = cloud_utils_url
        self.password = cloud_utils_access_key

        self._log(
            f"[bold green]Upsonic Cloud[bold green] active",
        )

    def _send_request(self, method, endpoint, data=None, make_json=True):
        try:
            response = self.requests.request(
                method,
                self.api_url + endpoint,
                data=data,
                auth=self.HTTPBasicAuth("", self.password),
                verify=self.verify
            )
            try:
                return response.text if not make_json else json.loads(response.text)
            except:  # pragma: no cover
                print(f"Error on '{self.api_url + endpoint}': ", response.text)
                return [None]  # pragma: no cover
        except:
            print("Error: Remote is down")
            return [None]

    def get_database(self, access_key):
        data = {"access_key": access_key}
        result = self._send_request("POST", "/get/databases", data)
        return result[0]

    def get_content(self, database_name):
        data = {"database_name": database_name}
        result = self._send_request("POST", "/get/keys", data)
        return result[0]

    def get_a_content(self, database_name, key):
        data = {"database_name": database_name, "key": key}
        result = self._send_request("POST", "/get/key", data)
        return result[0]

    def count_content(self, database_name):
        data = {"database_name": database_name}
        result = self._send_request("POST", "/count/key", data)
        return result[0]

    def edit_content(self, database_name, key, value):
        data = {"database_name": database_name, "key": key, "value": value}
        result = self._send_request("POST", "/edit/key", data)
        return result[0]

    def delete_content(self, database_name, key, custom_user):
        data = {"database_name": database_name, "key": key, "custom_user": custom_user}
        result = self._send_request("POST", "/delete/key", data)
        return result[0]

    def rename_database(self, database_name, new_database_name):
        data = {"database_name": database_name, "new_database_name": new_database_name}
        result = self._send_request("POST", "/rename/database", data)
        return result[0]

    def delete_database(self, database_name, custom_user):
        data = {"database_name": database_name, "custom_user": custom_user}
        result = self._send_request("POST", "/delete/database", data)
        return result[0]

    def pop_database(self, database_name):
        data = {"database_name": database_name}
        result = self._send_request("POST", "/pop/database", data)
        return result[0]

    def get_access_keys(self, cloud_type):
        data = {"cloud_type": cloud_type}
        result = self._send_request("POST", "/get/access_key", data)
        return result[0]

    def add_access_keys(self, cloud_type, access_key):
        data = {"cloud_type": cloud_type, "access_key": access_key}
        result = self._send_request("POST", "/add/access_key", data)
        return result[0]

    def remove_access_keys(self, cloud_type, access_key):
        data = {"cloud_type": cloud_type, "access_key": access_key}
        result = self._send_request("POST", "/remove/access_key", data)
        return result[0]

    def check_access_keys(self, cloud_type, access_key):
        data = {"cloud_type": cloud_type, "access_key": access_key}
        result = self._send_request("POST", "/check/access_key", data)
        return result[0]

    def add_runner(self, uniq_name, database_name, encryption_key, access_key, cloud_type):
        data = {"uniq_name": uniq_name, "database_name": database_name, "encryption_key": encryption_key,
                "access_key": access_key, "cloud_type": cloud_type}
        result = self._send_request("POST", "/add/runner", data)
        return result[0]

    def log_runner(self, uniq_name, database_name):
        data = {"uniq_name": uniq_name, "database_name": database_name}
        result = self._send_request("POST", "/log/runner", data)
        return result[0]

    def status_runner(self, uniq_name, database_name):
        data = {"uniq_name": uniq_name, "database_name": database_name}
        result = self._send_request("POST", "/status/runner", data)
        return result[0]

    def get_runner(self, uniq_name, database_name):
        data = {"uniq_name": uniq_name, "database_name": database_name}
        result = self._send_request("POST", "/get/runner", data)
        return result[0]

    def remove_runner(self, uniq_name, database_name):
        data = {"uniq_name": uniq_name, "database_name": database_name}
        result = self._send_request("POST", "/remove/runner", data)
        return result[0]
