from srumban.settings.base import *;
from srumban.settings.secret_config import *;

DEBUG = False

ALLOWED_HOSTS = [
    '*',
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_DATABASE,
	    'USER': DB_USER,
	    'PASSWORD': DB_PASSWORD,
	    'HOST': 'localhost',
	    'PORT': '',
    }
}