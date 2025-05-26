from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_table, name='stock_table'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
    #path("chart/<str:symbol>/", views.chart_data, name="chart_data"),
]
