import hashlib
from upsonic_on_prem.api import app

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.utils import storage, storage_2, storage_4, AccessKey, Scope, AI

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


@app.route(get_tags_of_scope_url, methods=["POST"])
def get_tags_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).tags})

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


@app.route(create_tags_of_scope_url, methods=["POST"])
def create_tags_of_scope():
    scope = request.form.get("scope")
    return jsonify({"status": True, "result": Scope(scope).create_tags()})


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
        if result[0] in the_read_scopes or user.is_admin:
            access_control_list.append(result)

    return jsonify({"status": True, "result": access_control_list})




@app.route(ai_completion_url, methods=["POST"])
def ai_completion():
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
    return jsonify({"status": True, "result": AI.default_model})


@app.route(create_readme_url, methods=["POST"])
def create_readme():
    top_library = request.form.get("top_library")
    all_scopes = Scope.get_all_scopes_name_prefix(AccessKey(request.authorization.password), top_library)

    # order by alphabetical
    all_scopes.sort()

    result = f"{top_library}"
    for i in all_scopes:
        result += i + "\n"
    
    #Create sha256 hash of the result
    sha256 = hashlib.sha256(result.encode()).hexdigest()

    summary_list = ""
    for each_scope in all_scopes:
        summary_list += each_scope +" - " + Scope(each_scope).type + "\n"
        summary_list += Scope(each_scope).documentation + "\n\n"


    result = AI.generate_readme(top_library, summary_list)

    storage_4.set(sha256, result)

    return jsonify({"status": True, "result": result})

@app.route(get_readme_url, methods=["POST"])
def get_readme():
    top_library = request.form.get("top_library")
    all_scopes = Scope.get_all_scopes_name_prefix(AccessKey(request.authorization.password), top_library)

    # order by alphabetical
    all_scopes.sort()

    result = f"{top_library}"
    for i in all_scopes:
        result += i + "\n"

    print("TOP_library", top_library)
    print("All scopes", result)
    
    #Create sha256 hash of the result
    sha256 = hashlib.sha256(result.encode()).hexdigest()

    return jsonify({"status": True, "result": storage_4.get(sha256)})