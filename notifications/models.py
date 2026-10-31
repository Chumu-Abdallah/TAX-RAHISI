import uuid
from django.db import models
from django.conf import settings

class NotificationChannel(models.TextChoices):
    SMS = 'SMS', 'SMS / (Beem / NextSMS)'
    EMAIL = 'EMAIL', 'Email'
    IN_APP = 'IN_APP', 'In_App Dashboad'

class NotificationType(models.TextChoices):
    TAX_DUE_REMAINDER = 'TAX_DUE', 'Ukumbusho wa Kodi'
    PAIMENT_SUCCESS = 'PAYMENT_OK', 'Malipo Yamefanikiwa'
    CONTROL_NUMBER = 'CONTROL_NO', 'Control NaUmber'
    DEADLINE_ALERT = 'DEADLINE', 'Deadline Inakaribia'
    SYSTEM = 'SYSTEM', 'Taafifa ya Mfumo'

class Nottification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    type = models.CharField(max_length=20, choices=NotificationType.choices)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)

    title = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Kwa ajili ya retry na logging
    extanal_id = models.CharField(max_length=100, null=True, blank=True) #ID kutokaBeem
    failure_reason = models.TextField(null=True, blank=True)
    related_object_id = models.CharField(max_length=100, null=True, blank=True) # mfano paiment_id 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient} - {self.title} [{self.channel}]"

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read'])]