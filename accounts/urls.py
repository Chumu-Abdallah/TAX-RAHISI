from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView, LoginView, PendingUsersView, ApproveUserView, RejectUserView, 
    CreateAdminView, ApprovedUsersView, DeleteApprovedUserView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    
    # PENDING
    path('pending/', PendingUsersView.as_view(), name='pending_users'),
    path('approve/<uuid:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    path('reject/<uuid:user_id>/', RejectUserView.as_view(), name='reject_user'),

    # ALIAS kwa taxpayers.html ili isilete NoReverseMatch
    path('approve-user/<uuid:user_id>/', ApproveUserView.as_view(), name='approve-user'),
    path('reject-user/<uuid:user_id>/', RejectUserView.as_view(), name='reject-user'),

    # APPROVED - hii ndio yako ya sasa
    path('approved/', ApprovedUsersView.as_view(), name='approved'),
    path('delete/<uuid:user_id>/', DeleteApprovedUserView.as_view(), name='delete_approved_user'),

    # Mkurugenzi only
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
]