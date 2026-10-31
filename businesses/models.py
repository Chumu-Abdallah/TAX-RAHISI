import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings

class BusinessType(models.TextChoices):
    RETAIL = 'RETAIL', 'Rejareja'
    WHOLESALE = 'WHILESALE', 'Jumla'
    SERVICES = 'SERVICER', 'Huduma'
    MANUFACTURING = 'MANUFACTURING', 'Viwanda'
    OTHER = 'OTHER', 'Nyingine'

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    taxpayer = models.ForeignKey('taxpayers.Taxpayer', on_delete=models.CASCADE, related_name='businesses')
    business_name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True)
    brela_reg_no = models.CharField(max_length=50, unique=True)
    tin = models.CharField(max_length=20, blank=True)
    business_type = models.CharField(max_length=20, choices=BusinessType.choices, default=BusinessType.RETAIL)

    # Location - Tanzania
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100, blank=True)

    # TRA Compliance
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_vat_registered = models.BooleanField(default=True)
    vat_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="VAT Number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    VAT_THRESHOLD = Decimal('100000000.00') # 100M TZS

    class Meta:
        verbose_name_plural = "Businesses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} - {self.brela_reg_no}"

    @property
    def is_vat_eligible(self):
        return self.annual_turnover >= self.VAT_THRESHOLD

    def save(self, *args, **kwargs):
        if self.is_vat_eligible and not self.is_vat_registered:
            # auto flag for TRA review, usi auto register
            pass
        super().save(*args, **kwargs)  
