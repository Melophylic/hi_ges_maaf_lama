from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("register/customer/", views.register_customer_view, name="register_customer"),
    path("register/organizer/", views.register_organizer_view, name="register_organizer"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("register/admin/", views.register_admin_view, name="register_admin"),
]