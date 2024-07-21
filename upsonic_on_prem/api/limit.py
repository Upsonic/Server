from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from upsonic_on_prem.api.app import app
from upsonic_on_prem.api.utils.configs import *
from upsonic_on_prem.api.utils.configs import white_list_ip

limiter = Limiter(get_remote_address, app=app, default_limits=rate_limit)


@limiter.request_filter
def ip_whitelist():
    """ """
    return request.remote_addr == white_list_ip
