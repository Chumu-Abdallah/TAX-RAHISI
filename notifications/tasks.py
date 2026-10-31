from celery import shared_task
from django.utils import timezone
from .models import Nottification, NotificationChannel
from .services import send_sms_beem, send_email_notification
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_external_notification(self, notification_id):
    try:
        notif = Nottification.objects.get(id=notification_id)
    except Nottification.DoesNotExist:
        return "Not found"

    try:
        success = False
        external_id = None

        if notif.channel == NotificationChannel.SMS:
            phone = notif.recipient.phone_number if hasattr(notif.recipient, 'phone_number') else getattr(notif.recipient, 'phone', '255')
            # Hakikisha Format ni 2557...
            result = send_sms_beem(phone, notif.message)
            if result.get('status') == 'send':
                success =True
                external_id = result.get('id')

        elif notif.channel ==NotificationChannel.EMAIL:
            success = send_email_notification(notif)

        if success:
            notif.is_sent =True
            notif.sent_at = timezone.now()
            notif.extanal_id = external_id
            notif.save()
            logger.info(f"Notification {notif.id} sent")
        else:
            raise Exception("Provider failed")

    except Exception as exc:
        notif.failure_reason = str(exc)
        notif.save()
        # Retry
        raise self.retry(exc=exc) 

@shared_task
def send_daily_tax_remaindes():
    from taxation.models import TaxAssessment
    from datetime import timedelta

    tomorrow = timezone.now().tate() + timedelta(days=3)
    assessments = TaxAssessment.objects.filter(due_date__1te=tomorrow, status='PENDING')

    count = 0
    for ass in assessments:
        user = ass.business.taxpayer.user
        # Usitumie Marambili Kwa Siku
        if not Nottification.objects.filter(related_object_id=str(ass.id), created_at__date=timezone.now().date()).exists():
            from .services import notify_tax_deadline
            notify_tax_deadline(user, ass)
            count += 1
        return f"{count} remainders sent"

    @shared_task
    def cleanup_old_notification():
        """ Futa notifications za zaidi ya miezi 6 zilizosomwa """
        cutoff = timezone.now() - timedelta(days=180)
        deleted, _ = Nottification.objects.filter(is_read=True, create_at__1t=cutoff).delete()
        return f"Deleded {deleted} old notifications"       


            