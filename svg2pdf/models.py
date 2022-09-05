# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
import os
from os.path import isdir

import cairosvg
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.signals import pre_save
from django.template import loader
from PyPDF2 import PdfFileMerger

# Validation


def validate_neg(value):
    if value < 0:
        raise ValidationError(f"{value} is negative")


def validate_zero(value):
    if value == 0:
        raise ValidationError(f"{value} is 0")


def validate_num(value):
    if value != float("%.2f" % value):
        raise ValidationError(f"{value} has more than 2 decimal places")


# Models


class Firma(models.Model):
    nazwa = models.CharField(max_length=45, primary_key=True)
    nip = models.CharField(max_length=13)
    ulica = models.CharField(max_length=45)
    adres = models.TextField()

    def __str__(self):
        return f"firma {self.nazwa}"


class JednostkaM(models.Model):
    nazwa = models.CharField(max_length=8, default="Szt")
    dziesietna = models.BooleanField()

    def __str__(self):
        return f"{self.nazwa}"


class SposobPlat(models.Model):

    nazwa = models.CharField(max_length=20, default="Przelew na konto")

    def __str__(self):
        return f"{self.nazwa}"


class Faktura(models.Model):
    nazwa_faktury = models.CharField(max_length=8)
    firma_sprzedawca = models.ForeignKey(Firma, related_name="sprzedawca", on_delete=CASCADE)
    firma_klient = models.ForeignKey(Firma, related_name="nabywca", on_delete=CASCADE)
    numer_faktury = models.CharField(max_length=15)
    data_sprzedazy = models.DateField()
    data_wystawienia = models.DateField()
    termin_platnosci = models.DateField()
    zaplacono = models.FloatField(default=0, validators=[validate_neg, validate_num])
    sposob_platnosci = models.ForeignKey(SposobPlat, on_delete=CASCADE)
    termin_platnosci_dni = models.PositiveIntegerField(default=1)
    fakture_wystawil = models.CharField(max_length=30)
    def __str__(self):
        return f"Faktura {self.numer_faktury}"


class Pozycjafaktury(models.Model):
    faktura = models.ForeignKey(Faktura, on_delete=CASCADE, related_name='pozycja_rel')
    nazwa = models.TextField()
    jednostka = models.ForeignKey(JednostkaM, on_delete=CASCADE)
    ilosc = models.FloatField(default=1, validators=[validate_neg, validate_zero])
    cena_Netto = models.FloatField(validators=[validate_neg, validate_num, validate_zero])
    podatek = models.IntegerField(default=23, validators=[validate_neg, validate_zero])

    def __str__(self):
        return f">{self.nazwa} x {self.ilosc}"


# signals


def dzies(sender, instance, *args, **kwargs): # czy ilosc ma zostac zmieniona przez jednostke
    if instance.ilosc != int(instance.ilosc):
        if instance.jednostka.dziesietna is False:
            instance.ilosc = int(instance.ilosc)


pre_save.connect(dzies, sender=Pozycjafaktury)

# Functions

# Get context from faktura


def name(nazwa):
    name = []
    i = 0
    lenght = 0
    for x in nazwa.split():
        if lenght + len(x) > 40:
            i += 1
            lenght = 0
        if lenght == 0:
            name += [""]
        name[i] += f"{x} "
        lenght += len(x) + 1
    return name, i


def getcontext(faktura_ostatinia):
    context = {
        "FVATNAME": faktura_ostatinia.nazwa_faktury,
        "NAB": faktura_ostatinia.firma_klient,
        "SPR": faktura_ostatinia.firma_sprzedawca,
        "VATNAME": faktura_ostatinia.numer_faktury,
        "DATASP": str(faktura_ostatinia.data_sprzedazy),
        "DATAWYS": str(faktura_ostatinia.data_wystawienia),
        "TERPLAT": str(faktura_ostatinia.termin_platnosci),
        "POZYCJE": faktura_ostatinia.pozycja_rel.all(),
        "ZAPLACONO": faktura_ostatinia.zaplacono,
        "DAYS": str(faktura_ostatinia.termin_platnosci_dni),
        "SPOSPLAT": faktura_ostatinia.sposob_platnosci,
        "FAKTUREWYS": faktura_ostatinia.fakture_wystawil,
        "STRGL": True,
        "STRKON": False,
    }
    return context


# Calc content of faktura


def faktura_context_calc(context):
    class Pozycja:
        def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
            self.nazwa, self.wys = name(nazwa)
            self.jednostka = jednostka
            self.ilosc = abs(ilosc)
            self.cenaN = abs(cenaN)
            if not jednostka.dziesietna:
                self.ilosc = int(self.ilosc)
                self.cenaN = int(self.cenaN)
            self.podatek = abs(podatek)
            self.wartoscN = self.cenaN * self.ilosc
            self.cenaVat = self.cenaN * (self.podatek / 100)
            self.wartoscVat = self.wartoscN * (self.podatek / 100)

    # Check for number of DAYS

    if context["DAYS"] == "1":
        context.update({"DAYS": context["DAYS"] + " dzień"})
    else:
        context.update({"DAYS": context["DAYS"] + " dni"})

    # Calc pozycja and update context
    # i = [Pozycje, [Podatki, Kwota Laczna Netto, Razem, Zaplacono]]

    i = [[], [{}, 0.0, 0.0, 0.0]]
    for x in context["POZYCJE"]:
        i[0] += [Pozycja(x.nazwa, x.jednostka, x.cena_Netto, x.ilosc, x.podatek)]

    for x in i[0]:
        try:
            i[1][0].update({f"{x.podatek}": x.wartoscVat + i[1][0][f"{x.podatek}"]})
        except Exception:
            i[1][0].update({f"{x.podatek}": x.wartoscVat})
        i[1][1] += x.wartoscN
        i[1][2] += x.wartoscVat
    i[1][2] += i[1][1]
    i[1][3] = i[1][2]

    if context["ZAPLACONO"] > 0:
        i[1][3] -= context["ZAPLACONO"]

    context.update(
        {
            "POZYCJE": i[0],
            "KLN": i[1][1],
            "KVAT": dict(sorted(i[1][0].items())),
            "RAZEM": i[1][2],
            "KDZ": i[1][3],
        }
    )

    # Calc pozycje on page

    linie = 25 - len(i[1][0].items())
    liniegl = linie - 20
    linie2 = 36
    linie2gl = 22
    if context["ZAPLACONO"] <= float(0):
        linie += 2
        liniegl += 2

    # some things on page
    # Tabelarys = [tabela_anchor]
    # i = [[strona = [pozycje]], nr strony , max linie ,c linie on page , strzalka poz]

    tabelarys = [467.6]
    i = [[[]], 0, linie, 0, 465.8]
    for x in context["POZYCJE"]:
        if i[3] + x.wys >= i[2]:
            i[1] += 1
            i[3] = 0
            i[0] += [[]]
            i[4] = 618.5
            i[2] = linie2
            tabelarys += [620]
        x.szczalka = i[4]
        i[4] -= ((x.wys + 1) * 11.2) + 2.4
        i[3] += x.wys + 1
        i[0][i[1]] += [x]

    # page wrap

    if len(i[0]) == 1:
        if len(i[0][0]) > liniegl:
            i[1] += 1
            i[0] += [[]]
    else:
        if i[3] > linie2gl:
            i[1] += 1
            i[0] += [[]]

    return context, i, tabelarys


# Gen pdf file


def context_to_pdf(context, pozycje_c, tabelarys, nazwa_faktury_wygenerowanej="faktura", dirf="faktura"):
    class Tabela:
        def __init__(self, x, kwotavpoz, zaplacono, wys):
            # ((x.wys + 1) * 11.2 )
            self.wys = 0
            self.cwys = 0
            self.liniah = []
            self.linawys = 0
            for i in x:
                self.wys += i.wys + 1
                self.cwys += i.wys
                self.liniah += [wys + 4 - (self.wys * 13.55) + (self.cwys * 2.3)]
                self.linawys -= i.wys * 2.2
            self.linawys += (self.wys * 13.4) + 7
            self.wys = self.liniah[-1]
            self.liniah = self.liniah[:-1]
            self.kln = self.wys - 15
            self.kwotav = self.kln
            self.kwotavh = []
            for x in kwotavpoz.items():
                self.kwotav -= 14.38
                self.kwotavh += [self.kwotav]
            self.kwotavh = self.kwotavh[:-1]
            if zaplacono > 0:
                self.zapl = self.kwotav - 22
            else:
                self.zapl = self.kwotav
            self.klb = self.zapl - 22
            self.klina = self.klb - 24
            self.linawysmax = (self.wys - self.klb) + 24 + self.linawys

    # variables

    pdfs = []
    temp = 0
    pozycje = pozycje_c[0]

    # gen single page

    for i in pozycje:

        # final context update

        temp += 1
        if len(i) != 0:
            context.update(
                {
                    "pozycje": i,
                    "TABELA": Tabela(i, context["KVAT"], context["ZAPLACONO"], tabelarys[temp - 1]),
                    "TABELARYS": (tabelarys[temp - 1] + 6.65),
                    "STRONA": temp,
                    "STRONY": pozycje_c[1] + 1,
                }
            )
        else:
            context.update(
                {
                    "pozycje": [],
                    "TABELA": -200,
                    "TABELARYS": -200,
                    "STRONA": temp,
                    "STRONY": pozycje_c[1] + 1,
                }
            )
        if pozycje_c[1] + 1 == temp:
            context.update({"STRKON": True})

        # create pdf
        if isdir(f"{dirf}") is False:
            os.mkdir(f"{dirf}")
        svg = loader.get_template("fv-pod.svg").render(context)
        cairosvg.svg2pdf(bytestring=svg, write_to=f"{dirf}/faktura{temp}.pdf")
        pdfs += [f"{dirf}/faktura{temp}.pdf"]
        context.update({"STRGL": False})

    # merge pdf
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write(f"{dirf}/fak-{nazwa_faktury_wygenerowanej}.pdf")

    for i in range(1, temp + 1):
        os.remove(f"{dirf}/faktura{i}.pdf")
