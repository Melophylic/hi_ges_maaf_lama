from functools import wraps
from django.shortcuts import redirect

DUMMY_USERS = [
    {
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa7",
        "username": "putri",
        "password": "lastname",
        "role": "administrator",
        "name": "Putri",
        "email": "admin@tiktaktuk.com",
        "phone": "-",
    },

    # ORGANIZER
    {
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2",
        "username": "nadzim",
        "password": "programmerhandal",
        "role": "organizer",
        "name": "PT Nada Penuh Cerita",
        "email": "hello@nadapenuhcerta.com",
        "phone": "08122222222",
        "organizer_id": "40000000-0000-0000-0000-000000000001",
    },
    {
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6",
        "username": "gilangbiru",
        "password": "bluespax",
        "role": "organizer",
        "name": "Sunset Wave Organizer",
        "email": "contact@sunsetwave.id",
        "phone": "08166666666",
        "organizer_id": "40000000-0000-0000-0000-000000000002",
    },

    # CUSTOMER
    {
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
        "username": "syafiq",
        "password": "panjangpanjangin",
        "role": "customer",
        "name": "Syafiq Faqih",
        "email": "syafiq@example.com",
        "phone": "08123456789",
        "customer_id": "dddddddd-dddd-dddd-dddd-ddddddddddd1",
    },
    {
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3",
        "username": "elizabeth",
        "password": "artisdepok",
        "role": "customer",
        "name": "Elizabeth Meilanny",
        "email": "elizabeth@example.com",
        "phone": "08133333333",
        "customer_id": "dddddddd-dddd-dddd-dddd-ddddddddddd3",
    },
]

def login_user(request, user):
    request.session["user"] = user

def logout_user(request):
    request.session.flush()

def get_current_user(request):
    return request.session.get("user")

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_current_user(request):
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return wrapper


def has_role(request, *roles):
    user = get_current_user(request)
    if not user:
        return False
    return user.get("role") in roles


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not get_current_user(request):
                return redirect("accounts:login")
            if not has_role(request, *roles):
                return redirect("accounts:login")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator