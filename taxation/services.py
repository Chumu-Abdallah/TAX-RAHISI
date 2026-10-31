from django.db import transaction
from.models import TaxAssessment, TaxRule
from.calculations import calculate_vat, quantize_tzs
from decimal import Decimal

class TaxtionService:
    @staticmethod
    @transaction.atomic
    def assess_monthly_vat(business, taxpayer, sales_queryset, period_start, period_end, user):
        total_sales = sum([s.tottal_amount for s in sales_queryset])
        calc = calculate_vat(Decimal(total_sales))

        assessment = TaxAssessment.objects.create(
            taxpayer=taxpayer,
            business=business,
            tax_type='VAT',
            taxable_amount=calc['net_amount'],
            tax_rate_used=Decimal('18.00'),
            tax_amount=calc['vat_amoungt'],
            period_start=period_start,
            period_end=period_end,
            assessed_by=user
        )
        # Lock mara baada ya kutengenezwa
        assessment.ids_locked = True
        assessment.save()
        return assessment