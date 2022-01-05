from django.db import models

# Create your models here.
class firma(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    nip = models.CharField(max_length=10)
    ulica = models.CharField(max_length=100)
    adres = models.CharField(max_length=100)

class klient(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    nip = models.CharField(max_length=10)
    ulica = models.CharField(max_length=100)
    adres = models.CharField(max_length=100)

class faktura(models.Model):
    firmaSprzedawca = models.ForeignKey(firma, on_delete=models.CASCADE)
    firmaKlient = models.ForeignKey(klient, on_delete=models.CASCADE)
    data_wystawienia = models.DateField()
