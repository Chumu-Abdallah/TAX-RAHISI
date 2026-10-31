from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.utils import timezone
from businesses.models import Business
from.services import get_business_dashboard_data, get_tra_compliance_report
from.pdf import generate_tax_summary_pdf

@login_required
def dashboard_report(request, business_id):
    business = get_object_or_404(Business, id=business_id, taxpayer__user=request.user)
    tax_year = int(request.GET.get9('year', timezone.now().year))

    data = get_business_dashboard_data(business, tax_year)
    return render(request, 'reports/dashboard.html', {
        'business': business,
        'data': data,
        'tax_year': tax_year,
        'monthly_chart_data': data['monthly'] #kwa Chart.js
    })

@login_required
def compliance_report(request):
    taxpayer = request.user.taxpayer_profile
    report = get_tra_compliance_report(taxpayer)
    return render(request, 'reports/compliance.html', {'report': report})

@login_required
def download_tax_pdf(request, business_id):
    business = get_object_or_404(Business, id=business_id, taxpayer__user=request.user)
    tax_year = int(request.GET.get('year', timezone.now().year))
    data = get_business_dashboard_data(business, tax_year)

    pdf_buffer = generate_tax_summary_pdf(business, data, tax_year)
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"TAX-RAHISI-{business.business_name}-{tax_year}.pdf"
    )

@login_required
def sales_vs_expenses_api(request, business_id):
    # Kwa Chart.js AJAX
    from django.http import JsonResponse
    business = get_object_or_404(Business, id=business_id)
    data= get_business_dashboard_data(business)
    return JsonResponse(data['monthly'], safe=False)