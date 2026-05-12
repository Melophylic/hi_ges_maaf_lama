import uuid

from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

from core.db import execute_query, fetch_all, fetch_one

DISCOUNT_TYPES = ["PERCENTAGE", "NOMINAL"]


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
    return redirect(f"/promotions/?role={role}")


def promotion_list(request):
    role = _get_role(request)
    search = request.GET.get("q", "").strip().lower()
    filter_type = request.GET.get("type", "all")

    where = ["1=1"]
    params = []
    if search:
        where.append("LOWER(p.promo_code) LIKE %s")
        params.append(f"%{search}%")
    if filter_type in DISCOUNT_TYPES:
        where.append("p.discount_type = %s")
        params.append(filter_type)

    promotions = fetch_all(
        f"""
        SELECT p.promotion_id::text, p.promo_code, p.discount_type, p.discount_value,
               p.start_date, p.end_date, p.usage_limit,
               COUNT(op.order_promotion_id) AS used
        FROM PROMOTION p
        LEFT JOIN ORDER_PROMOTION op ON p.promotion_id = op.promotion_id
        WHERE {' AND '.join(where)}
        GROUP BY p.promotion_id, p.promo_code, p.discount_type, p.discount_value,
                 p.start_date, p.end_date, p.usage_limit
        ORDER BY p.promo_code
        """,
        params,
    )

    totals = fetch_all(
        """
        SELECT COUNT(*) AS total_promos,
               SUM((SELECT COUNT(*) FROM ORDER_PROMOTION op WHERE op.promotion_id = p.promotion_id)) AS total_usage,
               COUNT(*) FILTER (WHERE p.discount_type = 'PERCENTAGE') AS total_percentage
        FROM PROMOTION p
        """
    )
    row = totals[0] if totals else {}

    return render(request, "promotions/promotion_list.html", {
        "role": role,
        "promotions": promotions,
        "search": search,
        "filter_type": filter_type,
        "discount_types": DISCOUNT_TYPES,
        "total_promos": row.get("total_promos", 0) or 0,
        "total_usage": row.get("total_usage", 0) or 0,
        "total_percentage": row.get("total_percentage", 0) or 0,
    })


def promotion_create(request):
    role = _get_role(request)

    if role != "admin":
        return JsonResponse({"success": False, "message": "Hanya admin yang dapat membuat promo."}, status=403)

    if request.method == "POST":
        promo_code = request.POST.get("promo_code", "").strip().upper()
        discount_type = request.POST.get("discount_type", "").strip()
        discount_value = request.POST.get("discount_value", "0")
        start_date = request.POST.get("start_date", "")
        end_date = request.POST.get("end_date", "")
        usage_limit = request.POST.get("usage_limit", "1")

        try:
            with transaction.atomic():
                execute_query(
                    "INSERT INTO PROMOTION "
                    "(promotion_id, promo_code, discount_type, discount_value, start_date, end_date, usage_limit) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [
                        str(uuid.uuid4()), promo_code, discount_type,
                        float(discount_value), start_date, end_date, int(usage_limit),
                    ],
                )
        except (DatabaseError, ValueError) as e:
            msg = str(e).split("\n")[0]
            return JsonResponse({"success": False, "message": msg}, status=400)

        if _is_ajax(request):
            return JsonResponse({"success": True, "message": "Promo baru berhasil dibuat!"})
        return _redirect_list(role)

    return _redirect_list(role)


def promotion_update(request, promotion_id):
    role = _get_role(request)

    if role != "admin":
        return JsonResponse({"success": False, "message": "Hanya admin yang dapat update promo."}, status=403)

    promo = fetch_one("SELECT promotion_id FROM PROMOTION WHERE promotion_id = %s", [promotion_id])
    if not promo:
        return JsonResponse({"success": False, "message": "Promo tidak ditemukan."}, status=404)

    if request.method == "POST":
        promo_code = request.POST.get("promo_code", "").strip().upper()
        discount_type = request.POST.get("discount_type", "").strip()
        discount_value = request.POST.get("discount_value", "0")
        start_date = request.POST.get("start_date", "")
        end_date = request.POST.get("end_date", "")
        usage_limit = request.POST.get("usage_limit", "1")

        try:
            execute_query(
                "UPDATE PROMOTION SET promo_code=%s, discount_type=%s, discount_value=%s, "
                "start_date=%s, end_date=%s, usage_limit=%s WHERE promotion_id=%s",
                [
                    promo_code, discount_type, float(discount_value),
                    start_date, end_date, int(usage_limit), promotion_id,
                ],
            )
        except (DatabaseError, ValueError) as e:
            msg = str(e).split("\n")[0]
            return JsonResponse({"success": False, "message": msg}, status=400)

        if _is_ajax(request):
            return JsonResponse({"success": True, "message": "Promo berhasil diperbarui!"})
        return _redirect_list(role)

    return _redirect_list(role)


def promotion_delete(request, promotion_id):
    role = _get_role(request)

    if role != "admin":
        return JsonResponse({"success": False, "message": "Hanya admin yang dapat delete promo."}, status=403)

    if request.method == "POST":
        promo = fetch_one("SELECT promotion_id FROM PROMOTION WHERE promotion_id = %s", [promotion_id])
        if not promo:
            return JsonResponse({"success": False, "message": "Promo tidak ditemukan."}, status=404)

        try:
            with transaction.atomic():
                execute_query("DELETE FROM PROMOTION WHERE promotion_id = %s", [promotion_id])
        except DatabaseError as e:
            return JsonResponse({"success": False, "message": str(e).split("\n")[0]}, status=500)

        if _is_ajax(request):
            return JsonResponse({"success": True, "message": "Promo berhasil dihapus!"})
        return _redirect_list(role)

    return _redirect_list(role)
