from django.http.response import FileResponse
from django.shortcuts import render
from django.template import loader
from .models import faktura
import cairosvg
from PyPDF2 import PdfFileMerger
# Create your views here.

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
        l += len(x)
    return name, i

class firma:
    def __init__(self, nazwa, nip, ulica, adres):
        self.nazwa = nazwa
        self.nip = nip
        self.ulica = ulica
        self.adres = adres

class pozycja:
    def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
        self.nazwa, self.wys = name(nazwa)
        self.jednostka = jednostka
        self.ilosc = ilosc
        self.podatek = podatek
        self.cenaN = '%.2f' % cenaN
        self.wartoscN = '%.2f' % float(float(self.cenaN) * self.ilosc)
        self.cenaVat = '%.2f' % float(float(self.cenaN) * (float(podatek)/ 100 + 1))
        self.wartoscVat = '%.2f' % float(float(self.wartoscN) * (float(podatek)/ 100 + 1))


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
    i = [0.0,0.0,0.0]
    for x in context['pozycje']:
        i[0] += float(x.wartoscN)
        i[1] += float(x.cenaVat)
        i[2] += float(x.wartoscVat)

    context.update({
        'wartoscN': '%.2f' % i[0],
        'cenaVat': '%.2f' % i[1],
        'wartoscVat': '%.2f' % i[2]
    })
    
    z = 0 
    i = [[]]
    lenght = 0
    for x in context['pozycje']:
        if lenght + x.wys > 16:
            z += 1
            i += [[]]
            lenght = 0
        i[z] += [x]
        lenght += x.wys + 1

    return context ,i

def strona_gl(request):
    faktury = list(faktura.objects.order_by('-id'))
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktury})


def faktura_temp(request, id=1):
    faktury = faktura.objects.order_by('-id')
    for x in faktury:
        if x.id == id:
            i = x
    #return render(request, 'faktura.svg', faktura_context_calc(i))
    
    
    context, pozycje = faktura_context_calc(i)
    pdfs = []
    temp = 0
    for x in pozycje:
        temp += 1
        context.update({
            'pozycje': x
        })
        svg = loader.get_template('faktura.svg').render(context, request)
        cairosvg.svg2pdf(bytestring=svg, write_to=f'faktura{temp}.pdf')
        pdfs += [f'faktura{temp}.pdf']
        
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("faktura.pdf")
    return FileResponse(open('faktura.pdf', 'rb'), as_attachment=0, filename='faktura.pdf')

