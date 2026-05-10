from django.urls import path
from . import views

app_name = "promotions"

urlpatterns = [
    path('', views.promotion_list, name='promotion_list'),
    path('create/', views.promotion_create, name='promotion_create'),
    path('<str:promotion_id>/update/', views.promotion_update, name='promotion_update'),
    path('<str:promotion_id>/delete/', views.promotion_delete, name='promotion_delete'),
]