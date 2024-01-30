from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, AccessKey

from flask import jsonify
from flask import request


@app.route(get_admins_url, methods=["get"])
def get_admins():
    return jsonify(AccessKey.get_admins())






@app.route(add_user_url, methods=["POST"])
def add_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.enable()


    return jsonify(True)



@app.route(enable_user_url, methods=["POST"])
def enable_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.enable()


    return jsonify(True)




@app.route(disable_user_url, methods=["POST"])
def disable_user():
    key = request.form.get("key")

    user = AccessKey(key)
    user.disable()


    return jsonify(True)



@app.route(enable_admin_url, methods=["POST"])
def enable_admin():
    key = request.form.get("key")

    user = AccessKey(key)
    user.set_is_admin(True)


    return jsonify(True)


@app.route(disable_admin_url, methods=["POST"])
def disable_admin():
    key = request.form.get("key")

    user = AccessKey(key)
    user.set_is_admin(False)


    return jsonify(True)

