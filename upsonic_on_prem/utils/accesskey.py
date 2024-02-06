import redis
import random
import os
import traceback


from upsonic_on_prem.utils import storage

from upsonic_on_prem.utils.configs import admin_key

class AccessKey:
    def __init__(self, key):
        self.key = key

    def set_robust(self, robust):
        return self._set(self.key + ":robust", robust)

    @property
    def robust(self):
        return self._get(self.key + ":robust") == True


    def _set(self, key, value):
        if self.robust:
            return False

        return storage.set(key, value)

    def _get(self, key):
        return storage.get(key)

    def _delete(self, key):
        if self.robust:
            return False

        return storage.delete(key)

    def _keys(self):
        if self.robust:
            return False

        return storage.keys()


    def enable(self):
        self._set(self.key + ":enable", True)
    def disable(self):
        self._set(self.key + ":enable", False)
    @property
    def is_enable(self):
        return self._get(self.key + ":enable") == True

    def set_is_admin(self, is_admin):
        return self._set(self.key + ":is_admin", is_admin)
    @property
    def is_admin(self):
        return self._get(self.key + ":is_admin") == True

    @staticmethod
    def get_admins():
        keys = storage.keys()
        admins = []
        for i in keys:
            if i.endswith(":is_admin") and storage.get(i):
                admins.append(i[:-9])

        return admins
    



    @property
    def name(self):
        return self._get(self.key + ":name")
    @property
    def scopes_write(self):

        return self._get(self.key + ":scopes_write") or []
        
    @property
    def scopes_read(self):
        return self._get(self.key + ":scopes_read") or []



        
    def set_name(self, name):
        return self._set(self.key + ":name", name)
    
    def set_scope_write(self, scope):
        currently_list = self.scopes_write
        currently_list.append(scope)
        return self._set(self.key + ":scopes_write", currently_list)
    
    def set_scope_read(self, scope):
        currently_list = self.scopes_read
        currently_list.append(scope)
        return self._set(self.key + ":scopes_read", currently_list)


    def delete_scope_write(self, scope):
        currently_list = self.scopes_write
        currently_list.remove(scope)
        return self._set(self.key + ":scopes_write", currently_list)

    def delete_scope_read(self, scope):
        currently_list = self.scopes_read
        currently_list.remove(scope)
        return self._set(self.key + ":scopes_read", currently_list)


    
    def delete(self):
        self._delete(self.key + ":name")
        self._delete(self.key + ":scopes_write")
        self._delete(self.key + ":scopes_read")
        self._delete(self.key + ":is_admin")
        self._delete(self.key + ":enable")

    

    def can_access_write(self, scope):
        all_scopes = self.scopes_write
        
        control = False

        for i in all_scopes:
            if scope == i:
                control = True
                break
            elif scope.startswith(i[:-1]) and i.endswith("*"):
                control = True
                break

        return control



    def can_access_read(self, scope):
        all_scopes = self.scopes_read
        
        control = False

        for i in all_scopes:
            if scope == i:
                control = True
                break
            elif scope.startswith(i[:-1]) and i.endswith("*"):
                control = True
                break

        return control

if admin_key is not None:
    the_admin = AccessKey(admin_key)
    the_admin.set_is_admin(True)
    the_admin.set_robust(True)
