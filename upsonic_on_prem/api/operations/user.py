from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, storage_2, AccessKey, Scope, AI

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
@app.route(get_requirements_of_scope_url, methods=["POST"])
def get_requirements_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).requirements})


@app.route(get_time_complexity_of_scope_url, methods=["POST"])
def get_time_complexity_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).time_complexity})



@app.route(get_mistakes_of_scope_url, methods=["POST"])
def get_mistakes_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).mistakes})


@app.route(get_required_test_types_of_scope_url, methods=["POST"])
def get_required_test_types_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).required_test_types})


@app.route(get_security_analysis_of_scope_url, methods=["POST"])
def get_security_analysis_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).security_analysis})



@app.route(get_code_of_scope_url, methods=["POST"])
def get_code_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).code})



@app.route(create_document_of_scope_url, methods=["POST"])
def create_document_of_scope():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_documentation()})

@app.route(create_time_complexity_of_scope_url, methods=["POST"])
def create_time_complexity_of_scope():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_time_complexity()})




@app.route(create_mistakes_of_scope_url, methods=["POST"])
def create_mistakes_of_scope():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_mistakes()})

@app.route(create_required_test_types_of_scope_url, methods=["POST"])
def create_required_test_types_of_scope():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_required_test_types()})

@app.route(create_security_analysis_of_scope_url, methods=["POST"])
def create_security_analysis_of_scope():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_security_analysis()})






@app.route(create_document_of_scope_url_old, methods=["POST"])
def create_document_of_scope_old():
    scope = request.form.get("scope")

    return jsonify({"status": True, "result": Scope(scope).create_documentation_old()})

@app.route(get_type_of_scope_url, methods=["POST"])
def get_type_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).type})

@app.route(get_python_version_of_scope_url, methods=["POST"])
def get_python_version_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).python_version})


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

@app.route(dump_requirements_url, methods=["POST"])
def dump_requirements():
    scope = request.form.get("scope")
    requirement = request.form.get("requirements")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_requirements(requirement)})



@app.route(dump_python_version_url, methods=["POST"])
def dump_python_version():
    scope = request.form.get("scope")
    python_version = request.form.get("python_version")

    the_scope = Scope(scope)

    return jsonify({"status": True, "result": the_scope.set_python_version(python_version)})




@app.route(search_by_documentation_url, methods=["POST"])
def search_by_documentation():
    question = request.form.get("question")
    min_score = float(request.form.get("min_score", 600))
    how_many_result = int(request.form.get("how_many_result", 10))

    user = AccessKey(request.authorization.password)
    scopes = Scope.get_all_scopes_with_documentation(user)
    if len(scopes) == 0:
        return jsonify({"status": False, "result": "No scope has documentation"})

    results = AI.search_by_documentation(scopes, question, min_score, how_many_result)

    return jsonify({"status": True, "result": results})