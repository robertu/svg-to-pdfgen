from django.urls import path

from . import views

urlpatterns = [path("", views.strona_gl), path("faktura-<int:id>/", views.faktura_temp), path("fakturag-<int:id>/", views.faktura_gen)]
