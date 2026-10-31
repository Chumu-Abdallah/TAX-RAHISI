from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_list, name='list'),
    path('create/', views.sale_create, name='create'),
    path('import/', views.sale_import_excel, name='import'),
    path('summary/<uuid:business_id>/', views.monthtly_summary_view, name='summary'),
]