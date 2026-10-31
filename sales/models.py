import uuid
from django.db import models
from django.conf import settings

class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='sales')

    invoice_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_tin = models.CharField(max_length=20, blank=True)

    sale_date = models.DateField()
    amount_excl_vat = models.DecimalField(max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_incl_vat = models.DecimalField(max_digits=12, decimal_places=2)

    has_efd_receipt = models.BooleanField(default=True)
    efd_receipt_no = models.CharField(max_length=100, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date']
        indexes = [models.Index(fields=['business', 'sale_date'])]

    def __str__(self):
        return f"{self.invoice_no} - {self.amount_incl_vat}"

    def save(self, *args, **kwargs):
        # Auto-calc kama VAT haijawekwa
        if not self.amount_incl_vat:
            self.amount_incl_vat = self.amount_excl_vat + self.vat_amount
        super().save(*args, **kwargs)