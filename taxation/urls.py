from django.urls import path
from .views import TaxCalculatorView

app_name = 'taxation'

urlpatterns = [
    path('', TaxCalculatorView.as_view(), name='list'),  # niliongeza hii tu kwa ajili ya menu, inatumia view yako ile ile
    path('calculate/', TaxCalculatorView.as_view(), name='tax_calculate'),
    path('assess/', TaxCalculatorView.as_view(), name='tax_assess'),
]