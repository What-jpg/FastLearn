from django import forms
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth import get_user_model
import json
from .utils import EmailVerificationActions, UserAuthRedisKeys
from collections import OrderedDict

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if (cd["password"] != cd["password2"]):
            raise forms.ValidationError("Passwords don't match")
        return cd['password2']
    
    def clean_email(self):
        cd = self.cleaned_data
        if get_user_model().local.filter(email=cd["email"]).exists():
            raise forms.ValidationError("The email is already in use")
        return cd["email"]
    
class VerificationCodeForm(forms.Form):
    def __init__(self, *args, email, action = EmailVerificationActions.register, **kwargs):
        super(VerificationCodeForm, self).__init__(*args, **kwargs)
        self.action = action
        self.email = email

    # action = forms.CharField(
    #     max_length=10,
    #     widget=forms.HiddenInput
    # )

    # email = forms.EmailField(
    #     widget=forms.HiddenInput
    # )

    code = forms.IntegerField(
        max_value = 999999,
        min_value = 100000,
        widget=forms.TextInput,
    )
    
    def clean_code(self):
        cd = self.cleaned_data
        passkey = cd['code']

        redis_key = UserAuthRedisKeys(self.email).get_auth_code(self.action)
        user_and_code = cache.get(redis_key)

        if self.action == EmailVerificationActions.register:
            if not user_and_code or (json.loads(user_and_code)["code"] != passkey):
                raise forms.ValidationError('The code has already expired or isn\'t correct.')
        else:
            if not user_and_code or user_and_code != passkey:
                raise forms.ValidationError('The code has already expired or isn\'t correct.')
            
        user = json.loads(user_and_code)["user"]

        cache.delete(redis_key)

        if get_user_model().local.filter(username=user['username']):
            raise forms.ValidationError('The username was already taken, so you should create an account with a different username.')

        if self.action == EmailVerificationActions.register:
            self.cleaned_data['user'] = user

        return passkey
    
class LoginForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.request = request

    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput
    )

    # def clean_username(self):
    #     cd = self.cleaned_data

    #     if not cd['username']:
    #         raise forms.ValidationError("The username field must be filled")

    # def clean_password(self):
    #     cd = self.cleaned_data

    #     if not cd['password']:
    #         raise forms.ValidationError("The password field must be filled")

    def clean(self):
        cd = super().clean()

        if self.errors:
            return cd

        user = authenticate(self.request, username=cd['username'], password=cd['password'])
        print(user)
        if user is None:
            raise forms.ValidationError("The username or password is not correct.")
        
        cd['user'] = user

        return cd
    
class UpdateForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["is_two_factor_auth_active"].label = "Enable two step log-in"
        self.fields["is_two_factor_auth_active"].initial = user.is_two_factor_auth_active

        self.fields = OrderedDict([
            ("new_password", self.fields['new_password']),
            ('new_password2', self.fields['new_password2']),
            ('is_two_factor_auth_active', self.fields['is_two_factor_auth_active']),
            ('password', self.fields['password']),
        ])

    class Meta:
        model = get_user_model()
        fields = ['is_two_factor_auth_active']

    new_password = forms.CharField(
        label="New password",
        required=False,
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label="Repeat new password",
        required=False,
        widget=forms.PasswordInput
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )


    def clean_new_password2(self):
        cd = self.cleaned_data
        p1 = cd['new_password']
        p2 = cd['new_password2']

        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        
        return p2
    
    def clean_password(self):
        p = self.cleaned_data['password']

        if not self.user.check_password(p):
            raise forms.ValidationError('The password is incorrect')