import uuid

from django.db import DatabaseError, transaction
from django.shortcuts import render, redirect
from django.urls import reverse

from core.db import execute_query, fetch_all, fetch_one


def _get_user_role(request):
    user = request.session.get("user")
    if user:
        return user.get("role", "guest")
    role = request.GET.get("role", "").strip().lower()
    if role in ["admin", "administrator"]:
        return "administrator"
    if role in ["organizer", "customer"]:
        return role
    return "guest"


def _can_manage_venue(request):
    return _get_user_role(request) in ["administrator", "organizer"]


def _get_page_role(request):
    user = request.session.get("user")
    if user:
        role = user.get("role", "guest")
        return "admin" if role == "administrator" else role
    role = request.GET.get("role", "admin").strip().lower()
    if role in ["admin", "administrator"]:
        return "admin"
    return role if role in ["organizer", "customer"] else "admin"


# ─── VENUE ────────────────────────────────────────────────────────────────────

def _fetch_venues(q="", city=""):
    where = ["1=1"]
    params = []
    if q:
        ql = f"%{q.lower()}%"
        where.append("(LOWER(venue_name) LIKE %s OR LOWER(address) LIKE %s)")
        params += [ql, ql]
    if city:
        where.append("LOWER(city) = %s")
        params.append(city.lower())
    return fetch_all(
        f"SELECT venue_id::text, venue_name, capacity, address, city FROM VENUE "
        f"WHERE {' AND '.join(where)} ORDER BY venue_name",
        params,
    )


def venue_list(request):
    q = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()

    venues = _fetch_venues(q, city)
    cities = [r["city"] for r in fetch_all("SELECT DISTINCT city FROM VENUE ORDER BY city")]

    return render(request, "venues/venue_list.html", {
        "venues": venues,
        "cities": cities,
        "q": q,
        "selected_city": city,
        "selected_seating": request.GET.get("seating", ""),
        "user_role": _get_user_role(request),
        "can_manage": _can_manage_venue(request),
        "total_venue": len(venues),
        "reserved_seating": 0,
        "total_capacity": f"{sum(v['capacity'] for v in venues):,}",
    })


def venue_partial(request):
    venues = fetch_all(
        "SELECT venue_id::text, venue_name, capacity, address, city FROM VENUE ORDER BY venue_name"
    )
    return render(request, "venues/partials/venue_table.html", {
        "venues": venues,
        "user_role": _get_user_role(request),
        "can_manage": _can_manage_venue(request),
    })


def venue_create(request):
    if not _can_manage_venue(request):
        return redirect("venues:venue_list")

    error = None
    if request.method == "POST":
        name = request.POST.get("venue_name", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        capacity = request.POST.get("capacity", "").strip()
        try:
            with transaction.atomic():
                execute_query(
                    "INSERT INTO VENUE (venue_id, venue_name, capacity, address, city) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    [str(uuid.uuid4()), name, int(capacity), address, city],
                )
            return redirect("venues:venue_list")
        except (DatabaseError, ValueError) as e:
            error = str(e).split("\n")[0]

    return render(request, "venues/venue_form.html", {
        "mode": "create",
        "venue": {},
        "error": error,
    })


def venue_edit(request, venue_id):
    venue = fetch_one(
        "SELECT venue_id::text, venue_name, capacity, address, city FROM VENUE WHERE venue_id = %s",
        [venue_id],
    )
    if not venue:
        return redirect("venues:venue_list")
    if not _can_manage_venue(request):
        return redirect("venues:venue_list")

    error = None
    if request.method == "POST":
        name = request.POST.get("venue_name", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        capacity = request.POST.get("capacity", "").strip()
        try:
            with transaction.atomic():
                execute_query(
                    "UPDATE VENUE SET venue_name=%s, capacity=%s, address=%s, city=%s "
                    "WHERE venue_id=%s",
                    [name, int(capacity), address, city, venue_id],
                )
            return redirect("venues:venue_list")
        except (DatabaseError, ValueError) as e:
            error = str(e).split("\n")[0]

    return render(request, "venues/venue_form.html", {
        "mode": "edit",
        "venue": venue,
        "error": error,
    })


def venue_delete(request, venue_id):
    venue = fetch_one(
        "SELECT venue_id::text, venue_name, city FROM VENUE WHERE venue_id = %s",
        [venue_id],
    )
    if not venue:
        return redirect("venues:venue_list")
    if not _can_manage_venue(request):
        return redirect("venues:venue_list")

    error = None
    if request.method == "POST":
        try:
            with transaction.atomic():
                execute_query("DELETE FROM VENUE WHERE venue_id = %s", [venue_id])
            return redirect("venues:venue_list")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    return render(request, "venues/venue_confirm_delete.html", {
        "venue": venue,
        "error": error,
    })


# ─── SEAT ─────────────────────────────────────────────────────────────────────

def _fetch_seats(q="", venue_filter=""):
    where = ["1=1"]
    params = []
    if q:
        ql = f"%{q.lower()}%"
        where.append(
            "(LOWER(s.section) LIKE %s OR LOWER(s.row_number) LIKE %s "
            "OR LOWER(s.seat_number) LIKE %s OR LOWER(v.venue_name) LIKE %s)"
        )
        params += [ql, ql, ql, ql]
    if venue_filter:
        where.append("s.venue_id = %s")
        params.append(venue_filter)
    return fetch_all(
        f"""
        SELECT s.seat_id::text, s.section, s.seat_number, s.row_number,
               s.venue_id::text, v.venue_name,
               CASE WHEN hr.seat_id IS NOT NULL THEN 'Terisi' ELSE 'Tersedia' END AS status
        FROM SEAT s
        JOIN VENUE v ON s.venue_id = v.venue_id
        LEFT JOIN HAS_RELATIONSHIP hr ON s.seat_id = hr.seat_id
        WHERE {' AND '.join(where)}
        ORDER BY v.venue_name, s.section, s.row_number, s.seat_number
        """,
        params,
    )


def _seat_stats(seats):
    filled = sum(1 for s in seats if s["status"] == "Terisi")
    return {"total": len(seats), "available": len(seats) - filled, "filled": filled}


def _seat_context(request, seats, **extra):
    page_role = _get_page_role(request)
    can_manage = page_role in ["admin", "organizer"]
    ctx = {
        "seats": seats,
        "venues": fetch_all("SELECT venue_id::text, venue_name FROM VENUE ORDER BY venue_name"),
        "stats": _seat_stats(seats),
        "page_role": page_role,
        "page_title": "Manajemen Kursi" if can_manage else "Daftar Kursi",
        "page_subtitle": (
            "Kelola kursi dan denah tempat duduk venue"
            if can_manage
            else "Lihat daftar kursi dan status ketersediaannya"
        ),
        "can_create_seat": can_manage,
        "can_manage_seat": can_manage,
        "user_role": "administrator" if page_role == "admin" else page_role,
    }
    ctx.update(extra)
    return ctx


def seat_list(request):
    q = request.GET.get("q", "").strip()
    venue_filter = request.GET.get("venue", "").strip()
    seats = _fetch_seats(q, venue_filter)
    return render(request, "venues/seat_list.html", _seat_context(request, seats))


def seat_partial(request):
    seats = _fetch_seats()
    return render(request, "venues/partials/seat_table.html", _seat_context(request, seats))


def seat_create(request):
    page_role = _get_page_role(request)
    if page_role not in ["admin", "organizer"]:
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")

    error = None
    if request.method == "POST":
        venue_id = request.POST.get("venue_id", "").strip()
        section = request.POST.get("section", "").strip()
        row_number = request.POST.get("row_number", "").strip()
        seat_number = request.POST.get("seat_number", "").strip()
        try:
            with transaction.atomic():
                execute_query(
                    "INSERT INTO SEAT (seat_id, section, seat_number, row_number, venue_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    [str(uuid.uuid4()), section, seat_number, row_number, venue_id],
                )
            return redirect(f"{reverse('venues:seat_list')}?role={page_role}")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    ctx = _seat_context(request, _fetch_seats(), form_mode="create", selected_seat={}, error=error)
    return render(request, "venues/seat_form.html", ctx)


def seat_edit(request, seat_id):
    page_role = _get_page_role(request)
    if page_role not in ["admin", "organizer"]:
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")

    seat = fetch_one(
        """
        SELECT s.seat_id::text, s.section, s.seat_number, s.row_number,
               s.venue_id::text, v.venue_name
        FROM SEAT s JOIN VENUE v ON s.venue_id = v.venue_id
        WHERE s.seat_id = %s
        """,
        [seat_id],
    )
    if not seat:
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")

    error = None
    if request.method == "POST":
        venue_id = request.POST.get("venue_id", "").strip()
        section = request.POST.get("section", "").strip()
        row_number = request.POST.get("row_number", "").strip()
        seat_number = request.POST.get("seat_number", "").strip()
        try:
            with transaction.atomic():
                execute_query(
                    "UPDATE SEAT SET venue_id=%s, section=%s, row_number=%s, seat_number=%s "
                    "WHERE seat_id=%s",
                    [venue_id, section, row_number, seat_number, seat_id],
                )
            return redirect(f"{reverse('venues:seat_list')}?role={page_role}")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    ctx = _seat_context(request, _fetch_seats(), form_mode="edit", selected_seat=seat, error=error)
    return render(request, "venues/seat_form.html", ctx)


def seat_delete(request, seat_id):
    page_role = _get_page_role(request)
    if page_role not in ["admin", "organizer"]:
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")

    seat = fetch_one(
        """
        SELECT s.seat_id::text, s.section, s.seat_number, s.row_number,
               s.venue_id::text, v.venue_name,
               CASE WHEN hr.seat_id IS NOT NULL THEN 'Terisi' ELSE 'Tersedia' END AS status
        FROM SEAT s JOIN VENUE v ON s.venue_id = v.venue_id
        LEFT JOIN HAS_RELATIONSHIP hr ON s.seat_id = hr.seat_id
        WHERE s.seat_id = %s
        """,
        [seat_id],
    )
    if not seat:
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")
    if seat["status"] == "Terisi":
        return redirect(f"{reverse('venues:seat_list')}?role={page_role}")

    error = None
    if request.method == "POST":
        try:
            with transaction.atomic():
                execute_query("DELETE FROM SEAT WHERE seat_id = %s", [seat_id])
            return redirect(f"{reverse('venues:seat_list')}?role={page_role}")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    ctx = _seat_context(request, _fetch_seats(), selected_seat=seat, error=error)
    return render(request, "venues/seat_confirm_delete.html", ctx)
