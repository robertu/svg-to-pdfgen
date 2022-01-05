from django.urls import path
from . import views

urlpatterns = [
    path('svg2pdf', views.strona_gl),
    path('svg2pdf/fakturatemp/<int:faktura_temp>/', views.faktura_temp),
]