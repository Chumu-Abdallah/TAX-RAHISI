from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='accounts/login.html'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # Alias tu ya API ili JS yako ya zamani isife
    path('api/accounts/', include(('accounts.urls', 'accounts'), namespace='api_accounts')),
    
    path('businesses/', include(('businesses.urls', 'businesses'), namespace='businesses')),
    path('taxpayers/', include(('taxpayers.urls', 'taxpayers'), namespace='taxpayers')),
    path('taxation/', include(('taxation.urls', 'taxation'), namespace='taxation')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
    path('sales/', include(('sales.urls', 'sales'), namespace='sales')),
    path('expenses/', include(('expenses.urls', 'expenses'), namespace='expenses')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "TAX-RAHISI Admin" 
admin.site.site_title = "TAX-RAHISI"  
admin.site.index_title = "Mfumo wa Kodi Tanzania"