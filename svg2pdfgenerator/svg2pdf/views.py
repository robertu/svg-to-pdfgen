from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
class firma:
    def __init__(self, nazwa, nip, ulica, addres):
        self.nazwa = nazwa
        self.nip = nip
        self.ulica = ulica
        self.addres = addres

class usluga:
    def __init__(self, nazwa, jm, ilosc, cenaN, wartoscN):
        self.nazwa = nazwa
        self.jm = jm
        self.ilosc = ilosc
        self.cenaN = cenaN
        self.wartoscN = wartoscN
        self.stawkaVat = 1.23
        self.kwotaVat = round(cenaN * self.stawkaVat)
        self.WartoscVat = round (wartoscN * self.stawkaVat)



content = {
    "miejsceWystawienia": 'Wesoła',
    "dataWystawienia": "04 - 01 - 2022",
    "dataWykonaniaUslugi": "03 - 01 - 2022",
    'firmasprzedawcza': firma('firma a', '1234567890', 'xyz 10', '10-100 xyz'),
    'firmanabywcza': firma('firma b', '0987654321', 'xyz 21', '11-111 xyz'),
    "datafakturaVat": '02/02/2022',
    'uslogi':[
        usluga('sysop', 'usł.', 1, 21.23, 1),
        usluga('sysop', 'usł.', 1, 21.23, 1),
        usluga('sysop', 'usł.', 1, 21.23, 1),
    ]
}



def index(request):
    return render(request, 'index.html', content)

