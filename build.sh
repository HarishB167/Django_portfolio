#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install pipenv

pipenv install

pipenv run python manage.py collectstatic --no-input
pipenv run python manage.py migrate
# pipenv run python manage.py createsuperuser --noinput

script="
from django.contrib.auth.models import User;

username = '$DJANGO_SUPERUSER_USERNAME';
password = '$DJANGO_SUPERUSER_PASSWORD';
email = '$DJANGO_SUPERUSER_EMAIL';

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell
