from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView

from django.contrib.auth import login, authenticate
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

def dashboard(request):
	return render(request, "DashBoard/index.html")




def stock(request):
	form = StockSearchForm(request.POST or None)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	

	queryset = Stock.objects.all().order_by('-id')


	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	
	form = StockSearchForm(request.POST or None)




	#MWISHO HAP




	context ={
		"queryset":queryset,
		"form":form,
		"page":page,
		"current_date":current_date
	}

	#kwa ajili ya kufilter items and category ktk form
	if request.method == 'POST':
		#category__icontains=form['category'].value(),
		category = form['category'].value()

		

										
		queryset = Stock.objects.filter(
										item_name__icontains=form['item_name'].value()
										#last_updated__gte=form['start_date'].value(),
										# last_updated__lte=form['end_date'].value()
										#last_updated__range=[
											#form['start_date'].value(),
											#form['end_date'].value()
										#]
			)
		if (category != ''):
			queryset = Stock.objects.all()
			queryset = queryset.filter(category_id=category)

			#To SET  PAGINATION IN STOCK LIST PAGE
			paginator = Paginator(queryset,5)
			page = request.GET.get('page')
			try:
				queryset=paginator.page(page)
			except PageNotAnInteger:
				queryset=paginator.page(1)
			except EmptyPage:
				queryset=paginator.page(paginator.num_pages)
			#ZINAISHIA HAPA ZA KUSEARCH ILA CONTEXT IPO KWA CHINI
		
#hii ni kwa ajili ya kudownload ile page nzima ya stock endapo mtu akiweka tiki kwenye field export to csv
		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['content-Disposition'] = 'attachment; filename="List oF Items.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
			instance = queryset
			for stock in queryset:
				writer.writerow([stock.category,stock.item_name,stock.quantity])
			return response
			#ZINAISHIA HAPA ZA KUDOWNLOAD

			#HII NI CONTEXT KWA AJILI YA KUSEARCH ITEM OR CATEGORY KWENYE FORMYETU
		context ={
		#"QuerySet":QuerySet,
		"form":form,
		"queryset":queryset,
		"page":page
	}	

	return render(request, 'DimosoApp/stock.html',context)


class add_items(SuccessMessageMixin, CreateView):
	model = Stock
	template_name = 'DimosoApp/add_items.html'
	form_class = StockCreateForm
	success_url = reverse_lazy('stock')
	success_message = "Item added successfully in your stock"
class update_items(SuccessMessageMixin, UpdateView):
	model = Stock
	template_name = 'DimosoApp/add_items.html'
	form_class = StockUpdateForm
	success_url = reverse_lazy('stock')
	success_message = "Item updated successfully in your stock"



def delete_items(request, id):
	queryset = Stock.objects.get(id=id)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	
	if request.method == 'POST':
		queryset.delete()
		messages.success(request,"Item deleted successfully from your stock")
		return redirect('stock')
		

	return render(request, 'DimosoApp/delete_items.html', {"current_date":current_date})

def stock_detailpage(request, id):
	queryset = Stock.objects.get(id=id)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	context ={
		"current_date":current_date,
		"queryset":queryset
	}
	
	
		

	return render(request, 'DimosoApp/stock_detailpage.html',context)

def issue_items(request, id):
	queryset = Stock.objects.get(id=id)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	form= IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity -= instance.issue_quantity
		instance.sales_amount += instance.receive_amount
		#instance.issue_by = str(request.user)
		messages.success(request,"Items Issued successfully. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		#return redirect('stock_detailpage/'+str(instance.id))
		return redirect('stock_detailpage',id=id)
		#return HttpResponseRedirect(instance.get_absolute_url())
	context ={
		"instance":queryset,
		"current_date":current_date,
		"form":form,
		#"username": 'Issued By: ' + str(request.user),
		"title": 'Issue ' + str(queryset.item_name),
	}
	
	
		

	return render(request, 'DimosoApp/issue_items.html',context)

def receive_items(request, id):
	queryset = Stock.objects.get(id=id)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	form= ReceiveForm(request.POST or None, instance=queryset)

	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity += instance.receive_quantity
		instance.purchasing_amount += instance.issued_amount
		#instance.issue_by = str(request.user)
		#messages.success(request,"Items Issued successfully. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		messages.success(request, "Received successfully. " + str(instance.quantity) + " " + str(instance.item_name) + "s in Your Store")
		#return redirect('stock_detailpage/'+str(instance.id))
		return redirect('stock_detailpage',id=id)
		#return HttpResponseRedirect(instance.get_absolute_url())
	context ={
		"instance":queryset,
		"form":form,
		"current_date":current_date,
		#"username": 'Issued By: ' + str(request.user),
		"title": 'Receive ' + str(queryset.item_name),
	}
	
	
		

	return render(request, 'DimosoApp/receive_items.html',context)

def reorder_level(request, id):
	queryset = Stock.objects.get(id=id)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	form= ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level of " + str(instance.item_name) + "is updated to " + str(instance.reorder_level))
		#return redirect('stock_detailpage/'+str(instance.id))
		return redirect('stock')
		#return HttpResponseRedirect(instance.get_absolute_url())
	context ={
		"instance":queryset,
		"form":form,
		"current_date":current_date
		
	}
	
	
		

	return render(request, 'DimosoApp/reorder_level.html',context)

def ending_products(request):
	form = StockSearchForm(request.POST or None)
	formu = ReorderLevelForm(request.POST or None)
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	

	queryset = Stock.objects.filter(quantity__lt = formu['reorder_level'].value()).order_by('-id')
	context ={
		"queryset":queryset,
		"form":form,
		"formu":formu,
		"current_date":current_date
	}

		

	return render(request, 'DimosoApp/ending_products.html',context)


def received_items_history(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)

	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	

	queryset = Stock.objects.filter(
		
		Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
		is_received=True
		).order_by('-id')

	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)

	get_sum = Stock.objects.filter(is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "DimosoApp/received_items_history.html",context)



def received_items_history_1(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =1) | Q(last_updated__month =1),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True 
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_1.html",context)

def received_items_history_2(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =2) | Q(last_updated__month =2),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_2.html",context)


def received_items_history_3(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =3) | Q(last_updated__month =3),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_3.html",context)

def received_items_history_4(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =4) | Q(last_updated__month =4),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_4.html",context)

def received_items_history_5(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =5) | Q(last_updated__month =5),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True 
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_5.html",context)


def received_items_history_6(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	

	queryset = Stock.objects.filter(
			Q(last_updated__month =6) | Q(timestamp__month =6),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_6.html",context)

def received_items_history_7(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =7) | Q(last_updated__month =7),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_7.html",context)


def received_items_history_8(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =8) | Q(last_updated__month =8),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_8.html",context)


def received_items_history_9(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =9) | Q(last_updated__month =9),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_9.html",context)




def received_items_history_10(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =10) | Q(last_updated__month =10),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_10.html",context)

def received_items_history_11(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =11) | Q(last_updated__month =11),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_11.html",context)


def received_items_history_12(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =12) | Q(last_updated__month =12),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(avg=Avg('purchasing_amount'))
	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,
		"current_month":current_month,
		"current_year":current_year,
	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_12.html",context)




def received_items_history_today(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	x= timezone.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%Y-%m-%d')

	queryset = Stock.objects.filter(
			#Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			#last_updated__month =5,

			last_updated__date = current_date,
			 is_received=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(sum=Sum('issued_amount'))
	get_max = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(max=Max('issued_amount'))
	get_min = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(min=Min('issued_amount'))
	get_avg = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(avg=Avg('issued_amount'))


	context ={
		"x":x,
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,
		

	}
	return render(request, "RECEIVED_ITEMS_MONTHS/received_items_history_today.html",context)




























def issued_items_history(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	


	

	queryset = Stock.objects.filter(
		Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
		is_issued=True

		).order_by('-id')

	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)

	get_sum = Stock.objects.filter(is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "DimosoApp/issued_items_history.html",context)












def issued_items_history_1(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =1) | Q(last_updated__month =1),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	 

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_1.html",context)

def issued_items_history_2(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =2) | Q(last_updated__month =2),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_2.html",context)

def issued_items_history_3(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =3) | Q(last_updated__month =3),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_3.html",context)

def issued_items_history_4(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =4) | Q(last_updated__month =4),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_4.html",context)

def issued_items_history_5(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =5) | Q(last_updated__month =5),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
			
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_5.html",context)


def issued_items_history_6(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =6) | Q(last_updated__month =6),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_6.html",context)

def issued_items_history_7(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =7) | Q(last_updated__month =7),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_7.html",context)

def issued_items_history_8(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =8) | Q(last_updated__month =8),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_8.html",context)

def issued_items_history_9(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =9) | Q(last_updated__month =9),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_9.html",context)


def issued_items_history_10(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =10) | Q(last_updated__month =10),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_10.html",context)

def issued_items_history_11(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =11) | Q(last_updated__month =11),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_11.html",context)


def issued_items_history_12(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =12) | Q(last_updated__month =12),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12), is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12), is_issued=True).aggregate(max=Max('sales_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12), is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12), is_issued=True).aggregate(avg=Avg('sales_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"current_date":current_date,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_12.html",context)



def issued_items_history_today(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	

	x= datetime.now()
	current_date = x.strftime('%Y-%m-%d')

	queryset = Stock.objects.filter(
			#last_updated__year=current_year,
			#last_updated__month =5,
			last_updated__date = current_date,
			 is_issued=True
		)
	#To SET  PAGINATION IN STOCK LIST PAGE
	paginator = Paginator(queryset,5)
	page = request.GET.get('page')
	try:
		queryset=paginator.page(page)
	except PageNotAnInteger:
		queryset=paginator.page(1)
	except EmptyPage:
		queryset=paginator.page(paginator.num_pages)


	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(last_updated__date = current_date, is_issued=True).aggregate(sum=Sum('receive_amount'))
	get_max = Stock.objects.filter(last_updated__date = current_date, is_issued=True).aggregate(max=Max('receive_amount'))
	get_min = Stock.objects.filter(last_updated__date = current_date, is_issued=True).aggregate(min=Min('receive_amount'))
	get_avg = Stock.objects.filter(last_updated__date = current_date, is_issued=True).aggregate(avg=Avg('receive_amount'))


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,
		

	}
	return render(request, "ISSUED_ITEMS_MONTHS/issued_items_history_today.html",context)









def point_of_sales(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month

	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')
	

	queryset = Stock.objects.filter(
		Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
		is_issued=True,
		is_received=True

		).order_by('-id')

	get_sum = Stock.objects.filter(is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(is_issued=True).aggregate(avg=Avg('sales_amount'))

	profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		"profit":profit
	}
	return render(request, "DimosoApp/point_of_sales.html",context)









def point_of_sales_1(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =1) | Q(last_updated__month =1),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			
			
			is_received=True,
			is_issued=True
			#Q(timestamp__month = 1) and Q(is_received=True), is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =1) | Q(last_updated__month =1),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,
		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_1.html",context)


def point_of_sales_2(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =2) | Q(last_updated__month =2),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =2) | Q(last_updated__month =2),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_2.html",context)

def point_of_sales_3(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =3) | Q(last_updated__month =3),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =3) | Q(last_updated__month =3),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_3.html",context)

def point_of_sales_4(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =4) | Q(last_updated__month =4),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =4) | Q(last_updated__month =4),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_4.html",context)

def point_of_sales_5(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =5) | Q(last_updated__month =5),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =5) | Q(last_updated__month =5),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_5.html",context)




def point_of_sales_6(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =6) | Q(last_updated__month =6),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =6) | Q(last_updated__month =6),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_6.html",context)


def point_of_sales_7(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =7) | Q(last_updated__month =7),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =7) | Q(last_updated__month =7),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_7.html",context)


def point_of_sales_8(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =8) | Q(last_updated__month =8),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =8) | Q(last_updated__month =8),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_8.html",context)

def point_of_sales_9(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =9) | Q(last_updated__month =9),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =9) | Q(last_updated__month =9),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_9.html",context)

def point_of_sales_10(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =10) | Q(last_updated__month =10),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =10) | Q(last_updated__month =10),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_10.html",context)

def point_of_sales_11(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =11) | Q(last_updated__month =11),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =11) | Q(last_updated__month =11),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_11.html",context)



def point_of_sales_12(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	
	x= datetime.now()
	current_date = x.strftime('%d-%m-%Y %H:%M')

	queryset = Stock.objects.filter(
			Q(timestamp__month =12) | Q(last_updated__month =12),
			Q(timestamp__year =current_year) | Q(last_updated__year =current_year),
			is_received=True,
			is_issued=True
			#timestamp__date = current_date,
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(sum=Sum('purchasing_amount'))
	get_max = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(max=Max('purchasing_amount'))
	get_min = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(min=Min('purchasing_amount'))
	get_avg = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_received=True).aggregate(avg=Avg('purchasing_amount'))


	get_sum2 = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_issued=True).aggregate(sum=Sum('sales_amount'))
	get_max2 = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_issued=True).aggregate(max=Max('sales_amount'))
	get_min2 = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_issued=True).aggregate(min=Min('sales_amount'))
	get_avg2 = Stock.objects.filter(Q(timestamp__month =12) | Q(last_updated__month =12),is_issued=True).aggregate(avg=Avg('sales_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_12.html",context)


def point_of_sales_today(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
	form = StockSearchForm(request.POST or None)
	month = month.capitalize()
	month_number = list(calendar.month_name).index(month)
	month_number = int(month_number)

	now = datetime.now()
	current_year = now.year
	current_month = now.month
	x= datetime.now()
	current_date = x.strftime('%Y-%m-%d')
	
	time = now.strftime('%I:%M %p')

	queryset = Stock.objects.filter(
			#last_updated__year=year,
			#timestamp__month =12,
			last_updated__date = current_date,
			 is_issued=True,
			  is_received=True
		)
	

	#queryset = Stock.objects.all().order_by('-id')

	get_sum = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(sum=Sum('issued_amount'))
	get_max = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(max=Max('issued_amount'))
	get_min = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(min=Min('issued_amount'))
	get_avg = Stock.objects.filter(last_updated__date = current_date, is_received=True).aggregate(avg=Avg('issued_amount'))


	get_sum2 = Stock.objects.filter(last_updated__date = current_date,is_issued=True).aggregate(sum=Sum('receive_amount'))
	get_max2 = Stock.objects.filter(last_updated__date = current_date,is_issued=True).aggregate(max=Max('receive_amount'))
	get_min2 = Stock.objects.filter(last_updated__date = current_date,is_issued=True).aggregate(min=Min('receive_amount'))
	get_avg2 = Stock.objects.filter(last_updated__date = current_date,is_issued=True).aggregate(avg=Avg('receive_amount'))

	#profit = 4-2


	context ={
		"queryset":queryset,
		"form":form,
		"get_sum":get_sum,
		"get_max":get_max,
		"get_min":get_min,
		"get_avg":get_avg,

		"get_sum2":get_sum2,
		"get_max2":get_max2,
		"get_min2":get_min2,
		"get_avg2":get_avg2,

		"current_month":current_month,
		"current_year":current_year,
		"current_date":current_date,

		#"profit":profit
	}
	return render(request, "POINT_OF_SALES_ALL_MONTHS/point_of_sales_today.html",context)

















def receive_amount(request, id):
	queryset = Stock.objects.get(id=id)

	form= ReceiveAmountForm(request.POST or None, instance=queryset)

	if form.is_valid():
		instance = form.save(commit=False)
		instance.sales_amount += instance.receive_amount
		
		#instance.issue_by = str(request.user)
		#messages.success(request,"Items Issued successfully. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		messages.success(request, "Received successfully. " + str(instance.receive_amount) + "Tshs.")
		#return redirect('stock_detailpage/'+str(instance.id))
		return redirect('stock_detailpage',id=id)
		#return HttpResponseRedirect(instance.get_absolute_url())
	context ={
		"instance":queryset,
		"form":form,
		#"username": 'Issued By: ' + str(request.user),
		"title": 'Receive ' + str(queryset.item_name),
	}
	return render(request, 'DimosoApp/receive_amount.html',context)

def issued_amount(request, id):
	queryset = Stock.objects.get(id=id)

	form= IssuedAmountForm(request.POST or None, instance=queryset)

	if form.is_valid():
		instance = form.save(commit=False)
		instance.purchasing_amount += instance.issued_amount
		
		#instance.issue_by = str(request.user)
		#messages.success(request,"Items Issued successfully. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in store")
		instance.save()
		messages.success(request, "Issued successfully. " + str(instance.issued_amount) + "Tshs")
		#return redirect('stock_detailpage/'+str(instance.id))
		return redirect('stock_detailpage',id=id)
		#return HttpResponseRedirect(instance.get_absolute_url())
	context ={
		"instance":queryset,
		"form":form,
		#"username": 'Issued By: ' + str(request.user),
		"title": 'Receive ' + str(queryset.item_name),
	}
	return render(request, 'DimosoApp/issued_amount.html',context)