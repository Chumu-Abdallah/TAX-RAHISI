from decouple import config
if config('DJANGO_ENV', default='development') == 'production':
    from .production import *
else:
    from .development import *    