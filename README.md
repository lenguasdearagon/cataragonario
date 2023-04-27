# CatAragonario
Diccionario dialectal del catalán de Aragón

Project based on Aragonario dictionary (linguatec-lexicon).

## API REST reference
You can check the linguatec-lexicon API reference on [Swagger Hub](https://app.swaggerhub.com/apis-docs/ribaguifi/linguatec-lexicon). If you find any issue or you want to use another service to see the schema, you can find a local copy on [docs/api-schema.yml](docs/api-schema.yml)

## Development installation

Get the app code:
```bash
git clone https://github.com/lenguasdearagon/cataragonario.git
```

Create devel project site
```bash
apt-get install --no-install-recommends python3-pip
pip3 install virtualenv

# create virtualenv and install requirements (included Django)
virtualenv env
source env/bin/activate
pip3 install -r cataragonario/requirements.txt

# add app source code as python site-package
# checking that has been linked properly
pip3 install -e cataragonario/
python -c "import cataragonario; print(cataragonario.get_version())"

# create a project (name it as you want!) & add cataragonario to INSTALLED_APPS
django-admin startproject mysite
```

Run migrations, start development server and go to http://127.0.0.1:8000/api/
```bash
cd mysite
python manage.py migrate
python manage.py runserver
```

You got it! Let's start creating magical code!


### Postgres database using docker
Start postgres using docker
```sh
POSTGRES_DB='cataragonario'
POSTGRES_USER='lenguasdearagon'
POSTGRES_PASSWORD='verys3cr3tp@as$'
POSTGRES__HOST='localhost'
POSTGRES_PORT=5432

docker run --name cataragonario -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_DB=$POSTGRES_DB -p $POSTGRES_PORT:$POSTGRES_PORT -d postgres
```

## Deployment using uwsgi
```sh
git clone git@github.com:lenguasdearagon/cataragonario.git
cd cataragonario

# create virtual environment
python3 -m venv env
. env/bin/activate

# install dependencies
pip install wheel
pip install -r aralan/requirements.txt
pip install -r env/src/linguatec-lexicon/requirements.txt

# install uwsgi (suit your taste: e.g. gunicorn)
pip install uwsgi
```
