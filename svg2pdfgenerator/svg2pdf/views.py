from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import faktura
import os
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
        l += len(x) + 1
    return name, i

class pozycja:
    def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
        self.nazwa, self.wys= name(nazwa)
        self.jednostka = jednostka
        self.ilosc = ilosc
        self.podatek = podatek
        self.cenaN = cenaN
        self.wartoscN = self.cenaN * self.ilosc
        self.cenaVat = self.cenaN * (podatek / 100)
        self.wartoscVat = self.wartoscN * (podatek / 100)

class tabela:
    def __init__(self, x, kwotavpoz, zaplacono):
        #((x.wys + 1) * 11.2 )
        self.wys = 0
        self.liniah = []
        for i in x:
            self.wys += i.wys + 1
            self.liniah += [467.6 - (self.wys * 12.7) + self.wys + 4]
        self.linawys = (self.wys * 11.2) + 2
        self.wys = self.liniah[-1]
        self.liniah = self.liniah[:-1]
        self.kln = self.wys - 15
        self.kwotav = self.kln
        self.kwotavh = []
        for x in kwotavpoz.items():
            self.kwotav -= 13.
            self.kwotavh += [self.kwotav]
        self.kwotavh = self.kwotavh[:-1]
        if zaplacono > 0:
            self.zapl = self.kwotav - 22
        else:
            self.zapl = self.kwotav
        self.klb = self.zapl - 22
        self.klina = self.klb - 24
        self.linawysmax = (self.wys - self.klb) + 24 + self.linawys

def faktura_context_calc(faktura_ostatinia):
    context = {
        'FVATNAME': faktura_ostatinia.Nazwa_faktury,
        'NAB' : faktura_ostatinia.firma_klient.Nazwa,
        'NABA' : faktura_ostatinia.firma_klient.Ulica,
        'NABK' : faktura_ostatinia.firma_klient.Adres,
        'NABNIP' : faktura_ostatinia.firma_klient.NIP,
        'VATNAME': faktura_ostatinia.Numer_faktury,
        'DATASP' : str(faktura_ostatinia.Data_sprzedaży),
        'DATAWYS': str(faktura_ostatinia.Data_wystawienia),
        'TERPLAT': str(faktura_ostatinia.Termin_płatności),
        'POZYCJE': list(faktura_ostatinia.pozycje.all()),
        'ZAPLACONO': faktura_ostatinia.Zapłacono,
        'DAYS': str(faktura_ostatinia.Termin_płatności_dni)
    }
    if context['DAYS'] == '1':
        context.update({'DAYS': context['DAYS'] + ' dzień'})
    else:
        context.update({'DAYS': context['DAYS'] + ' dni'})
    


    i = [[],[{}, 0., 0., 0.], '']
    for x in context['POZYCJE']:
        i[2] = pozycja(x.Nazwa, x.Jednostka, x.Cena_Netto, x.Ilosc, x.Podatek)
        i[0] += [i[2]]

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

    linie = 7 - len(i[1][0].items())
    print(context['ZAPLACONO'])
    if context['ZAPLACONO'] <= float(0):
        linie += 2

    i = [[[]], 0, linie, 0, 465.8]
    for x in context['POZYCJE']:
        if i[3] + x.wys >= i[2]:
            i[1] += 1
            i[3] = 0
            i[0] += [[]]
            i[4] = 467.6
        x.szczalka = i[4]
        i[4] -= ((x.wys + 1) * 11.2 )
        i[3] += x.wys + 1
        i[0][i[1]] += [x]

    return context, i

def strona_gl(request):
    faktury = list(faktura.objects.order_by('-id'))
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktury})


def faktura_temp(request, id=1):

    #get faktura by id
    faktury = faktura.objects.order_by('-id')
    for x in faktury:
        if x.id == id:
            id = x

    #calc context
    context, pozycje_c = faktura_context_calc(id)
    pdfs = []
    temp = 0
    pozycje = pozycje_c[0]
    for x in pozycje:
        temp += 1
        context.update({
            'pozycje': x,
            'TABELA': tabela(x, context['KVAT'], context['ZAPLACONO']),
            'STRONA': temp,
            'STRONY': pozycje_c[1] + 1
        })
        print(context['TABELA'].wys, context['TABELA'].kln, context['TABELA'].kwotav)
        svg = loader.get_template('fv-template.svg').render(context, request)
        cairosvg.svg2pdf(bytestring=svg, write_to=f'faktura/faktura{temp}.pdf')
        pdfs += [f'faktura/faktura{temp}.pdf']
    
    #return render(request, 'fv-template.svg', context)
    

    #merger pdf
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("faktura/faktura.pdf")
    for x in range(1, temp + 1):
        os.remove(f'faktura/faktura{x}.pdf')

    return FileResponse(open('faktura/faktura.pdf', 'rb'), as_attachment=0, filename='faktura.pdf')

