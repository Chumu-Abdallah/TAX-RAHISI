import uuid
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class TaxpayerType(models.TextChoices):
    INDIVIDUAL = 'IND', 'Mtu binafsi'
    SOLE = 'SOLE', 'Biashara Ndogo'
    COMPANY = 'LTD', 'Kampuni (LTD)'
    PARTNERSHIP = 'PART', 'Ubia'
    NGO = 'NGO', 'Asasi'

class VerificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Inasubiri'
    VERIFIED = 'VERIFIED', 'Imethobitishwa'
    REJECTED  = 'REJECTED', 'Imekataliwa'

class Taxpayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='taxpayer_profile')

    # utambulisho wa kitaifa 
    tin_validator = RegexValidator(r'^\d{9,10}$', 'TIN Lazima iwe 9 au 10 digits')
    tin_number = models.CharField(max_length=10, unique=True, validators=[tin_validator], verbose_name="TIN")

    nida_number = models.CharField(max_length=20, unique=True, verbose_name="NIDA")
    taxpayer_type = models.CharField(max_length=10, choices=TaxpayerType.choices, default=TaxpayerType.INDIVIDUAL)

    # Majina
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200, blank=True, help_text="Kama ni Kampuni au Sole Proprietor")

    # Location TRA
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    ward = models.CharField(max_length=50, blank=True)

    # Status 
    verification_status = models.CharField(max_length=10, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    is_vat_registered = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=20, blank=True, null=True)

    # Audit
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['tin_number']),
            models.Index(fields=['nida_number']),
            models.Index(fields=['region']),
        ] 

    def __str__(self):
        return f"{self.business_name or self.first_name} - {self.tin_number}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()