from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin), #GET request to display registration and login form
    path('/register', views.register), #POST request to register user
    path('/login', views.login), #POST request to login user
    path('/logout', views.logout), #POST request to logout user,
]