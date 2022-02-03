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
. env/bin/activate
pip3 install -r requirements.txt
```

Start serwera deweloperskiego
=============================

Wewnątrz katalogu `app`:

```
. env/bin/activate
./manage.py migrate
./manage.py createsuperuser
```
Tu podaj nazwę użytkownika oraz hasło.

```
./manage.py runserver {port}
```

Test aplikacji
==============

```
. env/bin/activate
pytest tests.py
```
