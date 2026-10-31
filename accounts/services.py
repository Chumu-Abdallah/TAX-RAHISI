from django.utils import timezone
from datetime import timedelta
from .models import User

def normalize_phone_tz(phone):
    if not phone:
        return None
    p = str(phone).strip().replace(' ', '').replace('-', '')
    if p.startswith('+'):
        p = p[1:]
    if p.startswith('0'):
        p = '255' + p[1:]
    if not p.startswith('255'):
        if len(p) == 9 and p.isdigit():
            p = '255' + p
        else:
            # kama tayari ni 255...
            pass
    return '+' + p

def _get_user_any_format(phone):
    if not phone:
        return None
    norm = normalize_phone_tz(phone)
    if not norm:
        return None
    suffix = norm[-9:]

    # Tafuta wote wenye suffix hii - kipaumbele MKURUGENZI > ADMIN > OWNER
    qs = User.objects.filter(phone__endswith=suffix)
    if not qs.exists():
        return None

    # Order: MKURUGENZI first, then ADMIN, then active
    # Tunatumia python sorting kwa sababu role ni string
    users = list(qs)
    def priority(u):
        order = {'MKURUGENZI': 0, 'ADMIN': 1, 'OWNER': 2}
        return (order.get(u.role, 3), 0 if u.is_active else 1)

    users.sort(key=priority)
    return users[0] if users else None

def authenticate_user_tz(phone, password, request_ip=None):
    if not phone or not password:
        return None

    user_obj = _get_user_any_format(phone)
    if not user_obj:
        return None

    # Auto-unlock after 30 min
    if user_obj.is_locked and user_obj.last_failed_at:
        if timezone.now() > user_obj.last_failed_at + timedelta(minutes=30):
            user_obj.failed_attempts = 0
            user_obj.is_locked = False
            user_obj.last_failed_at = None
            user_obj.save(update_fields=['failed_attempts','is_locked','last_failed_at'])

    if user_obj.is_locked and user_obj.failed_attempts >= 5:
        if user_obj.last_failed_at and timezone.now() < user_obj.last_failed_at + timedelta(minutes=30):
            return None

    if not user_obj.check_password(password):
        try:
            user_obj.failed_attempts = (user_obj.failed_attempts or 0) + 1
            user_obj.last_failed_at = timezone.now()
            if user_obj.failed_attempts >= 5:
                user_obj.is_locked = True
            user_obj.save(update_fields=['failed_attempts','last_failed_at','is_locked'])
        except Exception:
            pass
        return None

    # Success
    try:
        user_obj.failed_attempts = 0
        user_obj.is_locked = False
        user_obj.last_failed_at = None
        user_obj.last_login = timezone.now()
        fields = ['failed_attempts','is_locked','last_failed_at','last_login']
        if request_ip and hasattr(user_obj, 'last_login_ip'):
            user_obj.last_login_ip = request_ip
            fields.append('last_login_ip')
        user_obj.save(update_fields=fields)
    except Exception:
        try:
            user_obj.save(update_fields=['last_login'])
        except Exception:
            pass

    return user_obj