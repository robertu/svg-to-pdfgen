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


shutil.rmtree('faktura')
#tests
def test_podstawowy():
    context = basic_con()
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'test_podstawowy')
    assert os.path.exists('faktura/test_podstawowy.pdf')
