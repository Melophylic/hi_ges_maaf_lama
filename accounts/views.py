from django.shortcuts import render, redirect
from core.auth import DUMMY_USERS, login_user, logout_user, login_required, get_current_user

def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = next(
            (u for u in DUMMY_USERS if u["username"] == username and u["password"] == password),
            None
        )

        if user:
            login_user(request, user)
            return redirect("accounts:dashboard")

        error = "Username atau password salah."

    return render(request, "accounts/login.html", {"error": error})

def logout_view(request):
    logout_user(request)
    return redirect("accounts:login")

def register_view(request):
    return render(request, "accounts/register.html")

def register_customer_view(request):
    if request.method == "POST":
        return redirect("accounts:login")
    return render(request, "accounts/register_customer.html")

def register_organizer_view(request):
    if request.method == "POST":
        return redirect("accounts:login")
    return render(request, "accounts/register_organizer.html")

@login_required
def dashboard_view(request):
    user = get_current_user(request)

    if user["role"] == "administrator":
        return render(request, "accounts/dashboard_admin.html", {"user": user})
    if user["role"] == "organizer":
        return render(request, "accounts/dashboard_organizer.html", {"user": user})

    return render(request, "accounts/dashboard_customer.html", {"user": user})

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": get_current_user(request)})

def register_admin_view(request):
    if request.method == "POST":
        return redirect("accounts:login")
    return render(request, "accounts/register_admin.html")