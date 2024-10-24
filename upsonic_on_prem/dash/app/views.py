import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from app.api_integration import API_Integration
from app import models
from app import forms

from dash.logs import logger

import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")

github_active = os.environ.get("github_active", "false").lower() == "true"
github_repo_owner = os.environ.get("github_repo_owner")
github_repo_name = os.environ.get("github_repo_name")


def the_connection_code(request):
    custom_connection_url = os.getenv("custom_connection_url")
    use_one = os.environ.get("use_one", "false").lower() == "true"

    if custom_connection_url != None:
        the_connection_code = f"""from upsonic import UpsonicOnPrem
upsonic = UpsonicOnPrem('{custom_connection_url}', '{request.user.access_key}')
"""
    elif custom_connection_url == None and not use_one:
        the_connection_code = f"""from upsonic import UpsonicOnPrem
upsonic = UpsonicOnPrem('https://{request.get_host()}:7340', '{request.user.access_key}')
"""
    else:
        the_connection_code = f"""from upsonic import UpsonicOnPrem
upsonic = UpsonicOnPrem('https://{request.get_host()}/api', '{request.user.access_key}')
"""
        
    
    return the_connection_code


# Create your views here.
@login_required
def home(request, exception=None):
    # Get parameter from the URL
    the_view = request.GET.get("view")
    print("the_view", the_view)
    if the_view == None:
        the_view = "card"

    the_top_scopes = []
    for each in API_Integration(request.user.access_key).top_scopes:
        all_scopes_source = API_Integration(
            request.user.access_key
        ).get_all_scopes_name_prefix(each)
        total_sub_amount = len(all_scopes_source)
        the_top_scopes.append({"name": each, "total_sub_amount": total_sub_amount})


    zero_scope = False
    if len(the_top_scopes) == 0:
        zero_scope = True

    version = API_Integration(request.user.access_key).view_version()


    data = {
        "page_title": "Home",
        "top_scopes": the_top_scopes,
        "the_connection_code": the_connection_code(request),
        "the_view": the_view,
        "version": version,
        "zero_scope": zero_scope
    }

    return render(request, "templates/home.html", data)

@login_required
def quic_start_disabled(request, exception=None):


    the_top_scopes = []
    for each in API_Integration(request.user.access_key).top_scopes:
        all_scopes_source = API_Integration(
            request.user.access_key
        ).get_all_scopes_name_prefix(each)
        total_sub_amount = len(all_scopes_source)
        the_top_scopes.append({"name": each, "total_sub_amount": total_sub_amount})


    zero_scope = False
    if len(the_top_scopes) == 0:
        zero_scope = True


    if not zero_scope:
        request.user.notify(
            "Congrats",
            "Your first function sent. Now you can start to use Upsonic",
            "info",
            section="edit"
        )


    the_json = {"zero_scope": zero_scope}

    return JsonResponse(the_json, safe=False)



def notifications(request):
    the_notifications_of_the_user = request.user.notifications.filter(read=False)
    json_notifications = []
    for notification in the_notifications_of_the_user:
        json_notifications.append(
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "date": notification.date,
                "read": notification.read,
                "important": notification.important,
            }
        )
        if not notification.important:
            notification.read = True
        notification.save()
    return JsonResponse(json_notifications, safe=False)


def notification_read_id(request, id):
    notification = request.user.notifications.get(id=id)
    notification.read = True
    notification.save()
    return HttpResponse(status=200)


@login_required
def community(request):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_users = API_Integration(request.user.access_key).get_users()
    the_users.pop(0)
    data = {
        "page_title": "Community",
        "users": the_users,
    }
    return render(request, "templates/community.html", data)


@login_required
def control_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == "POST":
        user_form = forms.UpdateUserForm(request.POST, instance=the_user)

        if user_form.is_valid():
            user_form.save()
            the_user.set_password(request.POST.get("password"))
            the_user.save()
            request.user.notify(
                "User Updated",
                f"User {the_user.username} updated successfully, the user must login again to access",
                "info"
            )
            return redirect(to="control_user", id=id)

    else:
        gpt_model = False
        if (
            API_Integration(request.user.access_key)
            .get_default_ai_model()
            .startswith("gpt")
        ):
            gpt_model = True

        the_read_scopes = API_Integration(
            request.user.access_key
        ).get_read_scopes_of_user(the_user.access_key)
        the_write_scopes = API_Integration(
            request.user.access_key
        ).get_write_scopes_of_user(the_user.access_key)
        any_read_scope = True if len(the_read_scopes) != 0 else False
        any_write_scope = True if len(the_write_scopes) != 0 else False

        data = {
            "page_title": "Control User",
            "user": the_user,
            "gpt_model": gpt_model,
            "user_form": forms.UpdateUserForm(instance=the_user),
            "read_scopes": the_read_scopes,
            "write_scopes": the_write_scopes,
            "any_read_scope": any_read_scope,
            "any_write_scope": any_write_scope,
            "scope_form": forms.ScopeForm(),
            "is_enabled": API_Integration(request.user.access_key).is_enabed_user(
                the_user.access_key
            ),
            "is_admin": API_Integration(request.user.access_key).is_admin(
                the_user.access_key
            ),
            "is_robust_admin": API_Integration(request.user.access_key).is_robust_admin(
                the_user.access_key
            ),
        }
        return render(request, "templates/control_user.html", data)


@login_required
def add_write_scope(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == "POST":
        scope_form = forms.ScopeForm(request.POST)

        if scope_form.is_valid():
            API_Integration(request.user.access_key).add_write_scope(
                request.POST.get("scope"), the_user.access_key
            )
            request.user.notify(
                "Write Scope Added",
                f"Scope {request.POST.get('scope')} added to user {the_user.username}",
                "info"
            )
            return redirect(to="control_user", id=id)

    else:
        return HttpResponse(status=403)


def delete_write_scope(request, scope, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_write_scope(
        scope, the_user.access_key
    )
    request.user.notify(
        "Write Scope Deleted", f"Scope {scope} deleted from user {the_user.username}",
                "info"
    )
    return redirect(to="control_user", id=id)


def add_read_scope(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == "POST":
        scope_form = forms.ScopeForm(request.POST)

        if scope_form.is_valid():
            API_Integration(request.user.access_key).add_read_scope(
                request.POST.get("scope"), the_user.access_key
            )
            request.user.notify(
                "Read Scope Added",
                f"Scope {request.POST.get('scope')} added to user {the_user.username}",
                "info"
            )
            return redirect(to="control_user", id=id)

    else:
        return HttpResponse(status=403)


def delete_read_scope(request, id, scope):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_read_scope(
        scope, the_user.access_key
    )
    request.user.notify(
        "Read Scope Deleted", f"Scope {scope} deleted from user {the_user.username}",
                "info"
    )
    return redirect(to="control_user", id=id)


@login_required
def libraries(request):
    the_top_scopes = []
    for each in API_Integration(request.user.access_key).top_scopes:
        all_scopes_source = API_Integration(
            request.user.access_key
        ).get_all_scopes_name_prefix(each)
        total_sub_amount = len(all_scopes_source)
        the_top_scopes.append({"name": each, "total_sub_amount": total_sub_amount})

    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "the_connection_code": the_connection_code(request),
        "top_scopes": the_top_scopes,
    }

    return render(request, "templates/libraries/libraries.html", data)


@login_required
def control_library(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    code = ""

    the_name = id.replace(".", "_")

    if version != None:
        code = f'{the_name} = upsonic.load_module("{id}", version="{version}")'
    else:
        code = f'{the_name} = upsonic.load_module("{id}")'

    the_content = None
    try:
        the_content_response = API_Integration(request.user.access_key).subs_of_scope(
            id, version=version
        )
        if version != None:
            the_content = {}
            for each in the_content_response:
                the_content[each + ":" + version] = the_content_response[each]
        else:
            the_content = the_content_response
    except:
        pass

    if the_content == None:
        return redirect(to="libraries")

    docs_are_ready = True

    all_scopes = []
    all_scopes_source = API_Integration(
        request.user.access_key
    ).get_all_scopes_name_prefix(id)
    for each_scope in all_scopes_source:
        write_right = request.user.can_write(each_scope)
        if version != None:
            if version in API_Integration(request.user.access_key).get_version_history(
                each_scope
            ):
                sub_doc = API_Integration(request.user.access_key).get_documentation(
                    each_scope, version=version
                )
                if sub_doc == None:
                    docs_are_ready = False
                    if version == None:
                        the_id = id
                    else:
                        the_id = id + ":" + version
                    tasks = models.AI_Task.objects.filter(
                        task_name="documentation", key=the_id, status=False
                    )
                    if len(tasks) == 0:
                        pass
                        # models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
                    sub_doc = "Documentation is generating, it will be ready soon."

                all_scopes.append([each_scope, sub_doc])

        else:
            sub_doc = API_Integration(request.user.access_key).get_documentation(
                each_scope
            )

            if sub_doc == None:
                docs_are_ready = False
                if version == None:
                    the_id = id
                else:
                    the_id = id + ":" + version
                tasks = models.AI_Task.objects.filter(
                    task_name="documentation", key=the_id, status=False
                )
                if len(tasks) == 0:
                    pass
                    # models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
                sub_doc = "Documentation is generating, it will be ready soon."

            all_scopes.append([each_scope, sub_doc])

    if version == None:
        the_id = id
    else:
        the_id = id + ":" + version

    tasks = models.AI_Task.objects.filter(task_name="readme", key=the_id, status=False)
    if len(tasks) == 0:
        readme = (
            API_Integration(request.user.access_key).get_readme(id, version=version)
            if docs_are_ready
            else None
        )
        if readme == None:
            readme = "Generating..."

            if len(tasks) == 0:
                if not request.user.full_access(id):
                    readme = "No readme"
                # models.AI_Task(task_name="readme", key=the_id, access_key=request.user.access_key, owner=request.user).save()
    else:
        readme = "Generating..."

    github_synced = False

    github_url = f"https://github.com/{github_repo_owner}/{github_repo_name}/"
    if github_active:
        github_synced = API_Integration(request.user.access_key).get_readme_github_sync(
            id, version=version
        )

    total_sub_amount = len(all_scopes_source)

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Home",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "sub_module": True if "." in id else False,
        "full_write_access": request.user.full_access_write(id),
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": code,
        "readme": readme,
        "all_scopes": all_scopes,
        "total_sub_amount": total_sub_amount,
        "version": "" if version == None else version,
        "github_synced": github_synced,
        "github_url": github_url,
        "github_active": github_active,
    }
    return render(request, "templates/libraries/control_library.html", data)


def capitalize_first_letter(input_string):
    if not input_string:
        return input_string
    else:
        return input_string[0].upper() + input_string[1:]


@login_required
def control_element(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    using_code = ""
    if version == None:
        first_thing = id.split(".")[0]
        using_code = f'''
{first_thing} = upsonic.load_module("{first_thing}")

{id}()
'''
    else:
        using_code = f'upsonic.load("{id}", version="{version}")()'

    documentation = API_Integration(request.user.access_key).get_documentation(
        id, version=version
    )

    write_right = request.user.can_write(id)

    gpt_model = False
    if (
        API_Integration(request.user.access_key)
        .get_default_ai_model()
        .startswith("gpt")
    ):
        gpt_model = True

    if documentation == None:
        if version == None:
            the_id = id
        else:
            the_id = id + ":" + version
        tasks = models.AI_Task.objects.filter(
            task_name="documentation", key=the_id, status=False
        )
        if len(tasks) == 0:
            pass
            # models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        documentation = "Documentation is generating, it will be ready soon."

    time_complexity = API_Integration(request.user.access_key).get_time_complexity(
        id, version=version
    )
    if time_complexity == None:
        if version == None:
            the_id = id
        else:
            the_id = id + ":" + version
        tasks = models.AI_Task.objects.filter(
            task_name="time_complexity", key=the_id, status=False
        )
        if len(tasks) == 0:
            pass
            # models.AI_Task(task_name="time_complexity", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        time_complexity = "Time Complexity is generating, it will be ready soon."
    

    any_task = False
    if len(models.AI_Task.objects.filter(task_name="documentation", key=id, status=False)) > 0:
        any_task = True
    if len(models.AI_Task.objects.filter(task_name="time_complexity", key=id, status=False)) > 0:
        any_task = True




    tags = API_Integration(request.user.access_key).get_tags(id, version=version)
    if tags == None:
        if version == None:
            the_id = id
        else:
            the_id = id + ":" + version
        tasks = models.AI_Task.objects.filter(
            task_name="tags", key=the_id, status=False
        )
        if len(tasks) == 0:
            pass
            # models.AI_Task(task_name="tags", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        tags = "Tags are generating, it will be ready soon."



    requirements = API_Integration(request.user.access_key).get_requirements(
        id, version=version
    )
    the_type = API_Integration(request.user.access_key).get_type(id, version=version)
    python_version = API_Integration(request.user.access_key).get_python_version(
        id, version=version
    )

    the_dumps = []
    for dump in API_Integration(request.user.access_key).get_dump_history(id):
        dump_id = dump.split(":")[1]
        user = None
        user_response = API_Integration(request.user.access_key).get_dump_user(
            id, dump_id
        )
        if user_response != [None]:
            user = models.User.objects.get(access_key=user_response).username

        the_dumps.append({"dump_id": dump_id, "user": user})

    if version == None:
        cpu_usage_analyses_response = API_Integration(
            request.user.access_key
        ).get_settings(id)
        if cpu_usage_analyses_response == None:
            cpu_usage_analyses = False
        else:
            if "usage_analyses" in cpu_usage_analyses_response:
                try:
                    cpu_usage_analyses = (
                        cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                    )
                except:
                    cpu_usage_analyses = None
    else:
        cpu_usage_analyses = None

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Home",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
        "using_code": using_code,
        "documentation": documentation,
        "time_complexity": time_complexity,
        "any_task": any_task,

    
        "tags": tags,

        "requirements": requirements,
        "type": capitalize_first_letter(the_type),
        "python_version": python_version,
        "gpt_model": gpt_model,
        "version": "" if version == None else version,
        "dumps": the_dumps,
        "cpu_usage_analyses": cpu_usage_analyses,
        "can_write": request.user.can_write(id),
    }
    return render(request, "templates/libraries/element.html", data)


@login_required
def control_element_dependency(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    dependency = API_Integration(request.user.access_key).get_dependency(
        id, version=version
    )

    any_dependency = False
    if dependency["in"] != []:
        any_dependency = True
    if dependency["out"] != []:
        any_dependency = True

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Dependency",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "version": "" if version == None else version,
        "dependency": dependency,
        "any_dependency": any_dependency,
    }
    return render(request, "templates/libraries/element_dependency.html", data)


# Write a view to regererate the documentation
@login_required
def regenerate_documentation(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    request.user.notify(
        "Documentation is Generating",
        f"Documentation for {id} is generating, it will be ready soon.",
                "info"
    )
    models.AI_Task(
        task_name="documentation",
        key=id,
        access_key=request.user.access_key,
        owner=request.user,
    ).save()
    models.AI_Task(
        task_name="time_complexity",
        key=id,
        access_key=request.user.access_key,
        owner=request.user,
    ).save()


    models.AI_Task(
        task_name="tags", key=id, access_key=request.user.access_key, owner=request.user
    ).save()

    request.user.notify(
        "Documentation Generated",
        f"Documentation for {id} is generated, you can access it now.",
                "info"
    )
    return redirect(to="control_element", id=id)


@login_required
def regenerate_readme(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    print("STARTED TO REGENERATE README")
    models.AI_Task(
        task_name="readme",
        key=id,
        access_key=request.user.access_key,
        owner=request.user,
    ).save()
    print("returning to control_library")
    return redirect(to="control_library", id=id)


@login_required
def delete_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)

    if the_user.access_key == request.user.access_key:
        return HttpResponse(status=403)


    if API_Integration(request.user.access_key).is_robust_admin(the_user.access_key) == False:
        the_user.delete_user(request.user.access_key)
        the_user.delete()
        request.user.notify(
            "User Deleted", f"User {the_user.username} deleted successfully",
                "info"
        )
        return redirect(to="community")
    else:

        return redirect(to="community")


@login_required
def delete_scope(request, id):
    API_Integration(request.user.access_key).delete_code(id)
    request.user.notify("Scope Deleted", f"Scope {id} deleted successfully",
                "info")
    if "." in id:
        return redirect(to="control_library", id=".".join(id.split(".")[:-1]))
    return redirect(to="libraries")


@login_required
def enable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_user(the_user.access_key)
    request.user.notify(
        "User Enabled", f"User {the_user.username} enabled successfully",
                "info"
    )
    return redirect(to="community")


@login_required
def disable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)

    if the_user.access_key == request.user.access_key:
        return HttpResponse(status=403)


    API_Integration(request.user.access_key).disable_user(the_user.access_key)
    request.user.notify(
        "User Disabled", f"User {the_user.username} disabled successfully",
                "info"
    )
    return redirect(to="community")


@login_required
def enable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_admin(the_user.access_key)
    request.user.notify("Admin Enabled", f"User {the_user.username} is now an admin",
                "info")
    return redirect(to="community")


@login_required
def disable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    
    the_user = models.User.objects.get(id=id)

    if the_user.access_key == request.user.access_key:
        return HttpResponse(status=403)

    
    API_Integration(request.user.access_key).disable_admin(the_user.access_key)
    request.user.notify(
        "Admin Disabled", f"User {the_user.username} is no longer an admin",
                "info"
    )
    return redirect(to="community")


@login_required
def add_user(request):
    if not request.user.is_admin:
        return HttpResponse(status=403)

    if request.method == "POST":
        user_form = forms.CustomUserCreationForm(request.POST)

        if user_form.is_valid():
            user_form.save()

            request.user.notify(
                "User Added",
                f"User {user_form.cleaned_data.get('username')} added successfully",
                "info"
            )
            return redirect(to="community")
        else:
            data = {
                "page_title": "Add User",
                "user_form": forms.CustomUserCreationForm(),
                "error": user_form.errors,
            }
            return render(request, "templates/add_user.html", data)

    else:
        data = {
            "page_title": "Add User",
            "user_form": forms.CustomUserCreationForm(),
            "error": False,
        }
        return render(request, "templates/add_user.html", data)


@login_required
def profile(request):
    the_read_scopes = API_Integration(request.user.access_key).get_read_scopes_of_me()
    the_write_scopes = API_Integration(request.user.access_key).get_write_scopes_of_me()

    any_read_scope = True if len(the_read_scopes) != 0 else False
    any_write_scope = True if len(the_write_scopes) != 0 else False
    data = {
        "page_title": "Profile",
        "read_scopes": the_read_scopes,
        "write_scopes": the_write_scopes,
        "any_read_scope": any_read_scope,
        "any_write_scope": any_write_scope,
    }
    return render(request, "templates/profile.html", data)


@login_required
def search(request):
    if request.method == "POST":
        min_score = float(request.POST.get("min_score", 0))
        how_many_result = int(request.POST.get("how_many_result", 10))
        data = {
            "page_title": "Search",
            "results": API_Integration(request.user.access_key).search_by_documentation(
                request.POST.get("question"), min_score, how_many_result
            ),
            "question": request.POST.get("question"),
            "min_score": min_score,
            "how_many_result": how_many_result,
            "searched": True,
        }
        return render(request, "templates/search.html", data)

    else:
        data = {
            "page_title": "Search",
            "searched": False,
        }
        return render(request, "templates/search.html", data)


@login_required
def control_element_version(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    using_code = ""
    using_code = f'upsonic.load("{id}")()'

    write_right = request.user.can_write(id)

    requirements = API_Integration(request.user.access_key).get_requirements(id)
    the_type = API_Integration(request.user.access_key).get_type(id)
    python_version = API_Integration(request.user.access_key).get_python_version(id)

    print("id", id)
    the_versions = []
    the_versions_response = API_Integration(
        request.user.access_key
    ).get_version_history(id)
    no_version = False
    if the_versions_response == [None]:
        no_version = True
    else:
        for element in the_versions_response:
            code = None
            code_response = API_Integration(request.user.access_key).get_version_code(
                id, element
            )
            difference = API_Integration(
                request.user.access_key
            ).get_version_difference(id, element)
            if code_response != [None]:
                code = code_response
            user = None
            user_response = API_Integration(request.user.access_key).get_version_user(
                id, element
            )
            if user_response != [None]:
                user = models.User.objects.get(access_key=user_response).username
            release_note = API_Integration(
                request.user.access_key
            ).get_version_release_note(id, element)
            date = API_Integration(request.user.access_key).get_version_date(
                id, element
            )
            data = {
                "release_note": release_note,
                "version": element,
                "date": date,
                "code": code,
                "difference": difference,
                "using_code": f'upsonic.load("{id}", version="{element}")()',
                "link": id + ":" + element,
                "user": user,
            }
            the_versions.append(data)

    the_versions.reverse()
    data = {
        "page_title": "Libraries",
        "sub_page_title": "Version",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id),
        "using_code": using_code,
        "requirements": requirements,
        "type": capitalize_first_letter(the_type),
        "python_version": python_version,
        "the_versions": the_versions,
        "no_version": no_version,
        "version": "" if version == None else version,
        "using_code": f'upsonic.load("{id}")()',
        "create_version": request.user.can_write(id),
    }
    return render(request, "templates/libraries/element_version.html", data)


@login_required
def control_library_version(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    code = ""

    the_name = id.replace(".", "_")

    the_content = None
    try:
        the_content = API_Integration(request.user.access_key).subs_of_scope(id)
    except:
        pass
    if the_content == None:
        return redirect(to="libraries")

    all_scopes_response = API_Integration(
        request.user.access_key
    ).get_all_scopes_name_prefix(id)
    print(all_scopes_response)
    all_possible_versions = []
    the_version_history = []
    counter = {}
    for each_scope in all_scopes_response:
        scope_versions = API_Integration(request.user.access_key).get_version_history(
            each_scope
        )
        for each_version in scope_versions:
            user = None
            user_response = API_Integration(request.user.access_key).get_version_user(
                each_scope, each_version
            )
            if user_response != [None]:
                user = models.User.objects.get(access_key=user_response).username
            if each_version not in counter:
                counter[each_version] = 0
            counter[each_version] += 1
            if each_version not in all_possible_versions:
                all_possible_versions.append(each_version)
                date = API_Integration(request.user.access_key).get_version_date(
                    each_scope, each_version
                )
                the_time = API_Integration(request.user.access_key).get_version_time(
                    each_scope, each_version
                )
                the_version_history.append([each_version, user, date, the_time])

    the_version_history.sort(key=lambda x: x[3], reverse=True)

    the_versions = []
    for each_version in the_version_history:
        number = counter[each_version[0]]

        if number < len(all_scopes_response):
            pass
        else:
            pass
        if not request.user.full_access(id):
            the_release_note = "No release note"
        else:
            the_release_note = API_Integration(
                request.user.access_key
            ).create_get_release_note(id, each_version[0])
        the_versions.append(
            {
                "version": each_version[0],
                "date": each_version[2],
                "release_note": the_release_note,
                "using_code": f'{the_name} = upsonic.load_module("{id}", version="{each_version[0]}")',
                "link": id + ":" + each_version[0],
                "user": each_version[1],
            }
        )

    no_version = False
    if len(the_versions) == 0:
        no_version = True

    total_sub_amount = len(all_scopes_response)

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Version",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "sub_module": True if "." in id else False,
        "full_write_access": request.user.full_access_write(id),
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "the_versions": the_versions,
        "total_sub_amount": total_sub_amount,
        "no_version": no_version,
        "version": "" if version == None else version,
        "using_code": f'{the_name} = upsonic.load_module("{id}")',
    }
    return render(request, "templates/libraries/control_library_version.html", data)


@login_required
def control_element_version_create(request, id):
    if not request.user.can_write(id):
        return HttpResponse(status=403)

    if request.method == "POST":
        version = request.POST.get("version")
        API_Integration(request.user.access_key).create_version(id, version)
        return redirect(to="control_element_version", id=id)
    else:
        return redirect(to="control_element", id=id)


@login_required
def control_library_version_create(request, id):
    if request.method == "POST":
        version = request.POST.get("version")
        API_Integration(request.user.access_key).create_version_prefix(id, version)
        return redirect(to="control_library_version", id=id)
    else:
        return redirect(to="control_library", id=id)


@login_required
def control_library_version_delete(request, id, version):
    API_Integration(request.user.access_key).delete_version_prefix(id, version)
    return redirect(to="control_library_version", id=id)


@login_required
def control_element_version_delete(request, id, version):
    API_Integration(request.user.access_key).delete_version(id, version)
    return redirect(to="control_element_version", id=id)


@login_required
def activate_usage_analyses(request, id):
    the_settings = API_Integration(request.user.access_key).get_settings(id)
    try:
        if the_settings == None:
            the_settings = {}
        if not isinstance(the_settings, dict):
            the_settings = {}
        the_settings["usage_analyses"] = True
        print("Dumping the settings", the_settings)
        API_Integration(request.user.access_key).dump_settings(id, the_settings)
    except:
        pass
    return redirect(to="control_element_settings", id=id)


@login_required
def deactivate_usage_analyses(request, id):
    the_settings = API_Integration(request.user.access_key).get_settings(id)
    try:
        if the_settings == None:
            the_settings = {}
        if not isinstance(the_settings, dict):
            the_settings = {}
        the_settings["usage_analyses"] = False
        API_Integration(request.user.access_key).dump_settings(id, the_settings)
    except:
        pass
    return redirect(to="control_element_settings", id=id)


@login_required
def control_element_runs(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    get_last_runs = API_Integration(request.user.access_key).get_last_runs(id)
    latest_commit = (
        API_Integration(request.user.access_key).get_dump_history(id)[0].split(":")[1]
    )

    for each_run in get_last_runs:
        if each_run["data"]["version"] == latest_commit:
            each_run["data"]["version_short"] = "Latest"
            each_run["data"]["version_tag"] = "Latest"
        else:
            try:
                each_run["data"]["version_short"] = (
                    each_run["data"]["version"][:4]
                    + "..."
                    + each_run["data"]["version"][-4:]
                )
            except:
                pass

        number = float(each_run["data"]["cpu_usage"])
        each_run["data"]["cpu_usage"] = float(f"{number:.1f}")

        number2 = float(each_run["data"]["elapsed_time"])
        each_run["data"]["elapsed_time"] = float(f"{number2:.1f}")
        each_run["data"]["time"] = datetime.datetime.fromtimestamp(
            int(str(each_run["data"]["time"]).split(".")[0])
        ).strftime("%c")

    cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(
        id
    )
    if cpu_usage_analyses_response == None:
        cpu_usage_analyses = False
    else:
        if "usage_analyses" in cpu_usage_analyses_response:
            try:
                cpu_usage_analyses = (
                    cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                )
            except:
                cpu_usage_analyses = None

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Runs",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
        "get_last_runs": get_last_runs,
        "cpu_usage_analyses": cpu_usage_analyses,
        "version": "" if version == None else version,
        "can_write": request.user.can_write(id),
    }
    return render(request, "templates/libraries/element_runs.html", data)


@login_required
def control_element_runs_analyze(request, id, run_sha):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    get_last_run = API_Integration(request.user.access_key).get_run(id, run_sha)
    latest_commit = (
        API_Integration(request.user.access_key).get_dump_history(id)[0].split(":")[1]
    )

    if get_last_run["data"]["version"] == latest_commit:
        get_last_run["data"]["version_short"] = "Latest"
        get_last_run["data"]["version_tag"] = "Latest"
    else:
        try:
            get_last_run["data"]["version_short"] = (
                get_last_run["data"]["version"][:4]
                + "..."
                + get_last_run["data"]["version"][-4:]
            )
        except:
            pass

    number = float(get_last_run["data"]["cpu_usage"])
    get_last_run["data"]["cpu_usage"] = float(f"{number:.1f}")

    number2 = float(get_last_run["data"]["elapsed_time"])
    get_last_run["data"]["elapsed_time"] = float(f"{number2:.1f}")

    username = None
    try:
        access_key = get_last_run["data"]["access_key"]
        username = models.User.objects.get(access_key=access_key).username
    except:
        pass

    get_last_run["data"]["username"] = username

    get_last_run["data"]["time"] = datetime.datetime.fromtimestamp(
        int(str(get_last_run["data"]["time"]).split(".")[0])
    ).strftime("%c")

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Runs",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
        "run": get_last_run["data"],
        "version": "" if version == None else version,
        "can_write": request.user.can_write(id),
    }
    return render(request, "templates/libraries/element_runs_analyze.html", data)


@login_required
def control_element_settings(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(
        id
    )
    if cpu_usage_analyses_response == None:
        cpu_usage_analyses = False
    else:
        if "usage_analyses" in cpu_usage_analyses_response:
            try:
                cpu_usage_analyses = (
                    cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                )
            except:
                cpu_usage_analyses = None

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Settings",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "cpu_usage_analyses": cpu_usage_analyses,
        "version": "" if version == None else version,
    }
    return render(request, "templates/libraries/element_settings.html", data)


@login_required
def control_element_commits(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    the_dumps = []
    for dump in API_Integration(request.user.access_key).get_dump_history(id):
        dump_id = dump.split(":")[1]
        user = None
        user_response = API_Integration(request.user.access_key).get_dump_user(
            id, dump_id
        )
        if user_response != [None]:
            user = models.User.objects.get(access_key=user_response).username
        the_date = API_Integration(request.user.access_key).get_dump_date(id, dump_id)
        difference = API_Integration(request.user.access_key).get_dump_difference(
            id, dump_id
        )
        commit_message = API_Integration(
            request.user.access_key
        ).get_dump_commit_message(id, dump_id)
        the_dumps.append(
            {
                "commit_message": commit_message,
                "dump_id": dump_id,
                "user": user,
                "date": the_date,
                "difference": difference,
            }
        )

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Commits",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "version": "" if version == None else version,
        "dumps": the_dumps,
    }
    return render(request, "templates/libraries/element_commits.html", data)


@login_required
def control_library_settings(request, id):
    version = None
    if ":" in id:
        version = id.split(":")[1]
        id = id.split(":")[0]

    have_upper = False
    the_upper = ""
    if "." in id:
        print("Have upper 1")
        have_upper = True
        last = id.split(".")[-1]
        index_of_last = id.split(".").index(last)
        the_upper = id.split(".")[:index_of_last]
        print("the_upper", the_upper)
        print("last", last)
        the_upper = ".".join(the_upper)
        if version != None:
            the_upper = the_upper + ":" + version

    code = ""

    the_name = id.replace(".", "_")

    if version != None:
        code = f'{the_name} = upsonic.load_module("{id}", version="{version}")'
    else:
        code = f'{the_name} = upsonic.load_module("{id}")'

    the_content = None
    try:
        the_content_response = API_Integration(request.user.access_key).subs_of_scope(
            id, version=version
        )
        if version != None:
            the_content = {}
            for each in the_content_response:
                the_content[each + ":" + version] = the_content_response[each]
        else:
            the_content = the_content_response
    except:
        pass

    if the_content == None:
        return redirect(to="libraries")

    total_usage_analyses = True
    for each in API_Integration(request.user.access_key).get_all_scopes_name_prefix(id):
        cpu_usage_analyses_response = API_Integration(
            request.user.access_key
        ).get_settings(each)
        cpu_usage_analyses = None
        if cpu_usage_analyses_response == None:
            cpu_usage_analyses = False

        else:
            if "usage_analyses" in cpu_usage_analyses_response:
                try:
                    cpu_usage_analyses = (
                        cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                    )
                except:
                    cpu_usage_analyses = None
        if cpu_usage_analyses != True:
            total_usage_analyses = False
            break

    print(total_usage_analyses)

    all_scopes_response = API_Integration(
        request.user.access_key
    ).get_all_scopes_name_prefix(id)
    total_sub_amount = len(all_scopes_response)

    data = {
        "page_title": "Libraries",
        "sub_page_title": "Settings",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "sub_module": True if "." in id else False,
        "full_write_access": request.user.full_access_write(id),
        "control_library_with_version": id if version == None else id + ":" + version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "total_sub_amount": total_sub_amount,
        "total_usage_analyses": total_usage_analyses,
        "version": "" if version == None else version,
    }
    return render(request, "templates/libraries/control_library_settings.html", data)


@login_required
def activate_usage_analyses_prefix(request, id):
    for each in API_Integration(request.user.access_key).get_all_scopes_name_prefix(id):
        the_settings = API_Integration(request.user.access_key).get_settings(each)
        try:
            if the_settings == None:
                the_settings = {}
            if not isinstance(the_settings, dict):
                the_settings = {}
            the_settings["usage_analyses"] = True
            print("Dumping the settings", the_settings)
            API_Integration(request.user.access_key).dump_settings(each, the_settings)
        except:
            pass

    return redirect(to="control_library_settings", id=id)


@login_required
def deactivate_usage_analyses_prefix(request, id):
    for each in API_Integration(request.user.access_key).get_all_scopes_name_prefix(id):
        the_settings = API_Integration(request.user.access_key).get_settings(each)
        try:
            if the_settings == None:
                the_settings = {}
            if not isinstance(the_settings, dict):
                the_settings = {}
            the_settings["usage_analyses"] = False
            print("Dumping the settings", the_settings)
            API_Integration(request.user.access_key).dump_settings(each, the_settings)
        except:
            pass

    return redirect(to="control_library_settings", id=id)


def add_ai_task(request):
    if not request.method == "POST":
        redirect(to="home")

    task_name = request.POST.get("task_name")
    key = request.POST.get("key")
    access_key = request.POST.get("access_key")

    user_input = request.POST.get("user_input", "")

    user = models.User.objects.get(access_key=access_key)

    if not user.can_write(key):
        redirect(to="home")

    the_object = models.AI_Task(
        task_name=task_name,
        key=key,
        access_key=access_key,
        owner=user,
        not_start_task=True,
        user_input=user_input,
    )
    the_object.save()

    the_json = {"id": the_object.id}

    return JsonResponse(the_json, safe=False)


def complate_ai_task(request):
    if not request.method == "POST":
        redirect(to="home")

    the_id = request.POST.get("id")
    access_key = request.POST.get("access_key")

    ai_output = request.POST.get("ai_output", "")

    user = models.User.objects.get(access_key=access_key)

    the_object = models.AI_Task.objects.get(id=the_id)
    the_object.ai_output = ai_output

    if not user.can_write(the_object.key):
        redirect(to="home")

    the_object.status = True
    the_object.save()

    the_json = {"id": the_object.id}

    return JsonResponse(the_json, safe=False)


@login_required
def settings_dark_mode(request):
    request.user.dark_mode = True
    request.user.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def settings_light_mode(request):
    request.user.dark_mode = False
    request.user.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def analyze_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)

    events = API_Integration(request.user.access_key).get_last_x_events(
        the_user.access_key
    )

    data = {
        "page_title": "Analyze User",
        "user": the_user,
        "events": events,
        "user_form": forms.UpdateUserForm(instance=the_user),
    }
    return render(request, "templates/analyze_user.html", data)



from django.contrib.auth import get_user_model

from sesame.utils import get_query_string
from django.http import JsonResponse


from django.views.decorators.http import require_POST

@require_POST
def one_time_login(request):
    the_pass = request.POST.get('the_pass')
    username = request.POST.get('username')

    # Get the first user in the database
    first_user = get_user_model().objects.first()
    
    # Check if the provided password matches the first user's password
    if not first_user.check_password(the_pass):
        return HttpResponse(status=403)
    
    # Get the user by username
    user = models.User.objects.get(username=username)

    LOGIN_URL = "/sesame/login/"
    LOGIN_URL += get_query_string(user)

    return JsonResponse({'url': LOGIN_URL})



@require_POST
def add_admin_user_post(request):
    the_pass = request.POST.get('the_pass')

    # Get the first user in the database
    first_user = get_user_model().objects.first()
    
    # Check if the provided password matches the first user's password
    if not first_user.check_password(the_pass):
        return HttpResponse(status=403)
    
    first_name = request.POST.get('first_name')
    email = request.POST.get('email')
    last_name = request.POST.get('last_name')

    username = request.POST.get('username')

    password = request.POST.get('password')




    user = models.User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    user.add_user(first_user.access_key)

    API_Integration(first_user.access_key).enable_admin(user.access_key)


    return JsonResponse({'status': True})





@require_POST
def get_username_of_ak(request):
    access_key = request.POST.get('access_key')
    try:
        the_user = get_user_model().objects.get(access_key=access_key)
        the_username = the_user.username
        return JsonResponse({'status': True, "result":the_username})
    except:
        return JsonResponse({'status': True, "result":None})