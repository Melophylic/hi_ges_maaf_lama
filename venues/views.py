from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse


# =========================================================
# VENUE DUMMY DATA
# =========================================================

DUMMY_VENUES = [
    {
        "venue_id": "11111111-1111-1111-1111-111111111111",
        "venue_name": "Jakarta Convention Center",
        "capacity": 5000,
        "address": "Jl. Gatot Subroto, Jakarta",
        "city": "Jakarta",
        "seating_type": "reserved",
    },
    {
        "venue_id": "11111111-1111-1111-1111-111111111112",
        "venue_name": "Istora Senayan",
        "capacity": 12000,
        "address": "Jl. Pintu Satu Senayan, Gelora",
        "city": "Jakarta",
        "seating_type": "reserved",
    },
    {
        "venue_id": "11111111-1111-1111-1111-111111111113",
        "venue_name": "Bali Nusa Dua Convention Center",
        "capacity": 8000,
        "address": "Kawasan Pariwisata Nusa Dua",
        "city": "Bali",
        "seating_type": "reserved",
    },
    {
        "venue_id": "11111111-1111-1111-1111-111111111114",
        "venue_name": "Lapangan Merdeka Medan",
        "capacity": 15000,
        "address": "Jl. Pulau Pinang",
        "city": "Medan",
        "seating_type": "free",
    },
    {
        "venue_id": "11111111-1111-1111-1111-111111111115",
        "venue_name": "Gedung Kesenian Jakarta",
        "capacity": 2000,
        "address": "Jl. Gedung Kesenian No.1",
        "city": "Jakarta",
        "seating_type": "reserved",
    },
]


def _get_user_role(request):
    user_data = request.session.get("user", {})
    if user_data:
        return user_data.get("role", "guest")
    roles = request.session.get("roles", [])
    if "administrator" in roles:
        return "administrator"
    if "organizer" in roles:
        return "organizer"
    if "customer" in roles:
        return "customer"
    return "guest"


def _can_manage_venue(request):
   role = _get_user_role(request)
   return role in ["administrator", "organizer"]


def _find_venue(venue_id):
    for venue in DUMMY_VENUES:
        if str(venue["venue_id"]) == str(venue_id):
            return venue
    return None


def venue_list(request):
    q = request.GET.get("q", "").strip().lower()
    city = request.GET.get("city", "").strip().lower()
    seating = request.GET.get("seating", "").strip().lower()

    venues = DUMMY_VENUES[:]

    if q:
        venues = [
            v for v in venues
            if q in v["venue_name"].lower() or q in v["address"].lower()
        ]

    if city:
        venues = [v for v in venues if v["city"].lower() == city]

    if seating:
        venues = [v for v in venues if v["seating_type"].lower() == seating]

    total_venue = len(venues)
    reserved_seating = len([v for v in venues if v["seating_type"] == "reserved"])
    total_capacity = f"{sum(v['capacity'] for v in venues):,}"

    return render(request, "venues/venue_list.html", {
        "venues": venues,
        "cities": sorted({v["city"] for v in DUMMY_VENUES}),
        "search": request.GET.get("q", ""),
        "q": request.GET.get("q", ""),
        "selected_city": request.GET.get("city", ""),
        "selected_seating": request.GET.get("seating", ""),
        "user_role": _get_user_role(request),
        "can_manage": _can_manage_venue(request),
        "total_venue": total_venue,
        "reserved_seating": reserved_seating,
        "total_capacity": total_capacity,
    })


def venue_partial(request):
    return render(request, "venues/partials/venue_table.html", {
        "venues": DUMMY_VENUES,
        "user_role": _get_user_role(request),
        "can_manage": _can_manage_venue(request),
    })


def venue_create(request):
    if not _can_manage_venue(request):
        messages.error(request, "Kamu tidak punya akses untuk menambah venue.")
        return redirect("venues:venue_list")

    if request.method == "POST":
        messages.success(request, "Venue berhasil ditambahkan. Ini masih dummy frontend.")
        return redirect("venues:venue_list")

    return render(request, "venues/venue_form.html", {
        "action": "create",
        "user_role": _get_user_role(request),
        "can_manage": True,
        "venue": None,
    })


def venue_edit(request, venue_id):
    selected_venue = _find_venue(venue_id)

    if not selected_venue:
        messages.error(request, "Venue tidak ditemukan.")
        return redirect("venues:venue_list")

    if not _can_manage_venue(request):
        messages.error(request, "Kamu tidak punya akses untuk mengubah venue.")
        return redirect("venues:venue_list")

    if request.method == "POST":
        messages.success(request, "Venue berhasil diperbarui. Ini masih dummy frontend.")
        return redirect("venues:venue_list")

    return render(request, "venues/venue_form.html", {
        "action": "edit",
        "venue": selected_venue,
        "user_role": _get_user_role(request),
        "can_manage": True,
    })


def venue_delete(request, venue_id):
    selected_venue = _find_venue(venue_id)

    if not selected_venue:
        messages.error(request, "Venue tidak ditemukan.")
        return redirect("venues:venue_list")

    if not _can_manage_venue(request):
        messages.error(request, "Kamu tidak punya akses untuk menghapus venue.")
        return redirect("venues:venue_list")

    if request.method == "POST":
        messages.success(request, "Venue berhasil dihapus. Ini masih dummy frontend.")
        return redirect("venues:venue_list")

    return render(request, "venues/venue_confirm_delete.html", {
        "venue": selected_venue,
        "user_role": _get_user_role(request),
        "can_manage": True,
    })


# =========================================================
# SEAT DUMMY DATA
# =========================================================

FILLED_SEAT_IDS = {
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000002",
    "00000000-0000-0000-0000-000000000003",
    "00000000-0000-0000-0000-000000000004",
    "00000000-0000-0000-0000-000000000005",
    "00000000-0000-0000-0000-000000000006",
    "00000000-0000-0000-0000-000000000007",
    "00000000-0000-0000-0000-000000000008",
    "00000000-0000-0000-0000-000000000009",
    "00000000-0000-0000-0000-000000000010",
}

RAW_DUMMY_SEATS = [
    ("00000000-0000-0000-0000-000000000001", "WVIP", "1", "A", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000002", "WVIP", "2", "A", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000003", "WVIP", "3", "A", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000004", "WVIP", "4", "A", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000005", "WVIP", "5", "A", "11111111-1111-1111-1111-111111111111"),

    ("00000000-0000-0000-0000-000000000006", "VIP", "1", "B", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000007", "VIP", "2", "B", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000008", "VIP", "3", "B", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000009", "VIP", "4", "B", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000010", "VIP", "5", "B", "11111111-1111-1111-1111-111111111111"),

    ("00000000-0000-0000-0000-000000000011", "REGULER", "1", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000012", "REGULER", "2", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000013", "REGULER", "3", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000014", "REGULER", "4", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000015", "REGULER", "5", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000016", "REGULER", "6", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000017", "REGULER", "7", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000018", "REGULER", "8", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000019", "REGULER", "9", "C", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000020", "REGULER", "10", "C", "11111111-1111-1111-1111-111111111111"),

    ("00000000-0000-0000-0000-000000000021", "FESTIVAL", "1", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000022", "FESTIVAL", "2", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000023", "FESTIVAL", "3", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000024", "FESTIVAL", "4", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000025", "FESTIVAL", "5", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000026", "FESTIVAL", "6", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000027", "FESTIVAL", "7", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000028", "FESTIVAL", "8", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000029", "FESTIVAL", "9", "D", "11111111-1111-1111-1111-111111111111"),
    ("00000000-0000-0000-0000-000000000030", "FESTIVAL", "10", "D", "11111111-1111-1111-1111-111111111111"),
]


def _build_dummy_seats():
    venue_map = {venue["venue_id"]: venue["venue_name"] for venue in DUMMY_VENUES}
    seats = []

    for seat_id, section, seat_number, row_number, venue_id in RAW_DUMMY_SEATS:
        seats.append({
            "seat_id": seat_id,
            "section": section,
            "seat_number": seat_number,
            "row_number": row_number,
            "venue_id": venue_id,
            "venue_name": venue_map.get(venue_id, "-"),
            "status": "Terisi" if seat_id in FILLED_SEAT_IDS else "Tersedia",
        })

    return seats


DUMMY_SEATS = _build_dummy_seats()


def _seat_stats(seats):
    return {
        "total": len(seats),
        "available": len([seat for seat in seats if seat["status"] == "Tersedia"]),
        "filled": len([seat for seat in seats if seat["status"] == "Terisi"]),
    }


def _find_seat(seat_id):
    for seat in DUMMY_SEATS:
        if str(seat["seat_id"]) == str(seat_id):
            return seat
    return None


def _get_seat_page_role(request):
    role = request.GET.get("role", "admin").strip().lower()

    if role in ["admin", "administrator"]:
        return "admin"
    if role == "organizer":
        return "organizer"
    if role == "customer":
        return "customer"
    return "admin"


def _redirect_seat_list_with_role(page_role):
    url = reverse("seat_list")
    return redirect(f"{url}?role={page_role}")


def _seat_context(request, seats):
    page_role = _get_seat_page_role(request)
    can_manage_seat = page_role in ["admin", "organizer"]

    return {
        "seats": seats,
        "venues": DUMMY_VENUES,
        "stats": _seat_stats(seats),
        "page_role": page_role,
        "page_title": "Manajemen Kursi" if can_manage_seat else "Daftar Kursi",
        "page_subtitle": (
            "Kelola kursi dan denah tempat duduk venue"
            if can_manage_seat
            else "Lihat daftar kursi dan status ketersediaannya"
        ),
        "can_create_seat": can_manage_seat,
        "can_manage_seat": can_manage_seat,
        "user_role": "administrator" if page_role == "admin" else page_role,
    }


def seat_list(request):
    q = request.GET.get("q", "").strip().lower()
    venue = request.GET.get("venue", "").strip()

    filtered_seats = DUMMY_SEATS

    if q:
        filtered_seats = [
            seat for seat in filtered_seats
            if q in seat["section"].lower()
            or q in seat["row_number"].lower()
            or q in seat["seat_number"].lower()
            or q in seat["venue_name"].lower()
        ]

    if venue:
        filtered_seats = [
            seat for seat in filtered_seats
            if seat["venue_id"] == venue
        ]

    return render(request, "venues/seat_list.html", _seat_context(request, filtered_seats))


def seat_partial(request):
    return render(request, "venues/partials/seat_table.html", _seat_context(request, DUMMY_SEATS))


def seat_create(request):
    page_role = _get_seat_page_role(request)

    if page_role not in ["admin", "organizer"]:
        messages.error(request, "Hanya Admin atau Organizer yang dapat menambahkan kursi.")
        return _redirect_seat_list_with_role(page_role)

    if request.method == "POST":
        messages.success(request, "Kursi berhasil ditambahkan. Ini masih dummy frontend.")
        return _redirect_seat_list_with_role(page_role)

    context = _seat_context(request, DUMMY_SEATS)
    context.update({
        "form_mode": "create",
        "selected_seat": {},
    })

    return render(request, "venues/seat_form.html", context)


def seat_edit(request, seat_id):
    page_role = _get_seat_page_role(request)

    if page_role not in ["admin", "organizer"]:
        messages.error(request, "Hanya Admin atau Organizer yang dapat mengubah kursi.")
        return _redirect_seat_list_with_role(page_role)

    selected_seat = _find_seat(seat_id)

    if not selected_seat:
        messages.error(request, "Kursi tidak ditemukan.")
        return _redirect_seat_list_with_role(page_role)

    if request.method == "POST":
        messages.success(request, "Kursi berhasil diperbarui. Ini masih dummy frontend.")
        return _redirect_seat_list_with_role(page_role)

    context = _seat_context(request, DUMMY_SEATS)
    context.update({
        "form_mode": "edit",
        "selected_seat": selected_seat,
    })

    return render(request, "venues/seat_form.html", context)


def seat_delete(request, seat_id):
    page_role = _get_seat_page_role(request)

    if page_role not in ["admin", "organizer"]:
        messages.error(request, "Hanya Admin atau Organizer yang dapat menghapus kursi.")
        return _redirect_seat_list_with_role(page_role)

    selected_seat = _find_seat(seat_id)

    if not selected_seat:
        messages.error(request, "Kursi tidak ditemukan.")
        return _redirect_seat_list_with_role(page_role)

    if selected_seat["status"] == "Terisi":
        messages.error(request, "Kursi ini sudah di-assign ke tiket dan tidak dapat dihapus.")
        return _redirect_seat_list_with_role(page_role)

    if request.method == "POST":
        messages.success(request, "Kursi berhasil dihapus. Ini masih dummy frontend.")
        return _redirect_seat_list_with_role(page_role)

    context = _seat_context(request, DUMMY_SEATS)
    context.update({
        "selected_seat": selected_seat,
    })

    return render(request, "venues/seat_confirm_delete.html", context)