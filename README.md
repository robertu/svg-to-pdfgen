Repo
```
git clone https://github.com/robertu/svg2pdfgen app
```

Instalacja virtualenv
```
cd app
python3 -m venv env
. env/bin/activate
pip3 install -r ./requirements.txt
```

Start

```
cd app/svg2pdfgenerator
. env/bin/activate
python3 manage.py createsuperuser
(Podaj nazwę użytkownika oraz hasło)
python3 manage.py runserver {port}
```
