
from django.urls import path
from . import views

urlpatterns = [
    
    
    path('user_login/', views.user_login, name="user_login"),
    path('registration/', views.registration, name="registration"),
    path('user_logout/', views.user_logout, name="user_logout"),

    



]