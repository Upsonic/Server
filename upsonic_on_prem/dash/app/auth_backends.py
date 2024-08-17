# myapp/auth_backends.py
import logging
from django.contrib.auth.backends import ModelBackend
from allauth.account.auth_backends import AuthenticationBackend
from dash.logs import logger

class LdapBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"Login attempt for username: {username} with password: {password}")

