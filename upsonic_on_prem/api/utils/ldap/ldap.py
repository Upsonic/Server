# ldap_utils.py
import os
import sys
from ldap3 import Server, Connection, ALL

try:
    from upsonic_on_prem.api.utils.kot_db import kot_db
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from kot_db import kot_db


def authenticate(username, password):
    LDAP_SEARCH = kot_db.get("LDAP_SEARCH")
    LDAP_SERVER = kot_db.get("LDAP_SERVER")
    LDAP_PORT = kot_db.get("LDAP_PORT")
    LDAP_USE_SSL = kot_db.get("LDAP_USE_SSL")

    user_dn = f"uid={username},{LDAP_SEARCH}"
    server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL, use_ssl=LDAP_USE_SSL)
    conn = Connection(server, user=user_dn, password=password)
    
    if not conn.bind():
        return False
    
    conn.unbind()
    return True

def is_user_in_group(username, group_name):
    LDAP_SEARCH = kot_db.get("LDAP_SEARCH")
    LDAP_SERVER = kot_db.get("LDAP_SERVER")
    LDAP_PORT = kot_db.get("LDAP_PORT")
    LDAP_BIND_USER = kot_db.get("LDAP_BIND_USER")
    LDAP_BIND_PASSWORD = kot_db.get("LDAP_BIND_PASSWORD")
    LDAP_USE_SSL = kot_db.get("LDAP_USE_SSL")


    user_dn = f"uid={username},{LDAP_SEARCH}"
    server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL, use_ssl=LDAP_USE_SSL)

    # Bind as read-only admin
    conn = Connection(server, user=LDAP_BIND_USER, password=LDAP_BIND_PASSWORD)
    if not conn.bind():
        return False

    # Comprehensive search filter to check membership
    group_filter = f"(&(objectClass=groupOfUniqueNames)(cn={group_name})(uniqueMember={user_dn}))"
    conn.search(LDAP_SEARCH, group_filter, attributes=['cn'])

    if len(conn.entries) > 0:
        result = True
    else:
        result = False
    
    conn.unbind()
    return result

if __name__ == '__main__':
    print(authenticate('riemann', 'password'))
    print(is_user_in_group('riemann', 'mathematicians'))
