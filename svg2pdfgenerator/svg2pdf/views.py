from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
from django.template import loader
from .models import faktura
import os
import cairosvg
from PyPDF2 import PdfFileMerger
# Create your views here.
#
#def name(nazwa):
#    name = []
#    i = 0
#    l = 0
#    for x in nazwa.split():
#        if l + len(x) > 40:
#            i += 1
#            l = 0
#        if l == 0:
#            name += ['']
#        name[i] += f'{x} '
#        l += len(x)
#    return name, i

class pozycja:
    def __init__(self, nazwa, jednostka, cenaN, ilosc):
        self.nazwa = nazwa
        self.jednostka = jednostka
        self.ilosc = ilosc
        self.cenaN = '%.2f' % cenaN
        self.wartoscN = '%.2f' % float(float(self.cenaN) * self.ilosc)
        self.cenaVat = '%.2f' % float(float(self.cenaN) * 1.23)
        self.wartoscVat = '%.2f' % float(float(self.wartoscN) * 1.23)


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
        'DAYS': str(faktura_ostatinia.Termin_płatności_dni)
    }

    i = [[],[0., 0., 0., 0.]]
    for x in context['POZYCJE']:
        i[0] += [pozycja(x.Nazwa, x.Jednostka, x.Cena_Netto, x.Ilosc)]

    for x in i[0]:
        i[1][0] += float(x.wartoscN)
        i[1][1] += float(x.wartoscN) * 0.23
        i[1][2] = float(i[1][0] + i[1][1])
        i[1][3] = i[1][2]

    context.update({
        'POZYCJE': i[0],
        'KLN': '%.2f' % i[1][0],
        'KVAT': '%.2f' % i[1][1],
        'KLB': '%.2f' % i[1][2],
        'KDZ': '%.2f' % i[1][3],
    })

    return context

def strona_gl(request):
    faktury = list(faktura.objects.order_by('-id'))
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktury})


def faktura_temp(request, id=1):

    #get faktura by id
    faktury = faktura.objects.order_by('-id')
    for x in faktury:
        if x.id == id:
            i = x

    #calc context
    context = faktura_context_calc(i)
    pdfs = []
    temp = 0
    for x in context['POZYCJE']:
        temp += 1
        context.update({
            'OPIS' : x.nazwa,
            'ILOSC' : x.ilosc,
            'JM' :x.jednostka,
            'CJD' :x.cenaN,
            'CENA' :x.wartoscN,
        })
        svg = loader.get_template('fv-template.svg').render(context, request)
        cairosvg.svg2pdf(bytestring=svg, write_to=f'faktura{temp}.pdf')
        pdfs += [f'faktura{temp}.pdf']
    
    #return render(request, 'fv-template.svg', context)
    

    #merger pdf
    merger = PdfFileMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("faktura.pdf")
    for x in range(1, temp + 1):
        os.remove(f'faktura{x}.pdf')

    return FileResponse(open('faktura.pdf', 'rb'), as_attachment=0, filename='faktura.pdf')

