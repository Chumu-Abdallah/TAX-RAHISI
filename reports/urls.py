from django.urls import path
from .views import dashboard_report, compliance_report, download_tax_pdf, sales_vs_expenses_api

app_name = 'reports'

urlpatterns = [
    path('dashboard/<int:business_id>/', dashboard_report, name='dashboard'),
    path('compliance/', compliance_report, name='compliance'),
    path('download/<int:business_id>/', download_tax_pdf, name='download_pdf'),
    path('api/sales-expenses/<int:business_id>/', sales_vs_expenses_api, name='sales_vs_expenses_api'),
]