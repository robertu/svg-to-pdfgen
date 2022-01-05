from django.db import models

# Create your models here.
class firma(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    nip = models.CharField(max_length=10)
    ulica = models.CharField(max_length=100)
    adres = models.CharField(max_length=100)

    def __str__(self):
        return f'Firma {self.name}'

class klient(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    nip = models.CharField(max_length=10)
    ulica = models.CharField(max_length=100)
    adres = models.CharField(max_length=100)

    def __str__(self):
        return f'Klient {self.name}'

class pozycjafaktury(models.Model):
    class JM(models.TextChoices):
        SZT = 'Szt.'

    nazwa = models.CharField(max_length=40)
    jednostka = models.CharField(max_length=4, choices=JM.choices, default=JM.SZT)
    ilosc = models.IntegerField()
    Cena = models.CharField(max_length=12)

    def __str__(self):
        return f'PozFakt {self.nazwa} x {self.ilosc}'

class faktura(models.Model):
    miejsce_wystawienia = models.CharField(max_length=100)
    data_wystawienia = models.DateField()
    data_wykonania_uslugi = models.DateField()
    firmaSprzedawca = models.ForeignKey(firma, on_delete=models.CASCADE)
    firmaKlient = models.ForeignKey(klient, on_delete=models.CASCADE)
    pozycje = models.ManyToManyField(pozycjafaktury)
    numer_faktury = models.CharField(max_length=15)
    metoda_platnosci = models.CharField(max_length=30)
    termin_platnosci = models.DateField()
    numer_konta = models.CharField(max_length=12)

    def __str__(self):
        return f'Faktura {self.numer_faktury}'