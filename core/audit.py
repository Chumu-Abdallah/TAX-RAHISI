# core/audit.py
import json
from .models import AuditLog
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.__audit_old_data = None

    def process_response(self, request, response):
        # log only important methode
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and hasattr(request, 'user') and request.user.is_authenticate:
            if response.status_code < 400:
                # Hii ina kamata na signal kwenye servise
                pass
            return response

    def log_audit(user, action, model_name, object_id, old_data=None, new_data=None, request=None):
        ip = None
        if request:
            client_ip, _ = get_client_ip(request)
            ip = client_ip

        AuditLog.objects.create(
            user=user if user.is_authentcated else None,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            old_data=old_data,
            new_data=new_data,
            ip_address=ip
        )    