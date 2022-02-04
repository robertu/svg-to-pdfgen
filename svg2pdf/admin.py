from csv import list_dialects
from django.contrib import admin
from django.utils.html import format_html
from .models import firma, faktura, pozycjafaktury, jednostkaM

# Register your models here.

@admin.register(firma)
class firmaAdmin(admin.ModelAdmin):
    list_display = ['Nazwa','NIP','Ulica','Adres']


@admin.register(pozycjafaktury)
class pozycjaAdmin(admin.ModelAdmin):
    list_display = ['Nazwa', 'Ilosc', 'Jednostka' , 'Cena_Netto', 'Podatek']

@admin.register(jednostkaM)
class jednostkaMAdmin(admin.ModelAdmin):
    list_display = ['Nazwa','Dziesietna']



@admin.register(faktura)
class fakturaAdmin(admin.ModelAdmin):
    list_display = ['nazwa','Numer_faktury','wygeneruj_fakture']
    fieldsets = [
        ('Dane Faktury', {'fields':('Nazwa_faktury','Numer_faktury')}),
        ('Firmy', {'fields':(('firma_sprzedawca','firma_klient'),)}),
        ('Pozycje', {'fields':(('Data_sprzedaży','Data_wystawienia'),'pozycje')}),
        ('Platnosc', {'fields':('Termin_płatności','Zapłacono','Sposób_płatności','Termin_płatności_dni')})
    ]
    filter_horizontal = ('pozycje',)

    def nazwa(self, obj):
        return "Faktura-" + obj.Nazwa_faktury
    def wygeneruj_fakture(self, obj):
        return format_html("<a href='/fakturag-{url}/'>Wygeneruj</a>", url=obj.id)