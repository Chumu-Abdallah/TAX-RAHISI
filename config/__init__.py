#config/__init__.py Kwa Celery to

from .celery import app as celery_app
__all__ = ('celery_app',)