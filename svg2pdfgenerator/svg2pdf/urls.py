from django.urls import path
from . import views

urlpatterns = [
    path('svg2pdf', views.strona_gl),
    path('svg2pdf/faktura-<int:id>/', views.faktura_temp),
]