from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.db.models import Q
import datetime
from django.utils import timezone
from django.views.generic.base import TemplateView
#from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import letter
#from reportlab.lib.pagesizes import landscape
#from reportlab.platypus import Image
import os
from django.conf import settings
from django.http import HttpResponse
#from django.template.loader import get_template
#from xhtml2pdf import pisa
#from django.contrib.staticfiles import finders
import calendar
from calendar import HTMLCalendar
from DimosoApp.models import *
from DimosoApp.forms import *
#from hitcount.views import HitCountDetailView
from django.core.mail import send_mail
from django.conf import settings
import csv
from django.db.models import Sum, Max, Min, Avg

# Create your views here.
def user_login(request):
    context={}
    if request.POST:
        form=UserLoginForm(request.POST)
        if form.is_valid():
            email=request.POST['email']
            password=request.POST['password']
            user = authenticate(request, email=email,password=password)

            if user is not None:
                login(request,user)
                return redirect('home')
            messages.success(request, "password or username is incorrect")
        else:
            context['login_form']=form
            
    else:
        #messages.success(request, "password or username is incorrect")
        form=UserLoginForm(request.POST)
        context['login_form']=form    
        
    return render(request,'Account/user_login.html', context)


def user_logout(request):
    logout(request)
    return redirect('user_login')
    return render(request,'Account/logout.html')

def registration(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"you are already authenticated as {user.email}")
    context = {}
    
    #form = MyUserForm()

    if request.POST:

        form=MyUserForm(request.POST)
        if form.is_valid():
            form.save()

            #HIZI NI KWA AJILI KUTUMA EMAIL ENDAPO MTU AKIJISAJILI
            username = request.POST['username']
            #last_name = request.POST['last_name']
            email = request.POST['email']
            subject = "Welcome to Dimoso El Blog"
            message = f"Thanks {username}  for registering in our system as {email} "
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)

            #ZINAISHIA HAPA ZA KUTUMA EMAIL



            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            myuser = authenticate(email=email,password=raw_password)
            if myuser is not None:
                         login(request,myuser)
                         #messages.success(request,"account created Successfully, now you can login.")
                         
                         return redirect('home')
            
            

        else:
            context['registration_form'] = form
        
            
        
           


    return render(request,'Account/registration.html', context)
