from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import faktura
# Create your views here.


class firma:
    def __init__(self, nazwa, nip, ulica, adres):
        self.nazwa = nazwa
        self.nip = nip
        self.ulica = ulica
        self.adres = adres

class pozycja:
    def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
        self.nazwa = nazwa
        self.jednostka = jednostka
        self.ilosc = ilosc
        self.podatek = podatek
        self.cenaN = cenaN
        self.wartoscN = self.cenaN * self.ilosc
        self.cenaVat = round(self.cenaN * (float(podatek)/ 100), 2)
        self.wartoscVat = round(self.wartoscN * (float(podatek) / 100), 2)



def faktura_context_calc(faktura_ostatinia):
    context = {
        "title": 'abc',
        "miejsceWystawienia": faktura_ostatinia.miejsce_wystawienia,
        "dataWystawienia": str(faktura_ostatinia.data_wystawienia),
        "dataWykonaniaUslugi": str(faktura_ostatinia.data_wykonania_uslugi),
        'firmasprzedawcza': firma(
            faktura_ostatinia.firmaSprzedawca.name,
            faktura_ostatinia.firmaSprzedawca.nip,
            faktura_ostatinia.firmaSprzedawca.ulica,
            faktura_ostatinia.firmaSprzedawca.adres
        ),
        'firmanabywcza': firma(
            faktura_ostatinia.firmaKlient.name,
            faktura_ostatinia.firmaKlient.nip,
            faktura_ostatinia.firmaKlient.ulica,
            faktura_ostatinia.firmaKlient.adres
        ),
        "datafakturaVat": faktura_ostatinia.numer_faktury,
        'pozycje': list(faktura_ostatinia.pozycje.all()),
        'metodaPlatnosci': faktura_ostatinia.metoda_platnosci,
        'terminPlatnosci': str(faktura_ostatinia.termin_platnosci),
        'nrkonta': faktura_ostatinia.numer_konta
    }
    
    i = []
    for x in context['pozycje']:
        i += [pozycja(
            x.nazwa,
            x.jednostka,
            x.cena_Netto,
            x.ilosc,
            x.podatek
        )]

    context.update({'pozycje': i})
    
    # calculate last entry
    i = [0,0,0]
    for x in context['pozycje']:
        i[0] += x.wartoscN
        i[1] += x.cenaN
        i[2] += x.wartoscVat
    
    context.update({
        'wartoscN': round(i[0], 2),
        'cenaVat': round(i[1], 2),
        'wartoscVat': round(i[2], 2),
    })

    return context

def strona_gl(request):
    faktura_ostatnia = faktura.objects.order_by('-id')
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktura_ostatnia})


def faktura_temp(request, id=1):
    faktura_ostatnia = faktura.objects.order_by('-id')[id - 1]
    faktura_template = loader.get_template('faktura.svg')
    return HttpResponse(faktura_template.render(faktura_context_calc(faktura_ostatnia), request))
