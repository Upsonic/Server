# myapp/auth_backends.py
import logging
from django.contrib.auth.backends import ModelBackend
from allauth.account.auth_backends import AuthenticationBackend
from dash.logs import logger
from app.models import User
from app.api_integration import API_Integration

class LdapBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"Login attempt for username: {username} with password: {password}")

        is_ldap_active = API_Integration(username).ldap_active()

        if is_ldap_active:
            is_user_valid = API_Integration(username).ldap_auth(username, password)

            # Check the user is already created in the database
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            
            if is_user_valid and user is None:
                user = User.objects.create_user(username=username, password=password, ldap=True)
                user.save()
                # Get the first user in the database
                first_user = User.objects.first()
                user.add_user(first_user.access_key)
                logger.info(f"User {username} created in the database")

            if is_user_valid and user is not None:
                # Change the password if it is different
                if user.password != password:
                    user.set_password(password)
                    user.save()
                    logger.info(f"User {username} password updated")

