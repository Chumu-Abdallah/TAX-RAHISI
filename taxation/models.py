import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings

class TaxType(models.TextChoices):
    VAT = 'VAT', 'VAT 18%'
    CORPORATE = 'CORP', 'Corporate Tax 30%'
    PRESUMPTIVE = 'PRES', 'Presumptive Tax'
    WITHHOLDING = 'WHT', 'Withholding Tax 5%'
    PAYE = 'PAYE', 'PEYE'
    SDL = 'SDL', 'SDL 4%'

class TaxRule(models.Model):
    """Sheria zzinazo badilika kila mwaka"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tax_type = models.CharField(max_length=10, choices=TaxType.choices, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="mf 18.00 kwa 18%")
    threshold_min = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    threshold_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    effective_form = models.DateField()
    deccription = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tax_type_display()} - {self.rate}%"

class TaxAssessment(models.Model):
    """kila hesabu ya kodi inahifadhiwa hapa kwaajili ya Audit ya TRA"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE)
    tax_type = models.CharField(max_length=10, choices=TaxType.choices)

    # Hesabu 
    taxable_amount = models.DecimalField(max_digits=14, decimal_places=2) #mauzo yalio tozwa
    tax_rate_used = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2)

    period_start = models.DateField()
    period_end = models.DateField()

    assessed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_by = models.DateTimeField(auto_now_add=True)

    # Immutablility kwa production
    is_lockesd = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['business', 'tax_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]