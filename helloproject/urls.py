from django.http import HttpResponse
from django.urls import path

def home(request):
    return HttpResponse("Hello, world! This is a Django app deployed on Azure.")

urlpatterns = [
    path('', home),
]
