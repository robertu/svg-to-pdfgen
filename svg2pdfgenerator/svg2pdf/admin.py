from django.contrib import admin
from .models import firma, klient, faktura

# Register your models here.

admin.site.register(firma)
admin.site.register(klient)
admin.site.register(faktura)