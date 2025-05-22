from django.http import HttpResponse
from django.urls import path
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clock.urls')),  # 指到 clock app
]


def home(request):
    return HttpResponse("Hello, world! This is a Django app deployed on Azure.")

