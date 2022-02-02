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

```
. env/bin/activate
python3 manage.py migrate
python3 manage.py createsuperuser
(Podaj nazwę użytkownika oraz hasło)
python3 manage.py runserver {port}
```

Test aplikacji
==============

```
. env/bin/activate
pytest tests.py
```