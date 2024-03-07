#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import ast

from app import models
from rich.console import Console

console = Console()


from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

import traceback

load_dotenv(dotenv_path=".env")

api_url = "http://localhost:3000"

def transform_to_html_bold(text):
    try:
        # Find content within double asterisks
        start_idx = text.find('**')

        while start_idx != -1:
            end_idx = text.find('**', start_idx + 2)

            if end_idx == -1:
                break  # Break if no matching end double asterisks found

            # Extract content between double asterisks
            content = text[start_idx + 2:end_idx]
            
            # Replace content with HTML <b> tags
            text = text[:start_idx] + '<br><br><b>' + content + '</b><br>' + text[end_idx + 2:]

            # Find the next occurrence
            start_idx = text.find('**', end_idx + 2)

        if text.startswith("<br><br>"):
            text = text[8:]            
    except:
        traceback.print_exc()



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
                f"[bold green]Upsonic[bold green] active",
            )
        else:
            self._log(
                f"[bold red]Upsonic[bold red] is down",
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
            if i != '':
                result.append(i)
        

        result = list(set(result))
        result.sort()

        return result

    @property
    def sub_based_all_scopes(self):
        return self.sub_based_all_scopes_()

    def sub_based_all_scopes_(self, prefix=None):

        all_scopes = self.all_scopes

        def group_by_top_level_recursive(function_list):
            grouped_dict = {}

            for function_name in function_list:
                parts = function_name.split('.')
                current_dict = grouped_dict

                for part in parts:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]

            return grouped_dict
        grouped = group_by_top_level_recursive(all_scopes)
        result = grouped

        def add_top_level_names(dictionary, parent_name=''):
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

    def subs_of_scope(self, prefix):
        sub_scopes_general_list = self.sub_based_all_scopes_(prefix)

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
    def get_code(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/get_code_of_scope", data=data)

    def delete_code(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/delete_scope", data=data)


    def get_documentation(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_document_of_scope", data=data))


    def get_requirements(self, scope):
        data = {"scope": scope}
        requirements = self._send_request("POST", "/get_requirements_of_scope", data=data)
        if requirements is not None:
            requirements.replace(",", "")
        return requirements
    def get_python_version(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/get_python_version_of_scope", data=data)    
    def get_type(self, scope):
        data = {"scope": scope}
        return self._send_request("POST", "/get_type_of_scope", data=data)

    def get_time_complexity(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_time_complexity_of_scope", data=data))


    def get_mistakes(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_mistakes_of_scope", data=data))
    def get_required_test_types(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_required_test_types_of_scope", data=data))
    def get_tags(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_tags_of_scope", data=data))    
    def get_security_analysis(self, scope):
        data = {"scope": scope}
        return transform_to_html_bold(self._send_request("POST", "/get_security_analysis_of_scope", data=data))


    def create_documentation(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_document_of_scope", data=data
        )


    def create_time_complexity(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_time_complexity_of_scope", data=data
        )


    def create_mistakes(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_mistakes_of_scope", data=data
        )
    def create_required_test_types(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_required_test_types_of_scope", data=data
        )
    def create_tags(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_tags_of_scope", data=data
        )
    def create_security_analysis(self, scope):
        data = {"scope": scope}
        return self._send_request(
            "POST", "/create_security_analysis_of_scope", data=data
        )    


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
                [the_name, self.is_enabed_user(i), self.is_admin(i), models.User.objects.get(access_key=i).id])

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
        return self._send_request("POST", "/is_admin", data=data)

    def enable_admin(self, key):
        data = {"key": key}
        return self._send_request("POST", "/enable_admin", data=data)

    def disable_admin(self, key):
        data = {"key": key}
        return self._send_request("POST", "/disable_admin", data=data)



    def search_by_documentation(self, question, min_score=0.5, how_many_result=10):
        data = {"question": question, "min_score": min_score, "how_many_result": how_many_result}
        response = self._send_request("POST", "/search_by_documentation", data=data)
        result = []
        try:
            for i in response:
                result.append([i[0], transform_to_html_bold(i[1]), i[2]])
        except:
            traceback.print_exc()
        return result
    