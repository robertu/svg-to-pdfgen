import pytest
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()
import shutil
from svg2pdf.models import faktura, getcontext, faktura_context_calc, context_to_pdf

class pozycja:
    def __init__(self, nazwa, cenaN, ilosc=1, podatek=23, jednostka='Szt.'):
        self.Nazwa = nazwa
        self.Jednostka = jednostka
        self.Cena_Netto = cenaN
        self.Ilosc = ilosc
        self.Podatek = podatek
def basic_con():
    context = {
        'FVATNAME': 'test',
        'NAB' : 'test',
        'NABA' : 'test',
        'NABK' : 'test',
        'NABNIP' : '123 456 78 90',
        'VATNAME': 'test',
        'DATASP' : '01-01-0001',
        'DATAWYS': '01-01-0001',
        'TERPLAT': '01-01-0001',
        'POZYCJE': [
            pozycja('Poz 1', 10, 10)
        ],
        'ZAPLACONO': 2,
        'DAYS': '2',
        'STRGL': True,
        'STRKON': False,
    }
    return context

try:
    shutil.rmtree('faktura_testy')
except:
    pass
#tests
def test_podstawowy():
    context = basic_con()
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'test_podstawowy', 'faktura_testy')
    assert os.path.exists('faktura_testy/test_podstawowy.pdf')
def test_pozycje():
    context = basic_con()
    temp = []
    for x in range(100):
        temp += [pozycja(f'poz {x}', x)]
    context.update({
        'POZYCJE': temp
    })
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'test_pozycje', 'faktura_testy')
    assert os.path.exists('faktura_testy/test_pozycje.pdf')
def test_nazwa_wrap():
    context = basic_con()
    temp = []
    tempn =''
    for x in range(100):
        tempn = 'poz' + str(x) + ' a'*4*x
        temp += [pozycja(tempn, x)]
    context.update({
        'POZYCJE': temp
    })
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'test_nazwa_wrap', 'faktura_testy')
    assert os.path.exists('faktura_testy/test_nazwa_wrap.pdf')
def test_podatki_pozycje():
    context = basic_con()
    temp = []
    for x in range(100):
        temp += [pozycja(f'poz {x}', x, 1, 23)]
        temp += [pozycja(f'poz {x}', x, 2, 8)]
        temp += [pozycja(f'poz {x}', x, 3, 0)]
    context.update({
        'POZYCJE': temp
    })
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'test_podatki_pozycje', 'faktura_testy')
    assert os.path.exists('faktura_testy/test_podatki_pozycje.pdf')