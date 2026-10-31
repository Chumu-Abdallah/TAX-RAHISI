from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from sales.models import Sale
from expenses.models import Expense
from payments.models import Payment
from taxation.models import TaxAssessment

def get_business_dashboard_data(business, tax_year=None):
    tax_year = tax_year or timezone.now().year

    sales_qs = Sale.objects.filter(business=business, sale_date__year=tax_year)
    expenses_qs = Expense.objects.filter(business=business, expense_date__year=tax_year)

    sales_total = sales_qs.aggregate(t=Sum('amount_incl_vat'))['t'] or 0
    expenses_total = expenses_qs.aggregate(t=Sum('amount'))['t'] or 0
    profit = sales_total - expenses_total

    # Tax
    assessments = TaxAssessment.objects.filter(business=business, tax_year=tax_year)
    tax_payable = assessments.aggregate(t=Sum('total_payable'))['t'] or 0
    tax_paid = Payment.objects.filter(
        taxpayer=business.taxpayer, tax_year=tax_year, status='PAID'
    ).aggregate(t=Sum('amount'))['t'] or 0

    # Monthly Breakdown kwa chart
    monthly = []
    for m in range(1, 13):
        m_sales = sales_qs.filter(sale_data__month=m).aggregate(t=Sum('amount_incl_vat'))['t'] or 0
        m_exp = expenses_qs.filter(expense_date__month=m).aggregate(t=Sum('amount'))['t'] or 0
        monthly.append({'monthly': m, 'sale': float(m_sales), 'expenses': float(m_exp)})

    return {
        'sales_total': sales_total,
        'expenses_total': expenses_total,
        'profit': profit,
        'tax_payable': tax_payable,
        'tax_paid': tax_paid,
        'tax_balance': tax_payable - tax_paid,
        'monthly': monthly,
        'profit_margin': (profit / sales_total * 100) if sales_total else 0
    } 

def get_tra_compliance_report(taxpayer):
    businesses = taxpayer.businesses.all()
    data = []
    for biz in businesses:
        dash = get_business_dashboard_data(biz)
        # Check VAT tyheshold 100M
        is_vat_required = dash['sales_total'] >= 100_000_000
        data.append({
            'business': biz,
            'turnover': dash['sales_total'],
            'is_vat_required': is_vat_required,
            'is_vat_compliant': biz.is_vat_registered if is_vat_required else True
        })
    return data       