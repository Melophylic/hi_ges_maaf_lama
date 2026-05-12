from functools import wraps
from django.shortcuts import redirect
from core.db import fetch_one


def authenticate_user(username, password):
    user = fetch_one("""
        SELECT ua.user_id, ua.username, r.role_name AS role
        FROM USER_ACCOUNT ua
        JOIN ACCOUNT_ROLE ar ON ua.user_id = ar.user_id
        JOIN ROLE r ON ar.role_id = r.role_id
        WHERE LOWER(ua.username) = LOWER(%s) AND ua.password = %s
        LIMIT 1
    """, [username, password])

    if not user:
        return None

    if user['role'] == 'customer':
        extra = fetch_one(
            "SELECT customer_id, full_name AS name, phone_number FROM CUSTOMER WHERE user_id = %s",
            [user['user_id']]
        )
        if extra:
            user.update(extra)
    elif user['role'] == 'organizer':
        extra = fetch_one(
            "SELECT organizer_id, organizer_name AS name, contact_email FROM ORGANIZER WHERE user_id = %s",
            [user['user_id']]
        )
        if extra:
            user.update(extra)
    else:
        user['name'] = user['username']

    return user


def login_user(request, user):
    safe_user = user.copy()

    if 'user_id' in safe_user:
        safe_user['user_id'] = str(safe_user['user_id'])

    if 'customer_id' in safe_user:
        safe_user['customer_id'] = str(safe_user['customer_id'])

    if 'organizer_id' in safe_user:
        safe_user['organizer_id'] = str(safe_user['organizer_id'])

    request.session['user'] = safe_user


def logout_user(request):
    request.session.flush()


def get_current_user(request):
    return request.session.get('user')


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_current_user(request):
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def has_role(request, *roles):
    user = get_current_user(request)
    if not user:
        return False
    return user.get('role') in roles


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not get_current_user(request):
                return redirect('accounts:login')
            if not has_role(request, *roles):
                return redirect('accounts:login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
