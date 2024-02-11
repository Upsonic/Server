from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, storage_2, AccessKey, Scope

from flask import jsonify
from flask import request


@app.route(dump_url, methods=["POST"])
def dump():
    scope = request.form.get("scope")
    data = request.form.get("data")

    the_scope = Scope(scope)
    the_scope.dump(data)

    return jsonify({"status": True})



@app.route(load_url, methods=["POST"])
def load():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).source})


@app.route(get_read_scopes_of_me_url, methods=["get"])
def get_read_scopes_of_me():
    return jsonify({"status": True, "result": AccessKey(request.authorization.password).scopes_read})


@app.route(get_write_scopes_of_me_url, methods=["get"])
def get_write_scopes_of_me():
    return jsonify({"status": True, "result": AccessKey(request.authorization.password).scopes_write})


@app.route(get_document_of_scope_url, methods=["POST"])
def get_document_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).documentation})


@app.route(create_document_of_scope_url, methods=["POST"])
def create_document_of_scope():
    scope = request.form.get("scope")
    Scope(scope).create_documentation()
    return jsonify({"status": True})
