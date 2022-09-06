# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=E1101
# pylint: disable=W0613
# pylint: disable=C0103
# pylint: disable=broad-except
# pylint: disable=import-error

from django.http.response import FileResponse # noqa
from django.shortcuts import render

from .models import Faktura, context_to_pdf, faktura_context_calc, getcontext

# Settings

FOLDER_NA_FAKTURY = "faktury"

# Requests

# Str gl


def strona_gl(request):
    faktury = list(Faktura.objects.order_by("-id"))
    return render(request, "strona_gl.html", {"faktura_ostatnia": faktury})


# Get selected Faktura ID


def faktura_get_id(faktura_id):
    faktury = Faktura.objects.order_by("-id")
    id_is = -1
    for i in faktury:
        if i.id == faktura_id:
            id_is = i
    return id_is


# Gen faktura from id


def faktura_from_id(faktura_id):
    context = getcontext(faktura_id)
    context, pozycje_c, tabelarys = faktura_context_calc(context)
    context_to_pdf(context, pozycje_c, tabelarys, faktura_id.nazwa_faktury, FOLDER_NA_FAKTURY)


# Get faktura

# pylint: disable=W0622
def faktura_temp(request,id=1):

    # ID faktury
    faktura_id = faktura_get_id(id)
    try:
        return FileResponse(
            open(f"{FOLDER_NA_FAKTURY}/fak-{faktura_id.nazwa_faktury}.pdf", "rb"),
            as_attachment=0,
            filename=f"{faktura_id.nazwa_faktury}.pdf"
        )
    except Exception:
        faktura_from_id(faktura_id)
        return FileResponse(
            open(f"{FOLDER_NA_FAKTURY}/fak-{faktura_id.nazwa_faktury}.pdf", "rb"),
            as_attachment=0,
            filename=f"{faktura_id.nazwa_faktury}.pdf"
        )


# Gen faktura


def faktura_gen(request,id=1):

    # ID faktury
    faktura_id = faktura_get_id(id)
    faktura_from_id(faktura_id)

    return FileResponse(
        open(f"{FOLDER_NA_FAKTURY}/fak-{faktura_id.nazwa_faktury}.pdf", "rb"),
        as_attachment=0,
        filename=f"{faktura_id.nazwa_faktury}.pdf"
    )
