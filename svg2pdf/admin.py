from django.contrib import admin
from .models import firma, faktura, pozycjafaktury

# Register your models here.

admin.site.register(firma)
admin.site.register(faktura)
admin.site.register(pozycjafaktury)