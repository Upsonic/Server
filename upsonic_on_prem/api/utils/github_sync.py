import requests

import os

from dotenv import load_dotenv
import base64
load_dotenv(dotenv_path=".env")


class github_:
    def __init__(self, token, repo_owner, repo_name):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'

        self.author_name = 'getupsonic'
        self.author_email = 'info@upsonic.co'

        self.github_active = os.environ.get("github_active", "false").lower() == "true"
        if self.token is False or self.repo_owner is False or self.repo_name is False:
            self.github_active = False

    def get_file(self, path):
        url = f'{self.base_url}/contents/{path}'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except:
            return False
    

    def create_or_update_file_(self, path, content, message):
        # Attempt to get the file to see if it already exists
        get_url = f'{self.base_url}/contents/{path}'
        try:
            get_response = requests.get(get_url, headers=self.headers)

            data = {
                'message': message,
                'content': content,
                'author': {
                    'name': self.author_name,
                    'email': self.author_email
                },
                'committer': {
                    'name': self.author_name,
                    'email': self.author_email
                }
            }


            # If the file exists, get its SHA to update it
            if get_response.status_code == 200:
                data['sha'] = get_response.json()['sha']


       
            # Whether the file exists or not, try to create or update it
            put_response = requests.put(get_url, headers=self.headers, json=data)
            put_response.raise_for_status()

            return put_response.json()["content"]['sha']
        except:
            return False


    def create_or_update_file(self, scope, message):
        if not self.github_active:
            return False

    
        if ":" in scope.key:
            path = scope.key.split(":")[0].replace(".", "/")
        else:
            path = scope.key.replace(".", "/")
        path = f'{path}.py'
        content = scope.code

        

        # Inside your create_or_update_file function, before the PUT request
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        content = encoded_content


        return self.create_or_update_file_(path, content, message)



    def get_sha_(self, path):
        # Get the file to retrieve its SHA
        try:
            file_info = self.get_file(path)
            return file_info['sha']
        except:
            return False
    

    def get_sha(self, scope):
        if not self.github_active:
            return False
    
        if ":" in scope.key:
            path = scope.key.split(":")[0].replace(".", "/")
        else:
            path = scope.key.replace(".", "/")
        path = f'{path}.py'

        return self.get_sha_(path)



    def delete_file_(self, path, message):
        try:
            # First, get the file to retrieve its SHA
            file_info = self.get_file(path)
            sha = file_info['sha']

            # Prepare the URL and data for the DELETE request
            url = f'{self.base_url}/contents/{path}'
            data = {
                'message': message,
                'sha': sha,
                'author': {
                    'name': self.author_name,
                    'email': self.author_email
                },
                'committer': {
                    'name': self.author_name,
                    'email': self.author_email
                }
            }

            # Send the DELETE request
            response = requests.delete(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()        
        except:
            return False



    def delete_file(self, scope, message):
        if not self.github_active:
            return False
    
        if ":" in scope.key:
            path = scope.key.split(":")[0].replace(".", "/")
        else:
            path = scope.key.replace(".", "/")
        path = f'{path}.py'

        return self.delete_file_(path, message)


github = github_(os.environ.get("github_token", False), os.environ.get("github_repo_owner", False), os.environ.get("github_repo_name", False))