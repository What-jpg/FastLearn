from django.shortcuts import render
from .forms import RegistrationForm, VerificationCodeForm, LoginForm, UpdateForm
from .models import Subscribtion
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .utils import EmailVerificationActions, UserAuthRedisKeys, build_abs_uri_main
import random
import json
from django.forms.models import model_to_dict
from django.urls import reverse
from django.http import Http404
from .tasks import send_auth_code_email

# Create your views here.
def register(request):
    print(request.user)
    print(request.user.is_authenticated)
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)

        if user_form.is_valid():
            email = user_form.cleaned_data['email']
            user_dict = {
                'username': user_form.cleaned_data['username'],
                'password': user_form.cleaned_data['password'],
                'email': email
            }

            code = random.randint(100000, 999999)
            json_obj = json.dumps({
                "code": code, "user": user_dict,
                })
            
            cache.add(
                UserAuthRedisKeys(user_dict['email']).get_auth_code(EmailVerificationActions.register),
                json_obj,
                1200
                )
            
            send_auth_code_email.delay(build_abs_uri_main(request), user_dict['email'], code, EmailVerificationActions.register)

            return redirect(reverse('email_verification', args=[EmailVerificationActions.register,  user_dict['email']]))
    else:
        user_form = RegistrationForm()

    return render(
        request, 
        "account/register.html", 
        {'form': user_form}
        )

def email_verification(request, action, email, code = None):    
    def create_user():
        user_model = get_user_model()

        user_form.cleaned_data['user']['password'] = make_password(user_form.cleaned_data['user']['password'])

        return user_model.objects.create(**user_form.cleaned_data['user'])
    
    if request.method == 'POST':
        data = {'code': code}
        user_form = VerificationCodeForm(
            request.POST,
            email=email,
            action=action
            )

        if (user_form.is_valid()):
            if  action == EmailVerificationActions.register:
                user = create_user()
                
            login(request, user, backend="django.contrib.auth.ModelBackend")

            print(request.user)
            print(request.user.is_authenticated)

            return redirect('/')
    else:
        if code:
            data = {'code': code}
            user_form = VerificationCodeForm(data, email=email, action=action)
            
            if (user_form.is_valid()):
                if  action == EmailVerificationActions.register:
                    user = create_user()
                    
                login(request, user, backend="django.contrib.auth.ModelBackend")

                redirect('/')
        else:
            user_form = VerificationCodeForm(email=email, action=action)
    return render(
        request, 
        "account/email_verification_form.html",
        {'form': user_form, 'action': action}
    )

def login_view(request):
    if request.method == "POST":
        user_form = LoginForm(request, request.POST)

        if user_form.is_valid():
            user = user_form.cleaned_data['user']

            if user.is_two_factor_auth_active is False:
                login(request, user)

                return redirect('/')
            
            code = random.randint(100000, 999999)

            cache.set(
                UserAuthRedisKeys(user.email).get_auth_code(EmailVerificationActions.login),
                code,
                1200
            )

            send_auth_code_email.delay(build_abs_uri_main(request), user.email, code, EmailVerificationActions.login)

            return redirect(reverse('email_verification', args=[EmailVerificationActions.login, user.email]))

    else:
        user_form = LoginForm(request=request)
    return render(
        request,
        "account/login.html",
        {'form': user_form}
    )

def logout_view(request):
    logout(request)

    return render(
        request,
        'registration/logged_out.html',
    )

@login_required
def update(request):
    if get_user_model().social.filter(username=request.user.username).exists():
        raise Http404("Can't edit social accounts")
    if request.method == 'POST':
        form = UpdateForm(request.user, request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            if cd["new_password"]:
                request.user.password = make_password(cd['new_password'])

            request.user.is_two_factor_auth_active = cd['is_two_factor_auth_active']

            request.user.save()

            return redirect("/")
    else:
        form = UpdateForm(request.user)
    return render(
        request,
        "account/update.html",
        {"form": form}
    )