from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from .models import Expense 
import logging

logger = logging.getLogger(__name__)

class ExpenseService:
    @staticmethod
    @transaction.atomic
    def create_expense(business, taxpayer, user, validate_data):
        expense = Expense.objects.create(
            business=business,
            taxpayer=taxpayer,
            created_by=user,
            **validate_data
        )
        logger.info(f"Expense {expense.id} created for {business.business_name}")
        return expense

    @staticmethod
    def get_monthly_summary(business, year, month):
        qs = Expense.objects.filter(
            business=business,
            expense_date__year=year,
            expense_date__month=month,
            is_approved=True
        )
        total = qs.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        deductible = qs.filter(is_deductible=True).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        non_deductible = total - deductible
        vat_claimable = qs.filter(is_deductible=True).aggregate(Sum('vat_amount'))['vat_amount__sum'] or Decimal('0')

        return {
            'total_expense': total,
            'deductible': deductible,
            'non_deductible': non_deductible,
            'vat_claimable': vat_claimable,
            'count': qs.count()
        }

    @staticmethod
    def calculation_profit(sales_total: Decimal, deductible_expense: Decimal) -> Decimal:
        profit = sales_total - deductible_expense
        return profit if profit > 0 else Decimal('0.00')