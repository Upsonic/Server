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
    request.user.notify("Welcome to Upsonic", "Your free cloud is ready, you can start using it now.")
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
            return redirect(to='control_user', id=id)

    else:

        data = {
            "page_title": "Community",
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
            return redirect(to='control_user', id=id)

    else:
        return HttpResponse(status=403)


def delete_write_scope(request, scope, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_write_scope(scope, the_user.access_key)
    return redirect(to='control_user', id=id)


def add_read_scope(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    if request.method == 'POST':
        scope_form = forms.ScopeForm(request.POST)

        if scope_form.is_valid():
            API_Integration(request.user.access_key).add_read_scope(request.POST.get("scope"), the_user.access_key)
            return redirect(to='control_user', id=id)

    else:
        return HttpResponse(status=403)


def delete_read_scope(request, id, scope):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_read_scope(scope, the_user.access_key)
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
def control_element(request,id):

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
    }
    return render(request, f"templates/libraries/element.html", data)


# Write a view to regererate the documentation
@login_required
def regenerate_documentation(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    API_Integration(request.user.access_key).create_documentation(id)
    return redirect(to='control_element', id=id)

@login_required
def delete_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    the_user.delete_user(request.user.access_key)
    the_user.delete()
    return redirect(to='community')


@login_required
def delete_scope(request, id):
    API_Integration(request.user.access_key).delete_code(id)
    # if scope is an sub scope like onur.my_function return to control_element onur
    if "." in id:
        return redirect(to='control_library', id=".".join(id.split(".")[:-1]))
    return redirect(to='libraries')

@login_required
def enable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_user(the_user.access_key)
    return redirect(to='community')
@login_required
def disable_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).disable_user(the_user.access_key)
    return redirect(to='community')


@login_required
def enable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).enable_admin(the_user.access_key)
    return redirect(to='community')

@login_required
def disable_admin(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    the_user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).disable_admin(the_user.access_key)
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
            return redirect(to='community')
        else:
            print(user_form.errors)

    else:

        data = {
            "page_title": "Community",
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