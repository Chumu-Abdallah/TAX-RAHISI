import uuid
from django.db import models
from django.conf import settings

class PaymentMethod(models.TextChoices):
    MOBILE_MONEY = 'MOBILE', 'Mobile Money (M-Pesa / TigoPesa/Airtel)'
    BANK = 'BANK', 'Bank Transfer'
    CASH = 'CASH', 'Cash - TRA Office'

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Inasubiri'
    ISSUED = 'ISSUED', 'Inasubiri Control Number'
    PAID = 'PAID', 'Imelipwa'
    FAILED = 'FAILED', 'Imeshindwa'
    EXPIRED = 'EXPIRED', 'Ime-expire'

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    taxpayer = models.ForeignKey('taxpayers.Taxpayer', on_delete=models.PROTECT, null=True, blank=True, related_name='payments')
    assessment = models.ForeignKey('taxation.TaxAssessment', on_delete=models.PROTECT, null=True, blank=True, related_name='payments')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_type = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MOBILE_MONEY)

    control_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    methode = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.MOBILE_MONEY)

    phone_number = models.CharField(max_length=15, help_text="255 xxx xxx xxx")
    gap_request_id = models.CharField(max_length=100, null=True, blank=True)
    receipt_number = models.CharField(max_length=100, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.control_number or 'NO-CN'} - {self.amount} TZS - {self.status}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['control_number']), 
            models.Index(fields=['taxpayer'])
        ]

class PaymentLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    response_date = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)