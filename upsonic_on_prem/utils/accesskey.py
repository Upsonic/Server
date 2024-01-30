import redis
import random
import os
import traceback


from upsonic_on_prem.utils import storage

from upsonic_on_prem.utils.configs import admin_key

class AccessKey:
    def __init__(self, key):
        self.key = key


    def enable(self):
        storage.set(self.key, True)
    def disable(self):
        storage.set(self.key, False)
    @property
    def is_enable(self):
        return storage.get(self.key) == True

    def set_is_admin(self, is_admin):
        return storage.set(self.key+":is_admin", is_admin)
    @property
    def is_admin(self):
        return storage.get(self.key+":is_admin") == True

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
        return storage.get(self.key+":name")
    @property
    def scopes_write(self):

        return storage.get(self.key+":scopes_write") or []
        
    @property
    def scopes_read(self):
        return storage.get(self.key+":scopes_read") or []



        
    def set_name(self, name):
        return storage.set(self.key+":name", name)
    
    def set_scope_write(self, scope):
        currently_list = self.scopes_write
        currently_list.append(scope)
        return storage.set(self.key+":scopes_write", currently_list)
    
    def set_scope_read(self, scope):
        currently_list = self.scopes_read
        currently_list.append(scope)
        return storage.set(self.key+":scopes_read", currently_list)



    
    def delete(self):
        storage.delete(self.key+":name")
        storage.delete(self.key+":scopes_write")
        storage.delete(self.key+":scopes_read")
        storage.delete(self.key+":is_admin")
        storage.delete(self.key)

    

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
    AccessKey(admin_key).set_is_admin(True)