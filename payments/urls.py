from django.urls import path
from. import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('create/<uuid:assessment_id>/', views.create_payment_for_assessment, name='create'),
    path('<uuid:payment_id>/', views.payment_detail, name='detail'),
    # Callback - usiweke login_required
    path('api/callback/gepg/', views.gpg_callback_view, name='gepg-callback'),
]