from upsonic_on_prem.__init__ import __version__
from upsonic_on_prem.api.utils import storage


def diagnostic():
    # Return an dictionary with useful information about the system
    return {
        "version": str(__version__),
        "storage_total_size": storage.total_size(),
    }