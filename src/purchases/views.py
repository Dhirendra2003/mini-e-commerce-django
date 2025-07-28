from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from products.models import Product
from .models import Purchase

def purchase_start_view(request):
  if not req.method == "POST":
    return HttpResponseBadRequest("Invalid request method.")
  if not req.user.is_authenticated :
    return HttpResponseBadRequest("Login required to make a purchase.")
  handle = request.POST.get('handle')
  obj=Product.objects.get(handle=handle)
  purchase=Purchase.objects.create(user=request.user, product=obj)
  request.session['purchase_id'] = purchase.id

  return HttpResponse("started")
  
def purchase_success_view(request):
  return HttpResponse("Done")

def purchase_stopped_view(request):
  return HttpResponse("stopped")