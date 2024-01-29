from upsonic_on_prem.api import limiter
from flask import request

from upsonic_on_prem.utils.configs import white_list_ip


@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == white_list_ip