from django.shortcuts import render
from django.http import HttpResponse
import random

# Create your views here.
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
    "miejsceWystawienia": 'Wesoła',
    "dataWystawienia": "04 - 01 - 2022",
    "dataWykonaniaUslugi": "03 - 01 - 2022",
    'firmasprzedawcza': firma('firma a', '1234567890', 'xyz 10', '10-100 xyz'),
    'firmanabywcza': firma('firma b', '0987654321', 'xyz 21', '11-111 xyz'),
    "datafakturaVat": '02/02/2022',
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




def index(request):
    return render(request, 'index.svg', context)