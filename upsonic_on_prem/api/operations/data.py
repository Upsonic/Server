from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, storage_2, AccessKey

from flask import jsonify
from flask import request


@app.route(dump_url, methods=["POST"])
def dump():
    scope = request.form.get("scope")
    data = request.form.get("data")

    storage_2.set(scope, data)

    return jsonify({"status": True})



@app.route(load_url, methods=["POST"])
def load():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": storage_2.get(scope)})


@app.route(get_read_scopes_of_me_url, methods=["get"])
def get_read_scopes_of_me():
    return jsonify({"status": True, "result": AccessKey(request.authorization.password).scopes_read})


@app.route(get_write_scopes_of_me_url, methods=["get"])
def get_write_scopes_of_me():
    return jsonify({"status": True, "result": AccessKey(request.authorization.password).scopes_write})
