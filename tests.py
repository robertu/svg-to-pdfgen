import os
import shutil

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from svg2pdf.models import Faktura, Firma, JednostkaM, Pozycjafaktury, context_to_pdf, faktura_context_calc  # noqa

FOLDER_NA_FAKTURY_TESTOWE = "faktury_testowe"


class JednostkaTest:
    def __init__(self, nazwa, dziesietna):
        self.nazwa = nazwa
        self.dziesietna = dziesietna


class PozycjaTest:
    def __init__(self, nazwa, cenaN, ilosc=1, podatek=23, jednostka=JednostkaTest("SZT", False)):
        self.nazwa = nazwa
        self.jednostka = jednostka
        self.cena_Netto = cenaN
        self.ilosc = ilosc
        self.podatek = podatek


def basic_con():
    context = {
        "FVATNAME": "test",
        "NAB": "test",
        "NABA": "test",
        "NABK": "test",
        "NABNIP": "123 456 78 90",
        "VATNAME": "test",
        "DATASP": "01-01-0001",
        "DATAWYS": "01-01-0001",
        "TERPLAT": "01-01-0001",
        "POZYCJE": [PozycjaTest("Poz 1", 10, 10)],
        "ZAPLACONO": 2,
        "DAYS": "2",
        "STRGL": True,
        "STRKON": False,
    }
    return context


try:
    shutil.rmtree(FOLDER_NA_FAKTURY_TESTOWE)
except Exception:
    pass


# tests
def test_podstawowy():
    context = basic_con()
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_podstawowy", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_podstawowy.pdf")


def test_pozycje():
    context = basic_con()
    TEMP = []
    for x in range(100):
        TEMP += [PozycjaTest(f"poz {x}", x)]
    context.update({"POZYCJE": TEMP})
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_pozycje", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_pozycje.pdf")


def test_nazwa_wrap():
    context = basic_con()
    TEMP = []
    TEMPN = ""
    for x in range(100):
        TEMPN = "poz" + str(x) + " a" * 4 * x
        TEMP += [PozycjaTest(TEMPN, x)]
    context.update({"POZYCJE": TEMP})
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_nazwa_wrap", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_nazwa_wrap.pdf")


def test_podatki_pozycje():
    context = basic_con()
    TEMP = []
    for x in range(100):
        TEMP += [PozycjaTest(f"poz {x}", x, 1, 23)]
        TEMP += [PozycjaTest(f"poz {x}", x, 2, 8)]
        TEMP += [PozycjaTest(f"poz {x}", x, 3, 0)]
    context.update({"POZYCJE": TEMP})
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_podatki_pozycje", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_podatki_pozycje.pdf")


def test_vat():
    context = basic_con()
    TEMP = []
    for x in range(10):
        TEMP += [PozycjaTest(f"poz {x}", x, 1, x)]
    context.update({"POZYCJE": TEMP})
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_vat", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_vat.pdf")


def test_jednostki():
    context = basic_con()
    TEMP = []
    jednostki = [JednostkaTest("SZT", False), JednostkaTest("KG", True)]
    for x in range(10):
        TEMP += [PozycjaTest(f"poz {x}", x, float(f"{x}.{x}"), 23, jednostki[0])]
        TEMP += [PozycjaTest(f"poz {x}", x, float(f"{x}.{x}"), 23, jednostki[1])]
    context.update({"POZYCJE": TEMP})
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, "test_jednostki", FOLDER_NA_FAKTURY_TESTOWE)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-test_jednostki.pdf")


def test_overflow_db():
    NAZWA = "a"
    jm1 = JednostkaM(nazwa="testtesttest", dziesietna=False)
    jm1.save()
    jm2 = JednostkaM(nazwa="testtesttesttest", dziesietna=True)
    jm2.save()
    firma = Firma(nazwa=NAZWA * 50, nip="123456789123456789", ulica=NAZWA * 50, adres=NAZWA * 50)
    firma.save()
    faktura = Faktura(
        nazwa_faktury=NAZWA * 90,
        firma_sprzedawca=firma,
        firma_klient=firma,
        numer_faktury=NAZWA * 90,
        data_sprzedazy="2000-01-01",
        data_wystawienia="2000-01-01",
        termin_platnosci="2000-01-01",
        zaplacono=-1,
        sposob_platnosci=NAZWA * 90,
        termin_platnosci_dni=0,
    )
    faktura.save()
    for x in range(20):
        pozycja = Pozycjafaktury(nazwa=NAZWA * 36, jednostka=jm1, ilosc=-1, cena_Netto=1.1, podatek=-1)
        pozycja.save()
        faktura.pozycje.add(pozycja)
        pozycja = Pozycjafaktury(nazwa=(NAZWA + " ") * 36, jednostka=jm2, ilosc=-1, cena_Netto=2.2, podatek=-1)
        pozycja.save()
        faktura.pozycje.add(pozycja)
    assert 1 == 1
