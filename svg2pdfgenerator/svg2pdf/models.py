from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey

# Create your models here.
class klient(models.Model):
    Nazwa = models.CharField(max_length=50, primary_key=True)
    NIP = models.CharField(max_length=13)
    Ulica = models.CharField(max_length=100)
    Adres = models.CharField(max_length=100)

    def __str__(self):
        return f'Klient {self.Nazwa}'

class pozycjafaktury(models.Model):
    class JM(models.TextChoices):
        SZT = 'Szt.'
        USL = 'Usł.'
        OPAK = 'Opak.'

    Nazwa = models.TextField()
    Jednostka = models.CharField(max_length=5, choices=JM.choices, default=JM.SZT)
    Ilosc = models.IntegerField(default=1)
    Cena_Netto = models.FloatField()
    Podatek = models.IntegerField(default=23)

    def __str__(self):
        return f'PozFakt {self.Nazwa} x {self.Ilosc}'

class faktura(models.Model):
    Nazwa_faktury = models.CharField(max_length=90)
    firma_klient = models.ForeignKey(klient, on_delete=CASCADE)
    Numer_faktury = models.CharField(max_length=90)
    Data_sprzedaży = models.DateField()
    Data_wystawienia = models.DateField()
    Termin_płatności = models.DateField()
    pozycje = models.ManyToManyField(pozycjafaktury)
    Termin_płatności_dni = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Faktura {self.Numer_faktury}'