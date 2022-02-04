from django.db import models
from django.db.models.deletion import CASCADE
from django.template import loader
from django.core.exceptions import ValidationError
import os
from os.path import isdir
import cairosvg
from PyPDF2 import PdfFileMerger

########### Validation

def validate_neg(value):
    if value < 0:
        raise ValidationError(
            f"{value} is negative"
        )


########### Models

class firma(models.Model):
    Nazwa = models.CharField(max_length=50, primary_key=True)
    NIP = models.CharField(max_length=13)
    Ulica = models.CharField(max_length=100)
    Adres = models.CharField(max_length=100)

    def __str__(self):
        return f'firma {self.Nazwa}'

class pozycjafaktury(models.Model):

    Nazwa = models.TextField()
    Jednostka = models.CharField(max_length=5, default="Szt.")
    Ilosc = models.FloatField(default=1,validators=[validate_neg])
    Cena_Netto = models.FloatField(validators=[validate_neg])
    Podatek = models.IntegerField(default=23,validators=[validate_neg])

    def __str__(self):
        return f'PozFakt {self.Nazwa} x {self.Ilosc}'

class faktura(models.Model):
    Nazwa_faktury = models.CharField(max_length=90)
    firma_sprzedawca = models.ForeignKey(firma,related_name='sprzedawca', on_delete=CASCADE)
    firma_klient = models.ForeignKey(firma,related_name='nabywca', on_delete=CASCADE)
    Numer_faktury = models.CharField(max_length=90)
    Data_sprzedaży = models.DateField()
    Data_wystawienia = models.DateField()
    Termin_płatności = models.DateField()
    pozycje = models.ManyToManyField(pozycjafaktury)
    Zapłacono = models.FloatField(default=0,validators=[validate_neg])
    Sposób_płatności = models.CharField(max_length=90, default='Przelew na konto')
    Termin_płatności_dni = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Faktura {self.Numer_faktury}'

########### Functions

# Get context from faktura

def getcontext(faktura_ostatinia):
    context = {
        'FVATNAME': faktura_ostatinia.Nazwa_faktury,
        'NAB' : faktura_ostatinia.firma_klient.Nazwa,
        'NABA' : faktura_ostatinia.firma_klient.Ulica,
        'NABK' : faktura_ostatinia.firma_klient.Adres,
        'NABNIP' : 'NIP: ' + str(faktura_ostatinia.firma_klient.NIP),
        'SPR' : faktura_ostatinia.firma_sprzedawca.Nazwa,
        'SPRA' : faktura_ostatinia.firma_sprzedawca.Ulica,
        'SPRK' : faktura_ostatinia.firma_sprzedawca.Adres,
        'SPRNIP' : 'NIP: ' + str(faktura_ostatinia.firma_sprzedawca.NIP),
        'VATNAME': faktura_ostatinia.Numer_faktury,
        'DATASP' : str(faktura_ostatinia.Data_sprzedaży),
        'DATAWYS': str(faktura_ostatinia.Data_wystawienia),
        'TERPLAT': str(faktura_ostatinia.Termin_płatności),
        'POZYCJE': list(faktura_ostatinia.pozycje.all()),
        'ZAPLACONO': faktura_ostatinia.Zapłacono,
        'DAYS': str(faktura_ostatinia.Termin_płatności_dni),
        'SPOSPLAT': faktura_ostatinia.Sposób_płatności ,
        'STRGL': True,
        'STRKON': False,
    }
    return context

# Calc content of faktura

def faktura_context_calc(context):

    class pozycja:
        def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
            def name(nazwa):
                name = []
                i = 0
                l = 0
                for x in nazwa.split():
                    if l + len(x) > 40:
                        i += 1
                        l = 0
                    if l == 0:
                        name += ['']
                    name[i] += f'{x} '
                    l += len(x) + 1
                return name, i

            self.nazwa, self.wys= name(nazwa)
            self.jednostka = jednostka
            self.ilosc = ilosc
            if ilosc == int(ilosc):
                self.ilosc = int(ilosc)
            self.podatek = podatek
            self.cenaN = cenaN
            self.wartoscN = self.cenaN * self.ilosc
            self.cenaVat = self.cenaN * (podatek / 100)
            self.wartoscVat = self.wartoscN * (podatek / 100)

    # Check for number of DAYS 

    if context['DAYS'] == '1':
        context.update({'DAYS': context['DAYS'] + ' dzień'})
    else:
        context.update({'DAYS': context['DAYS'] + ' dni'})
    
    # Calc pozycja and update context
    # i = [Pozycje, [Podatki, Kwota Laczna Netto, Razem, Zaplacono]]

    i = [[],[{}, 0., 0., 0.]]
    for x in context['POZYCJE']:
        i[0] += [pozycja(x.Nazwa, x.Jednostka, x.Cena_Netto, x.Ilosc, x.Podatek)]

    for x in i[0]:
        try:
            i[1][0].update({f'{x.podatek}':x.wartoscVat + i[1][0][f'{x.podatek}']})
        except:
            i[1][0].update({f'{x.podatek}':x.wartoscVat})
        i[1][1] += x.wartoscN
        i[1][2] += x.wartoscVat
    i[1][2] += i[1][1]
    i[1][3] = i[1][2]

    if context['ZAPLACONO'] > 0:
        i[1][3] -= context['ZAPLACONO']

    context.update({
        'POZYCJE': i[0],
        'KLN': i[1][1],
        'KVAT': dict(sorted(i[1][0].items())),
        'RAZEM': i[1][2],
        'KDZ': i[1][3],
    })

    # Calc pozycje on page

    linie = 25 - len(i[1][0].items())
    liniegl = linie - 20
    linie2 = 36
    linie2gl = 22
    if context['ZAPLACONO'] <= float(0):
        linie += 2
        liniegl += 2
    
    # some things on page
    # Tabelarys = [tabela_anchor]
    # i = [[strona = [pozycje]], nr strony , max linie ,c linie on page , strzalka poz]
    
    tabelarys = [467.6]
    i = [[[]], 0, linie, 0, 465.8]
    for x in context['POZYCJE']:
        if i[3] + x.wys >= i[2]:
            i[1] += 1
            i[3] = 0
            i[0] += [[]]
            i[4] = 618.5
            i[2] = linie2
            tabelarys +=[620]
        x.szczalka = i[4]
        i[4] -= ((x.wys + 1) * 11.2 ) + 2.4
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

def context_to_pdf(context, pozycje_c, tabelarys, Nazwa_faktury_Wygenerowanej='faktura', dirf="faktura"):
    class tabela:
        def __init__(self, x, kwotavpoz, zaplacono, wys):
            #((x.wys + 1) * 11.2 )
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

    for x in pozycje:

        # final context update

        temp += 1
        if len(x) != 0:
            context.update({
                'pozycje': x,
                'TABELA': tabela(x, context['KVAT'], context['ZAPLACONO'], tabelarys[temp - 1]),
                'TABELARYS': (tabelarys[temp - 1] + 6.65),
                'STRONA': temp,
                'STRONY': pozycje_c[1] + 1,
            })
        else:
            context.update({
                'pozycje': [],
                'TABELA': -200,
                'TABELARYS': -200,
                'STRONA': temp,
                'STRONY': pozycje_c[1] + 1,
            })
        if pozycje_c[1] + 1 == temp:
            context.update({
                'STRKON': True
            })
        
        # create pdf

        if isdir(f'{dirf}') == False:
            os.mkdir(f'{dirf}')
        svg = loader.get_template('fv-pod.svg').render(context)
        cairosvg.svg2pdf(bytestring=svg, write_to=f'{dirf}/faktura{temp}.pdf')
        pdfs += [f'{dirf}/faktura{temp}.pdf']
        context.update({
            'STRGL': False
        })
    
    # merge pdf
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write(f"{dirf}/fak-{Nazwa_faktury_Wygenerowanej}.pdf")
    
    for x in range(1, temp + 1):
        os.remove(f'{dirf}/faktura{x}.pdf')