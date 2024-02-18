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

    return jsonify(
        {"status": True, "result": the_scope.dump(data, AccessKey(request.authorization.password), pass_str=True)})


@app.route(dump_code_url, methods=["POST"])
def dump_code():
    scope = request.form.get("scope")
    code = request.form.get("code")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_code(code)})


@app.route(dump_type_url, methods=["POST"])
def dump_type():
    scope = request.form.get("scope")
    type = request.form.get("type")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_type(type)})



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

    return jsonify({"status": True, "result": Scope(scope).create_documentation()})


@app.route(create_document_of_scope_url_old, methods=["POST"])
def create_document_of_scope_old():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_documentation_old()})

@app.route(get_type_of_scope_url, methods=["POST"])
def get_type_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).type})


@app.route(get_all_scopes_user_url, methods=["get"])
def get_all_scopes_user():
    user = AccessKey(request.authorization.password)
    return jsonify({"status": True, "result": Scope.get_all_scopes_name(user)})


@app.route(delete_scope_url, methods=["POST"])
def delete_scope():
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.delete()})


@app.route(get_dump_history_url, methods=["POST"])
def get_dump_history():
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.dump_history})


@app.route(get_version_history_url, methods=["POST"])
def get_version_history():
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.version_history})



@app.route(load_specific_dump_url, methods=["POST"])
def load_specific_dump():
    dump_id = request.form.get("dump_id")
    object = Scope.get_dump(dump_id)
    return jsonify({"status": True, "result": object.source})


@app.route(get_all_scopes_name_prefix_url, methods=["POST"])
def get_all_scopes_name_prefix():
    user = AccessKey(request.authorization.password)
    prefix = request.form.get("prefix")
    return jsonify({"status": True, "result": Scope.get_all_scopes_name_prefix(user, prefix)})


@app.route(create_version_url, methods=["POST"])
def create_version():
    user = AccessKey(request.authorization.password)
    version = request.form.get("version")
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.create_version(version, user)})
