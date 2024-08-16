from flask import jsonify
from flask import request

from upsonic_on_prem.api import app
from upsonic_on_prem.api.urls import *
from upsonic_on_prem.api.utils import AccessKey, storage, Scope, AI
from upsonic_on_prem.api.utils.ai.ai_history import get_all_ai_calls, reset_ai_calls


@app.route(get_all_ai_calls_url, methods=["GET"])
def get_all_ai_calls_view():
    return jsonify({"status": True, "result": get_all_ai_calls()})


@app.route(reset_ai_calls_url, methods=["GET"])
def reset_ai_calls_view():
    return jsonify({"status": True, "result": reset_ai_calls()})


@app.route(get_admins_url, methods=["get"])
def get_admins():
    return jsonify({"status": True, "result": AccessKey.get_admins()})


@app.route(get_users_url, methods=["get"])
def get_users():
    return jsonify({"status": True, "result": AccessKey.get_users()})


@app.route(get_users_keys_url, methods=["get"])
def get_users_keys():
    return jsonify({"status": True, "result": AccessKey.get_users_keys()})


@app.route(add_user_url, methods=["POST"])
def add_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.enable()

    return jsonify({"status": True, "result": True})


@app.route(set_name_user_url, methods=["POST"])
def set_name_user():
    key = request.form.get("key")
    name = request.form.get("name")

    user = AccessKey(key)
    user.set_name(name)

    return jsonify({"status": True, "result": True})


@app.route(get_name_user_url, methods=["POST"])
def get_name_user():
    key = request.form.get("key")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.name})


@app.route(enable_user_url, methods=["POST"])
def enable_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.enable()

    return jsonify({"status": True, "result": True})


@app.route(disable_user_url, methods=["POST"])
def disable_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.disable()

    return jsonify({"status": True, "result": True})


@app.route(is_enabled_user_url, methods=["POST"])
def is_enabled_user():
    key = request.form.get("key")
    user = AccessKey(key)
    return jsonify({"status": True, "result": user.is_enable})


@app.route(enable_admin_url, methods=["POST"])
def enable_admin():
    key = request.form.get("key")

    user = AccessKey(key)
    user.set_is_admin(True)

    return jsonify({"status": True, "result": True})


@app.route(disable_admin_url, methods=["POST"])
def disable_admin():
    key = request.form.get("key")

    user = AccessKey(key)
    user.set_is_admin(False)

    return jsonify({"status": True, "result": True})


@app.route(id_admin_url, methods=["POST"])
def is_admin():
    key = request.form.get("key")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.is_admin})


@app.route(delete_user_url, methods=["POST"])
def delete_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.delete()

    return jsonify({"status": True, "result": True})


@app.route(total_size_url, methods=["GET"])
def total_size():
    return jsonify({"status": True, "result": storage.total_size()})


@app.route(scope_write_add_url, methods=["POST"])
def scope_write_add():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    user.set_scope_write(scope)

    return jsonify({"status": True, "result": True})


@app.route(scope_write_delete_url, methods=["POST"])
def scope_write_delete():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    user.delete_scope_write(scope)

    return jsonify({"status": True, "result": True})


@app.route(scope_read_add_url, methods=["POST"])
def scope_read_add():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    user.set_scope_read(scope)

    return jsonify({"status": True, "result": True})


@app.route(scope_read_delete_url, methods=["POST"])
def scope_read_delete():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    user.delete_scope_read(scope)

    return jsonify({"status": True, "result": True})


@app.route(get_write_scopes_of_user_url, methods=["post"])
def get_write_scopes_of_user():
    key = request.form.get("key")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.scopes_write})


@app.route(get_read_scopes_of_user_url, methods=["post"])
def get_read_scopes_of_user():
    key = request.form.get("key")

    user = AccessKey(key)

    return jsonify({"status": True, "result": user.scopes_read})


@app.route(can_access_read_user_url, methods=["post"])
def can_access_read_user():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.can_access_read(scope)})


@app.route(can_access_write_user_url, methods=["post"])
def can_access_write_user():
    key = request.form.get("key")
    scope = request.form.get("scope")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.can_access_write(scope)})


@app.route(get_len_of_users_url, methods=["get"])
def get_len_of_users():
    return jsonify({"status": True, "result": AccessKey.get_len_of_users()})


@app.route(get_len_of_admins_url, methods=["get"])
def get_len_of_admins():
    return jsonify({"status": True, "result": AccessKey.get_len_of_admins()})


@app.route(scopes_write_clear_url, methods=["post"])
def scopes_write_clear_url():
    key = request.form.get("key")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.scopes_write_clear()})


@app.route(scopes_read_clear_url, methods=["post"])
def scopes_read_clear():
    key = request.form.get("key")

    user = AccessKey(key)
    return jsonify({"status": True, "result": user.scopes_read_clear()})


@app.route(event_url, methods=["post"])
def event():
    key = request.form.get("key")
    event = request.form.get("event")
    target = request.form.get("target")
    detail = request.form.get("detail")
    user = AccessKey(key)
    return jsonify({"status": True, "resul": user.event(event, target, detail)})


@app.route(get_last_x_event_url, methods=["post"])
def get_last_x_event():
    key = request.form.get("key")

    user = AccessKey(key)
    x = request.form.get("x", type=int)
    return jsonify({"status": True, "result": user.get_last_x_events(x)})


@app.route(get_all_scopes_url, methods=["get"])
def get_all_scopes():
    return jsonify({"status": True, "result": Scope.get_all_scopes()})


@app.route(ai_code_to_document_url, methods=["post"])
def ai_code_to_document():
    code = request.form.get("code", type=str)
    return jsonify({"status": True, "result": AI.code_to_documentation(code)})
