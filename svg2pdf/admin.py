from django.contrib import admin
from django.utils.html import format_html
from .models import firma, faktura, pozycjafaktury

# Register your models here.

admin.site.register(firma)
admin.site.register(pozycjafaktury)

@admin.register(faktura)
class fakturaAdmin(admin.ModelAdmin):
    list_display = ['nazwa','wygeneruj_fakture']

    def nazwa(self, obj):
        return "Faktura-" + obj.Nazwa_faktury
    def wygeneruj_fakture(self, obj):
        return format_html("<a href='/fakturag-{url}/'>Wygeneruj</a>", url=obj.id)