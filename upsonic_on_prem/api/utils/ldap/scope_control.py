from upsonic_on_prem.api.utils.kot_db import kot_db


def save_conf(conf):
    return kot_db.set("LDAP_CONFIG", conf)

def get_conf():
    the_conf = kot_db.get("LDAP_CONFIG")

    if not the_conf:
        the_conf = {}
        save_conf(the_conf)

    return the_conf



def add_group_to_scope(scope_name, group_name):
    conf = get_conf()
    if scope_name not in conf:
        conf[scope_name] = []

    if group_name not in conf[scope_name]:
        conf[scope_name].append(group_name)

    return save_conf(conf)

def remove_group_from_scope(scope_name, group_name):

    conf = get_conf()
    if scope_name not in conf:
        return

    if group_name in conf[scope_name]:
        conf[scope_name].remove(group_name)

    if len(conf[scope_name]) == 0:
        del conf[scope_name]

    return save_conf(conf)


def is_group_in_scope(scope_name, group_name):
    conf = get_conf()
    if scope_name not in conf:
        return False

    if group_name in conf[scope_name]:
        return True

    return False

def get_groups_in_scope(scope_name):
    conf = get_conf()
    if scope_name not in conf:
        return []

    return conf[scope_name]

def get_all_scopes():
    conf = get_conf()
    return list(conf.keys())

