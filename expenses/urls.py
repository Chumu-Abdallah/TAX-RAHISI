from django.urls import path
from .views import ExpenseListCreateView, ExpenseSummaryView, expense_html_page

app_name = 'expenses'

urlpatterns = [
    path('api/', ExpenseListCreateView.as_view(), name='api-list'),
    path('api/summary/', ExpenseSummaryView.as_view(), name='api-summary'),
    path('', expense_html_page, name='list'),
    path('create/', expense_html_page, name='create'), # <- Tumia ile ile, hakuna haja ya view tofauti
    path('<uuid:pk>/', expense_html_page, name='detail'), # detail pia unaiona kwenye modal
]