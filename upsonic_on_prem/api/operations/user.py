import base64
import hashlib
import time
import traceback

import requests
from flask import jsonify, request

from upsonic_on_prem.api import app
from upsonic_on_prem.api.urls import *
from upsonic_on_prem.api.utils import (AI, AccessKey, Scope, storage,
                                       storage_2, storage_4)
from upsonic_on_prem.api.utils.configs import openai_api_key
from upsonic_on_prem.api.utils.github_sync import github


def forward_request_to_openai_ollama(path, method, headers, data):
    """

    :param path:
    :param method:
    :param headers:
    :param data:

    """
    url = f"http://localhost:11434/v1/{path}"
    headers["Authorization"] = f"Bearer {openai_api_key}"

    if method == "GET":
        response = requests.get(url, headers=headers, params=data)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, json=data)
    else:
        return jsonify({"error": "Unsupported HTTP method"}), 405

    return response


@app.route("/openai_ollama/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_openai_ollama(path):
    """

    :param path:

    """
    try:

        # Forward the request to OpenAI
        headers = {key: value for (key, value) in request.headers if key != "Host"}
        data = request.json if request.method in ["POST", "PUT"] else request.args

        # Call the forward_request function

        response = forward_request_to_openai_ollama(path, request.method, headers, data)

        # Pass the response back to the client

        return response.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def forward_request_to_ollama(path, method, headers, data):
    """

    :param path:
    :param method:
    :param headers:
    :param data:

    """
    url = f"http://localhost:11434/{path}"

    unallowed_path_list = [
        "/api/push",
        "/api/create",
        "/api/blobs/",
        "/api/tags",
        "/api/show",
        "/api/copy",
        "/api/delete",
        "/api/pull",
        "/api/delete",
        "/api/delete",
    ]

    # if path incude something from the unallowed_path_list, return error
    for each in unallowed_path_list:
        if each in path:
            return jsonify({"error": "Unsupported HTTP method"}), 405

    if method == "GET":
        response = requests.get(url, headers=headers, params=data)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, json=data)
    else:
        return jsonify({"error": "Unsupported HTTP method"}), 405

    return response


@app.route("/ollama/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_ollama(path):
    """

    :param path:

    """
    try:

        # Forward the request to OpenAI
        headers = {key: value for (key, value) in request.headers if key != "Host"}
        data = request.json if request.method in ["POST", "PUT"] else request.args

        # Call the forward_request function

        response = forward_request_to_ollama(path, request.method, headers, data)

        # Pass the response back to the client

        return response.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def forward_request_to_openai(path, method, headers, data):
    """

    :param path:
    :param method:
    :param headers:
    :param data:

    """
    url = f"https://api.openai.com/v1/{path}"
    headers["Authorization"] = f"Bearer {openai_api_key}"

    if method == "GET":
        response = requests.get(url, headers=headers, params=data)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, json=data)
    else:
        return jsonify({"error": "Unsupported HTTP method"}), 405

    return response


@app.route("/openai/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_openai(path):
    """

    :param path:

    """
    try:

        # Forward the request to OpenAI
        headers = {key: value for (key, value) in request.headers if key != "Host"}
        data = request.json if request.method in ["POST", "PUT"] else request.args

        # Call the forward_request function

        response = forward_request_to_openai(path, request.method, headers, data)

        # Pass the response back to the client

        return response.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route(dump_together_url, methods=["POST"])
def dump_together():
    """ """
    scope = request.form.get("scope")
    the_scope = Scope(scope)

    # code
    code = request.form.get("code")
    the_scope.set_code(code, access_key=request.authorization.password)

    # type
    type = request.form.get("type")
    the_scope.set_type(type)

    # requirements
    requirements = request.form.get("requirements")
    the_scope.set_requirements(requirements)

    # python_version
    python_version = request.form.get("python_version")
    the_scope.set_python_version(python_version)

    data = request.form.get("data")
    commit_message = request.form.get("commit_message")

    return jsonify(
        {
            "status": True,
            "result": the_scope.dump(
                data,
                AccessKey(request.authorization.password),
                pass_str=True,
                commit_message=commit_message,
            ),
        }
    )


@app.route(dump_url, methods=["POST"])
def dump():
    """ """
    scope = request.form.get("scope")
    data = request.form.get("data")
    commit_message = request.form.get("commit_message")

    the_scope = Scope(scope)

    return jsonify(
        {
            "status": True,
            "result": the_scope.dump(
                data,
                AccessKey(request.authorization.password),
                pass_str=True,
                commit_message=commit_message,
            ),
        }
    )


@app.route(dump_code_url, methods=["POST"])
def dump_code():
    """ """
    scope = request.form.get("scope")
    code = request.form.get("code")

    the_scope = Scope(scope)

    return jsonify(
        {
            "status": True,
            "result": the_scope.set_code(
                code, access_key=request.authorization.password
            ),
        }
    )


@app.route(dump_type_url, methods=["POST"])
def dump_type():
    """ """
    scope = request.form.get("scope")
    type = request.form.get("type")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_type(type)})


@app.route(load_url, methods=["POST"])
def load():
    """ """
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).source})


@app.route(get_read_scopes_of_me_url, methods=["get"])
def get_read_scopes_of_me():
    """ """
    return jsonify(
        {
            "status": True,
            "result": AccessKey(request.authorization.password).scopes_read,
        }
    )


@app.route(get_write_scopes_of_me_url, methods=["get"])
def get_write_scopes_of_me():
    """ """
    return jsonify(
        {
            "status": True,
            "result": AccessKey(request.authorization.password).scopes_write,
        }
    )


@app.route(get_document_of_scope_url, methods=["POST"])
def get_document_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.documentation})


@app.route(get_requirements_of_scope_url, methods=["POST"])
def get_requirements_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.requirements})


@app.route(get_dependency_of_scope_url, methods=["POST"])
def get_dependency_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.dependency})


@app.route(get_settings_of_scope_url, methods=["POST"])
def get_settings_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.settings})


@app.route(get_time_complexity_of_scope_url, methods=["POST"])
def get_time_complexity_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.time_complexity})


@app.route(get_mistakes_of_scope_url, methods=["POST"])
def get_mistakes_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.mistakes})


@app.route(get_required_test_types_of_scope_url, methods=["POST"])
def get_required_test_types_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.required_test_types})


@app.route(get_tags_of_scope_url, methods=["POST"])
def get_tags_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.tags})

    scope = request.form.get("scope")


@app.route(get_security_analysis_of_scope_url, methods=["POST"])
def get_security_analysis_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.security_analysis})


@app.route(get_code_of_scope_url, methods=["POST"])
def get_code_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.code})


@app.route(get_dump_user_of_scope_url, methods=["POST"])
def get_dump_user_of_scope():
    """ """
    dump = request.form.get("dump")
    object = Scope.get_dump(dump)
    return jsonify({"status": True, "result": object.user})


@app.route(get_dump_time_of_scope_url, methods=["POST"])
def get_dump_time_of_scope():
    """ """
    dump = request.form.get("dump")
    object = Scope.get_dump(dump)
    return jsonify({"status": True, "result": object.dump_time})


@app.route(get_dump_difference_of_scope_url, methods=["POST"])
def get_dump_difference_of_scope():
    """ """
    dump = request.form.get("dump")
    object = Scope.get_dump(dump)
    return jsonify({"status": True, "result": object.difference})


@app.route(get_dump_commit_message_of_scope_url, methods=["POST"])
def get_dump_commit_message_of_scope():
    """ """
    dump = request.form.get("dump")
    object = Scope.get_dump(dump)
    return jsonify({"status": True, "result": object.commit_message})


@app.route(get_version_user_of_scope_url, methods=["POST"])
def get_version_user_of_scope():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.user})


@app.route(get_version_code_of_scope_url, methods=["POST"])
def get_version_code_of_scope():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.code})


@app.route(get_version_difference_of_scope_url, methods=["POST"])
def get_version_difference_of_scope():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.difference})


@app.route(get_version_time_of_scope_url, methods=["POST"])
def get_version_time_of_scope():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.dump_time})


@app.route(get_version_release_note_of_scope_url, methods=["POST"])
def get_version_release_note_of_scope():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.release_note})


documentation_tasks = {}


def create_document_of_scope_(scope, version, create_ai_task=False, access_key=None):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in documentation_tasks:
        time.sleep(1)

    if not task_name in documentation_tasks:
        documentation_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={
                    "task_name": "documentation",
                    "key": scope,
                    "access_key": access_key,
                },
            ).json()["id"]
            if create_ai_task
            else None
        )
        try:
            work = the_scope.create_documentation()
        except:
            pass
        try:
            documentation_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated doc task: ", scope)

    return work


time_complexity_tasks = {}


def create_time_complexity_of_scope_(
    scope, version, create_ai_task=False, access_key=None
):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in time_complexity_tasks:
        time.sleep(1)

    if not task_name in time_complexity_tasks:
        time_complexity_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={
                    "task_name": "time_complexity",
                    "key": scope,
                    "access_key": access_key,
                },
            ).json()["id"]
            if create_ai_task
            else None
        )

        try:
            work = the_scope.create_time_complexity()
        except:
            pass
        try:
            time_complexity_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated time_complexity  task: ", scope)
    return work


mistakes_tasks = {}


def create_mistakes_of_scope_(scope, version, create_ai_task=False, access_key=None):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in mistakes_tasks:
        time.sleep(1)

    if not task_name in mistakes_tasks:
        mistakes_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={"task_name": "mistakes", "key": scope, "access_key": access_key},
            ).json()["id"]
            if create_ai_task
            else None
        )
        try:
            work = the_scope.create_mistakes()
        except:
            pass
        try:
            mistakes_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated mistakes_tasks  task: ", scope)
    return work


commit_message_tasks = {}


def create_commit_message_of_scope_(scope, version):
    """

    :param scope:
    :param version:

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in commit_message_tasks:
        time.sleep(1)
    work = None
    if not task_name in commit_message_tasks:
        commit_message_tasks[task_name] = True

        try:
            work = the_scope.create_commit_message()
        except:
            pass
        try:
            commit_message_tasks.pop(task_name)

        except:
            pass

    print("Complated commit_message_tasks  task: ", scope)
    return work


required_test_types_tasks = {}


def create_required_test_types_of_scope_(
    scope, version, create_ai_task=False, access_key=None
):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in required_test_types_tasks:
        time.sleep(1)

    if not task_name in required_test_types_tasks:
        required_test_types_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={
                    "task_name": "required_test_types",
                    "key": scope,
                    "access_key": access_key,
                },
            ).json()["id"]
            if create_ai_task
            else None
        )
        try:
            work = the_scope.create_required_test_types()
        except:
            pass
        try:
            required_test_types_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated required_test_types_tasks  task: ", scope)
    return work


tags_tasks = {}


def create_tags_of_scope_(scope, version, create_ai_task=False, access_key=None):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in tags_tasks:
        time.sleep(1)

    if not task_name in tags_tasks:
        tags_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={"task_name": "tags", "key": scope, "access_key": access_key},
            ).json()["id"]
            if create_ai_task
            else None
        )
        try:
            work = the_scope.create_tags()
        except:
            pass
        try:
            tags_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated tags_tasks  task: ", scope)
    return work


@app.route(create_document_of_scope_url, methods=["POST"])
def create_document_of_scope():
    """ """
    global documentation_tasks

    scope = request.form.get("scope")
    version = request.form.get("version")

    return jsonify(
        {"status": True, "result": create_document_of_scope_(scope, version)}
    )


@app.route(create_time_complexity_of_scope_url, methods=["POST"])
def create_time_complexity_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")

    return jsonify(
        {"status": True, "result": create_time_complexity_of_scope_(scope, version)}
    )


@app.route(create_mistakes_of_scope_url, methods=["POST"])
def create_mistakes_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")

    return jsonify(
        {"status": True, "result": create_mistakes_of_scope_(scope, version)}
    )


@app.route(create_required_test_types_of_scope_url, methods=["POST"])
def create_required_test_types_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")

    return jsonify(
        {"status": True, "result": create_required_test_types_of_scope_(scope, version)}
    )


@app.route(create_tags_of_scope_url, methods=["POST"])
def create_tags_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)
    return jsonify({"status": True, "result": create_tags_of_scope_(scope, version)})


@app.route(create_security_analysis_of_scope_url, methods=["POST"])
def create_security_analysis_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify(
        {"status": True, "result": create_security_analyses_of_scope_(scope, version)}
    )


@app.route(create_document_of_scope_url_old, methods=["POST"])
def create_document_of_scope_old():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.create_documentation_old()})


@app.route(get_type_of_scope_url, methods=["POST"])
def get_type_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.type})


@app.route(get_lock_of_scope_url, methods=["POST"])
def get_lock_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.lock})


@app.route(get_python_version_of_scope_url, methods=["POST"])
def get_python_version_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.python_version})


@app.route(get_all_scopes_user_url, methods=["get"])
def get_all_scopes_user():
    """ """
    user = AccessKey(request.authorization.password)
    return jsonify({"status": True, "result": Scope.get_all_scopes_name(user)})


@app.route(delete_scope_url, methods=["POST"])
def delete_scope():
    """ """
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify(
        {
            "status": True,
            "result": object.delete(AccessKey(request.authorization.password)),
        }
    )


@app.route(delete_version_url, methods=["POST"])
def delete_version():
    """ """
    version = request.form.get("version")
    object = Scope.delete_version(version)
    return jsonify({"status": True, "result": object})


@app.route(get_dump_history_url, methods=["POST"])
def get_dump_history():
    """ """
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.dump_history})


@app.route(get_version_history_url, methods=["POST"])
def get_version_history():
    """ """
    scope = request.form.get("scope")
    object = Scope(scope)

    return jsonify({"status": True, "result": object.version_history})


@app.route(get_module_version_history_url, methods=["POST"])
def get_module_version_history():
    """ """
    top_library = request.form.get("top_library")
    user = AccessKey(request.authorization.password)

    all_scopes_response = Scope.get_all_scopes_name_prefix(user, top_library)

    all_possible_versions = []
    for each_scope in all_scopes_response:
        scope_versions = Scope(each_scope).version_history
        for each_version in scope_versions:
            if each_version not in all_possible_versions:
                all_possible_versions.append(each_version.split(":")[1])

    return jsonify({"status": True, "result": all_possible_versions})


@app.route(load_specific_dump_url, methods=["POST"])
def load_specific_dump():
    """ """
    dump_id = request.form.get("dump_id")
    object = Scope.get_dump(dump_id)
    return jsonify({"status": True, "result": object.source})


@app.route(load_specific_version_url, methods=["POST"])
def load_specific_version():
    """ """
    version = request.form.get("version")
    object = Scope.get_version(version)
    return jsonify({"status": True, "result": object.source})


@app.route(get_all_scopes_name_prefix_url, methods=["POST"])
def get_all_scopes_name_prefix():
    """ """
    user = AccessKey(request.authorization.password)
    prefix = request.form.get("prefix")
    return jsonify(
        {"status": True, "result": Scope.get_all_scopes_name_prefix(user, prefix)}
    )


@app.route(create_version_url, methods=["POST"])
def create_version():
    """ """
    user = AccessKey(request.authorization.password)
    version = request.form.get("version")
    scope = request.form.get("scope")
    object = Scope(scope)
    return jsonify({"status": True, "result": object.create_version(version, user)})


@app.route(dump_requirements_url, methods=["POST"])
def dump_requirements():
    """ """
    scope = request.form.get("scope")
    settings = request.form.get("requirements")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_requirements(settings)})


@app.route(dump_settings_url, methods=["POST"])
def dump_settings():
    """ """
    scope = request.form.get("scope")
    settings = request.form.get("settings")

    the_settings = {}
    for key, value in request.form.items():
        if key != "scope":
            the_settings[key] = value

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_settings(the_settings)})


@app.route(dump_python_version_url, methods=["POST"])
def dump_python_version():
    """ """
    scope = request.form.get("scope")
    python_version = request.form.get("python_version")

    the_scope = Scope(scope)

    return jsonify(
        {"status": True, "result": the_scope.set_python_version(python_version)}
    )


@app.route(search_by_documentation_url, methods=["POST"])
def search_by_documentation():
    """ """
    question = request.form.get("question")
    min_score = float(request.form.get("min_score", 0))
    how_many_result = int(request.form.get("how_many_result", 10))

    user = AccessKey(request.authorization.password)
    scopes = Scope.get_all_scopes_with_documentation()

    the_read_scopes = user.scopes_read

    if len(scopes) == 0:
        return jsonify({"status": False, "result": "No scope has documentation"})

    results = AI.search_by_documentation(scopes, question, min_score, how_many_result)

    # Remove the results that not able to access by the user
    access_control_list = []
    for result in results:
        if user.can_access_read(result[0]) or user.is_admin:
            access_control_list.append(result)

    return jsonify({"status": True, "result": access_control_list})


@app.route(ai_completion_url, methods=["POST"])
def ai_completion():
    """ """
    message = request.form.get("message")
    model = request.form.get("model")
    result = None
    if model != None:
        result = AI.completion(message, model)
    else:
        result = AI.default_completion(message)
    return jsonify({"status": True, "result": result})


@app.route(get_default_ai_model, methods=["get"])
def get_default_ai_model():
    """ """
    return jsonify({"status": True, "result": AI.default_model})


security_analyses_tasks = {}


def create_security_analyses_of_scope_(
    scope, version, create_ai_task=False, access_key=None
):
    """

    :param scope:
    :param version:
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    task_name = scope
    if version != None:
        task_name = scope + ":" + version
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    while task_name in security_analyses_tasks:
        time.sleep(1)

    if not task_name in security_analyses_tasks:
        security_analyses_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={
                    "task_name": "security_analyses",
                    "key": scope,
                    "access_key": access_key,
                },
            ).json()["id"]
            if create_ai_task
            else None
        )
        try:
            work = the_scope.create_security_analysis()
        except:
            pass
        try:
            security_analyses_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            pass

    print("Complated security_analyses_tasks  task: ", scope)
    return work


readme_tasks = {}


def create_readme_(
    top_library, version, request=None, create_ai_task=False, access_key=None
):
    """

    :param top_library:
    :param version:
    :param request:  (Default value = None)
    :param create_ai_task:  (Default value = False)
    :param access_key:  (Default value = None)

    """
    global documentation_tasks
    print("CREATE README TASK for: ", top_library)

    task_name = top_library
    if version != None:
        task_name = top_library + ":" + version

    while task_name in readme_tasks:
        print("TASK POOL: ", readme_tasks)
        time.sleep(1)

    try:
        readme_tasks[task_name] = True
        the_task_id = (
            requests.post(
                "http://localhost:3001/add_ai_task",
                data={
                    "task_name": "readme",
                    "key": top_library,
                    "access_key": access_key,
                },
            ).json()["id"]
            if create_ai_task
            else None
        )

        all_scopes_response = (
            Scope.get_all_scopes_name_prefix(
                AccessKey(request.authorization.password), top_library
            )
            if request != None
            else Scope.get_all_scopes_name_prefix(prefix=top_library)
        )
        all_scopes = []
        for each_scope in all_scopes_response:
            if version != None:
                the_version_history_response = Scope(each_scope).version_history
                the_version_history = []
                for element in the_version_history_response:
                    the_version_history.append(element.replace(each_scope + ":", ""))
                if version in the_version_history:
                    all_scopes.append(each_scope)
            else:
                all_scopes.append(each_scope)

        # order by alphabetical
        all_scopes.sort()

        result = f"{top_library}"
        for i in all_scopes:
            result += i + "\n"

        summary_list = ""
        for each_scope in all_scopes:
            task_name_ = each_scope
            if version == None:
                the_scope = Scope(each_scope)
            else:
                task_ntask_name_ame = each_scope + ":" + version
                the_scope = Scope.get_version(each_scope + ":" + version)

            while task_name_ in documentation_tasks:
                time.sleep(1)

            if the_scope.documentation == None:
                documentation_tasks[task_name_] = True
                the_scope.create_documentation()
                try:
                    documentation_tasks.pop(task_name_)
                except:
                    pass

            summary_list += each_scope + " - " + str(the_scope.type) + "\n"
            summary_list += str(the_scope.documentation) + "\n\n"

        # Create sha256 hash of the result
        sha256 = hashlib.sha256((summary_list + top_library).encode()).hexdigest()

        result = AI.generate_readme(top_library, summary_list)

        storage_4.set(sha256, result)

        make_sync = False
        if request != None:
            make_sync = (
                len(AccessKey(request.authorization.password).scopes_read) == ["*"]
                or AccessKey(request.authorization.password).is_admin == True
            )
        else:
            make_sync = True
        if make_sync:
            path = top_library.replace(".", "/") if "." in top_library else top_library
            path += f"/README.md"

            code = ""
            the_name = top_library.replace(".", "_")
            code = f'{the_name} = upsonic.load_module("{top_library}")'

            content = '<b class="custom_code_highlight_green">Imporing:</b><br>'
            content += "\n```python\n"
            content += code
            content += "\n```\n"
            content += "<br>"

            content += result

            content += '\n<br><b class="custom_code_highlight_green">Content:</b><br>\n'
            for each in all_scopes:
                content += f"  - {each}\n"

            # Inside your create_or_update_file function, before the PUT request
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            content = encoded_content

            github.create_or_update_file_(path, content, f"Changes for {path}")
            sha_of_readme = github.get_sha_(path)

            storage_4.set(sha256 + "github_sha", sha_of_readme)
            get_sha = storage_4.get(sha256 + "github_sha")

        try:
            readme_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            traceback.print_exc()
            pass

        print("Complated readme task for: ", top_library)

        return result
    except:
        traceback.print_exc()
        try:
            readme_tasks.pop(task_name)
            (
                requests.post(
                    "http://localhost:3001/complate_ai_task",
                    data={"id": the_task_id, "access_key": access_key},
                ).json()["id"]
                if create_ai_task
                else None
            )
        except:
            traceback.print_exc()
            pass


@app.route(create_readme_url, methods=["POST"])
def create_readme():
    """ """
    top_library = request.form.get("top_library")
    version = request.form.get("version")

    return jsonify(
        {"status": True, "result": create_readme_(top_library, version, request)}
    )


@app.route(get_readme_github_sync_url, methods=["POST"])
def get_readme_github_sync():
    """ """
    top_library = request.form.get("top_library")
    version = request.form.get("version")
    all_scopes_response = Scope.get_all_scopes_name_prefix(
        AccessKey(request.authorization.password), top_library
    )
    all_scopes = []
    for each_scope in all_scopes_response:
        if version != None:
            the_version_history_response = Scope(each_scope).version_history
            the_version_history = []
            for element in the_version_history_response:
                the_version_history.append(element.replace(each_scope + ":", ""))
            if version in the_version_history:
                all_scopes.append(each_scope)
        else:
            all_scopes.append(each_scope)

    # order by alphabetical
    all_scopes.sort()

    result = f"{top_library}"
    for i in all_scopes:
        result += i + "\n"

    summary_list = ""
    for each_scope in all_scopes:
        task_name = each_scope
        if version == None:
            the_scope = Scope(each_scope)
        else:
            task_name = each_scope + ":" + version
            the_scope = Scope.get_version(each_scope + ":" + version)

        while task_name in documentation_tasks:
            return jsonify({"status": True, "result": None})
            time.sleep(1)

        if the_scope.documentation == None:
            documentation_tasks[task_name] = True
            the_scope.create_documentation()
            try:
                documentation_tasks.pop(task_name)
            except:
                pass

        summary_list += each_scope + " - " + str(the_scope.type) + "\n"
        summary_list += str(the_scope.documentation) + "\n\n"

    # Create sha256 hash of the result
    sha256 = hashlib.sha256((summary_list + top_library).encode()).hexdigest()

    the_currently_sha = storage_4.get(sha256 + "github_sha")
    path = top_library.replace(".", "/") if "." in top_library else top_library
    path += f"/README.md"

    github_sha = github.get_sha_(path)

    result = the_currently_sha == github_sha

    if (
        len(AccessKey(request.authorization.password).scopes_read) == ["*"]
        or AccessKey(request.authorization.password).is_admin == True
    ):
        return jsonify({"status": True, "result": result})
    else:
        result = None


@app.route(get_readme_url, methods=["POST"])
def get_readme():
    """ """
    top_library = request.form.get("top_library")
    version = request.form.get("version")
    all_scopes_response = Scope.get_all_scopes_name_prefix(
        AccessKey(request.authorization.password), top_library
    )
    all_scopes = []
    for each_scope in all_scopes_response:
        if version != None:
            the_version_history_response = Scope(each_scope).version_history
            the_version_history = []
            for element in the_version_history_response:
                the_version_history.append(element.replace(each_scope + ":", ""))
            if version in the_version_history:
                all_scopes.append(each_scope)
        else:
            all_scopes.append(each_scope)

    # order by alphabetical
    all_scopes.sort()

    result = f"{top_library}"
    for i in all_scopes:
        result += i + "\n"

    summary_list = ""
    for each_scope in all_scopes:
        task_name = each_scope
        if version == None:
            the_scope = Scope(each_scope)
        else:
            task_name = each_scope + ":" + version
            the_scope = Scope.get_version(each_scope + ":" + version)

        while task_name in documentation_tasks:
            return jsonify({"status": True, "result": None})
            time.sleep(1)

        if the_scope.documentation == None:
            documentation_tasks[task_name] = True
            the_scope.create_documentation()
            try:
                documentation_tasks.pop(task_name)
            except:
                pass

        summary_list += each_scope + " - " + str(the_scope.type) + "\n"
        summary_list += str(the_scope.documentation) + "\n\n"

    # Create sha256 hash of the result
    sha256 = hashlib.sha256((summary_list + top_library).encode()).hexdigest()

    return jsonify({"status": True, "result": storage_4.get(sha256)})


@app.route(create_version_prefix_url, methods=["post"])
def create_version_prefix():
    """ """
    user = AccessKey(request.authorization.password)
    top_library = request.form.get("top_library")
    version = request.form.get("version")
    all_scopes = Scope.get_all_scopes_name_prefix(user, top_library)
    write_scopes = user.scopes_write
    for each_scope in all_scopes:
        if each_scope in write_scopes or user.is_admin:
            Scope(each_scope).create_version(version, user)

    return jsonify({"status": True, "result": True})


@app.route(delete_version_prefix_url, methods=["post"])
def delete_version_prefix():
    """ """
    user = AccessKey(request.authorization.password)
    top_library = request.form.get("top_library")
    version = request.form.get("version")

    all_scopes = Scope.get_all_scopes_name_prefix(user, top_library)
    write_scopes = user.scopes_write
    for each_scope in all_scopes:
        if each_scope in write_scopes or user.is_admin:
            try:
                Scope(each_scope).delete_version(each_scope + ":" + version)
            except:
                pass

    return jsonify({"status": True, "result": True})


@app.route(dump_run_url, methods=["POST"])
def dump_run():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    os_type = request.form.get("os_type")
    os_architecture = request.form.get("os_architecture")
    os_version = request.form.get("os_version")
    python_version = request.form.get("python_version")
    _type = request.form.get("type")
    cpu_usage = request.form.get("cpu_usage")
    memory_usage = request.form.get("memory_usage")
    elapsed_time = request.form.get("elapsed_time")
    the_scope = Scope(scope)
    op = the_scope.add_run_history(
        version=version,
        os_type=os_type,
        os_architecture=os_architecture,
        os_version=os_version,
        python_version=python_version,
        type=_type,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        elapsed_time=elapsed_time,
    )
    return jsonify({"status": True, "result": op})


@app.route(get_last_runs_url, methods=["POST"])
def get_last_runs():
    """ """
    scope = request.form.get("scope")
    last_runs = request.form.get("n")
    the_scope = Scope(scope)
    if last_runs != None:
        op = the_scope.get_last_runs(int(last_runs))
    else:
        op = the_scope.get_last_runs()
    return jsonify({"status": True, "result": op})


@app.route(get_github_sync_of_scope_url, methods=["POST"])
def get_github_sync_of_scope():
    """ """
    scope = request.form.get("scope")
    version = request.form.get("version")
    if version != None:
        the_scope = Scope.get_version(scope + ":" + version)
    else:
        the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.is_it_github_synced()})


def create_get_release_note_(top_library, version, request=None):
    """

    :param top_library:
    :param version:
    :param request:  (Default value = None)

    """
    global documentation_tasks
    print("RELEASE NOTE TASK for: ", top_library)

    all_scopes_response = (
        Scope.get_all_scopes_name_prefix(
            AccessKey(request.authorization.password), top_library
        )
        if request != None
        else Scope.get_all_scopes_name_prefix(prefix=top_library)
    )
    all_scopes = []

    for each_scope in all_scopes_response:
        if version != None:
            the_version_history_response = Scope(each_scope).version_history
            the_version_history = []
            for element in the_version_history_response:
                the_version_history.append(element.replace(each_scope + ":", ""))
            if version in the_version_history:
                all_scopes.append(each_scope)
        else:
            all_scopes.append(each_scope)

    # order by alphabetical
    all_scopes.sort()

    result = f"{top_library}"
    for i in all_scopes:
        result += i + "\n"

    summary_list = ""
    any_update = False
    for each_scope in all_scopes:
        task_name = each_scope
        if version == None:
            the_scope = Scope(each_scope)
        else:
            task_name = each_scope + ":" + version
            the_scope = Scope.get_version(each_scope + ":" + version)

        summary_list += each_scope + " - " + str(the_scope.type) + "\n"
        the_release_note = the_scope.release_note
        if the_release_note != None and the_release_note != "No Changes Made":
            any_update = True
        else:
            the_release_note = "No Changes Made."
        summary_list += str(the_release_note) + "\n\n"

    print("summary list", summary_list)

    # Create sha256 hash of the result
    sha256 = hashlib.sha256((summary_list + top_library).encode()).hexdigest()

    request_from = storage_4.get(sha256)
    if request_from == None:
        result = (
            AI.generate_releate_note(top_library, summary_list, version)
            if any_update
            else "No Changes Made"
        )

        storage_4.set(sha256, result)
    else:
        result = request_from

    print("Release Note task complated for: ", top_library)

    return result


@app.route(create_get_release_note_url, methods=["POST"])
def create_get_release_note():
    """ """
    top_library = request.form.get("top_library")
    version = request.form.get("version")

    return jsonify(
        {
            "status": True,
            "result": create_get_release_note_(top_library, version, request),
        }
    )
