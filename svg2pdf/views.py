from django.http.response import FileResponse, HttpResponse  # noqa
from django.shortcuts import render

from .models import context_to_pdf, faktura, faktura_context_calc, getcontext

# Settings

FOLDER_NA_FAKTURY = "faktury"

# Requests

# Str gl


def strona_gl(request):
    faktury = list(faktura.objects.order_by("-id"))
    return render(request, "strona_gl.html", {"faktura_ostatnia": faktury})


# Get selected faktura ID


def faktura_id(id):
    faktury = faktura.objects.order_by("-id")
    for x in faktury:
        if x.id == id:
            return x


# Gen faktura from id


def faktura_from_id(id):
    context = getcontext(id)
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, id.Nazwa_faktury, FOLDER_NA_FAKTURY)


# Get faktura


def faktura_temp(request, id=1):

    # ID faktury
    id = faktura_id(id)
    try:
        return FileResponse(open(f"{FOLDER_NA_FAKTURY}/fak-{id.Nazwa_faktury}.pdf", "rb"), as_attachment=0, filename=f"{id.Nazwa_faktury}.pdf")
    except Exception:
        faktura_from_id(id)
        return FileResponse(open(f"{FOLDER_NA_FAKTURY}/fak-{id.Nazwa_faktury}.pdf", "rb"), as_attachment=0, filename=f"{id.Nazwa_faktury}.pdf")


# Gen faktura


def faktura_gen(request, id=1):

    # ID faktury
    id = faktura_id(id)
    faktura_from_id(id)

    return FileResponse(open(f"{FOLDER_NA_FAKTURY}/fak-{id.Nazwa_faktury}.pdf", "rb"), as_attachment=0, filename=f"{id.Nazwa_faktury}.pdf")
