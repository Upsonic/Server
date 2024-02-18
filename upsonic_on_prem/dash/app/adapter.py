from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login


class CustomAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Whether to allow sign ups.
        """
        return False
