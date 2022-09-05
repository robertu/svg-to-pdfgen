from ast import Delete
import os
import shutil

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from svg2pdf.models import Faktura, Firma, JednostkaM, Pozycjafaktury, SposobPlat, context_to_pdf, faktura_context_calc, getcontext  # noqa

FOLDER_NA_FAKTURY_TESTOWE = "faktury_testowe"


try:
    shutil.rmtree(FOLDER_NA_FAKTURY_TESTOWE)
except Exception:
    pass

Firma.objects.filter().delete()
Firma.objects.create(nazwa = "Firma a",nip = "12345678",ulica = "ul.xyz",adres = "adres 1")
Firma.objects.create(nazwa = "Firma b",nip = "87654321",ulica = "ul.abc",adres = "adres 2")

JednostkaM.objects.filter().delete()
JednostkaM.objects.create(nazwa = "Szt",dziesietna = False)
JednostkaM.objects.create(nazwa = "Kg",dziesietna = True)

SposobPlat.objects.filter().delete()
SposobPlat.objects.create(nazwa = "Przelew na konto")

Faktura.objects.filter().delete()

def podstawowa_faktura(numer):
    Faktura.objects.create(
        nazwa_faktury = f"Test {numer}",
        firma_sprzedawca = Firma.objects.get(nazwa="Firma a"),
        firma_klient = Firma.objects.get(nazwa="Firma b"),
        numer_faktury = f"Test {numer}",
        data_sprzedazy = "0001-01-01",
        data_wystawienia = "0001-01-01",
        termin_platnosci = "0001-01-01",
        zaplacono = 0,
        sposob_platnosci = SposobPlat.objects.get(nazwa="Przelew na konto"),
        termin_platnosci_dni = 1,
        fakture_wystawil = f"Test {numer}"
    )

podstawowa_faktura(1)

Pozycjafaktury.objects.filter().delete()
Pozycjafaktury.objects.create(
    faktura = Faktura.objects.get(nazwa_faktury = "Test 1"),
    nazwa = "Pozycja 1.1 test",
    jednostka = JednostkaM.objects.get(nazwa = "Szt"),
    ilosc = 1,
    cena_Netto = 10,
    podatek = 23,
)
Pozycjafaktury.objects.create(
    faktura = Faktura.objects.get(nazwa_faktury = "Test 1"),
    nazwa = "Pozycja 1.2 test",
    jednostka = JednostkaM.objects.get(nazwa = "Kg"),
    ilosc = 1.20,
    cena_Netto = 10,
    podatek = 23,
)

def factura_gen(nazwa_faktury_do_wygenerowania,nazwa_testu):
    context = getcontext(Faktura.objects.get(nazwa_faktury = nazwa_faktury_do_wygenerowania))
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, nazwa_testu, FOLDER_NA_FAKTURY_TESTOWE)

# tests
def test_podstawowy():
    nazwa_testu = "test_podstawowy"
    factura_gen("Test 1", nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")

def test_pozycje():
    podstawowa_faktura(2)
    for x in range(70):
        Pozycjafaktury.objects.create(
            faktura = Faktura.objects.get(nazwa_faktury = "Test 2"),
            nazwa = f"Pozycja 2.{x} test",
            jednostka = JednostkaM.objects.get(nazwa = "Szt"),
            ilosc = x,
            cena_Netto = 10,
            podatek = 23,
        )
    nazwa_testu = "test_pozycje"
    factura_gen("Test 2", nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")

def test_jednostki():
    podstawowa_faktura(3)
    Pozycjafaktury.objects.create(
        faktura = Faktura.objects.get(nazwa_faktury = "Test 3"),
        nazwa = f"Pozycja 3.1 test",
        jednostka = JednostkaM.objects.get(nazwa = "Szt"),
        ilosc = 1.10,
        cena_Netto = 10,
        podatek = 23,
    )
    Pozycjafaktury.objects.create(
        faktura = Faktura.objects.get(nazwa_faktury = "Test 3"),
        nazwa = f"Pozycja 3.2 test",
        jednostka = JednostkaM.objects.get(nazwa = "Kg"),
        ilosc = 1.0,
        cena_Netto = 10,
        podatek = 23,
    )
    nazwa_testu = "test_jednostki"
    factura_gen("Test 3", nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")

def test_pozycja_nazwa():
    podstawowa_faktura(4)
    for x in range(4):
        Pozycjafaktury.objects.create(
            faktura = Faktura.objects.get(nazwa_faktury = "Test 4"),
            nazwa = f"Pozycja 4.{x} test" + "a "*100*x,
            jednostka = JednostkaM.objects.get(nazwa = "Szt"),
            ilosc = 1,
            cena_Netto = 10,
            podatek = 23,
        )
    nazwa_testu = "test_pozycja_nazwa"
    factura_gen("Test 4", nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")

def test_pozycja_podatek():
    podstawowa_faktura(5)
    Pozycjafaktury.objects.create(
        faktura = Faktura.objects.get(nazwa_faktury = "Test 5"),
        nazwa = f"Pozycja 5.1 test",
        jednostka = JednostkaM.objects.get(nazwa = "Szt"),
        ilosc = 1,
        cena_Netto = 10,
        podatek = 23,
    )
    Pozycjafaktury.objects.create(
        faktura = Faktura.objects.get(nazwa_faktury = "Test 5"),
        nazwa = f"Pozycja 5.1 test",
        jednostka = JednostkaM.objects.get(nazwa = "Szt"),
        ilosc = 1,
        cena_Netto = 10,
        podatek = 8,
    )
    Pozycjafaktury.objects.create(
        faktura = Faktura.objects.get(nazwa_faktury = "Test 5"),
        nazwa = f"Pozycja 5.1 test",
        jednostka = JednostkaM.objects.get(nazwa = "Szt"),
        ilosc = 1,
        cena_Netto = 10,
        podatek = 0,
    )
    
    nazwa_testu = "test_pozycja_podatek"
    factura_gen("Test 5", nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")

def test_overflow():
    Firma.objects.create(nazwa = "a"*50,nip = "123456789123456789",ulica = "a"*50,adres = "a"*50)
    JednostkaM.objects.create(nazwa = "a"*16,dziesietna = False)
    JednostkaM.objects.create(nazwa = "b"*16,dziesietna = True)
    Faktura.objects.create(
        nazwa_faktury = "Test 6 " + "a"*90,
        firma_sprzedawca = Firma.objects.get(nip = "123456789123456789"),
        firma_klient = Firma.objects.get(nip = "123456789123456789"),
        numer_faktury = "Test 6 " + "a"*90,
        data_sprzedazy = "0001-01-01",
        data_wystawienia = "0001-01-01",
        termin_platnosci = "0001-01-01",
        zaplacono = -1,
        sposob_platnosci = SposobPlat.objects.get(nazwa="Przelew na konto"),
        termin_platnosci_dni = 0,
        fakture_wystawil = "Test 6 " + "a"*90
    )
    for x in range(50):
        Pozycjafaktury.objects.create(
            faktura = Faktura.objects.get(nazwa_faktury = "Test 6 " + "a"*90),
            nazwa = "a" * 36,
            jednostka = JednostkaM.objects.get(nazwa = "a"*16),
            ilosc = -x,
            cena_Netto = float(f"{x}.{x}"),
            podatek = -1,
        )
        Pozycjafaktury.objects.create(
            faktura = Faktura.objects.get(nazwa_faktury = "Test 6 " + "a"*90),
            nazwa = "a " * 36,
            jednostka = JednostkaM.objects.get(nazwa = "b"*16),
            ilosc = -x,
            cena_Netto = float(f"{x}.{x}"),
            podatek = -1,
        )
    
    nazwa_testu = "test_overflow"
    factura_gen("Test 6 " + "a"*90, nazwa_testu)
    assert os.path.exists(f"{FOLDER_NA_FAKTURY_TESTOWE}/fak-{nazwa_testu}.pdf")