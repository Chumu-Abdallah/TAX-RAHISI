import random
from datetime import timedelta
from django.utils import timezone
from django.conf import Settings
from.models import Payment, PaymentLog, PaymentStatus

def generate_control_number():
    # Format Ya TRA GePG: 99XXXXXXXXXX.
    # kwa local test tuna genetrate Random
    return f"99{random.randint(1000000000, 9999999999)}"

def request_control_number(payment: Payment):
    """
    hapa ndipo una intagrate na GePG API ya serikali.
    kwa sasa ni mock - inafanya kazi bila Internet.
    """
    if payment.control_number:
        return payment

    # 1. Prepare Payload for GePG (mock)
    payload = {
        "taxpayer_tin": payment.taxpayer.tin,
        "amount": float(payment.amount),
        "tax_type": payment.tax_type,
    }

    # 2. Simulate GePG call
    control_number = generate_control_number()

    payment.control_number = control_number
    payment.status = PaymentStatus.ISSUED
    payment.expires_at = timezone.now() + timedelta(days=3)
    payment.gpg_request_id = f"GEPG-{random.randint(10000,99999)}"
    payment.save()

    PaymentLog.objects.create(
        payment=payment,
        action="CONTROL_NUMBER_ISSUED",
        response_date={
            "control_number": control_number, "payload": payload
        }
    )
    return payment

def verify_payment_status(payment: Payment):
    # Hii itaitwa na Cron au Callback kutoka GePG
    # Mock: kama kuna Receipt_number, mark as PAID 
    if payment.status == PaymentStatus.PAID:
        return payment
    # Kwa production, Hapa tunfanya GET kwa GePG API
    return payment

def handle_gepg_callback(control_number: str, receipt_number: str, amount: float):
    try:
        payment = Payment.objects.get(control_number=control_number)
        if float(payment.amount) == float(amount):
            payment.status=PaymentStatus.PAID
            payment.receipt_number = receipt_number
            payment.paid_at = timezone.now()
            payment.save()
            PaymentLog.objects.create(
                payment=payment,
                action="PAYMENT_CONFIRMED_CALLBACK",
                response_data={"receipt": receipt_number, "amount": amount}
            )
            return True
    except Payment.DoesNotExist:
        pass
    return False