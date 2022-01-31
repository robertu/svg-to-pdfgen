```
git clone https://github.com/robertu/svg2pdfgen app
```

venv
```
python3 -m venv ./env
. env/bin/activate
cd app && pip3 install -r ./requirements.txt
```

Start

```
cd svg2pdfgen/svg2pdfgenerator
. ../env/bin/activate
python3 manage.py createsuperuser
(Podaj nazwę użytkownika oraz hasło)
python3 manage.py runserver {port}
```
