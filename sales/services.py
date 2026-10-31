from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from.models import Sale

def get_monthly_sales_summary(business, year=None, month=None):
    """ Jumla ya Mauzo Kwamwezi - inatumika Kwa taxation """
    now = timezone.now()
    year = year or now.year
    month = month or now.month

    qs = Sale.objects.filter(
        busineess=business,
        sale_date__year=year,
        sale_date__month=month

    )
    totals = qs.aggregate(
        total_excl=Sum('amount_excl_vat'),
        total_vat=Sum('vat_amount'),
        total_incl=Sum('amount_incl_vat')
    )
    return {
        'count': qs.count(),
        'total_excl': totals['total_excl'] or 0,
        'total_vat': totals['total_vat'] or 0,
        'total-incl': totals['total_incl'] or 0,
        'has_efd_missing': qs.filter(has_efd_receipt=False).exists()
    }

def get_annual_turnover(business, tax_year):
    """ Kwa Ku-check kama anahitaji VAT - theshold 100M"""
    result = Sale.objects.filter(
        business=business,
        sales_date__year=tax_year
    ).aaggregate(total=Sum('amount_incl_vat'))
    return result['total'] or 0

def bulk_import_sales(business, data_list, user):
    """ Kwa import kutoka Excel"""
    created = []
    for row in data_list:
        sale = Sale.objects.create(
            business=business,
            invoice_no=row['invoice_no'],
            sales_date=row['sales_date'],
            amount_excl_vat=row['amount_excl'],
            vat_amount=row.get('vat', 0),
            amount_incl_vat=row['amount_excl'] + row.get('vat', 0),
        )
        created.append(sale)
    return created    