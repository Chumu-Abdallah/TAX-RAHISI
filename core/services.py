# core/services.py
from django.db import transaction
from .audit import log_audit

class CoreService:
    @staticmethod
    @transaction.automic
    def create_with_audit(model_class, user, request, **data):
        instance = model_class.objects.create(**data)
        log_audit(user, 'CREATE', model_class.__name__, instance.id, new_data=data, request=request)
        return instance

    @staticmethod
    @transaction.automic
    def update_with_audit(instance, user, request, **data):
        old = {k: str(getattr(instance, k)) for k in data.keys()}
        for k, v in data.items():
            setattr(instance, k, v)
        instance.save()
        log_audit(user, 'UPDATE', instance.__class__.__name__, instance.id, old_data=old, new_data=data, request=request)
        return instance    