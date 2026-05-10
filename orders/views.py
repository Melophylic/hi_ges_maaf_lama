import uuid

from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

from core.db import execute_query, fetch_all, fetch_one

PAYMENT_STATUSES = ["PAID", "PENDING", "CANCELLED"]


def _get_role(request):
    user = request.session.get("user")
    if user:
        role = user.get("role", "")
        if role == "administrator":
            return "admin"
        if role in ("organizer", "customer"):
            return role
    return request.GET.get("role", "admin")


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _redirect_list(role):
    return redirect(f"/orders/?role={role}")


def _format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")


def _get_orders(role, customer_id=None, organizer_id=None,
                filter_status=None, search=""):
    where = ["1=1"]
    params = []

    if role == "customer" and customer_id:
        where.append("o.customer_id = %s")
        params.append(customer_id)
    elif role == "organizer" and organizer_id:
        where.append("""
            o.order_id IN (
                SELECT DISTINCT t.torder_id FROM TICKET t
                JOIN TICKET_CATEGORY tc ON t.tcategory_id = tc.category_id
                JOIN EVENT e ON tc.tevent_id = e.event_id
                WHERE e.organizer_id = %s
            )
        """)
        params.append(organizer_id)

    if filter_status in PAYMENT_STATUSES:
        where.append("o.payment_status = %s")
        params.append(filter_status)

    if search:
        s = f"%{search.lower()}%"
        where.append("(LOWER(o.order_id::text) LIKE %s OR LOWER(c.full_name) LIKE %s)")
        params += [s, s]

    return fetch_all(
        f"""
        SELECT o.order_id::text, o.order_date, o.payment_status, o.total_amount,
               c.customer_id::text, c.full_name AS customer_name,
               (SELECT e.event_title FROM TICKET t
                JOIN TICKET_CATEGORY tc ON t.tcategory_id = tc.category_id
                JOIN EVENT e ON tc.tevent_id = e.event_id
                WHERE t.torder_id = o.order_id LIMIT 1) AS event_name
        FROM "ORDER" o
        JOIN CUSTOMER c ON o.customer_id = c.customer_id
        WHERE {' AND '.join(where)}
        ORDER BY o.order_date DESC
        """,
        params,
    )


def order_list(request):
    role = _get_role(request)
    user = request.session.get("user", {})

    customer_id = user.get("customer_id")
    organizer_id = user.get("organizer_id")
    filter_status = request.GET.get("status", "all")
    search = request.GET.get("q", "").strip().lower()

    all_role_orders = _get_orders(role, customer_id, organizer_id)
    filtered_orders = _get_orders(role, customer_id, organizer_id, filter_status, search)

    total_orders = len(all_role_orders)
    total_paid = sum(1 for o in all_role_orders if o["payment_status"] == "PAID")
    total_pending = sum(1 for o in all_role_orders if o["payment_status"] == "PENDING")
    total_revenue = sum(
        float(o["total_amount"]) for o in all_role_orders if o["payment_status"] == "PAID"
    )

    return render(request, "orders/order_list.html", {
        "orders": filtered_orders,
        "role": role,
        "payment_statuses": PAYMENT_STATUSES,
        "filter_status": filter_status,
        "search": search,
        "total_orders": total_orders,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "total_revenue_display": _format_rupiah(total_revenue),
    })


def checkout(request):
    role = _get_role(request)
    user = request.session.get("user", {})
    customer_id = user.get("customer_id")

    event_id = request.GET.get("event_id") or request.POST.get("event_id", "")

    if not event_id:
        first = fetch_one(
            "SELECT event_id::text FROM EVENT WHERE event_datetime >= NOW() "
            "ORDER BY event_datetime LIMIT 1"
        )
        event_id = first["event_id"] if first else None

    if not event_id:
        return redirect("events:event_list")

    if request.method == "POST":
        category_id = request.POST.get("category_id", "").strip()
        quantity = int(request.POST.get("quantity", 1))
        seat_id = request.POST.get("seat_id", "").strip()
        promo_code = request.POST.get("promo_code", "").strip()

        cat = fetch_one(
            "SELECT category_id::text, category_name, price FROM TICKET_CATEGORY "
            "WHERE category_id = %s",
            [category_id],
        )
        if not cat:
            return JsonResponse({"success": False, "message": "Kategori tiket tidak ditemukan."}, status=400)

        base_price = float(cat["price"])
        total_amount = base_price * quantity

        promo = None
        if promo_code:
            promo = fetch_one(
                "SELECT promotion_id::text, discount_type, discount_value, "
                "start_date, end_date, usage_limit FROM PROMOTION "
                "WHERE UPPER(promo_code) = UPPER(%s)",
                [promo_code],
            )
            if not promo:
                msg = "Kode promo tidak ditemukan."
                return JsonResponse({"success": False, "message": msg}) if _is_ajax(request) else render(
                    request, "orders/checkout.html", {"error": msg, "role": role, "event": _build_event(event_id)})
            if promo["discount_type"] == "PERCENTAGE":
                total_amount -= total_amount * float(promo["discount_value"]) / 100
            else:
                total_amount -= float(promo["discount_value"])
            total_amount = max(total_amount, 0)

        try:
            with transaction.atomic():
                if not customer_id:
                    raise DatabaseError("Hanya customer yang bisa checkout.")

                order_id = str(uuid.uuid4())
                execute_query(
                    'INSERT INTO "ORDER" (order_id, order_date, payment_status, total_amount, customer_id) '
                    "VALUES (%s, NOW(), 'PENDING', %s, %s)",
                    [order_id, total_amount, customer_id],
                )

                first_ticket_id = None
                for _ in range(quantity):
                    tid = str(uuid.uuid4())
                    ticket_code = f"TIK-{tid[:8].upper()}"
                    execute_query(
                        "INSERT INTO TICKET (ticket_id, ticket_code, tcategory_id, torder_id) "
                        "VALUES (%s, %s, %s, %s)",
                        [tid, ticket_code, category_id, order_id],
                    )
                    if first_ticket_id is None:
                        first_ticket_id = tid

                if seat_id and first_ticket_id:
                    execute_query(
                        "INSERT INTO HAS_RELATIONSHIP (seat_id, ticket_id) VALUES (%s, %s)",
                        [seat_id, first_ticket_id],
                    )

                if promo:
                    execute_query(
                        "INSERT INTO ORDER_PROMOTION (order_promotion_id, promotion_id, order_id) "
                        "VALUES (%s, %s, %s)",
                        [str(uuid.uuid4()), promo["promotion_id"], order_id],
                    )

            if _is_ajax(request):
                return JsonResponse({"success": True, "message": "Order berhasil dibuat! Status pembayaran: PENDING."})
            return _redirect_list(role)

        except DatabaseError as e:
            msg = str(e).split("\n")[0]
            if _is_ajax(request):
                return JsonResponse({"success": False, "message": msg})
            event_ctx = _build_event(event_id)
            return render(request, "orders/checkout.html", {"error": msg, "role": role, "event": event_ctx})

    event_ctx = _build_event(event_id)
    if not event_ctx:
        return redirect("events:event_list")

    return render(request, "orders/checkout.html", {"role": role, "event": event_ctx})


def _build_event(event_id):
    ev = fetch_one(
        """
        SELECT e.event_id::text, e.event_title, e.event_datetime,
               v.venue_name, v.venue_id::text
        FROM EVENT e JOIN VENUE v ON e.venue_id = v.venue_id
        WHERE e.event_id = %s
        """,
        [event_id],
    )
    if not ev:
        return None

    artists = fetch_all(
        """
        SELECT a.name FROM ARTIST a
        JOIN EVENT_ARTIST ea ON a.artist_id = ea.artist_id
        WHERE ea.event_id = %s ORDER BY a.name
        """,
        [event_id],
    )

    cats = fetch_all(
        """
        SELECT tc.category_id::text, tc.category_name, tc.price, tc.quota,
               COUNT(t.ticket_id) AS used
        FROM TICKET_CATEGORY tc
        LEFT JOIN TICKET t ON t.tcategory_id = tc.category_id
        WHERE tc.tevent_id = %s
        GROUP BY tc.category_id, tc.category_name, tc.price, tc.quota
        ORDER BY tc.price
        """,
        [event_id],
    )

    seats = fetch_all(
        """
        SELECT s.seat_id::text, s.section, s.row_number, s.seat_number
        FROM SEAT s
        WHERE s.venue_id = %s
          AND s.seat_id NOT IN (SELECT seat_id FROM HAS_RELATIONSHIP)
        ORDER BY s.section, s.row_number, s.seat_number
        """,
        [ev["venue_id"]],
    )

    return {
        "event_id": ev["event_id"],
        "event_title": ev["event_title"],
        "event_datetime": ev["event_datetime"],
        "venue_name": ev["venue_name"],
        "artists": [a["name"] for a in artists],
        "categories": cats,
        "has_reserved_seating": len(seats) > 0,
        "seats": seats,
    }


def order_update(request, order_id):
    role = _get_role(request)

    if role != "admin":
        return JsonResponse({"success": False, "message": "Hanya admin yang dapat update order."}, status=403)

    if request.method == "POST":
        new_status = request.POST.get("payment_status")
        if new_status not in PAYMENT_STATUSES:
            return JsonResponse({"success": False, "message": "Status tidak valid."}, status=400)

        order = fetch_one('SELECT order_id FROM "ORDER" WHERE order_id = %s', [order_id])
        if not order:
            return JsonResponse({"success": False, "message": "Order tidak ditemukan."}, status=404)

        try:
            execute_query(
                'UPDATE "ORDER" SET payment_status = %s WHERE order_id = %s',
                [new_status, order_id],
            )
        except DatabaseError as e:
            return JsonResponse({"success": False, "message": str(e).split("\n")[0]}, status=500)

        return JsonResponse({"success": True, "message": f"Order berhasil diupdate menjadi {new_status}."})

    return _redirect_list(role)


def order_delete(request, order_id):
    role = _get_role(request)

    if role != "admin":
        return JsonResponse({"success": False, "message": "Hanya admin yang dapat delete order."}, status=403)

    if request.method == "POST":
        order = fetch_one('SELECT order_id FROM "ORDER" WHERE order_id = %s', [order_id])
        if not order:
            return JsonResponse({"success": False, "message": "Order tidak ditemukan."}, status=404)

        try:
            with transaction.atomic():
                execute_query('DELETE FROM "ORDER" WHERE order_id = %s', [order_id])
        except DatabaseError as e:
            return JsonResponse({"success": False, "message": str(e).split("\n")[0]}, status=500)

        return JsonResponse({"success": True, "message": "Order berhasil dihapus."})

    return _redirect_list(role)
