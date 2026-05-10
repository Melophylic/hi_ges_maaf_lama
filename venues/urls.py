from django.urls import path
from . import views
app_name = "venues"

app_name = 'venues'

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('create/', views.venue_create, name='venue_create'),
    path('<str:venue_id>/edit/', views.venue_edit, name='venue_edit'),
    path('<str:venue_id>/delete/', views.venue_delete, name='venue_delete'),
    path('partial/', views.venue_partial, name='venue_partial'),
    path('seats/', views.seat_list, name='seat_list'),
    path('seats/create/', views.seat_create, name='seat_create'),
    path('seats/<str:seat_id>/edit/', views.seat_edit, name='seat_edit'),
    path('seats/<str:seat_id>/delete/', views.seat_delete, name='seat_delete'),
    path('seats/partial/', views.seat_partial, name='seat_partial'),
]
