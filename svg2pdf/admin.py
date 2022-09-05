from django.contrib import admin
from django.utils.html import format_html

from .models import Faktura, Firma, JednostkaM, Pozycjafaktury, SposobPlat

# Register your models here.


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ["nazwa", "nip", "ulica", "adres"]


@admin.register(Pozycjafaktury)
class PozycjaAdmin(admin.ModelAdmin):
    list_display = ["nazwa", "faktura", "ilosc", "jednostka", "cena_Netto", "podatek"]


@admin.register(JednostkaM)
class JednostkaMAdmin(admin.ModelAdmin):
    list_display = ["nazwa", "dziesietna"]


@admin.register(Faktura)
class FakturaAdmin(admin.ModelAdmin):
    list_display = ["nazwa", "numer_faktury", "faktura"]
    fieldsets = [
        ("Dane Faktury", {"fields": ("nazwa_faktury", "numer_faktury")}),
        ("Firmy", {"fields": (("firma_sprzedawca", "firma_klient"),)}),
        ("Pozycje", {"fields": ("data_sprzedazy", "data_wystawienia")}),
        ("Platnosc", {"fields": ("termin_platnosci", "zaplacono", "sposob_platnosci", "termin_platnosci_dni")}),
        ("Informacje", {"fields": ("fakture_wystawil",)}),
    ]
    # filter_horizontal = ("pozycje",)

    def nazwa(self, obj):
        return "Faktura-" + obj.nazwa_faktury

    def faktura(self, obj):
        return format_html("<a href='/fakturag-{url}/'>Faktura</a>", url=obj.id)


@admin.register(SposobPlat)
class SposobPlatAdmin(admin.ModelAdmin):
    list_display = [
        "nazwa",
    ]
