from upsonic_on_prem.utils import access_key
from upsonic_on_prem.api.urls import *


def free_operation(scope):
    return True
def user_pre_process(the_access_key:access_key, request):
    scope = request.form.get("scope")
    endpoint = "/"+request.endpoint

    operation_type = None
    if endpoint == dump_url:
        operation_type = the_access_key.can_access_write
    elif endpoint == load_url:
        operation_type = the_access_key.can_access_read
    else:
        operation_type = free_operation
    

    if not operation_type(scope):
        return False
    

    return True
    