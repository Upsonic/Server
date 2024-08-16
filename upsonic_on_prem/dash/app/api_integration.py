#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from app import models
from rich.console import Console

console = Console()


from dotenv import load_dotenv
from cryptography.fernet import Fernet

import traceback

import datetime

load_dotenv(dotenv_path=".env")

api_url = "http://localhost:3000"


def bold_first_word(s):
    # Split the string into a list of words
    words = s.split(" ")

    # Add the HTML bold tags to the first word
    words[0] = "<b>" + words[0] + "</b>"

    # Join the words back into a single string
    s = " ".join(words)

    return s


def transform_to_html_bold(text):
    try:
        # Find content within double asterisks
        start_idx = text.find("**")

        while start_idx != -1:
            end_idx = text.find("**", start_idx + 2)

            if end_idx == -1:
                break  # Break if no matching end double asterisks found

            # Extract content between double asterisks
            content = text[start_idx + 2 : end_idx]

            # Replace content with HTML <b> tags
            text = (
                text[:start_idx]
                + '<br><br><b class="custom_code_highlight_green">'
                + content
                + "</b><br>"
                + text[end_idx + 2 :]
            )

            # Find the next occurrence
            start_idx = text.find("**", end_idx + 2)

        if text.startswith("<br><br>"):
            text = text[8:]
    except:
        print("Error in transform_to_html_bold")

    return text


class API_Integration:
    def _log(self, message):
        console.log(message)

    def __enter__(self):
        return self  # pragma: no cover

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # pragma: no cover

    def __init__(self, admin_key):
        import requests
        from requests.auth import HTTPBasicAuth

        self.requests = requests
        self.HTTPBasicAuth = HTTPBasicAuth

        self.api_url = api_url
        self.password = admin_key

        if self.status == True:
            self._log(
                "[bold green]Upsonic[bold green] active",
            )
        else:
            self._log(
                "[bold red]Upsonic[bold red] is down",
            )

    @staticmethod
    def create_access_key():
        return (
            "ACK_"
            + (
                ((Fernet.generate_key()).decode())
                .replace("-", "")
                .replace("_", "")
                .replace("=", "")
            )[:60]
        )

    def _send_request(self, method, endpoint, data=None, make_json=True):
        try:
            response = self.requests.request(
                method,
                self.api_url + endpoint,
                data=data,
                auth=self.HTTPBasicAuth("", self.password),
                verify=False,
            )
            try:
                result = None
                if not make_json:
                    result = response.text
                else:
                    result = json.loads(response.text)
                    if result["status"] == False:
                        self._log(
                            f"[bold red]Error: {endpoint}",
                        )
                    else:
                        result = result["result"]

                return result
            except:  # pragma: no cover
                print(f"Error on '{self.api_url + endpoint}': ", response.text)

                return [None]  # pragma: no cover
        except:
            print("Error: Remote is down")

            return [None]

    @property
    def status(self):
        return self._send_request("GET", "/status")

    @property
    def users(self):
        return self._send_request("GET", "/get_users")

    @property
    def users_keys(self):
        return self._send_request("GET", "/get_users_keys")

    @property
    def admins(self):
        return self._send_request("GET", "/get_admins")

    @property
    def total_size(self):
        return self._send_request("GET", "/total_size")

    @property
    def all_scopes(self):
        result = self._send_request("GET", "/get_all_scopes_user")

        return result if result != [None] else []

    @property
    def top_scopes(self):
        all_scopes = self.all_scopes
        result_before = []

        for i in all_scopes:
            if "." in i:
                result_before.append(i.split(".")[0])

        result = []
        for i in result_before:
            if i != "":
                result.append(i)

        result = list(set(result))
        result.sort()

        return result

    @property
    def sub_based_all_scopes(self):
        return self.sub_based_all_scopes_()

    def sub_based_all_scopes_(self, prefix=None, version=None):
        all_scopes_response = self.all_scopes
        all_scopes = []
        for each_scope in all_scopes_response:
            if version != None:
                print("Version chec AAAAAAAAAAAAAAAAAAAAAAAAA")
                if version in self.get_version_history(each_scope):
                    print("pass", each_scope)
                    all_scopes.append(each_scope)
            else:
                all_scopes.append(each_scope)

        def group_by_top_level_recursive(function_list):
            grouped_dict = {}

            for function_name in function_list:
                parts = function_name.split(".")
                current_dict = grouped_dict

                for part in parts:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]

            return grouped_dict

        grouped = group_by_top_level_recursive(all_scopes)
        result = grouped

        def add_top_level_names(dictionary, parent_name=""):
            result = {}
            for key, value in dictionary.items():
                current_name = f"{parent_name}.{key}" if parent_name else key
                if isinstance(value, dict):
                    result[current_name] = add_top_level_names(value, current_name)
                else:
                    result[current_name] = value
            return result

        result = add_top_level_names(result)

        def extract_key(dictionary, target_key):
            if target_key in dictionary:
                return {target_key: dictionary[target_key]}

            for key, value in dictionary.items():
                if isinstance(value, dict):
                    result = extract_key(value, target_key)
                    if result:
                        return result

            return None

        if prefix != None:
            result = extract_key(result, prefix)

        def replace_empty_with_false(dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    if not value:
                        dictionary[key] = False
                    else:
                        replace_empty_with_false(value)
            return dictionary

        # Your example dictionary
        result = replace_empty_with_false(result)

        return result

    def subs_of_scope(self, prefix, version=None):
        sub_scopes_general_list = self.sub_based_all_scopes_(prefix, version=version)

        def match_prefix(dictionary, prefix):
            for key, value in dictionary.items():
                if key == prefix:
                    return value
                else:
                    if value != False:
                        return match_prefix(value, prefix)
            return None

        result = match_prefix(sub_scopes_general_list, prefix)

        return result

    def get_code(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_code_of_scope", data=data)

    def delete_code(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/delete_scope", data=data)

    def get_documentation(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_document_of_scope", data=data)
        )

    def get_github_sync(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return (
            self._send_request("POST", "/get_github_sync_of_scope", data=data) == True
        )

    def get_requirements(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        requirements = self._send_request(
            "POST", "/get_requirements_of_scope", data=data
        )

        if requirements is not None and requirements != [None]:
            requirements.replace(",", "")
        return requirements

    def get_dependency(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        requirements = self._send_request("POST", "/get_dependency_of_scope", data=data)

        return requirements

    def get_settings(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_settings_of_scope", data=data)

    def dump_settings(self, scope, settings):
        data = {"scope": scope}
        for key, value in settings.items():
            data[key] = value
        return self._send_request("POST", "/dump_settings", data=data)

    def get_python_version(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/get_python_version_of_scope", data=data)

    def get_type(self, scope, version=None):
        data = {"scope": scope}
        return self._send_request("POST", "/get_type_of_scope", data=data)

    def get_time_complexity(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_time_complexity_of_scope", data=data)
        )

    def get_mistakes(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_mistakes_of_scope", data=data)
        )

    def get_required_test_types(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_required_test_types_of_scope", data=data)
        )

    def get_tags(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_tags_of_scope", data=data)
        )

    def get_security_analysis(self, scope, version=None):
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return transform_to_html_bold(
            self._send_request("POST", "/get_security_analysis_of_scope", data=data)
        )

    def create_documentation(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version

        return self._send_request("POST", "/create_document_of_scope", data=data)

    def create_time_complexity(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/create_time_complexity_of_scope", data=data)

    def create_mistakes(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/create_mistakes_of_scope", data=data)

    def create_required_test_types(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request(
            "POST", "/create_required_test_types_of_scope", data=data
        )

    def create_tags(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/create_tags_of_scope", data=data)

    def create_security_analysis(self, scope):
        version = None
        if ":" in scope:
            version = scope.split(":")[1]
            scope = scope.split(":")[0]
        data = {"scope": scope}
        if version != None:
            data["version"] = version
        return self._send_request(
            "POST", "/create_security_analysis_of_scope", data=data
        )

    def get_last_x_events(self, user, x=10):
        data = {"key": user}
        data["x"] = x
        response = self._send_request("POST", "/get_last_x_event", data=data)

        new_dict = {}
        try:
            for each, value in response.items():
                new_key = datetime.datetime.fromtimestamp(
                    int(each.split(".")[0])
                ).strftime("%c")
                new_dict[new_key] = value
        except:
            print("error")
            traceback.print_exc()

        print("the_ return", new_dict)

        new_list = []
        for each, value in new_dict.items():
            try:
                new_list.append(
                    {
                        "time": each,
                        "event": value["event"],
                        "target": value["target"],
                        "detail": value["detail"],
                        "scope_target": value["scope_target"],
                        "meta": value["meta"],
                    }
                )
            except:
                print()
                print(value)
                pass

        # reverse it
        new_list.reverse()

        return new_list

    def get_read_scopes_of_user(self, key):
        data = {"key": key}

        scopes = self._send_request("POST", "/get_read_scopes_of_user", data=data)

        result = []
        for i in scopes:
            if i != None:
                result.append(i)
        return result

    def get_write_scopes_of_user(self, key):
        data = {"key": key}

        scopes = self._send_request("POST", "/get_write_scopes_of_user", data=data)

        result = []
        for i in scopes:
            if i != None:
                result.append(i)
        return result

    def get_write_scopes_of_me(self):
        scopes = self._send_request("GET", "/get_write_scopes_of_me")

        result = []
        for i in scopes:
            if i != None:
                result.append(i)
        return result

    def get_read_scopes_of_me(self):
        scopes = self._send_request("GET", "/get_read_scopes_of_me")

        result = []
        for i in scopes:
            if i != None:
                result.append(i)
        return result

    def get_users(self):
        users = self.users_keys

        result = []
        for i in users:
            the_name = self.get_name(i)
            if the_name == None:
                the_name = "Robust Admin"
            result.append(
                [
                    the_name,
                    self.is_enabed_user(i),
                    self.is_admin(i),
                    models.User.objects.get(access_key=i).id,
                ]
            )

        # sort
        result.sort(key=lambda x: x[0])
        return result

    def add_write_scope(self, scope, key):
        data = {"scope": scope, "key": key}

        return self._send_request("POST", "/scope_write_add", data=data)

    def delete_write_scope(self, scope, key):
        data = {"scope": scope, "key": key}
        return self._send_request("POST", "/scope_write_delete", data=data)

    def add_read_scope(self, scope, key):
        data = {"scope": scope, "key": key}

        return self._send_request("POST", "/scope_read_add", data=data)

    def delete_read_scope(self, scope, key):
        data = {"scope": scope, "key": key}
        return self._send_request("POST", "/scope_read_delete", data=data)

    def add_user(self, key):
        data = {"key": key}
        return self._send_request("POST", "/add_user", data=data)

    def set_name(self, key, name):
        data = {"key": key, "name": name}
        return self._send_request("POST", "/set_name", data=data)

    def get_name(self, key):
        data = {"key": key}
        return self._send_request("POST", "/get_name", data=data)

    def delete_user(self, key):
        data = {"key": key}
        return self._send_request("POST", "/delete_user", data=data)

    def disable_user(self, key):
        data = {"key": key}
        return self._send_request("POST", "/disable_user", data=data)

    def enable_user(self, key):
        data = {"key": key}
        return self._send_request("POST", "/enable_user", data=data)

    def is_enabed_user(self, key):
        data = {"key": key}
        return self._send_request("POST", "/is_enabled_user", data=data)

    def is_admin(self, key):
        data = {"key": key}
        result = self._send_request("POST", "/is_admin", data=data)
        return True if result == True else False

    def enable_admin(self, key):
        data = {"key": key}
        return self._send_request("POST", "/enable_admin", data=data)

    def disable_admin(self, key):
        data = {"key": key}
        return self._send_request("POST", "/disable_admin", data=data)

    def search_by_documentation(self, question, min_score=0, how_many_result=10):
        data = {
            "question": question,
            "min_score": min_score,
            "how_many_result": how_many_result,
        }
        response = self._send_request("POST", "/search_by_documentation", data=data)
        result = []
        try:
            if response != [None]:
                for i in response:
                    result.append(
                        [
                            i[0],
                            transform_to_html_bold(i[1]),
                            i[2],
                            self.get_code(i[0]),
                            f'upsonic.load("{i[0]}")()',
                        ]
                    )
        except:
            traceback.print_exc()
        return result

    def ai_completion(self, message, model=None):
        data = {"message": message}
        if model != None:
            data["model"] = model
        response = self._send_request("POST", "/ai_completion", data=data)
        return response

    def create_readme(self, top_library):
        version = None
        if ":" in top_library:
            version = top_library.split(":")[1]
            top_library = top_library.split(":")[0]
        data = {"top_library": top_library}
        if version != None:
            data["version"] = version
        return self._send_request("POST", "/create_readme", data=data)

    def create_get_release_note(self, top_library, version):
        data = {"top_library": top_library, "version": version}

        return self._send_request("POST", "/create_get_release_note", data=data)

    def get_readme(self, top_library, version=None):
        data = {"top_library": top_library}
        if version != None:
            data["version"] = version
        result = self._send_request("POST", "/get_readme", data=data)
        try:
            return transform_to_html_bold(result)
        except:
            return result

    def get_readme_github_sync(self, top_library, version=None):
        data = {"top_library": top_library}
        if version != None:
            data["version"] = version
        result = self._send_request("POST", "/get_readme_github_sync", data=data)
        try:
            return result
        except:
            return result

    def get_all_scopes_name_prefix(self, prefix):
        data = {"prefix": prefix}
        return self._send_request("POST", "/get_all_scopes_name_prefix", data=data)

    def get_default_ai_model(self):
        return self._send_request("GET", "/get_default_ai_model")

    def change_default_ai_model(self, model):
        data = {"model": model}
        return self._send_request("POST", "/change/default/model", data=data)

    def get_dump_history(self, scope):
        data = {"scope": scope}
        result = self._send_request("POST", "/get_dump_history", data=data)
        return result

    def get_version_history(self, scope):
        data = {"scope": scope}
        response = self._send_request("POST", "/get_version_history", data=data)
        result = []
        if response != [None]:
            for element in response:
                result.append(element.replace(scope + ":", ""))
        return result

    def delete_version(self, scope, version):
        data = {"version": scope + ":" + version}
        return self._send_request("POST", "/delete_version", data)

    def create_version(self, scope, version):
        data = {"scope": scope, "version": version}
        return self._send_request("POST", "/create_version", data)

    def create_version_prefix(self, top_library, version):
        data = {"top_library": top_library, "version": version}
        return self._send_request("POST", "/create_version_prefix", data)

    def delete_version_prefix(self, top_library, version):
        data = {"top_library": top_library, "version": version}
        return self._send_request("POST", "/delete_version_prefix", data)

    def get_version_code(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        return self._send_request("POST", "/get_version_code_of_scope", data=data)

    def get_version_difference(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        return self._send_request("POST", "/get_version_difference_of_scope", data=data)

    def get_version_date(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        the_time = self._send_request("POST", "/get_version_time_of_scope", data=data)
        print(the_time)
        the_time = int(the_time)
        return datetime.datetime.fromtimestamp(the_time).strftime("%c")

    def get_version_time(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        the_time = self._send_request("POST", "/get_version_time_of_scope", data=data)
        print(the_time)
        the_time = int(the_time)
        return the_time

    def get_version_user(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        return self._send_request("POST", "/get_version_user_of_scope", data=data)

    def get_version_release_note(self, scope, version):
        data = {"version": scope + ":" + version}
        data["scope"] = scope
        return self._send_request(
            "POST", "/get_version_release_note_of_scope", data=data
        )

    def get_dump_user(self, scope, dump):
        data = {"dump": scope + ":" + dump}
        data["scope"] = scope
        return self._send_request("POST", "/get_dump_user_of_scope", data=data)

    def get_dump_difference(self, scope, dump):
        data = {"dump": scope + ":" + dump}
        data["scope"] = scope
        return self._send_request("POST", "/get_dump_difference_of_scope", data=data)

    def get_dump_commit_message(self, scope, dump):
        data = {"dump": scope + ":" + dump}
        data["scope"] = scope
        result = self._send_request(
            "POST", "/get_dump_commit_message_of_scope", data=data
        )
        print("Commit message ", result)
        if result == [None] or result == None or result == "No Changes Made":
            result = "No Commit Message"
        else:
            result = bold_first_word(result)
        return result

    def get_dump_date(self, scope, dump):
        data = {"dump": scope + ":" + dump}
        data["scope"] = scope
        the_time = self._send_request("POST", "/get_dump_time_of_scope", data=data)
        print(the_time)
        the_time = int(the_time)
        return datetime.datetime.fromtimestamp(the_time).strftime("%c")

    def get_last_runs(self, scope, n=None):
        data = {"scope": scope}
        if n != None:
            data["n"] = n
        return self._send_request("POST", "/get_last_runs", data=data)

    def get_run(self, scope, run_sha):
        data = {"scope": scope}
        data["run_sha"] = run_sha

        return self._send_request("POST", "/get_run", data=data)
