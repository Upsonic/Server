import contextlib
import requests
import time
import unittest
import os
import sys
import shutil
import copy
from unittest.mock import patch
import cloudpickle
import threading
from waitress.server import create_server

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from upsonic_on_prem.api import app
from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import AccessKey
from upsonic_on_prem.utils import storage



from requests.auth import HTTPBasicAuth


all_urls = [dump_url, load_url, get_admins_url, status_url]
admin_urls = [get_admins_url]
user_urls = [dump_url, load_url]




from cryptography.fernet import Fernet
import base64
import hashlib



class Test_Storage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = create_server(app, host="localhost", port=7777)
        cls.proc = threading.Thread(target=cls.result.run)
        cls.proc.start()
        storage.pop()

    @classmethod
    def tearDownClass(cls):
        cls.result.close()

    
    def test_unauthorized_access_status(self):
        for url in [status_url]:
            id = "test_unauthorized_access_status"+url
            the_access_key =  AccessKey(id)

            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)

            the_access_key.enable()
            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))

            self.assertEqual(response.status_code, 200)

            the_access_key.disable()
            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)

    def test_unauthorized_access(self):
        for url in all_urls:
            id = "test_unauthorized_access"+url
            the_access_key =  AccessKey(id)

            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)



    def test_user_area_access(self):
        for url in user_urls:
            id = "test_user_area_access"+url
            the_access_key =  AccessKey(id)
            

            response = requests.post("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)

            the_access_key.enable()


        
            response = requests.post("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
  
            self.assertNotEqual(response.status_code, 403)



    def test_admin_area_restriction(self):
        for url in admin_urls:
            id = "test_admin_area_restriction"+url
            the_access_key =  AccessKey(id)
            the_access_key.enable()

            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)

            the_access_key.set_is_admin(True)
            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 200)

            the_access_key.set_is_admin(False)

            response = requests.get("http://localhost:7777"+url, auth=HTTPBasicAuth("", id))
            self.assertEqual(response.status_code, 403)




    def test_user_dump_load(self):
        dumped_data = None
        loaded_data = None

        def my_function():
            return True

        for url in [dump_url]:
            id = "test_user_dump_load"
            the_access_key =  AccessKey(id)


            dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(cloudpickle.dumps(my_function))

            scope = "onur.my_function"
            data = {"scope": scope, "data": dumped_data}

            the_access_key.enable()
            the_access_key.set_scope_write(scope)
            the_access_key.set_scope_read(scope)


        
            response = requests.post("http://localhost:7777"+url, auth=HTTPBasicAuth("", id), data=data)





        for url in [load_url]:
            id = "test_user_dump_load"
            the_access_key =  AccessKey(id)

            dumped_data = cloudpickle.dumps(my_function)
            scope = "onur.my_function"
            data = {"scope": scope,}

            the_access_key.enable()


        
            response = requests.post("http://localhost:7777"+url, auth=HTTPBasicAuth("", id), data=data)

            loaded_data = response.content

            loaded_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).decrypt(loaded_data)




        self.assertEqual(dumped_data, loaded_data)
        self.assertEqual(cloudpickle.loads(loaded_data)(), True)





    def test_add_admin(self):
        id = "test_add_admin"
        id_admin = "test_add_admin_admin"
        the_admin_access_key =  AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        
        # Testing to access get_admins_url and expected to get 403
        response = requests.get("http://localhost:7777"+get_admins_url, auth=HTTPBasicAuth("", id), )
        self.assertEqual(response.status_code, 403)


        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post("http://localhost:7777"+add_admin_url, auth=HTTPBasicAuth("", id_admin), data=data)



        # Testing to access get_admins_url and expected to get 200
        response = requests.get("http://localhost:7777"+get_admins_url, auth=HTTPBasicAuth("", id), )
        self.assertEqual(response.status_code, 200)




backup = sys.argv
sys.argv = [sys.argv[0]]
unittest.main(exit=False)
sys.argv = backup