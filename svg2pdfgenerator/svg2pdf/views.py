from django.shortcuts import render
from django.http import HttpResponse
from .models import faktura
import random

# Create your views here.



def faktura_context_calc():

    faktura_ostatnia = faktura.objects.order_by('-numer_faktury')[:1]

    class firma:
        def __init__(self, nazwa, nip, ulica, adres):
            self.nazwa = nazwa
            self.nip = nip
            self.ulica = ulica
            self.adres = adres

    class usluga:
        def __init__(self, nazwa, jm, ilosc, cenaN):
            self.nazwa = nazwa
            self.jm = jm
            self.ilosc = ilosc
            self.cenaN = cenaN
            self.wartoscN = cenaN * ilosc
            self.cenaVat = round(cenaN * .23, 2)
            self.wartoscVat = round(self.wartoscN + self.cenaVat, 2)

    context = {
    "miejsceWystawienia": ''.join([q.miejsce_wystawienia for q in faktura_ostatnia]),
    "dataWystawienia": ''.join(str([q.data_wystawienia for q in faktura_ostatnia])),
    "dataWykonaniaUslugi": ''.join(str([q.data_wykonania_uslugi for q in faktura_ostatnia])),
    'firmasprzedawcza': firma('firma a', '1234567890', 'xyz 10', '10-100 xyz'),
    'firmanabywcza': firma('firma b', '0987654321', 'xyz 21', '11-111 xyz'),
    "datafakturaVat": ''.join([q.numer_faktury for q in faktura_ostatnia]),
    'uslogi':[
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
        usluga('sysop', 'usł.', random.randrange(0,10000), round(float(random.randrange(0,10000)), 2)),
    ],
    'metodaPlatnosci': 'Przelew w terminie 2 dni',
    'terminPlatnosci': '02/02/2022',
    'nrkonta': '6735 7256 7247 7192'
    }

    i = [0,0,0]
    for x in context['uslogi']:
        i[0] += x.wartoscN
        i[1] += x.cenaVat
        i[2] += x.wartoscVat

    context.update({
        'wartoscN': round(i[0], 2),
        'cenaVat': round(i[1], 2),
        'wartoscVat': round(i[2], 2),
    })
    return context

def strona_gl(request):
    faktura_ostatnia = faktura.objects.order_by('-numer_faktury')
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktura_ostatnia})


def faktura_temp(request):
    return render(request, 'index.svg', faktura_context_calc())
