from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

class EmailVerificationActions:
    register = "register" 
    login = 'login'

class UserAuthRedisKeys:
    def __init__(self, email):
        self.email = email

    def get_auth_code(self, action):
        return "%s:%s" % (action, self.email)
    
def build_abs_uri_main(request):
    return request.build_absolute_uri('/')[:-1]