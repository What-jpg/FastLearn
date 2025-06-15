from django.urls import include, path
from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update/', views.update, name='update'),
    path('', include('django.contrib.auth.urls')),
    path ('emailverification/<str:action>/<str:email>/<int:code>', views.email_verification, name="email_verification"),
    path ('emailverification/<str:action>/<str:email>', views.email_verification, name="email_verification"),
]