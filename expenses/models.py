import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings

class ExpenseCategory(models.TextChoices):
    RENT = 'RENT', 'Kodi ya Pango'
    SALARY = 'SALARY', 'Mishahara'
    FUEL = 'FUEL', 'Mafuta / Umeme / Usafiri'
    OFFICE = 'OFFICE', 'Vifaa Vya Ofisini'
    MARKETING = 'MARKE', 'Masoko'
    UTILITIES = 'UTIL', 'Leseni / TRA'
    REPAIR = 'REPAIR', 'Matengenezo'
    BANK = 'BANK', 'Tozo za Bank'
    # Hizi hazikubaliki na TRA
    FINE = 'FINE', 'Faini / Adhabu - haikubaliki'
    DONATION = 'DON', 'Msaada Binafsi - Haikubaliki'

# TRA inasema hizi hazipuguzwi kwenye faida
NON_DEDUCTIBLE = ['FINE', 'DON', 'PERSONAL']

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='expenses')
    taxpayer = models.ForeignKey('taxpayers.Taxpayer', on_delete=models.CASCADE, related_name='expenses')

    category = models.CharField(max_length=20, choices=ExpenseCategory.choices)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)

    # TAX Comliance
    is_deductible = models.BooleanField(default=True, help_text="TRA Inaruhusu Kupunguza Kwenye Faida?")
    receipt_number = models.CharField(max_length=100, blank=True)
    receipt_file = models.FileField(upload_to='expenses/receipts/%Y/%m/', null=True, blank=True)
    supplier_tin = models.CharField(max_length=10, blank=True, help_text="TIN ya muuzaji Kwa VAT claim")

    expense_date = models.DateField()

    # Audit
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=False)
    is_loked = models.BooleanField(default=False) # Baada ya kufunga mwezi haihaririki
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['business', 'expense_date']),
            models.Index(fields=['category']),
            models.Index(fields=['is_deductible']),
        ]
    def save(self, *args, **kwargs):
        #auto_logigc ya TRA
        if self.category in NON_DEDUCTIBLE:
            self.is_deductible = False
        self.total_amount = self.amount + self.vat_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.total_amount} TZS"