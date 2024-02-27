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

    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "top_control_library": id.split(".")[0],
        "content": API_Integration(request.user.access_key).subs_of_scope(id),
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": code,
    }
    return render(request, f"templates/libraries/control_library.html", data)



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
    if documentation == None:
        API_Integration(request.user.access_key).create_documentation(id)
        documentation = API_Integration(request.user.access_key).get_documentation(id)
    
    time_complexity = API_Integration(request.user.access_key).get_time_complexity(id)
    if time_complexity == None:
        API_Integration(request.user.access_key).create_time_complexity(id)
        time_complexity = API_Integration(request.user.access_key).get_time_complexity(id)


    mistakes = API_Integration(request.user.access_key).get_mistakes(id)
    if mistakes == None:
        API_Integration(request.user.access_key).create_mistakes(id)
        mistakes = API_Integration(request.user.access_key).get_mistakes(id)

    required_test_types = API_Integration(request.user.access_key).get_required_test_types(id)
    if required_test_types == None:
        API_Integration(request.user.access_key).create_required_test_types(id)
        required_test_types = API_Integration(request.user.access_key).get_required_test_types(id)
    security_analysis = API_Integration(request.user.access_key).get_security_analysis(id)
    if security_analysis == None:
        API_Integration(request.user.access_key).create_security_analysis(id)
        security_analysis = API_Integration(request.user.access_key).get_security_analysis(id)


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
        "security_analysis": security_analysis,
    }
    return render(request, f"templates/libraries/element.html", data)


# Write a view to regererate the documentation
@login_required
def regenerate_documentation(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    request.user.notify("Documentation is Generating", f"Documentation for {id} is generating, it will be ready soon.")
    API_Integration(request.user.access_key).create_documentation(id)
    request.user.notify("Documentation Generated", f"Documentation for {id} is generated, you can access it now.")
    return redirect(to='control_element', id=id)

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