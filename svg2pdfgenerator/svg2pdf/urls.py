from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path('svg2pdf/index', views.index)
]