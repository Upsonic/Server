from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.http.response import HttpResponse
from app.api_integration import API_Integration
from app import models

from app import forms


# Create your views here.
@login_required
def home(request, exception=None):

    data = {
        "page_title": "Home",
        "top_scopes": API_Integration(request.user.access_key).top_scopes
    }

    return render(request, "templates/home.html",data)



def notifications(request):
    the_notifications_of_the_user = request.user.notifications.filter(read=False)
    json_notifications = []
    for notification in the_notifications_of_the_user:
        json_notifications.append({"id": notification.id, "title": notification.title, "message": notification.message,
                                   "date": notification.date, "read": notification.read,
                                   "important": notification.important})
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
    data = {
        "page_title": "Community",
        "users": API_Integration(request.user.access_key).get_users(),
    }
    return render(request, "templates/community.html", data)

@login_required
def control_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == 'POST':
        user_form = forms.UpdateUserForm(request.POST, instance=the_user)

        if user_form.is_valid():
            user_form.save()
            the_user.set_password(request.POST.get("password"))
            the_user.save()
            request.user.notify("User Updated", f"User {the_user.username} updated successfully, the user must login again to access")
            return redirect(to='control_user', id=id)

    else:

        data = {
            "page_title": "Control User",
            "user": the_user,
            "user_form": forms.UpdateUserForm(instance=the_user),
            "read_scopes": API_Integration(request.user.access_key).get_read_scopes_of_user(the_user.access_key),
            "write_scopes": API_Integration(request.user.access_key).get_write_scopes_of_user(the_user.access_key),
            "scope_form": forms.ScopeForm(),
        }
        return render(request, "templates/control_user.html", data)


@login_required
def add_write_scope(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == 'POST':
        scope_form = forms.ScopeForm(request.POST)

        if scope_form.is_valid():
            API_Integration(request.user.access_key).add_write_scope(request.POST.get("scope"), the_user.access_key)
            request.user.notify("Write Scope Added", f"Scope {request.POST.get('scope')} added to user {the_user.username}")
            return redirect(to='control_user', id=id)

    else:
        return HttpResponse(status=403)


def delete_write_scope(request, scope, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_write_scope(scope, the_user.access_key)
    request.user.notify("Write Scope Deleted", f"Scope {scope} deleted from user {the_user.username}")
    return redirect(to='control_user', id=id)


def add_read_scope(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == 'POST':
        scope_form = forms.ScopeForm(request.POST)

        if scope_form.is_valid():
            API_Integration(request.user.access_key).add_read_scope(request.POST.get("scope"), the_user.access_key)
            request.user.notify("Read Scope Added", f"Scope {request.POST.get('scope')} added to user {the_user.username}")
            return redirect(to='control_user', id=id)

    else:
        return HttpResponse(status=403)


def delete_read_scope(request, id, scope):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_read_scope(scope, the_user.access_key)
    request.user.notify("Read Scope Deleted", f"Scope {scope} deleted from user {the_user.username}")
    return redirect(to='control_user', id=id)

@login_required
def libraries(request):
    data = {"page_title": "Libraries", "libraries": API_Integration(request.user.access_key).top_scopes}

    return render(request, f"templates/libraries/libraries.html", data)

@login_required
def control_library(request,id):

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



    code = ""

    the_name = id.replace(".", "_")

    code = f'{the_name} = upsonic.load_module("{id}")'

    the_content = None
    try:
        the_content = API_Integration(request.user.access_key).subs_of_scope(id)
    except:
        pass
    if the_content == None:
        return redirect(to='libraries')

    readme = API_Integration(request.user.access_key).get_readme(id)
    if readme == None:
        readme = "Generating..."
        tasks = models.AI_Task.objects.filter(task_name="readme", key=id, status=False)
        if len(tasks) == 0:        
            models.AI_Task(task_name="readme", key=id, access_key=request.user.access_key, owner=request.user).save()
    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": code,
        "readme": readme,
    }
    return render(request, f"templates/libraries/control_library.html", data)
def capitalize_first_letter(input_string):
    if not input_string:
        return input_string
    else:
        return input_string[0].upper() + input_string[1:]


@login_required
def control_element(request, id):

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


    using_code = ""
    using_code = f'upsonic.load("{id}")()'

    documentation = API_Integration(request.user.access_key).get_documentation(id)

    write_right = request.user.can_write(id)

    if documentation == None and write_right:
        tasks = models.AI_Task.objects.filter(task_name="documentation", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="documentation", key=id, access_key=request.user.access_key, owner=request.user).save()
        documentation = "Documentation is generating, it will be ready soon."

    
    time_complexity = API_Integration(request.user.access_key).get_time_complexity(id)
    if time_complexity == None and write_right:

        tasks = models.AI_Task.objects.filter(task_name="time_complexity", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="time_complexity", key=id, access_key=request.user.access_key, owner=request.user).save()
        time_complexity = "Time Complexity is generating, it will be ready soon."



    mistakes = API_Integration(request.user.access_key).get_mistakes(id)
    if mistakes == None and write_right:

        tasks = models.AI_Task.objects.filter(task_name="mistakes", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="mistakes", key=id, access_key=request.user.access_key, owner=request.user).save()
        mistakes = "Mistakes are generating, it will be ready soon."


    required_test_types = API_Integration(request.user.access_key).get_required_test_types(id)
    if required_test_types == None and write_right:

        tasks = models.AI_Task.objects.filter(task_name="required_test_types", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="required_test_types", key=id, access_key=request.user.access_key, owner=request.user).save()
        required_test_types = "Required Test Types are generating, it will be ready soon."



    tags = API_Integration(request.user.access_key).get_tags(id)
    if tags == None and write_right:

        tasks = models.AI_Task.objects.filter(task_name="tags", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="tags", key=id, access_key=request.user.access_key, owner=request.user).save()
        tags = "Tags are generating, it will be ready soon."



    security_analysis = API_Integration(request.user.access_key).get_security_analysis(id)
    if security_analysis == None and write_right:
        tasks = models.AI_Task.objects.filter(task_name="security_analysis", key=id, status=False)
        if len(tasks) == 0:
            models.AI_Task(task_name="security_analysis", key=id, access_key=request.user.access_key, owner=request.user).save()
        security_analysis = "Security Analysis is generating, it will be ready soon."






    requirements = API_Integration(request.user.access_key).get_requirements(id)
    the_type = API_Integration(request.user.access_key).get_type(id)
    python_version = API_Integration(request.user.access_key).get_python_version(id)

    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id),
        "using_code": using_code,
        "documentation": documentation,
        "time_complexity": time_complexity,
        "mistakes": mistakes,
        "required_test_types": required_test_types,
        "tags": tags,
        "security_analysis": security_analysis,
        "requirements": requirements,
        "type": capitalize_first_letter(the_type),
        "python_version": python_version,
    }
    return render(request, f"templates/libraries/element.html", data)


# Write a view to regererate the documentation
@login_required
def regenerate_documentation(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    request.user.notify("Documentation is Generating", f"Documentation for {id} is generating, it will be ready soon.")
    models.AI_Task(task_name="documentation", key=id, access_key=request.user.access_key, owner=request.user).save()
    models.AI_Task(task_name="time_complexity", key=id, access_key=request.user.access_key, owner=request.user).save()
    models.AI_Task(task_name="mistakes", key=id, access_key=request.user.access_key, owner=request.user).save()
    models.AI_Task(task_name="required_test_types", key=id, access_key=request.user.access_key, owner=request.user).save()
    models.AI_Task(task_name="tags", key=id, access_key=request.user.access_key, owner=request.user).save()
    models.AI_Task(task_name="security_analysis", key=id, access_key=request.user.access_key, owner=request.user).save()
    request.user.notify("Documentation Generated", f"Documentation for {id} is generated, you can access it now.")
    return redirect(to='control_element', id=id)


@login_required
def regenerate_readme(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    print("STARTED TO REGENERATE README")
    models.AI_Task(task_name="readme", key=id, access_key=request.user.access_key, owner=request.user).save()
    print("returning to control_library")
    return redirect(to='control_library', id=id)

@login_required
def delete_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    the_user.delete_user(request.user.access_key)
    the_user.delete()
    request.user.notify("User Deleted", f"User {the_user.username} deleted successfully")
    return redirect(to='community')


@login_required
def delete_scope(request, id):
    API_Integration(request.user.access_key).delete_code(id)
    request.user.notify("Scope Deleted", f"Scope {id} deleted successfully")
    if "." in id:
        return redirect(to='control_library', id=".".join(id.split(".")[:-1]))
    return redirect(to='libraries')

@login_required
def enable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_user(the_user.access_key)
    request.user.notify("User Enabled", f"User {the_user.username} enabled successfully")
    return redirect(to='community')
@login_required
def disable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).disable_user(the_user.access_key)
    request.user.notify("User Disabled", f"User {the_user.username} disabled successfully")
    return redirect(to='community')


@login_required
def enable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_admin(the_user.access_key)
    request.user.notify("Admin Enabled", f"User {the_user.username} is now an admin")
    return redirect(to='community')

@login_required
def disable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).disable_admin(the_user.access_key)
    request.user.notify("Admin Disabled", f"User {the_user.username} is no longer an admin")
    return redirect(to='community')


@login_required
def add_user(request):
    if not request.user.is_admin:
        return HttpResponse(status=403)

    if request.method == 'POST':
        user_form = forms.CustomUserCreationForm(request.POST)

        if user_form.is_valid():
            user_form.save()
            user_form.user.add_user(request.user.access_key)
            request.user.notify("User Added", f"User {user_form.cleaned_data.get('username')} added successfully")
            return redirect(to='community')
        else:
            print(user_form.errors)

    else:

        data = {
            "page_title": "Add User",
            "user_form": forms.CustomUserCreationForm()
        }
        return render(request, "templates/add_user.html", data)


@login_required
def profile(request):
    data = {
        "page_title": "Profile",
        "read_scopes": API_Integration(request.user.access_key).get_read_scopes_of_me(),
        "write_scopes": API_Integration(request.user.access_key).get_write_scopes_of_me(),
    }
    return render(request, "templates/profile.html", data)




@login_required
def ai(request):
    result = None

    if request.method == "POST":
        input_data = request.POST.get("ai_input")
        result = API_Integration(request.user.access_key).ai_completion(input_data)

    the_list = models.AI_Task.objects.filter(status=False)
    tasks = []
    for task in the_list:
        if request.user.can_read(task.key):
            tasks.append(task)
    data = {
        "page_title": "AI",
        "tasks": tasks,
        "result": result,
    }
    return render(request, "templates/ai.html", data)


@login_required
def search(request):
    if request.method == 'POST':
        min_score = float(request.POST.get("min_score", 0))
        how_many_result = int(request.POST.get("how_many_result", 10))
        data = {
            "page_title": "Search",
            "results": API_Integration(request.user.access_key).search_by_documentation(request.POST.get("question"), min_score, how_many_result),
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