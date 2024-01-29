from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, AccessKey

from flask import jsonify
from flask import request


@app.route(get_admins_url, methods=["get"])
def get_admins():
    return jsonify(AccessKey.get_admins())
