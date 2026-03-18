python 3.11.9

# setup
## activate venv
socio_venv\Scripts\activate
cd uml_experiment

## install requirements
pip install -r requirements.txt

## create database 
CREATE DATABASE uml_experiment_db;

## run migrate
python manage.py makemigrations
python manage.py migrate

## sample data
python generate_sample_data.py

### admin
user name:admin
password :admin123
### user
user name :participant1 to participant20
password:password123

## run server
python manage.py runserver
