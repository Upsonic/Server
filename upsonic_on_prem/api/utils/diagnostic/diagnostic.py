import time

from upsonic_on_prem.__init__ import __version__
from upsonic_on_prem.api.utils import storage
from upsonic_on_prem.api.utils.accesskey import AccessKey
from upsonic_on_prem.api.utils.scope import Scope

start_time = time.time()

def uptime():
    # Return the time since the server started
    return time.time() - start_time





def diagnostic():
    # Return an dictionary with useful information about the system
    return {
        "version": str(__version__),
        "storage_total_size": storage.total_size(),
        "storage_redis_status": storage.status(),
        "total_user": AccessKey.get_len_of_users(),
        "total_scopes": Scope.get_all_scopes_len(),
        "uptime": uptime(),
    }