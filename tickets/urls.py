from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "tickets"

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='tickets:ticket_category_list', permanent=False)),
    path('categories/', views.ticket_category_list, name='ticket_category_list'),
    path('categories/create/', views.ticket_category_create, name='ticket_category_create'),
    path('categories/<str:category_id>/edit/', views.ticket_category_edit, name='ticket_category_edit'),
    path('categories/<str:category_id>/delete/', views.ticket_category_delete, name='ticket_category_delete'),
    path('categories/partial/', views.ticket_category_partial, name='ticket_category_partial'),

    path('my-tickets/', views.ticket_list, name='ticket_list'),
    path('my-tickets/create/', views.ticket_create, name='ticket_create'),
    path('my-tickets/<str:ticket_id>/edit/', views.ticket_edit, name='ticket_edit'),
    path('my-tickets/<str:ticket_id>/delete/', views.ticket_delete, name='ticket_delete'),
    path('my-tickets/partial/', views.ticket_partial, name='ticket_partial'),
]