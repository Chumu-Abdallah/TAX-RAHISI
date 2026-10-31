from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Sale
from .forms import SaleForm
from .services import get_monthly_sales_summary, bulk_import_sales
from businesses.models import Business

@login_required
def sales_list(request):
    business_id = request.GET.get('business')
    sales = Sale.objects.filter(created_by=request.user)
    if business_id:
        sales = sales.filter(business_id=business_id)
    paginator = Paginator(sales, 20)
    page = request.GET.get('page')
    sales_page = paginator.get_page(page)

    businesses = Business.objects.filter(taxpayer__user=request.user)
    return render(request, 'sales/list.html', {
        'sales': sales_page,  # <-- FIX: uliandika sales-page
        'businesses': businesses
    })

@login_required
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            sale.amount_incl_vat = form.cleaned_data['amount_incl_vat']
            sale.save()
            messages.success(request, f"Sale {sale.invoice_no} imehifadhiwa")
            return redirect('sales:list')
    else:  # <-- FIX: else ilikuwa ndani ya if
        form = SaleForm()
    return render(request, 'sales/form.html', {'form': form})

@login_required
def sale_import_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        # FIX: Lazy import ili isiangushe server yote kama DLL imeblockiwa
        try:
            import pandas as pd
        except ImportError as e:
            messages.error(request, f"Pandas haija-load (DLL blocked): {e}. Hamisha project nje ya OneDrive au install Visual C++ Redistributable")
            return redirect('sales:list')

        business = get_object_or_404(Business, id=request.POST.get('business'))
        file = request.FILES['excel_file']
        try:
            df = pd.read_excel(file)
            # Tarajia Columns: invoice_no, sale_date, amount_excl, vat
            data = df.to_dict('records')
            bulk_import_sales(business, data, request.user)
            messages.success(request, f"{len(data)} mauzo yameingizwa")
        except Exception as e:
            messages.error(request, f"Imeshindwa Kueka: {e}")
        return redirect('sales:list')

    businesses = Business.objects.filter(taxpayer__user=request.user)
    return render(request, 'sales/import.html', {'businesses': businesses})  # <-- FIX: ilikuwa {businesses} si dict

@login_required
def monthtly_summary_view(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    summary = get_monthly_sales_summary(business)
    return render(request, 'sales/summary.html', {
        'business': business,
        'summary': summary
    })