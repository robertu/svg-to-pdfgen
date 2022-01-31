Repo
====

```
git clone git@github.com:robertu/svg2pdfgen.giti app
```

Instalacja virtualenv
=====================

Wewnątrz katalogu `app`:

```
python3 -m venv env
. .env
pip3 install -r requirements.txt
```


Start serwera deweloperskiego
=============================

```
. .env
python3 manage.py createsuperuser
(Podaj nazwę użytkownika oraz hasło)
python3 manage.py runserver {port}
```
