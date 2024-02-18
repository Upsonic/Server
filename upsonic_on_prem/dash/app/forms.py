from allauth.account.forms import LoginForm, AuthenticationMethod, get_username_max_length, app_settings, \
    set_form_field_order
from django import forms
from django.urls import reverse, NoReverseMatch
from django.utils.translation import pgettext, gettext_lazy as _

from django.utils.safestring import mark_safe


class MyCustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)
        if app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.EMAIL:
            login_widget = forms.EmailInput(
                attrs={
                    "placeholder": _("Email address"),
                    "autocomplete": "email",
                }
            )
            login_field = forms.EmailField(label=_("Email"), widget=login_widget)
        elif app_settings.AUTHENTICATION_METHOD == AuthenticationMethod.USERNAME:
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username"), "autocomplete": "username"}
            )
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length(),
            )
        else:
            assert (
                    app_settings.AUTHENTICATION_METHOD
                    == AuthenticationMethod.USERNAME_EMAIL
            )
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username or email"), "autocomplete": "email"}
            )
            login_field = forms.CharField(
                label=pgettext("field label", "Login"), widget=login_widget
            )
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]
        try:
            reset_url = reverse("account_reset_password")
        except NoReverseMatch:
            pass
