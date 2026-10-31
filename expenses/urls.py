from django.urls import path
from .views import ExpenseListCreateView, ExpenseSummaryView

app_name = 'expenses'

urlpatterns = [
    path('', ExpenseListCreateView.as_view(), name='list'),
    path('summary/', ExpenseSummaryView.as_view(), name='summary'),
    
    # HTML Views - kwa ajili ya form.html na detail.html
    path('create/', ExpenseListCreateView.as_view(), name='create'),
    path('<uuid:pk>/', ExpenseListCreateView.as_view(), name='detail'),
]