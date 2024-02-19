from allauth.account.forms import LoginForm, AuthenticationMethod, get_username_max_length, app_settings, \
    set_form_field_order
from django import forms
from django.urls import reverse, NoReverseMatch
from django.utils.translation import pgettext, gettext_lazy as _

from django.utils.safestring import mark_safe

from app import models
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.core.exceptions import ValidationError



class CustomUserCreationForm(forms.Form):

    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput(attrs={'class': 'form-control custom_form'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control custom_form'}))


    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = models.User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = models.User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = models.User.objects.create_user(
            username=self.cleaned_data['username'],
            email="info@upsonic.co",
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        self.user= user
        return user

class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control custom_form'}))
    password = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.PasswordInput(attrs={'class': 'form-control custom_form'}))
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", 'username', 'password']

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
