from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.http.response import HttpResponse
from app.api_integration import API_Integration
from app import models

from app import forms

import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


def the_connection_code(request):
    custom_connection_url = os.getenv("custom_connection_url")
    if custom_connection_url == None:
        the_connection_code = f"""
from upsonic import Upsonic_On_Prem
upsonic = Upsonic_On_Prem('https://{request.get_host()}:7340', '{request.user.access_key}')
"""
    else:
        the_connection_code = f"""
from upsonic import Upsonic_On_Prem
upsonic = Upsonic_On_Prem('{custom_connection_url}', '{request.user.access_key}')
"""
    return the_connection_code

# Create your views here.
@login_required
def home(request, exception=None):



    data = {
        "page_title": "Home",
        "top_scopes": API_Integration(request.user.access_key).top_scopes,
        "the_connection_code": the_connection_code(request),
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

        openai_api_key = API_Integration(the_user.access_key).get_openai_api_key_user()
        if openai_api_key["special"] == False:
            openai_api_key = "SHARED_KEY"
        else:
            openai_api_key = openai_api_key["api_key"]

        gpt_model = False
        if API_Integration(request.user.access_key).get_default_ai_model().startswith("gpt"):
            gpt_model = True

        data = {
            "page_title": "Control User",
            "user": the_user,
            "openai_api_key": openai_api_key,
            "gpt_model": gpt_model,
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
    data = {"page_title": "Libraries", "libraries": API_Integration(request.user.access_key).top_scopes, "the_connection_code": the_connection_code(request),}

    return render(request, f"templates/libraries/libraries.html", data)

@login_required
def control_library(request,id):

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
            the_upper = the_upper +":"+ version



    code = ""

    the_name = id.replace(".", "_")

    if version != None:
        code = f'{the_name} = upsonic.load_module("{id}", version="{version}")'
    else:
        code = f'{the_name} = upsonic.load_module("{id}")'

    the_content = None
    try:
        the_content_response = API_Integration(request.user.access_key).subs_of_scope(id, version=version)
        if version != None:
            the_content = {}
            for each in the_content_response:
                the_content[each+":"+version] = the_content_response[each]
        else:
            the_content = the_content_response
    except:
        pass

    

    if the_content == None:
        return redirect(to='libraries')

    docs_are_ready = True

    all_scopes = []
    for each_scope in API_Integration(request.user.access_key).get_all_scopes_name_prefix(id):
        write_right = request.user.can_write(each_scope)
        if version != None:
            if version in API_Integration(request.user.access_key).get_version_history(each_scope):
                sub_doc =  API_Integration(request.user.access_key).get_documentation(each_scope, version=version)
                if sub_doc == None and write_right:
                    docs_are_ready = False
                    if version == None:
                            the_id = id
                    else:
                            the_id = id +":"+version         
                    tasks = models.AI_Task.objects.filter(task_name="documentation", key=the_id, status=False)
                    if len(tasks) == 0:
                    
                        models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
                    sub_doc = "Documentation is generating, it will be ready soon."

                all_scopes.append([each_scope, sub_doc])

        else:
            sub_doc = API_Integration(request.user.access_key).get_documentation(each_scope)

            if sub_doc == None and write_right:
                    docs_are_ready = False
                    if version == None:
                            the_id = id
                    else:
                            the_id = id +":"+version         
                    tasks = models.AI_Task.objects.filter(task_name="documentation", key=the_id, status=False)
                    if len(tasks) == 0:
                    
                        models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
                    sub_doc = "Documentation is generating, it will be ready soon."

            all_scopes.append([each_scope, sub_doc])            



    if version == None:
        the_id = id
    else:
        the_id = id +":"+version    

    tasks = models.AI_Task.objects.filter(task_name="readme", key=the_id, status=False)
    if len(tasks) == 0:  

        readme = API_Integration(request.user.access_key).get_readme(id, version=version) if docs_are_ready else None
        if readme == None:
            readme = "Generating..."
    
            if len(tasks) == 0:        

                models.AI_Task(task_name="readme", key=the_id, access_key=request.user.access_key, owner=request.user).save()
    else:
        readme = "Generating..."

    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": code,
        "readme": readme,
        "all_scopes": all_scopes,
        "version": "" if version == None else version,
    }
    return render(request, f"templates/libraries/control_library.html", data)


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
            the_upper = the_upper +":"+ version



    using_code = ""
    using_code = f'upsonic.load("{id}")()'

    documentation = API_Integration(request.user.access_key).get_documentation(id, version=version)

    write_right = request.user.can_write(id)


    gpt_model = False
    if API_Integration(request.user.access_key).get_default_ai_model().startswith("gpt"):
        gpt_model = True


    if documentation == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version         
        tasks = models.AI_Task.objects.filter(task_name="documentation", key=the_id, status=False)
        if len(tasks) == 0:
         
            models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        documentation = "Documentation is generating, it will be ready soon."

    
    time_complexity = API_Integration(request.user.access_key).get_time_complexity(id, version=version)
    if time_complexity == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="time_complexity", key=the_id, status=False)
        if len(tasks) == 0:
           
            models.AI_Task(task_name="time_complexity", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        time_complexity = "Time Complexity is generating, it will be ready soon."



    mistakes = API_Integration(request.user.access_key).get_mistakes(id, version=version)
    if mistakes == None and write_right and gpt_model:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="mistakes", key=the_id, status=False)
        if len(tasks) == 0:
         
            models.AI_Task(task_name="mistakes", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        mistakes = "Mistakes are generating, it will be ready soon."


    required_test_types = API_Integration(request.user.access_key).get_required_test_types(id, version=version)
    if required_test_types == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="required_test_types", key=the_id, status=False)
        if len(tasks) == 0:
          
            models.AI_Task(task_name="required_test_types", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        required_test_types = "Required Test Types are generating, it will be ready soon."



    tags = API_Integration(request.user.access_key).get_tags(id, version=version)
    if tags == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version  
        tasks = models.AI_Task.objects.filter(task_name="tags", key=the_id, status=False)
        if len(tasks) == 0:
          
            models.AI_Task(task_name="tags", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        tags = "Tags are generating, it will be ready soon."



    security_analysis = API_Integration(request.user.access_key).get_security_analysis(id, version=version)
    if security_analysis == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version            
        tasks = models.AI_Task.objects.filter(task_name="security_analysis", key=the_id, status=False)
        if len(tasks) == 0:
        
            models.AI_Task(task_name="security_analysis", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        security_analysis = "Security Analysis is generating, it will be ready soon."






    requirements = API_Integration(request.user.access_key).get_requirements(id, version=version)
    the_type = API_Integration(request.user.access_key).get_type(id, version=version)
    python_version = API_Integration(request.user.access_key).get_python_version(id, version=version)

    the_dumps = []
    for dump in API_Integration(request.user.access_key).get_dump_history(id):
        dump_id = dump.split(":")[1]
        user = None
        user_response = API_Integration(request.user.access_key).get_dump_user(id, dump_id)
        if user_response != [None]:
            user = models.User.objects.get(access_key=user_response).username

        the_dumps.append({"dump_id": dump_id, "user":user})


    
    if version == None:
        cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(id)
        if cpu_usage_analyses_response == None:
            cpu_usage_analyses = False
        else:
            if "usage_analyses" in cpu_usage_analyses_response:
                try:
                    cpu_usage_analyses = cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                except:
                    
                    cpu_usage_analyses = None
    else:
        cpu_usage_analyses = None


    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
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
        "gpt_model": gpt_model,
        "version": "" if version == None else version,
        "dumps": the_dumps,
        "cpu_usage_analyses": cpu_usage_analyses,
        "can_write": request.user.can_write(id)
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
            data = {
                "page_title": "Add User",
                "user_form": forms.CustomUserCreationForm(),
                "error": user_form.errors
            }
            return render(request, "templates/add_user.html", data)

    else:

        data = {
            "page_title": "Add User",
            "user_form": forms.CustomUserCreationForm(),
            "error": False
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
    


@login_required
def set_openai_api_key_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    
    if request.method == 'POST':
        openai_api_key = request.POST.get("openai_api_key")
        user = models.User.objects.get(id=id)
        API_Integration(request.user.access_key).set_openai_api_key_user(user.access_key, openai_api_key)
        return redirect(to='control_user', id=id)
    else:
        return redirect(to='community')


@login_required
def delete_openai_api_key_user(request, id):
    if not request.user.is_admin:
        return HttpResponse(status=403)
    user = models.User.objects.get(id=id)
    API_Integration(request.user.access_key).delete_openai_api_key_user(user.access_key)
    return redirect(to='control_user', id=id)






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
            the_upper = the_upper +":"+ version



    using_code = ""
    using_code = f'upsonic.load("{id}")()'

    write_right = request.user.can_write(id)





    requirements = API_Integration(request.user.access_key).get_requirements(id)
    the_type = API_Integration(request.user.access_key).get_type(id)
    python_version = API_Integration(request.user.access_key).get_python_version(id)

    print("id", id)
    the_versions = []
    the_versions_response = API_Integration(request.user.access_key).get_version_history(id)
    no_version = False
    if the_versions_response == [None]:
        no_version = True
    else:
        for element in the_versions_response:
            code = None
            code_response = API_Integration(request.user.access_key).get_version_code(id, element)
            if code_response != [None]:
                code = code_response
            user = None
            user_response = API_Integration(request.user.access_key).get_version_user(id, element)
            if user_response != [None]:
                user = models.User.objects.get(access_key=user_response).username              
            data = {"version":element, "code": code, "using_code":f'upsonic.load("{id}", version="{element}")()', "link":id+":"+element, "user":user}
            the_versions.append(data)


    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
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
        "using_code":f'upsonic.load("{id}")()',
        "create_version":request.user.can_write(id)
    }
    return render(request, f"templates/libraries/element_version.html", data)



@login_required
def control_library_version(request,id):
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
            the_upper = the_upper +":"+ version



    code = ""

    the_name = id.replace(".", "_")



    the_content = None
    try:
        the_content = API_Integration(request.user.access_key).subs_of_scope(id)
    except:
        pass
    if the_content == None:
        return redirect(to='libraries')



    all_scopes_response = API_Integration(request.user.access_key).get_all_scopes_name_prefix(id)
    print(all_scopes_response)
    all_possible_versions = []
    the_version_history = []
    for each_scope in all_scopes_response:
        scope_versions = API_Integration(request.user.access_key).get_version_history(each_scope)
        for each_version in scope_versions:
            if each_version not in all_possible_versions:
                user = None
                user_response = API_Integration(request.user.access_key).get_version_user(each_scope, each_version)
                if user_response != [None]:
                    user = models.User.objects.get(access_key=user_response).username                   
                all_possible_versions.append(each_version)
                the_version_history.append([each_version, user])
    

    the_versions = []
    for each_version in the_version_history:
        the_versions.append({"version": each_version[0], "using_code": f'{the_name} = upsonic.load_module("{id}", version="{each_version[0]}")', "link":id+":"+each_version[0], "user":each_version[1]})

    no_version = False
    if len(the_versions) == 0:
        no_version = True


    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "the_versions": the_versions,
        "no_version": no_version,
        "version": "" if version == None else version,
        "using_code": f'{the_name} = upsonic.load_module("{id}")'
    }
    return render(request, f"templates/libraries/control_library_version.html", data)


@login_required
def control_element_version_create(request, id):
    if not request.user.can_write(id):
        return HttpResponse(status=403)
    
    if request.method == 'POST':
        version = request.POST.get("version")
        API_Integration(request.user.access_key).create_version(id, version)
        return redirect(to='control_element_version', id=id)
    else:
        return redirect(to='control_element', id=id)


@login_required
def control_library_version_create(request, id):

    if request.method == 'POST':
        version = request.POST.get("version")
        API_Integration(request.user.access_key).create_version_prefix(id, version)
        return redirect(to='control_library_version', id=id)
    else:
        return redirect(to='control_library', id=id)


@login_required
def control_library_version_delete(request, id, version):
        API_Integration(request.user.access_key).delete_version_prefix(id, version)
        return redirect(to='control_library_version', id=id)

@login_required
def control_element_version_delete(request, id, version):
        API_Integration(request.user.access_key).delete_version(id, version)
        return redirect(to='control_element_version', id=id)



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
    return redirect(to='control_element_settings', id=id)

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
    return redirect(to='control_element_settings', id=id)    



    


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
            the_upper = the_upper +":"+ version



    get_last_runs = API_Integration(request.user.access_key).get_last_runs(id)



    cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(id)
    if cpu_usage_analyses_response == None:
            cpu_usage_analyses = False
    else:
        if "usage_analyses" in cpu_usage_analyses_response:
            try:
                cpu_usage_analyses = cpu_usage_analyses_response["usage_analyses"].lower() == "true"
            except:
                    
                cpu_usage_analyses = None


    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
        "get_last_runs": get_last_runs,
        "cpu_usage_analyses":cpu_usage_analyses,
        "version": "" if version == None else version,
        "can_write": request.user.can_write(id)
    }
    return render(request, f"templates/libraries/element_runs.html", data)    


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
            the_upper = the_upper +":"+ version



    using_code = ""
    using_code = f'upsonic.load("{id}")()'

    documentation = API_Integration(request.user.access_key).get_documentation(id, version=version)

    write_right = request.user.can_write(id)


    gpt_model = False
    if API_Integration(request.user.access_key).get_default_ai_model().startswith("gpt"):
        gpt_model = True


    if documentation == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version         
        tasks = models.AI_Task.objects.filter(task_name="documentation", key=the_id, status=False)
        if len(tasks) == 0:
         
            models.AI_Task(task_name="documentation", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        documentation = "Documentation is generating, it will be ready soon."

    
    time_complexity = API_Integration(request.user.access_key).get_time_complexity(id, version=version)
    if time_complexity == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="time_complexity", key=the_id, status=False)
        if len(tasks) == 0:
           
            models.AI_Task(task_name="time_complexity", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        time_complexity = "Time Complexity is generating, it will be ready soon."



    mistakes = API_Integration(request.user.access_key).get_mistakes(id, version=version)
    if mistakes == None and write_right and gpt_model:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="mistakes", key=the_id, status=False)
        if len(tasks) == 0:
         
            models.AI_Task(task_name="mistakes", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        mistakes = "Mistakes are generating, it will be ready soon."


    required_test_types = API_Integration(request.user.access_key).get_required_test_types(id, version=version)
    if required_test_types == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version 
        tasks = models.AI_Task.objects.filter(task_name="required_test_types", key=the_id, status=False)
        if len(tasks) == 0:
          
            models.AI_Task(task_name="required_test_types", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        required_test_types = "Required Test Types are generating, it will be ready soon."



    tags = API_Integration(request.user.access_key).get_tags(id, version=version)
    if tags == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version  
        tasks = models.AI_Task.objects.filter(task_name="tags", key=the_id, status=False)
        if len(tasks) == 0:
          
            models.AI_Task(task_name="tags", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        tags = "Tags are generating, it will be ready soon."



    security_analysis = API_Integration(request.user.access_key).get_security_analysis(id, version=version)
    if security_analysis == None and write_right:
        if version == None:
                the_id = id
        else:
                the_id = id +":"+version            
        tasks = models.AI_Task.objects.filter(task_name="security_analysis", key=the_id, status=False)
        if len(tasks) == 0:
        
            models.AI_Task(task_name="security_analysis", key=the_id, access_key=request.user.access_key, owner=request.user).save()
        security_analysis = "Security Analysis is generating, it will be ready soon."






    requirements = API_Integration(request.user.access_key).get_requirements(id, version=version)
    the_type = API_Integration(request.user.access_key).get_type(id, version=version)
    python_version = API_Integration(request.user.access_key).get_python_version(id, version=version)



    


    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "code": API_Integration(request.user.access_key).get_code(id, version=version),
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
        "gpt_model": gpt_model,
        "version": "" if version == None else version,
        "can_write": request.user.can_write(id)
    }
    return render(request, f"templates/libraries/element.html", data)



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
            the_upper = the_upper +":"+ version

    

    cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(id)
    if cpu_usage_analyses_response == None:
            cpu_usage_analyses = False
    else:
            if "usage_analyses" in cpu_usage_analyses_response:
                try:
                    cpu_usage_analyses = cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                except:
                    
                    cpu_usage_analyses = None




    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "cpu_usage_analyses": cpu_usage_analyses,
        "version": "" if version == None else version,

    }
    return render(request, f"templates/libraries/element_settings.html", data)






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
            the_upper = the_upper +":"+ version



    the_dumps = []
    for dump in API_Integration(request.user.access_key).get_dump_history(id):
        dump_id = dump.split(":")[1]
        user = None
        user_response = API_Integration(request.user.access_key).get_dump_user(id, dump_id)
        if user_response != [None]:
            user = models.User.objects.get(access_key=user_response).username

        the_dumps.append({"dump_id": dump_id, "user":user})




    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "have_upper": have_upper,
        "the_upper": the_upper,
        "version": "" if version == None else version,
        "dumps": the_dumps,
    }
    return render(request, f"templates/libraries/element_commits.html", data)




@login_required
def control_library_settings(request,id):

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
            the_upper = the_upper +":"+ version



    code = ""

    the_name = id.replace(".", "_")

    if version != None:
        code = f'{the_name} = upsonic.load_module("{id}", version="{version}")'
    else:
        code = f'{the_name} = upsonic.load_module("{id}")'

    the_content = None
    try:
        the_content_response = API_Integration(request.user.access_key).subs_of_scope(id, version=version)
        if version != None:
            the_content = {}
            for each in the_content_response:
                the_content[each+":"+version] = the_content_response[each]
        else:
            the_content = the_content_response
    except:
        pass

    

    if the_content == None:
        return redirect(to='libraries')

    total_usage_analyses = True
    for each in API_Integration(request.user.access_key).get_all_scopes_name_prefix(id):   
        cpu_usage_analyses_response = API_Integration(request.user.access_key).get_settings(each)
        cpu_usage_analyses = None
        if cpu_usage_analyses_response == None:
                cpu_usage_analyses = False

        else:
            if "usage_analyses" in cpu_usage_analyses_response:
                try:
                    cpu_usage_analyses = cpu_usage_analyses_response["usage_analyses"].lower() == "true"
                except:
                    cpu_usage_analyses = None
        if cpu_usage_analyses != True:
            total_usage_analyses = False
            break

    print(total_usage_analyses)

    data = {
        "page_title": "Libraries",
        "libraries": API_Integration(request.user.access_key).top_scopes,
        "control_library": id,
        "control_library_with_version": id if version == None else id +":"+version,
        "top_control_library": id.split(".")[0],
        "content": the_content,
        "have_upper": have_upper,
        "the_upper": the_upper,
        "total_usage_analyses":total_usage_analyses,
        "version": "" if version == None else version,
    }
    return render(request, f"templates/libraries/control_library_settings.html", data)


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

    return redirect(to='control_library_settings', id=id)


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

    return redirect(to='control_library_settings', id=id)

