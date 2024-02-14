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

from upsonic_on_prem.utils import storage, storage_2, storage_3
from upsonic_on_prem.utils import AccessKey
from upsonic_on_prem.utils import Scope
from upsonic_on_prem.utils import AI
import cloudpickle
import dill

from cryptography.fernet import Fernet
import base64
import hashlib


class Test_Storage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        storage.pop()

    def test_status(self):
        self.assertTrue(storage.status())



    def test_set(self):
        storage.set("test", "test")
        self.assertEqual(storage.get("test"), "test")

    def test_total_size(self):
        self.assertTrue(storage.total_size() > 0)


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

        accesskey.delete_scope_write("onur.*")
        self.assertEqual(accesskey.scopes_write, ["onur.mehmet.*"])
        accesskey.delete_scope_write("onur.mehmet.*")
        self.assertEqual(accesskey.scopes_write, [])


    def test_scope_read(self):
        id = "test_scope"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_read, [])
        accesskey.set_scope_read("onur.*")
        accesskey.set_scope_read("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_read, ["onur.*", "onur.mehmet.*"])

        accesskey.delete_scope_read("onur.*")
        self.assertEqual(accesskey.scopes_read, ["onur.mehmet.*"])
        accesskey.delete_scope_read("onur.mehmet.*")
        self.assertEqual(accesskey.scopes_read, [])

    def test_scope_read_clear(self):
        id = "test_scope_read_clear"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_read, [])
        accesskey.set_scope_read("onur.*")
        accesskey.set_scope_read("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_read, ["onur.*", "onur.mehmet.*"])

        accesskey.scopes_read_clear()
        self.assertEqual(accesskey.scopes_read, [])

    def test_scope_write_clear(self):
        id = "test_scope_write_clear"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_write, [])
        accesskey.set_scope_write("onur.*")
        accesskey.set_scope_write("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_write, ["onur.*", "onur.mehmet.*"])

        accesskey.scopes_write_clear()
        self.assertEqual(accesskey.scopes_write, [])

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

    def test_robust(self):
        id = "test_robust"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.robust, False)
        self.assertEqual(accesskey._set("robust", True), True)
        self.assertEqual(accesskey._get("robust"), True)
        self.assertEqual(accesskey._delete("robust"), True)
        self.assertNotEqual(accesskey._keys(), False)

        accesskey.set_robust(True)

        self.assertEqual(accesskey._set("robust", True), False)
        self.assertEqual(accesskey._get("robust"), None)
        self.assertEqual(accesskey._delete("robust"), False)
        self.assertEqual(accesskey._keys(), False)

        self.assertEqual(accesskey.robust, True)

    def test_get_users(self):
        id = "test_get_users"
        id_2 = "test_get_users_"
        accesskey = AccessKey(id)
        accesskey.enable()
        self.assertEqual(accesskey.get_users(), [id])
        accesskey.delete()
        self.assertEqual(accesskey.get_users(), [])
        accesskey.enable()
        self.assertEqual(accesskey.get_users(), [id])
        accesskey_2 = AccessKey(id_2)
        accesskey_2.enable()
        self.assertIn(id, accesskey.get_users())
        self.assertIn(id_2, accesskey.get_users())
        self.assertEqual(len(accesskey.get_users()), 2)

    def test_get_users_len(self):
        storage.pop()
        id = "test_get_users_len"
        accesskey = AccessKey(id)
        accesskey.enable()
        self.assertEqual(AccessKey.get_len_of_users(), 1)
        storage.pop()

    def test_get_admins_len(self):
        storage.pop()
        the_first = AccessKey.get_len_of_admins()
        id = "test_get_admins_len"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_is_admin(True)

        id_2 = "test_get_admins_len_"
        accesskey_2 = AccessKey(id_2)
        accesskey_2.enable()

        self.assertEqual(AccessKey.get_len_of_admins(), the_first + 1)
        storage.pop()

    def test_events(self):
        storage.pop()

        id = "test_events"
        accesskey = AccessKey(id)
        accesskey.enable()

        accesskey.event("Test a")

        the_events = [value for value in accesskey.events.values()]

        self.assertEqual(the_events, ["Test a"])

        storage.pop()

    def test_events_get_x(self):
        storage.pop()

        id = "test_events"
        accesskey = AccessKey(id)
        accesskey.enable()

        accesskey.event("Test a")
        accesskey.event("Test b")
        accesskey.event("Test c")
        accesskey.event("Test d")

        the_events = [value for value in accesskey.get_last_x_events(2).values()]

        self.assertEqual(the_events, ["Test d", "Test c"])

        storage.pop()

    def test_scope_dump_source(self):
        storage_2.pop()
        id = "test_scope_dump_source"

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        self.assertEqual(the_scope.source, dumped_data)

        storage_2.pop()

    def test_scope_python(self):
        storage_2.pop()
        id = "test_scope_dump_source"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        self.assertEqual(the_scope.python(), my_function())

        storage_2.pop()

    def test_scope_type(self):
        storage_2.pop()
        id = "test_scope_dump_source"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        self.assertEqual(the_scope.type, "function")

        storage_2.pop()

    def test_scope_code(self):
        storage_2.pop()
        id = "test_scope_dump_source"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        print(the_scope.code)
        self.assertEqual(the_scope.code, """def my_function():\n    return "aaa"\n""")

        storage_2.pop()

    def test_scope_documentation(self):
        storage_2.pop()
        id = "test_scope_documentation"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))
        self.assertEqual(the_scope.documentation, None)
        the_scope.create_documentation()

        print(the_scope.documentation)
        self.assertEqual(the_scope.documentation, "Returns a function instance for a my_function method .")

        storage_2.pop()

    def test_ai_code_to_document(self):
        storage_2.pop()

        print(AI.code_to_documentation("def my_function():\n    return \"aaa\"\n"))
        self.assertEqual(AI.code_to_documentation("def my_function():\n    return \"aaa\"\n"),
                         "Returns a function instance for a my_function method .")

        storage_2.pop()

    def test_scope_dump_history(self):
        storage_2.pop()
        id = "test_scope_dump_source"

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        self.assertEqual(the_scope.dump_history, [])

        the_scope.dump(dumped_data, AccessKey(id))
        self.assertNotEqual(the_scope.dump_history, [])
        self.assertEqual(len(the_scope.dump_history), 1)
        self.assertEqual(Scope.get_dump(the_scope.dump_history[0]).source, the_scope.source)

        def my_function():
            return False

        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))
        self.assertNotEqual(Scope.get_dump(the_scope.dump_history[0]).source, the_scope.source)

        self.assertNotEqual(Scope.get_dump(the_scope.dump_history[1]).python(), True)
        self.assertNotEqual(Scope.get_dump(the_scope.dump_history[0]).python(), False)
        self.assertEqual(the_scope.python(), False)

        storage_2.pop()

    def test_scope_get_all_scopes(self):
        storage_2.pop()
        id = "onur.my_function"
        id2 = "onur.sub.my_awesome"
        id3 = "onur.sub.my_sub_function"

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        self.assertEqual(the_scope.get_all_scopes(), [])

        the_scope.dump(dumped_data, AccessKey(id))
        Scope(id2).dump(dumped_data, AccessKey(id2))
        Scope(id3).dump(dumped_data, AccessKey(id2))

        self.assertEqual(the_scope.get_all_scopes(),
                         ['onur.my_function', 'onur.sub.my_awesome', 'onur.sub.my_sub_function'])

        storage_2.pop()


    def test_accesskey_get_all_scopes_name_and_prefix(self):
        storage.pop()
        storage_2.pop()

        id = "test_accesskey_get_all_scopes_name.my_function"
        id2 = "aa.sub.my_awesome"
        id3 = "test_accesskey_get_all_scopes_name.sub.my_sub_function"
        user = AccessKey(id)
        user.enable()

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        self.assertEqual(Scope.get_all_scopes_name(user), [])

        the_scope.dump(dumped_data, user)
        Scope(id2).dump(dumped_data, user)
        Scope(id3).dump(dumped_data, user)

        self.assertEqual(Scope.get_all_scopes_name(user), [])

        user.set_scope_read("test_accesskey_get_all_scopes_name.my_function")

        self.assertEqual(Scope.get_all_scopes_name(user), ['test_accesskey_get_all_scopes_name.my_function'])

        user.set_scope_read("aa.sub.my_awesome")

        self.assertEqual(Scope.get_all_scopes_name(user),
                         ['aa.sub.my_awesome', 'test_accesskey_get_all_scopes_name.my_function'])

        user.set_scope_read("test_accesskey_get_all_scopes_name.sub.my_sub_function")

        self.assertEqual(Scope.get_all_scopes_name(user),
                         ['aa.sub.my_awesome', 'test_accesskey_get_all_scopes_name.my_function',
                          "test_accesskey_get_all_scopes_name.sub.my_sub_function"])

        self.assertEqual(Scope.get_all_scopes_name_prefix(user, "test_accesskey_get_all_scopes_name"),
                         ['test_accesskey_get_all_scopes_name.my_function',
                          "test_accesskey_get_all_scopes_name.sub.my_sub_function"])
        self.assertEqual(Scope.get_all_scopes_name_prefix(user, "aa"),
                         ['aa.sub.my_awesome'])

        storage.pop()
        storage_2.pop()

    def test_scope_delete(self):
        storage_2.pop()
        storage_3.pop()
        id = "test_scope_delete"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))
        self.assertEqual(the_scope.code, """def my_function():\n    return "aaa"\n""")

        the_scope.delete()
        self.assertEqual(the_scope.code, None)
        self.assertEqual(the_scope.python, None)
        self.assertEqual(the_scope.source, None)
        self.assertEqual(the_scope.type, None)
        self.assertEqual(the_scope.documentation, None)
        self.assertEqual(the_scope.dump_history, [])
        self.assertEqual(the_scope.the_storage.get(id), None)

        storage_2.pop()
        storage_3.pop()

    def test_scope_version(self):
        storage_2.pop()
        storage_3.pop()
        id = "test_scope_version"

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        self.assertEqual(the_scope.python(), "aaa")

        the_scope.create_version("v0.1.1", AccessKey(id))
        self.assertEqual(the_scope.python(), "aaa")

        def my_function():
            return "bbbb"

        the_scope = Scope(id)
        dumped_data = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).encrypt(
            cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))

        self.assertEqual(the_scope.python(), "bbbb")

        self.assertEqual(Scope.get_version(the_scope.version_history[0]).python(), "aaa")

        storage_2.pop()
        storage_3.pop()



backup = sys.argv
sys.argv = [sys.argv[0]]
unittest.main(exit=False)
sys.argv = backup