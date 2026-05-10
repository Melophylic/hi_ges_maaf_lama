import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import DatabaseError, transaction
from django.urls import reverse

from core.db import fetch_all, fetch_one, execute_query


def _get_user_role(request):
    user = request.session.get('user')
    if user:
        role = user.get('role', '')
        if role == 'administrator':
            return 'admin'
        return role
    role = request.GET.get('role', 'admin').strip().lower()
    if role in ['admin', 'administrator']:
        return 'admin'
    return role


def _get_customer_id(request):
    user = request.session.get('user')
    if user and user.get('role') == 'customer':
        return str(user.get('customer_id', ''))
    return None


def _fmt_price(value):
    return f"{int(value):,}".replace(',', '.')


def _redirect_ticket_list(page_role):
    return redirect(f"{reverse('tickets:ticket_list')}?role={page_role}")


# ============================================================
# TICKET CATEGORY
# ============================================================

def ticket_category_list(request):
    user_role = _get_user_role(request)
    q         = request.GET.get('q', '').strip().lower()
    event_filter = request.GET.get('event_id', '')

    sql = """
        SELECT tc.category_id, tc.category_name, tc.quota, tc.price,
               e.event_id, e.event_title
        FROM TICKET_CATEGORY tc
        JOIN EVENT e ON tc.tevent_id = e.event_id
        WHERE 1=1
    """
    params = []
    if event_filter:
        sql += " AND e.event_id = %s"
        params.append(event_filter)
    if q:
        sql += " AND (LOWER(tc.category_name) LIKE %s OR LOWER(e.event_title) LIKE %s)"
        params += [f'%{q}%', f'%{q}%']
    sql += " ORDER BY e.event_title, tc.category_name"

    categories = fetch_all(sql, params)
    for cat in categories:
        cat['price'] = _fmt_price(cat['price'])

    events = fetch_all("SELECT event_id, event_title FROM EVENT ORDER BY event_title")

    total_kuota     = sum(c['quota'] for c in fetch_all("SELECT quota FROM TICKET_CATEGORY"))
    max_price_row   = fetch_one("SELECT MAX(price) AS mp FROM TICKET_CATEGORY")
    harga_tertinggi = _fmt_price(max_price_row['mp']) if max_price_row and max_price_row['mp'] else '0'

    return render(request, 'tickets/ticket_category_list.html', {
        'categories':      categories,
        'events':          events,
        'event_filter':    event_filter,
        'total_kategori':  len(fetch_all("SELECT 1 FROM TICKET_CATEGORY")),
        'total_kuota':     total_kuota,
        'harga_tertinggi': harga_tertinggi,
        'user_role':       user_role,
        'can_manage':      user_role in ['admin', 'organizer'],
    })


def ticket_category_create(request):
    user_role = _get_user_role(request)
    if user_role not in ['admin', 'organizer']:
        messages.error(request, 'Hanya Admin atau Organizer yang dapat menambah kategori tiket.')
        return redirect('tickets:ticket_category_list')

    events = fetch_all("SELECT event_id, event_title FROM EVENT ORDER BY event_title")

    if request.method == 'POST':
        tevent_id     = request.POST.get('tevent_id')
        category_name = request.POST.get('category_name', '').strip()
        price         = request.POST.get('price')
        quota         = request.POST.get('quota')
        try:
            execute_query(
                "INSERT INTO TICKET_CATEGORY (category_id, category_name, quota, price, tevent_id) VALUES (%s, %s, %s, %s, %s)",
                [str(uuid.uuid4()), category_name, quota, price, tevent_id]
            )
            messages.success(request, 'Kategori tiket berhasil ditambahkan.')
            return redirect('tickets:ticket_category_list')
        except DatabaseError as e:
            messages.error(request, str(e).split('\n')[0])

    return render(request, 'tickets/ticket_category_form.html', {
        'action': 'create', 'events': events, 'category': {}, 'user_role': user_role,
    })


def ticket_category_edit(request, category_id):
    user_role = _get_user_role(request)
    if user_role not in ['admin', 'organizer']:
        messages.error(request, 'Hanya Admin atau Organizer yang dapat mengubah kategori tiket.')
        return redirect('tickets:ticket_category_list')

    category = fetch_one(
        "SELECT tc.*, e.event_title FROM TICKET_CATEGORY tc JOIN EVENT e ON tc.tevent_id = e.event_id WHERE tc.category_id = %s",
        [category_id]
    )
    if not category:
        messages.error(request, 'Kategori tiket tidak ditemukan.')
        return redirect('tickets:ticket_category_list')

    events = fetch_all("SELECT event_id, event_title FROM EVENT ORDER BY event_title")

    if request.method == 'POST':
        tevent_id     = request.POST.get('tevent_id')
        category_name = request.POST.get('category_name', '').strip()
        price         = request.POST.get('price')
        quota         = request.POST.get('quota')
        try:
            execute_query(
                "UPDATE TICKET_CATEGORY SET category_name=%s, price=%s, quota=%s, tevent_id=%s WHERE category_id=%s",
                [category_name, price, quota, tevent_id, category_id]
            )
            messages.success(request, 'Kategori tiket berhasil diperbarui.')
            return redirect('tickets:ticket_category_list')
        except DatabaseError as e:
            messages.error(request, str(e).split('\n')[0])

    return render(request, 'tickets/ticket_category_form.html', {
        'action': 'edit', 'events': events, 'category': category, 'user_role': user_role,
    })


def ticket_category_delete(request, category_id):
    user_role = _get_user_role(request)
    if user_role not in ['admin', 'organizer']:
        messages.error(request, 'Hanya Admin atau Organizer yang dapat menghapus kategori tiket.')
        return redirect('tickets:ticket_category_list')

    category = fetch_one(
        "SELECT tc.*, e.event_title FROM TICKET_CATEGORY tc JOIN EVENT e ON tc.tevent_id = e.event_id WHERE tc.category_id = %s",
        [category_id]
    )
    if not category:
        messages.error(request, 'Kategori tiket tidak ditemukan.')
        return redirect('tickets:ticket_category_list')

    if request.method == 'POST':
        try:
            execute_query("DELETE FROM TICKET_CATEGORY WHERE category_id = %s", [category_id])
            messages.success(request, 'Kategori tiket berhasil dihapus.')
        except DatabaseError as e:
            messages.error(request, str(e).split('\n')[0])
        return redirect('tickets:ticket_category_list')

    return render(request, 'tickets/ticket_category_confirm_delete.html', {
        'selected_category': category, 'user_role': user_role,
    })


def ticket_category_partial(request):
    user_role  = _get_user_role(request)
    categories = fetch_all("""
        SELECT tc.category_id, tc.category_name, tc.quota, tc.price, e.event_title
        FROM TICKET_CATEGORY tc JOIN EVENT e ON tc.tevent_id = e.event_id
        ORDER BY e.event_title, tc.category_name
    """)
    for cat in categories:
        cat['price'] = _fmt_price(cat['price'])
    return render(request, 'tickets/partials/ticket_category_table.html', {
        'categories': categories, 'user_role': user_role,
    })


# ============================================================
# TICKET
# ============================================================

def _ticket_query(extra_where='', params=None):
    sql = """
        SELECT
            t.ticket_id, t.ticket_code, t.tcategory_id, t.torder_id,
            tc.category_name, tc.price,
            e.event_title, e.event_datetime,
            v.venue_name,
            c.full_name  AS customer_name,
            o.payment_status,
            s.section    AS seat_section,
            s.row_number AS seat_row,
            s.seat_number
        FROM TICKET t
        JOIN TICKET_CATEGORY tc ON t.tcategory_id = tc.category_id
        JOIN EVENT e             ON tc.tevent_id   = e.event_id
        JOIN VENUE v             ON e.venue_id      = v.venue_id
        JOIN "ORDER" o           ON t.torder_id     = o.order_id
        JOIN CUSTOMER c          ON o.customer_id   = c.customer_id
        LEFT JOIN HAS_RELATIONSHIP hr ON t.ticket_id = hr.ticket_id
        LEFT JOIN SEAT s              ON hr.seat_id  = s.seat_id
    """
    if extra_where:
        sql += f" WHERE {extra_where}"
    sql += " ORDER BY t.ticket_code"
    return fetch_all(sql, params or [])


def _build_ticket(row):
    seat_label = '-'
    if row.get('seat_section'):
        seat_label = f"{row['seat_section']} {row['seat_row']}-{row['seat_number']}"

    status = 'Valid'
    if row['payment_status'] == 'CANCELLED':
        status = 'Terpakai'

    return {
        **row,
        'price':      f"Rp {_fmt_price(row['price'])}",
        'order_code': str(row['torder_id'])[:8].upper(),
        'seat_label': seat_label,
        'status':     status,
        'event_datetime': str(row['event_datetime'])[:16],
    }


def _ticket_context(request, tickets):
    user_role = _get_user_role(request)
    return {
        'tickets':          tickets,
        'stats': {
            'total': len(tickets),
            'valid': sum(1 for t in tickets if t['status'] == 'Valid'),
            'used':  sum(1 for t in tickets if t['status'] == 'Terpakai'),
        },
        'page_role':        user_role,
        'page_title':       'Tiket Saya' if user_role == 'customer' else 'Manajemen Tiket',
        'page_subtitle':    'Kelola dan akses tiket pertunjukan Anda' if user_role == 'customer'
                            else 'Kelola tiket: tambah, ubah status, dan hapus tiket',
        'is_customer_view': user_role == 'customer',
        'can_create_ticket':user_role in ['admin', 'organizer'],
        'can_manage_ticket':user_role == 'admin',
        'user_role':        user_role,
    }


def ticket_list(request):
    user_role   = _get_user_role(request)
    customer_id = _get_customer_id(request)
    q      = request.GET.get('q', '').strip().lower()
    status = request.GET.get('status', '').strip()

    where_parts, params = [], []
    if user_role == 'customer' and customer_id:
        where_parts.append("c.customer_id = %s")
        params.append(customer_id)

    rows    = _ticket_query(' AND '.join(where_parts) if where_parts else '', params)
    tickets = [_build_ticket(r) for r in rows]

    if q:
        tickets = [t for t in tickets if q in t['ticket_code'].lower() or q in t['event_title'].lower()]
    if status:
        tickets = [t for t in tickets if t['status'] == status]

    return render(request, 'tickets/ticket_list.html', _ticket_context(request, tickets))


def ticket_partial(request):
    user_role   = _get_user_role(request)
    customer_id = _get_customer_id(request)
    where, params = '', []
    if user_role == 'customer' and customer_id:
        where  = "c.customer_id = %s"
        params = [customer_id]
    rows    = _ticket_query(where, params)
    tickets = [_build_ticket(r) for r in rows]
    return render(request, 'tickets/partials/ticket_cards.html', _ticket_context(request, tickets))


def ticket_create(request):
    user_role = _get_user_role(request)
    if user_role not in ['admin', 'organizer']:
        messages.error(request, 'Hanya Admin atau Organizer yang dapat membuat tiket.')
        return _redirect_ticket_list(user_role)

    error = None
    if request.method == 'POST':
        torder_id    = request.POST.get('order_id')
        tcategory_id = request.POST.get('category_id')
        seat_id      = request.POST.get('seat_id', '').strip()
        try:
            ticket_id   = str(uuid.uuid4())
            ticket_code = f"TIK-{ticket_id[:8].upper()}"
            with transaction.atomic():
                execute_query(
                    "INSERT INTO TICKET (ticket_id, ticket_code, tcategory_id, torder_id) VALUES (%s, %s, %s, %s)",
                    [ticket_id, ticket_code, tcategory_id, torder_id]
                )
                if seat_id:
                    execute_query(
                        "INSERT INTO HAS_RELATIONSHIP (seat_id, ticket_id) VALUES (%s, %s)",
                        [seat_id, ticket_id]
                    )
            messages.success(request, f'Tiket {ticket_code} berhasil dibuat.')
            return _redirect_ticket_list(user_role)
        except DatabaseError as e:
            error = str(e).split('\n')[0]

    orders = fetch_all("""
        SELECT o.order_id, c.full_name AS customer_name
        FROM "ORDER" o JOIN CUSTOMER c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    """)
    for o in orders:
        o['label'] = f"{str(o['order_id'])[:8].upper()} — {o['customer_name']}"

    categories = fetch_all("""
        SELECT tc.category_id, tc.category_name, tc.price, e.event_title,
               tc.quota - COUNT(t.ticket_id) AS remaining
        FROM TICKET_CATEGORY tc
        JOIN EVENT e ON tc.tevent_id = e.event_id
        LEFT JOIN TICKET t ON t.tcategory_id = tc.category_id
        GROUP BY tc.category_id, tc.category_name, tc.price, e.event_title, tc.quota
        ORDER BY e.event_title, tc.category_name
    """)
    for cat in categories:
        cat['label'] = f"{cat['category_name']} — Rp {_fmt_price(cat['price'])} ({cat['event_title']}) [{cat['remaining']} sisa]"

    seats = fetch_all("""
        SELECT s.seat_id, s.section, s.row_number, s.seat_number, v.venue_name
        FROM SEAT s JOIN VENUE v ON s.venue_id = v.venue_id
        WHERE s.seat_id NOT IN (SELECT seat_id FROM HAS_RELATIONSHIP)
        ORDER BY s.section, s.row_number, s.seat_number
    """)
    for s in seats:
        s['label'] = f"{s['section']} — Baris {s['row_number']}, No. {s['seat_number']} ({s['venue_name']})"

    show_seat = request.GET.get('reserved', '1') == '1'
    rows      = _ticket_query()
    tickets   = [_build_ticket(r) for r in rows]
    ctx       = _ticket_context(request, tickets)
    ctx.update({
        'form_mode': 'create', 'orders': orders, 'categories': categories,
        'seats': seats, 'selected_ticket': {}, 'show_seat_field': show_seat, 'error': error,
    })
    return render(request, 'tickets/ticket_form.html', ctx)


def ticket_edit(request, ticket_id):
    user_role = _get_user_role(request)
    if user_role != 'admin':
        messages.error(request, 'Hanya Admin yang dapat mengubah tiket.')
        return _redirect_ticket_list(user_role)

    rows = _ticket_query("t.ticket_id = %s", [ticket_id])
    if not rows:
        messages.error(request, 'Tiket tidak ditemukan.')
        return _redirect_ticket_list('admin')
    selected = _build_ticket(rows[0])

    error = None
    if request.method == 'POST':
        seat_id = request.POST.get('seat_id', '').strip()
        try:
            with transaction.atomic():
                execute_query("DELETE FROM HAS_RELATIONSHIP WHERE ticket_id = %s", [ticket_id])
                if seat_id:
                    execute_query(
                        "INSERT INTO HAS_RELATIONSHIP (seat_id, ticket_id) VALUES (%s, %s)",
                        [seat_id, ticket_id]
                    )
            messages.success(request, 'Tiket berhasil diperbarui.')
            return _redirect_ticket_list('admin')
        except DatabaseError as e:
            error = str(e).split('\n')[0]

    seats = fetch_all("""
        SELECT s.seat_id, s.section, s.row_number, s.seat_number, v.venue_name
        FROM SEAT s JOIN VENUE v ON s.venue_id = v.venue_id
        WHERE s.seat_id NOT IN (
            SELECT seat_id FROM HAS_RELATIONSHIP WHERE ticket_id != %s
        )
        ORDER BY s.section, s.row_number, s.seat_number
    """, [ticket_id])
    for s in seats:
        s['label'] = f"{s['section']} — Baris {s['row_number']}, No. {s['seat_number']} ({s['venue_name']})"

    all_tickets = [_build_ticket(r) for r in _ticket_query()]
    ctx = _ticket_context(request, all_tickets)
    ctx.update({
        'form_mode': 'edit', 'selected_ticket': selected,
        'seats': seats, 'orders': [], 'categories': [], 'show_seat_field': True, 'error': error,
    })
    return render(request, 'tickets/ticket_form.html', ctx)


def ticket_delete(request, ticket_id):
    user_role = _get_user_role(request)
    if user_role != 'admin':
        messages.error(request, 'Hanya Admin yang dapat menghapus tiket.')
        return _redirect_ticket_list(user_role)

    rows = _ticket_query("t.ticket_id = %s", [ticket_id])
    if not rows:
        messages.error(request, 'Tiket tidak ditemukan.')
        return _redirect_ticket_list('admin')
    selected = _build_ticket(rows[0])

    if request.method == 'POST':
        try:
            execute_query("DELETE FROM TICKET WHERE ticket_id = %s", [ticket_id])
            messages.success(request, 'Tiket berhasil dihapus.')
        except DatabaseError as e:
            messages.error(request, str(e).split('\n')[0])
        return _redirect_ticket_list('admin')

    all_tickets = [_build_ticket(r) for r in _ticket_query()]
    ctx = _ticket_context(request, all_tickets)
    ctx.update({'selected_ticket': selected})
    return render(request, 'tickets/ticket_confirm_delete.html', ctx)
