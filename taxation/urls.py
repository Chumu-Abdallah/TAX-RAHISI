from django.urls import path
from .views import TaxCalculatorView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TaxAssessment

@login_required
def taxation_list_view(request):
    assessments = TaxAssessment.objects.select_related('business').order_by('-created_by')[:30]
    return render(request, 'taxation/list.html', {'assessments': assessments})

app_name = 'taxation'

urlpatterns = [
    path('', taxation_list_view, name='list'),  # Hii ndio inaondoa error 405
    path('calculate/', TaxCalculatorView.as_view(), name='tax_calculate'),
    path('assess/', TaxCalculatorView.as_view(), name='tax_assess'),
    path('api/calculate/', TaxCalculatorView.as_view(), name='api-calculate'),
]