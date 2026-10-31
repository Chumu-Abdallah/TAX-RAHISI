from django.conf import Settings
from django.core.mail import send_mail
from django.utils import timezone
import requests
import logging
from.models import Nottification, NotificationChannel

logger = logging.getLogger(__name__)

def create_notification(recipient, type, title, message, channel=NotificationChannel.IN_APP, related_id=None):
    """ Hii ndio function kuu inayotumika kila mahali kwenye System """
    notif = Nottification.objects.create(
        recipient=recipient,
        type=type,
        title=title,
        message=message,
        channel=channel,
        related_object_id=str(related_id) if related_id else None
    )
    # Tuma mara moja kama ni IN_APP, kama ni SMS/EMAIL tuma via Celery
    if channel == NotificationChannel.IN_APP:
        notif.is_sent = True
        notif.sent_at = timezone.now()
        notif.save()
    else:
        # Ita task
        from .tasks import send_external_notification
        send_external_notification.delay(str(notif.id))
    return notif 

def send_sms_beem(phone_number, message):
    """
    Intergration na Beem Africa au NextSMS - provider wa Tanzania
    """
    if not api_key:
        locals.warning("BEEM_API_KEY  missing, using mock")
        return {"status": "sent", "id": "MOCK-ID"}
    try:
        url = "https://apisms.beem.afrika/v1/send"
        payload = {
            "source_addr": "TAX-RAHISI",
            "schedule_time": "",
            "encoding": 0,
            "message": message,
            "recipients": [{"recipient_id": 1, "dest_addr": phone_number}]
        }
        response = requests.post(url, json=payload, auth=(api_key, secrat_key), timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"SMS Failed: {e}")
        return {"status": "failed", "error": str(e)}

def send_email_notification(notification: Nottification):
    try:
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=Settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False

# Helper Shotcuts kwa ajili ya modules zingine
def notify_payment_success(user, payment):
    return create_notification(
        recipient=user,
        type='PAYMENT_OK',
        channel=NotificationChannel.SMS,
        title='Malipo Yamepokelewa',
        message=f'Hongera! Malipo ya TZS {payment.amount} kwa Control No. {payment.control_number} Yamefanikiwa. Risiti: {payment.receipt_number}',
        related_id=payment.id
    ) 

def notify_tax_deadline(user, assessment):
    return create_notification(
        recipient=user,
        type='DEADLINE',
        channel=NotificationChannel.IN_APP,
        title='Deadline ya kodi inakaribia',
        message=f'Kodi yako ya {assessment.tax_type} TZS {assessment.total_payable} inadaiwa tarehe {assessment.due_date}. Lipa sasa Kuepuka Faini.',
        related_id=assessment.id
    )    