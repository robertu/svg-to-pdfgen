from logging import exception
import re
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
from .models import *
# Create your views here.

def strona_gl(request):
    faktury = list(faktura.objects.order_by('-id'))
    return render(request, 'strona_gl.html', {"faktura_ostatnia" : faktury})

def faktura_temp(request, id=1):
    #get faktura by id
    faktury = faktura.objects.order_by('-id')
    for x in faktury:
        if x.id == id:
            id = x
    try:
        return FileResponse(open(f'faktura/{x.Nazwa_faktury}.pdf', 'rb'), as_attachment=0, filename=f'{x.Nazwa_faktury}.pdf')
    except:
        context = getcontext(id)
        context, pozycje_c, tabelarys = faktura_context_calc(context)
        context_to_pdf(context, pozycje_c, tabelarys, x.Nazwa_faktury)

        return FileResponse(open(f'faktura/{x.Nazwa_faktury}.pdf', 'rb'), as_attachment=0, filename=f'{x.Nazwa_faktury}.pdf')

def faktura_gen(request, id=1):
    #get faktura by id
    faktury = faktura.objects.order_by('-id')
    for x in faktury:
        if x.id == id:
            id = x

    #calc context
    context = getcontext(id)
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, x.Nazwa_faktury)

    return FileResponse(open(f'faktura/{x.Nazwa_faktury}.pdf', 'rb'), as_attachment=0, filename=f'{x.Nazwa_faktury}.pdf')
