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

    #calc context
    context = getcontext(id)
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, 'faktura')

    return FileResponse(open('faktura/faktura.pdf', 'rb'), as_attachment=0, filename='faktura.pdf')

