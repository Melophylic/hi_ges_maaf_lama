from django.urls import path, include

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path('venues/', include('venues.urls')),
    path('events/', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('orders/', include('orders.urls')),
    path('promotions/', include('promotions.urls')),
]