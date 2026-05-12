from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/events/', permanent=False)),
    path("accounts/", include("accounts.urls")),
    path('venues/', include('venues.urls')),
    path('events/', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('orders/', include('orders.urls')),
    path('promotions/', include('promotions.urls')),
]