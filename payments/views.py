from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Payment
from .services import request_control_number, handle_gepg_callback
from taxation.models import TaxAssessment

@login_required
def payment_list(request):
    # Hii ndio ilikua inakupa 0 - uliandika 'payment' badala ya 'payments'
    if request.user.is_staff:
        payments = Payment.objects.all().order_by('-created_at')
    else:
        payments = Payment.objects.filter(taxpayer__user=request.user).order_by('-created_at')
    return render(request, 'payments/list.html', {'payments': payments})

@login_required
def create_payment_for_assessment(request, assessment_id):
    assessment = get_object_or_404(TaxAssessment, id=assessment_id)

    if request.method == 'POST':
        phone = request.POST.get('phone_number') # FIX: uliandika phone_numbre
        method = request.POST.get('method', 'MOBILE')

        payment = Payment.objects.create(
            taxpayer=assessment.business.taxpayer,
            assessment=assessment,
            amount=assessment.total_payable, # FIX: amoun
            tax_type=assessment.tax_type,
            tax_year=assessment.tax_year,
            phone_number=phone,
            method=method,
            created_by=request.user
        )
        # Omba Control Number
        payment = request_control_number(payment)
        messages.success(request, f"Control Number: {payment.control_number} - Lipa Ndani Ya Siku 3") # FIX
        return redirect('payments:detail', payment_id=payment.id) # FIX: detai

    return render(request, 'payments/create.html', {'assessment': assessment})

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id) # FIX: payment-id
    return render(request, 'payments/detail.html', {'payment': payment}) # FIX: return request

@csrf_exempt
def gpg_callback_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        control_no = data.get('control_number')
        receipt = data.get('receipt_number') # FIX: receipt-number
        amount = data.get('amount')
        ok = handle_gepg_callback(control_no, receipt, amount)
        return JsonResponse({"status": "ok" if ok else "not-found"})
    return JsonResponse({"error": "Invalid method"}, status=405)