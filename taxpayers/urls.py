from django.urls import path
from .views import (
    TaxpayerCreateView, TaxpayerDetailView, 
    TaxpayerVerifyView, TaxpayerRejectView, 
    TaxpayerDeleteView, TaxpayerListView
)

app_name = 'taxpayers'

urlpatterns = [
    path('', TaxpayerListView.as_view(), name='list'),
    path('register/', TaxpayerCreateView.as_view(), name='taxpayer-register'),
    path('me/', TaxpayerDetailView.as_view(), name='taxpayer-me'),
    path('<uuid:pk>/', TaxpayerDetailView.as_view(), name='taxpayer-detail'),
    path('<uuid:pk>/verify/', TaxpayerVerifyView.as_view(), name='taxpayer-verify'),
    path('<uuid:pk>/reject/', TaxpayerRejectView.as_view(), name='taxpayer-reject'),
    path('<uuid:pk>/delete/', TaxpayerDeleteView.as_view(), name='taxpayer-delete'),
]