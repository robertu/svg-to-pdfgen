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
        if l + len(x) > 30:
            i += 1
            l = 0
        if l == 0:
            name += ['']
        name[i] += f'{x} '
        l += len(x)
    return name, i + 1

class pozycja:
    def __init__(self, nazwa, jednostka, cenaN, ilosc, podatek):
        self.nazwa, self.wys= name(nazwa)
        self.jednostka = jednostka
        self.ilosc = ilosc
        self.podatek = podatek
        self.cenaN = '%.2f' % cenaN
        self.wartoscN = '%.2f' % float(float(self.cenaN) * self.ilosc)
        self.cenaVat = '%.2f' % float(float(self.cenaN) * (podatek / 100))
        self.wartoscVat = '%.2f' % float(float(self.wartoscN) * (podatek / 100))


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

    i = [[],[{}, 0., 0., 0.], '']
    for x in context['POZYCJE']:
        i[2] = pozycja(x.Nazwa, x.Jednostka, x.Cena_Netto, x.Ilosc, x.Podatek)
        i[0] += [i[2]]

    for x in i[0]:
        if x.podatek > 0:
            try:
                i[1][0].update({f'{x.podatek}':float(float(x.wartoscVat) + i[1][0][f'{x.podatek}'])})
            except:
                i[1][0].update({f'{x.podatek}':float(x.wartoscVat)})
        i[1][1] += float(x.wartoscN)
        i[1][2] += float(x.wartoscVat)
    i[1][2] += i[1][1]
    i[1][3] = i[1][2]

    context.update({
        'POZYCJE': i[0],
        'KLN': i[1][1],
        'KVAT': dict(sorted(i[1][0].items())),
        'KLB': i[1][2],
        'KDZ': i[1][3],
    })
    
    i = [[[]], 0, 10 - len(i[1][0].items()), 0, 467.6]
    for x in context['POZYCJE']:
        print(i[3], ' / ', i[1], ' / ',i[2], ' / ', i[0])
        if i[3] >= i[2]:
            print('x')
            i[1] += 1
            i[3] = 0
            i[0] += [[]]
            i[4] = 467.6
        x.szczalka = i[4]
        i[4] -= 9.6 + ((x.wys - 1) * 9.6 )
        i[3] += x.wys
        i[0][i[1]] += [x]
    
    print(i[0])

    return context, i

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
    context, pozycje_c = faktura_context_calc(i)
    pdfs = []
    temp = 0
    pozycje = pozycje_c[0]
    for x in pozycje:
        temp += 1
        context.update({
            'pozycje': x,
            'STRONA': temp,
            'STRONY': pozycje_c[1] + 1
        })
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

