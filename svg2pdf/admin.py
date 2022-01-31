from django.contrib import admin
from .models import klient, faktura, pozycjafaktury

# Register your models here.

admin.site.register(klient)
admin.site.register(faktura)
admin.site.register(pozycjafaktury)