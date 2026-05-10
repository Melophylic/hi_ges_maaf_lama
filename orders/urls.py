from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('checkout/', views.checkout, name='checkout'),
    path('<str:order_id>/update/', views.order_update, name='order_update'),
    path('<str:order_id>/delete/', views.order_delete, name='order_delete'),
]