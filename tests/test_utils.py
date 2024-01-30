import contextlib
import time
import unittest
import os
import sys
import shutil
import copy
from unittest.mock import patch
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from upsonic_on_prem.utils import storage
from upsonic_on_prem.utils import AccessKey


class Test_Storage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        storage.pop()

    def test_status(self):
        self.assertTrue(storage.status())



    def test_set(self):
        storage.set("test", "test")
        self.assertEqual(storage.get("test"), "test")


    def test_delete(self):
        storage.delete("test")
        self.assertEqual(storage.get("test"), None)


    def test_pop(self):
        storage.set("test", "test")
        self.assertEqual(storage.get("test"), "test")
        storage.pop()
        self.assertEqual(storage.get("test"), None)
        




class Test_Accesskey(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
            storage.pop()
    


    def test_name(self):
        id = "test_name"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.name, None)
        accesskey.set_name("test")
        self.assertEqual(accesskey.name, "test")


    def test_scope_write(self):
        id = "test_scope"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_write, [])
        accesskey.set_scope_write("onur.*")
        accesskey.set_scope_write("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_write, ["onur.*", "onur.mehmet.*"])


    def test_scope_read(self):
        id = "test_scope"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_read, [])
        accesskey.set_scope_read("onur.*")
        accesskey.set_scope_read("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_read, ["onur.*", "onur.mehmet.*"])


    def test_is_admin(self):
        id = "test_is_admin"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.is_admin, False)
        accesskey.set_is_admin(True)
        self.assertEqual(accesskey.is_admin, True)



    def test_can_access_write_star(self):
        id = "test_can_access"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.can_access_write("onur.ulusoy"), False)
        accesskey.set_scope_write("onur.*")
        self.assertEqual(accesskey.can_access_write("onur.ulusoy"), True)
        self.assertEqual(accesskey.can_access_write("onur.mehmet"), True)
        self.assertEqual(accesskey.can_access_write("ahmet.mehmet"), False)
        accesskey.set_scope_write("ahmet.mehmet")
        self.assertEqual(accesskey.can_access_write("ahmet.mehmet"), True)
        self.assertEqual(accesskey.can_access_write("ahmet.mehmet.cengiz"), False)


        self.assertEqual(accesskey.can_access_write("oo.aa.bb.cc"), False)
        accesskey.set_scope_write("oo.aa.bb")
        self.assertEqual(accesskey.can_access_write("oo.aa.bb.cc"), False)
        accesskey.set_scope_write("oo.aa.bb.dd")
        self.assertEqual(accesskey.can_access_write("oo.aa.bb.cc"), False)
        self.assertEqual(accesskey.can_access_write("oo.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_write("oo.aa"), False)



        self.assertEqual(accesskey.can_access_write("nn.aa.bb.cc"), False)
        accesskey.set_scope_write("nn.aa.bb.*")
        self.assertEqual(accesskey.can_access_write("nn.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_write("nn.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_write("nn.aa"), False)

        self.assertEqual(accesskey.can_access_write("tt.aa.bb.cc"), False)
        accesskey.set_scope_write("tt.*")
        self.assertEqual(accesskey.can_access_write("tt.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_write("tt.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_write("tt.aa"), True)



        self.assertEqual(accesskey.can_access_write("ee.aa.bb.cc"), False)
        accesskey.set_scope_write("*")
        self.assertEqual(accesskey.can_access_write("ee.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_write("ee.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_write("ee.aa"), True)


    def test_can_access_read_star(self):
        id = "test_can_access"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.can_access_read("onur.ulusoy"), False)
        accesskey.set_scope_read("onur.*")
        self.assertEqual(accesskey.can_access_read("onur.ulusoy"), True)
        self.assertEqual(accesskey.can_access_read("onur.mehmet"), True)
        self.assertEqual(accesskey.can_access_read("ahmet.mehmet"), False)
        accesskey.set_scope_read("ahmet.mehmet")
        self.assertEqual(accesskey.can_access_read("ahmet.mehmet"), True)
        self.assertEqual(accesskey.can_access_read("ahmet.mehmet.cengiz"), False)


        self.assertEqual(accesskey.can_access_read("oo.aa.bb.cc"), False)
        accesskey.set_scope_read("oo.aa.bb")
        self.assertEqual(accesskey.can_access_read("oo.aa.bb.cc"), False)
        accesskey.set_scope_read("oo.aa.bb.dd")
        self.assertEqual(accesskey.can_access_read("oo.aa.bb.cc"), False)
        self.assertEqual(accesskey.can_access_read("oo.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_read("oo.aa"), False)



        self.assertEqual(accesskey.can_access_read("nn.aa.bb.cc"), False)
        accesskey.set_scope_read("nn.aa.bb.*")
        self.assertEqual(accesskey.can_access_read("nn.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_read("nn.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_read("nn.aa"), False)

        self.assertEqual(accesskey.can_access_read("tt.aa.bb.cc"), False)
        accesskey.set_scope_read("tt.*")
        self.assertEqual(accesskey.can_access_read("tt.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_read("tt.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_read("tt.aa"), True)



        self.assertEqual(accesskey.can_access_read("ee.aa.bb.cc"), False)
        accesskey.set_scope_read("*")
        self.assertEqual(accesskey.can_access_read("ee.aa.bb.cc"), True)
        self.assertEqual(accesskey.can_access_read("ee.aa.bb.dd"), True)
        self.assertEqual(accesskey.can_access_read("ee.aa"), True)

    def test_delete(self):
        id = "test_delete"
        accesskey = AccessKey(id)
        accesskey.set_scope_write("onur.*")
        self.assertEqual(accesskey.can_access_write("onur.*"), True)
        accesskey.delete()
        self.assertEqual(accesskey.can_access_write("onur.*"), False)
        self.assertEqual(accesskey.name, None)
        self.assertEqual(accesskey.is_admin, False)
        self.assertEqual(accesskey.is_enable, False)
        self.assertEqual(accesskey.scopes_write, [])
        self.assertEqual(accesskey.scopes_read, [])



    def test_get_admins(self):
        id = "test_get_admins"
        id_2 = "test_get_admins_"
        accesskey = AccessKey(id)
        accesskey.set_is_admin(True)
        self.assertEqual(accesskey.get_admins(), [id])
        accesskey.set_is_admin(False)
        self.assertEqual(accesskey.get_admins(), [])
        accesskey.set_is_admin(True)
        self.assertEqual(accesskey.get_admins(), [id])
        accesskey_2 = AccessKey(id_2)
        accesskey_2.set_is_admin(True)
        self.assertIn(id, accesskey.get_admins())
        self.assertIn(id_2, accesskey.get_admins())
        self.assertEqual(len(accesskey.get_admins()), 2)



backup = sys.argv
sys.argv = [sys.argv[0]]
unittest.main(exit=False)
sys.argv = backup