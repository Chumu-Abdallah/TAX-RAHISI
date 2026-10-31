from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS = ['*']

# MySQL development kwa Tanzania
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='taxrahisi'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='Chumu@83'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# kwa matumizi ya PyMySQL badala ya mysqlclient, zachini ndo zinafaa
# import pymysql
# pymysql.install_as_MySQLdb()