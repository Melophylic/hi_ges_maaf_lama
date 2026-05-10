from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('partial/', views.event_partial, name='event_partial'),
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/create/', views.artist_create, name='artist_create'),
    path('artists/partial/', views.artist_partial, name='artist_partial'),
    path('artists/<str:artist_id>/edit/', views.artist_edit, name='artist_edit'),
    path('artists/<str:artist_id>/delete/', views.artist_delete, name='artist_delete'),
    path('<str:event_id>/edit/', views.event_edit, name='event_edit'),
    path('<str:event_id>/', views.event_detail, name='event_detail'),
]
