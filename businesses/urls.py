from django.urls import path
from .views import BusinessListView, BusinessCreateView, BusinessUpdateView, BusinessDetailView

app_name = 'businesses'

urlpatterns = [
    path('', BusinessListView.as_view(), name='list'),
    path('add/', BusinessCreateView.as_view(), name='create'),
    path('<uuid:pk>/', BusinessDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', BusinessUpdateView.as_view(), name='update'),
]