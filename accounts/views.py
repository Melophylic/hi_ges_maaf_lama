import uuid
from django.shortcuts import render, redirect
from django.db import DatabaseError, transaction
from core.auth import authenticate_user, login_user, logout_user, login_required, get_current_user
from core.db import execute_query

CUSTOMER_ROLE_ID  = '00000000-0000-0000-0000-000000000103'
ORGANIZER_ROLE_ID = '00000000-0000-0000-0000-000000000102'
ADMIN_ROLE_ID     = '00000000-0000-0000-0000-000000000101'


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate_user(username, password)
        if user:
            login_user(request, user)
            return redirect('accounts:dashboard')
        error = 'Username atau password salah.'
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    logout_user(request)
    return redirect('accounts:login')


def register_view(request):
    return render(request, 'accounts/register.html')


def register_customer_view(request):
    error = None
    if request.method == 'POST':
        full_name    = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        username     = request.POST.get('username', '').strip()
        password     = request.POST.get('password', '')
        confirm      = request.POST.get('confirm_password', '')

        if password != confirm:
            error = 'Password dan konfirmasi password tidak cocok.'
        else:
            try:
                user_id     = str(uuid.uuid4())
                customer_id = str(uuid.uuid4())
                with transaction.atomic():
                    execute_query(
                        'INSERT INTO USER_ACCOUNT (user_id, username, password) VALUES (%s, %s, %s)',
                        [user_id, username, password]
                    )
                    execute_query(
                        'INSERT INTO ACCOUNT_ROLE (role_id, user_id) VALUES (%s, %s)',
                        [CUSTOMER_ROLE_ID, user_id]
                    )
                    execute_query(
                        'INSERT INTO CUSTOMER (customer_id, full_name, phone_number, user_id) VALUES (%s, %s, %s, %s)',
                        [customer_id, full_name, phone_number, user_id]
                    )
                return redirect('accounts:login')
            except DatabaseError as e:
                error = str(e).split('\n')[0]

    return render(request, 'accounts/register_customer.html', {'error': error})


def register_organizer_view(request):
    error = None
    if request.method == 'POST':
        organizer_name = request.POST.get('organizer_name', '').strip()
        contact_email  = request.POST.get('contact_email', '').strip()
        username       = request.POST.get('username', '').strip()
        password       = request.POST.get('password', '')
        confirm        = request.POST.get('confirm_password', '')

        if password != confirm:
            error = 'Password dan konfirmasi password tidak cocok.'
        else:
            try:
                user_id      = str(uuid.uuid4())
                organizer_id = str(uuid.uuid4())
                with transaction.atomic():
                    execute_query(
                        'INSERT INTO USER_ACCOUNT (user_id, username, password) VALUES (%s, %s, %s)',
                        [user_id, username, password]
                    )
                    execute_query(
                        'INSERT INTO ACCOUNT_ROLE (role_id, user_id) VALUES (%s, %s)',
                        [ORGANIZER_ROLE_ID, user_id]
                    )
                    execute_query(
                        'INSERT INTO ORGANIZER (organizer_id, organizer_name, contact_email, user_id) VALUES (%s, %s, %s, %s)',
                        [organizer_id, organizer_name, contact_email, user_id]
                    )
                return redirect('accounts:login')
            except DatabaseError as e:
                error = str(e).split('\n')[0]

    return render(request, 'accounts/register_organizer.html', {'error': error})


def register_admin_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')

        if password != confirm:
            error = 'Password dan konfirmasi password tidak cocok.'
        else:
            try:
                user_id = str(uuid.uuid4())
                with transaction.atomic():
                    execute_query(
                        'INSERT INTO USER_ACCOUNT (user_id, username, password) VALUES (%s, %s, %s)',
                        [user_id, username, password]
                    )
                    execute_query(
                        'INSERT INTO ACCOUNT_ROLE (role_id, user_id) VALUES (%s, %s)',
                        [ADMIN_ROLE_ID, user_id]
                    )
                return redirect('accounts:login')
            except DatabaseError as e:
                error = str(e).split('\n')[0]

    return render(request, 'accounts/register_admin.html', {'error': error})


@login_required
def dashboard_view(request):
    user = get_current_user(request)
    if user['role'] == 'administrator':
        return render(request, 'accounts/dashboard_admin.html', {'user': user})
    if user['role'] == 'organizer':
        return render(request, 'accounts/dashboard_organizer.html', {'user': user})
    return render(request, 'accounts/dashboard_customer.html', {'user': user})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': get_current_user(request)})
