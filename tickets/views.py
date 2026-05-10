from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse


# Ticket Category Dummy Data

DUMMY_TICKET_CATEGORIES = [
    {
        "category_id": "cat_vip",
        "category_name": "VIP",
        "quota": 150,
        "price": "Rp 750,000",
        "event_title": "Konser Melodi Senja",
    },
    {
        "category_id": "cat_ga",
        "category_name": "General Admission",
        "quota": 500,
        "price": "Rp 150,000",
        "event_title": "Festival Seni Budaya",
    },
    {
        "category_id": "cat_wvip",
        "category_name": "WVIP",
        "quota": 50,
        "price": "Rp 1,500,000",
        "event_title": "Rock Legends Tour",
    },
]


def _find_ticket_category(category_id):
    for category in DUMMY_TICKET_CATEGORIES:
        if str(category["category_id"]) == str(category_id):
            return category
    return None


def ticket_category_list(request):
    return render(request, "tickets/ticket_category_list.html", {
        "categories": DUMMY_TICKET_CATEGORIES,
        "stats": {
            "total": len(DUMMY_TICKET_CATEGORIES),
            "available": 0,
            "revenue": 0,
        },
        "user_role": "administrator",
    })


def ticket_category_create(request):
    if request.method == "POST":
        messages.success(request, "Kategori tiket berhasil dibuat. Ini masih dummy frontend.")
        return redirect("tickets:ticket_category_list")

    return render(request, "tickets/ticket_category_form.html", {
        "form_mode": "create",
        "selected_category": {},
        "user_role": "administrator",
    })


def ticket_category_edit(request, category_id):
    selected_category = _find_ticket_category(category_id)

    if not selected_category:
        messages.error(request, "Kategori tiket tidak ditemukan.")
        return redirect("tickets:ticket_category_list")

    if request.method == "POST":
        messages.success(request, "Kategori tiket berhasil diperbarui. Ini masih dummy frontend.")
        return redirect("tickets:ticket_category_list")

    return render(request, "tickets/ticket_category_form.html", {
        "form_mode": "edit",
        "selected_category": selected_category,
        "user_role": "administrator",
    })


def ticket_category_delete(request, category_id):
    selected_category = _find_ticket_category(category_id)

    if not selected_category:
        messages.error(request, "Kategori tiket tidak ditemukan.")
        return redirect("tickets:ticket_category_list")

    if request.method == "POST":
        messages.success(request, "Kategori tiket berhasil dihapus. Ini masih dummy frontend.")
        return redirect("tickets:ticket_category_list")

    return render(request, "tickets/ticket_category_confirm_delete.html", {
        "selected_category": selected_category,
        "user_role": "administrator",
    })


def ticket_category_partial(request):
    return render(request, "tickets/partials/ticket_category_table.html", {
        "categories": DUMMY_TICKET_CATEGORIES,
        "user_role": "administrator",
    })


# Ticket Dummy data

DUMMY_TICKET_CATEGORY_MAP = {
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001": {
        "category_name": "WVIP",
        "price": "Rp 1,500,000",
        "label": "WVIP — Rp 1,500,000 (1/50)",
    },
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002": {
        "category_name": "VIP",
        "price": "Rp 750,000",
        "label": "VIP — Rp 750,000 (3/150)",
    },
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003": {
        "category_name": "REGULER",
        "price": "Rp 350,000",
        "label": "REGULER — Rp 350,000 (10/500)",
    },
    "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004": {
        "category_name": "FESTIVAL",
        "price": "Rp 150,000",
        "label": "FESTIVAL — Rp 150,000 (20/1000)",
    },
}

DUMMY_ORDER_MAP = {
    "cccccccc-cccc-cccc-cccc-ccccccccc001": {
        "order_code": "ord_001",
        "customer_name": "Budi Santoso",
        "event_title": "Konser Melodi Senja",
        "event_datetime": "2024-05-15 19:00",
        "venue_name": "Jakarta Convention Center",
        "label": "ord_001 — Budi Santoso — Konser Melodi Senja",
    },
    "cccccccc-cccc-cccc-cccc-ccccccccc002": {
        "order_code": "ord_002",
        "customer_name": "Siti Rahayu",
        "event_title": "Festival Seni Budaya",
        "event_datetime": "2024-06-01 18:30",
        "venue_name": "Jakarta Convention Center",
        "label": "ord_002 — Siti Rahayu — Festival Seni Budaya",
    },
    "cccccccc-cccc-cccc-cccc-ccccccccc003": {
        "order_code": "ord_003",
        "customer_name": "Andi Wijaya",
        "event_title": "Rock Legends Tour",
        "event_datetime": "2024-08-15 20:00",
        "venue_name": "Jakarta Convention Center",
        "label": "ord_003 — Andi Wijaya — Rock Legends Tour",
    },
    "cccccccc-cccc-cccc-cccc-ccccccccc004": {
        "order_code": "ord_004",
        "customer_name": "Dewi Lestari",
        "event_title": "Jazz Night Live",
        "event_datetime": "2024-09-10 19:30",
        "venue_name": "Jakarta Convention Center",
        "label": "ord_004 — Dewi Lestari — Jazz Night Live",
    },
}

DUMMY_TICKET_SEAT_MAP = {
    "11111111-1111-1111-1111-111111111101": "WVIP A-1",
    "11111111-1111-1111-1111-111111111102": "WVIP A-2",
    "11111111-1111-1111-1111-111111111103": "WVIP A-3",
    "11111111-1111-1111-1111-111111111104": "WVIP A-4",
    "11111111-1111-1111-1111-111111111105": "WVIP A-5",
    "11111111-1111-1111-1111-111111111106": "VIP B-1",
    "11111111-1111-1111-1111-111111111107": "VIP B-2",
    "11111111-1111-1111-1111-111111111108": "VIP B-3",
    "11111111-1111-1111-1111-111111111109": "VIP B-4",
    "11111111-1111-1111-1111-111111111110": "VIP B-5",
}

USED_TICKET_IDS = {
    "11111111-1111-1111-1111-111111111103",
    "11111111-1111-1111-1111-111111111108",
    "11111111-1111-1111-1111-111111111112",
    "11111111-1111-1111-1111-111111111116",
}

RAW_DUMMY_TICKETS = [
    ("11111111-1111-1111-1111-111111111101", "TIK-A001", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001", "cccccccc-cccc-cccc-cccc-ccccccccc001"),
    ("11111111-1111-1111-1111-111111111102", "TIK-A002", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001", "cccccccc-cccc-cccc-cccc-ccccccccc001"),
    ("11111111-1111-1111-1111-111111111103", "TIK-A003", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002", "cccccccc-cccc-cccc-cccc-ccccccccc002"),
    ("11111111-1111-1111-1111-111111111104", "TIK-A004", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002", "cccccccc-cccc-cccc-cccc-ccccccccc002"),
    ("11111111-1111-1111-1111-111111111105", "TIK-A005", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003", "cccccccc-cccc-cccc-cccc-ccccccccc003"),

    ("11111111-1111-1111-1111-111111111106", "TIK-B001", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003", "cccccccc-cccc-cccc-cccc-ccccccccc003"),
    ("11111111-1111-1111-1111-111111111107", "TIK-B002", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004", "cccccccc-cccc-cccc-cccc-ccccccccc004"),
    ("11111111-1111-1111-1111-111111111108", "TIK-B003", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004", "cccccccc-cccc-cccc-cccc-ccccccccc004"),
    ("11111111-1111-1111-1111-111111111109", "TIK-B004", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001", "cccccccc-cccc-cccc-cccc-ccccccccc001"),
    ("11111111-1111-1111-1111-111111111110", "TIK-B005", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002", "cccccccc-cccc-cccc-cccc-ccccccccc002"),

    ("11111111-1111-1111-1111-111111111111", "TIK-C001", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003", "cccccccc-cccc-cccc-cccc-ccccccccc003"),
    ("11111111-1111-1111-1111-111111111112", "TIK-C002", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004", "cccccccc-cccc-cccc-cccc-ccccccccc004"),
    ("11111111-1111-1111-1111-111111111113", "TIK-C003", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001", "cccccccc-cccc-cccc-cccc-ccccccccc001"),
    ("11111111-1111-1111-1111-111111111114", "TIK-C004", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002", "cccccccc-cccc-cccc-cccc-ccccccccc002"),
    ("11111111-1111-1111-1111-111111111115", "TIK-C005", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003", "cccccccc-cccc-cccc-cccc-ccccccccc003"),

    ("11111111-1111-1111-1111-111111111116", "TIK-D001", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004", "cccccccc-cccc-cccc-cccc-ccccccccc004"),
    ("11111111-1111-1111-1111-111111111117", "TIK-D002", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001", "cccccccc-cccc-cccc-cccc-ccccccccc001"),
    ("11111111-1111-1111-1111-111111111118", "TIK-D003", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002", "cccccccc-cccc-cccc-cccc-ccccccccc002"),
    ("11111111-1111-1111-1111-111111111119", "TIK-D004", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003", "cccccccc-cccc-cccc-cccc-ccccccccc003"),
    ("11111111-1111-1111-1111-111111111120", "TIK-D005", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004", "cccccccc-cccc-cccc-cccc-ccccccccc004"),
]


def _build_dummy_tickets():
    tickets = []

    for ticket_id, ticket_code, tcategory_id, torder_id in RAW_DUMMY_TICKETS:
        category = DUMMY_TICKET_CATEGORY_MAP[tcategory_id]
        order = DUMMY_ORDER_MAP[torder_id]

        tickets.append({
            "ticket_id": ticket_id,
            "ticket_code": ticket_code,
            "tcategory_id": tcategory_id,
            "torder_id": torder_id,
            "event_title": order["event_title"],
            "event_datetime": order["event_datetime"],
            "venue_name": order["venue_name"],
            "category_name": category["category_name"],
            "price": category["price"],
            "order_code": order["order_code"],
            "customer_name": order["customer_name"],
            "seat_label": DUMMY_TICKET_SEAT_MAP.get(ticket_id, "-"),
            "status": "Used" if ticket_id in USED_TICKET_IDS else "Valid",
        })

    return tickets


DUMMY_TICKETS = _build_dummy_tickets()

DUMMY_ORDERS = [
    {
        "order_id": order_id,
        "label": order_data["label"],
    }
    for order_id, order_data in DUMMY_ORDER_MAP.items()
]

DUMMY_CATEGORIES = [
    {
        "category_id": category_id,
        "label": category_data["label"],
    }
    for category_id, category_data in DUMMY_TICKET_CATEGORY_MAP.items()
]

DUMMY_SEATS = [
    {
        "seat_id": "00000000-0000-0000-0000-000000000011",
        "label": "REGULER — Baris C, No. 1",
    },
    {
        "seat_id": "00000000-0000-0000-0000-000000000012",
        "label": "REGULER — Baris C, No. 2",
    },
    {
        "seat_id": "00000000-0000-0000-0000-000000000013",
        "label": "REGULER — Baris C, No. 3",
    },
    {
        "seat_id": "00000000-0000-0000-0000-000000000021",
        "label": "FESTIVAL — Baris D, No. 1",
    },
    {
        "seat_id": "00000000-0000-0000-0000-000000000022",
        "label": "FESTIVAL — Baris D, No. 2",
    },
]


def get_ticket_stats(tickets=None):
    if tickets is None:
        tickets = DUMMY_TICKETS

    return {
        "total": len(tickets),
        "valid": len([ticket for ticket in tickets if ticket["status"] == "Valid"]),
        "used": len([ticket for ticket in tickets if ticket["status"] == "Used"]),
    }


def _get_page_role(request):
    role = request.GET.get("role", "admin").strip().lower()

    if role in ["admin", "administrator"]:
        return "admin"
    if role == "organizer":
        return "organizer"
    if role == "customer":
        return "customer"

    return "admin"


def _filter_tickets_by_role(tickets, page_role):
    if page_role == "customer":
        return [
            ticket for ticket in tickets
            if ticket["customer_name"] == "Budi Santoso"
        ]
    return tickets


def _find_ticket(ticket_id):
    for ticket in DUMMY_TICKETS:
        if str(ticket["ticket_id"]) == str(ticket_id):
            return ticket
    return None


def _redirect_ticket_list_with_role(page_role):
    url = reverse("tickets:ticket_list")
    return redirect(f"{url}?role={page_role}")


def _ticket_context(request, tickets):
    page_role = _get_page_role(request)

    return {
        "tickets": tickets,
        "stats": get_ticket_stats(tickets),
        "page_role": page_role,
        "page_title": "Tiket Saya" if page_role == "customer" else "Manajemen Tiket",
        "page_subtitle": (
            "Kelola dan akses tiket pertunjukan Anda"
            if page_role == "customer"
            else "Kelola tiket: tambah, ubah status, dan hapus tiket"
        ),
        "is_customer_view": page_role == "customer",
        "can_create_ticket": page_role in ["admin", "organizer"],
        "can_manage_ticket": page_role == "admin",
        "user_role": "administrator" if page_role == "admin" else page_role,
    }


def ticket_list(request):
    page_role = _get_page_role(request)
    q = request.GET.get("q", "").strip().lower()
    status = request.GET.get("status", "").strip()

    tickets = _filter_tickets_by_role(DUMMY_TICKETS, page_role)

    if q:
        tickets = [
            ticket for ticket in tickets
            if q in ticket["ticket_code"].lower()
            or q in ticket["event_title"].lower()
        ]

    if status:
        tickets = [
            ticket for ticket in tickets
            if ticket["status"] == status
        ]

    return render(request, "tickets/ticket_list.html", _ticket_context(request, tickets))


def ticket_partial(request):
    page_role = _get_page_role(request)
    tickets = _filter_tickets_by_role(DUMMY_TICKETS, page_role)

    return render(request, "tickets/partials/ticket_cards.html", _ticket_context(request, tickets))


def ticket_create(request):
    page_role = _get_page_role(request)

    if page_role not in ["admin", "organizer"]:
        messages.error(request, "Hanya Admin atau Organizer yang dapat membuat tiket.")
        return _redirect_ticket_list_with_role(page_role)

    if request.method == "POST":
        messages.success(request, "Tiket berhasil dibuat. Ini masih dummy frontend.")
        return _redirect_ticket_list_with_role(page_role)

    show_seat_field = request.GET.get("reserved", "1") == "1"

    tickets = _filter_tickets_by_role(DUMMY_TICKETS, page_role)
    context = _ticket_context(request, tickets)

    context.update({
        "form_mode": "create",
        "orders": DUMMY_ORDERS,
        "categories": DUMMY_CATEGORIES,
        "seats": DUMMY_SEATS,
        "selected_ticket": {},
        "show_seat_field": show_seat_field,
    })

    return render(request, "tickets/ticket_form.html", context)


def ticket_edit(request, ticket_id):
    page_role = _get_page_role(request)

    if page_role != "admin":
        messages.error(request, "Hanya Admin yang dapat mengubah tiket.")
        return _redirect_ticket_list_with_role(page_role)

    selected_ticket = _find_ticket(ticket_id)

    if not selected_ticket:
        messages.error(request, "Tiket tidak ditemukan.")
        return _redirect_ticket_list_with_role("admin")

    if request.method == "POST":
        messages.success(request, "Tiket berhasil diperbarui. Ini masih dummy frontend.")
        return _redirect_ticket_list_with_role("admin")

    tickets = _filter_tickets_by_role(DUMMY_TICKETS, page_role)
    context = _ticket_context(request, tickets)

    context.update({
        "form_mode": "edit",
        "orders": DUMMY_ORDERS,
        "categories": DUMMY_CATEGORIES,
        "seats": DUMMY_SEATS,
        "selected_ticket": selected_ticket,
        "show_seat_field": True,
    })

    return render(request, "tickets/ticket_form.html", context)


def ticket_delete(request, ticket_id):
    page_role = _get_page_role(request)

    if page_role != "admin":
        messages.error(request, "Hanya Admin yang dapat menghapus tiket.")
        return _redirect_ticket_list_with_role(page_role)

    selected_ticket = _find_ticket(ticket_id)

    if not selected_ticket:
        messages.error(request, "Tiket tidak ditemukan.")
        return _redirect_ticket_list_with_role("admin")

    if request.method == "POST":
        messages.success(request, "Tiket berhasil dihapus. Ini masih dummy frontend.")
        return _redirect_ticket_list_with_role("admin")

    tickets = _filter_tickets_by_role(DUMMY_TICKETS, page_role)
    context = _ticket_context(request, tickets)

    context.update({
        "selected_ticket": selected_ticket,
    })

    return render(request, "tickets/ticket_confirm_delete.html", context)
