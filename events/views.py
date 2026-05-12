import uuid

from django.db import DatabaseError, transaction
from django.shortcuts import render, redirect

from core.auth import role_required
from core.db import execute_query, fetch_all, fetch_one


def _can_manage(request):
    user = request.session.get("user", {})
    return user.get("role", "") in ["administrator", "organizer"]


def _get_organizer_id(request):
    user = request.session.get("user", {})
    return user.get("organizer_id")


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _fetch_events(q="", venue_name_filter=""):
    where = ["1=1"]
    params = []
    if q:
        where.append("(LOWER(e.event_title) LIKE %s)")
        params.append(f"%{q.lower()}%")
    if venue_name_filter:
        where.append("v.venue_name = %s")
        params.append(venue_name_filter)

    events = fetch_all(
        f"""
        SELECT e.event_id::text, e.event_title, e.event_datetime,
               v.venue_id::text, v.venue_name,
               o.organizer_id::text, o.organizer_name,
               COALESCE(
                   array_agg(DISTINCT a.name ORDER BY a.name)
                   FILTER (WHERE a.name IS NOT NULL),
                   ARRAY[]::varchar[]
               ) AS performers
        FROM EVENT e
        JOIN VENUE v    ON e.venue_id    = v.venue_id
        JOIN ORGANIZER o ON e.organizer_id = o.organizer_id
        LEFT JOIN EVENT_ARTIST ea ON e.event_id  = ea.event_id
        LEFT JOIN ARTIST a        ON ea.artist_id = a.artist_id
        WHERE {' AND '.join(where)}
        GROUP BY e.event_id, e.event_title, e.event_datetime,
                 v.venue_id, v.venue_name, o.organizer_id, o.organizer_name
        ORDER BY e.event_datetime
        """,
        params,
    )

    if not events:
        return events

    # Batch-fetch ticket categories for all events
    event_ids = [e["event_id"] for e in events]
    placeholders = ",".join(["%s"] * len(event_ids))
    cats = fetch_all(
        f"SELECT tevent_id::text AS event_id, category_name AS name, price "
        f"FROM TICKET_CATEGORY WHERE tevent_id IN ({placeholders}) ORDER BY price",
        event_ids,
    )
    cats_by_event = {}
    for cat in cats:
        cats_by_event.setdefault(cat["event_id"], []).append(
            {"name": cat["name"], "price": cat["price"]}
        )

    for event in events:
        event["ticket_categories"] = cats_by_event.get(event["event_id"], [])
        event["image"] = ""
        event["description"] = ""

    return events


def _fetch_event(event_id):
    event = fetch_one(
        """
        SELECT e.event_id::text, e.event_title, e.event_datetime,
               v.venue_id::text, v.venue_name,
               o.organizer_id::text, o.organizer_name
        FROM EVENT e
        JOIN VENUE v    ON e.venue_id    = v.venue_id
        JOIN ORGANIZER o ON e.organizer_id = o.organizer_id
        WHERE e.event_id = %s
        """,
        [event_id],
    )
    if not event:
        return None

    artists = fetch_all(
        """
        SELECT a.name FROM ARTIST a
        JOIN EVENT_ARTIST ea ON a.artist_id = ea.artist_id
        WHERE ea.event_id = %s ORDER BY a.name
        """,
        [event_id],
    )
    event["performers"] = [a["name"] for a in artists]

    cats = fetch_all(
        "SELECT category_name AS name, price FROM TICKET_CATEGORY "
        "WHERE tevent_id = %s ORDER BY price",
        [event_id],
    )
    event["ticket_categories"] = cats
    event["image"] = ""
    event["description"] = ""
    return event


def _sync_performers(event_id, performers_text):
    names = [n.strip() for n in performers_text.split(",") if n.strip()]
    execute_query("DELETE FROM EVENT_ARTIST WHERE event_id = %s", [event_id])
    for name in names:
        artist = fetch_one(
            "SELECT artist_id::text FROM ARTIST WHERE LOWER(name) = LOWER(%s)", [name]
        )
        if artist:
            artist_id = artist["artist_id"]
        else:
            artist_id = str(uuid.uuid4())
            execute_query(
                "INSERT INTO ARTIST (artist_id, name) VALUES (%s, %s)",
                [artist_id, name],
            )
        execute_query(
            "INSERT INTO EVENT_ARTIST (event_id, artist_id, role) VALUES (%s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            [event_id, artist_id, "Performer"],
        )


def _add_new_categories(event_id, ticket_categories_text):
    names = [n.strip() for n in ticket_categories_text.split(",") if n.strip()]
    existing = {
        r["category_name"]
        for r in fetch_all(
            "SELECT category_name FROM TICKET_CATEGORY WHERE tevent_id = %s", [event_id]
        )
    }
    for name in names:
        if name not in existing:
            execute_query(
                "INSERT INTO TICKET_CATEGORY (category_id, category_name, quota, price, tevent_id) "
                "VALUES (%s, %s, 0, 0, %s)",
                [str(uuid.uuid4()), name, event_id],
            )


# ─── EVENT VIEWS ──────────────────────────────────────────────────────────────

def event_list(request):
    q = request.GET.get("q", "").strip()
    venue_filter = request.GET.get("venue", "").strip()

    events = _fetch_events(q, venue_filter)
    venues = [
        r["venue_name"]
        for r in fetch_all("SELECT DISTINCT venue_name FROM VENUE ORDER BY venue_name")
    ]

    return render(request, "events/event_list.html", {
        "events": events,
        "venues": venues,
        "q": q,
        "selected_venue": venue_filter,
        "can_manage": _can_manage(request),
    })


def event_partial(request):
    events = _fetch_events()
    return render(request, "events/partials/event_cards.html", {"events": events})


def event_detail(request, event_id):
    event = _fetch_event(event_id)
    if not event:
        return redirect("events:event_list")

    return render(request, "events/event_detail.html", {
        "event": event,
        "can_manage": _can_manage(request),
    })


def event_create(request):
    if not _can_manage(request):
        return redirect("events:event_list")

    error = None
    if request.method == "POST":
        title = request.POST.get("event_title", "").strip()
        event_datetime = request.POST.get("event_datetime", "").strip()
        venue_id = request.POST.get("venue_id", "").strip()
        organizer_id = request.POST.get("organizer_id", "").strip()
        performers_text = request.POST.get("performers", "").strip()
        ticket_categories_text = request.POST.get("ticket_categories", "").strip()

        try:
            with transaction.atomic():
                event_id = str(uuid.uuid4())
                execute_query(
                    "INSERT INTO EVENT (event_id, event_title, event_datetime, venue_id, organizer_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    [event_id, title, event_datetime, venue_id, organizer_id],
                )
                _sync_performers(event_id, performers_text)
                _add_new_categories(event_id, ticket_categories_text)
            return redirect("events:event_list")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    venues = fetch_all("SELECT venue_id::text, venue_name FROM VENUE ORDER BY venue_name")
    organizers = fetch_all(
        "SELECT organizer_id::text, organizer_name FROM ORGANIZER ORDER BY organizer_name"
    )
    return render(request, "events/partials/event_modal.html", {
        "mode": "create",
        "event": {},
        "venues": venues,
        "organizers": organizers,
        "performers_text": request.POST.get("performers", "") if error else "",
        "ticket_categories_text": request.POST.get("ticket_categories", "") if error else "",
        "error": error,
    })


def event_edit(request, event_id):
    if not _can_manage(request):
        return redirect("events:event_list")

    event = _fetch_event(event_id)
    if not event:
        return redirect("events:event_list")

    error = None
    if request.method == "POST":
        title = request.POST.get("event_title", "").strip()
        event_datetime = request.POST.get("event_datetime", "").strip()
        venue_id = request.POST.get("venue_id", "").strip()
        organizer_id = request.POST.get("organizer_id", "").strip()
        performers_text = request.POST.get("performers", "").strip()
        ticket_categories_text = request.POST.get("ticket_categories", "").strip()

        try:
            with transaction.atomic():
                execute_query(
                    "UPDATE EVENT SET event_title=%s, event_datetime=%s, venue_id=%s, organizer_id=%s "
                    "WHERE event_id=%s",
                    [title, event_datetime, venue_id, organizer_id, event_id],
                )
                _sync_performers(event_id, performers_text)
                _add_new_categories(event_id, ticket_categories_text)
            return redirect("events:event_list")
        except DatabaseError as e:
            error = str(e).split("\n")[0]

    venues = fetch_all("SELECT venue_id::text, venue_name FROM VENUE ORDER BY venue_name")
    organizers = fetch_all(
        "SELECT organizer_id::text, organizer_name FROM ORGANIZER ORDER BY organizer_name"
    )
    performers_text = ", ".join(event["performers"])
    ticket_categories_text = ", ".join(c["name"] for c in event["ticket_categories"])

    return render(request, "events/partials/event_modal.html", {
        "mode": "edit",
        "event": event,
        "venues": venues,
        "organizers": organizers,
        "performers_text": performers_text,
        "ticket_categories_text": ticket_categories_text,
        "error": error,
    })


# ─── ARTIST VIEWS ─────────────────────────────────────────────────────────────

def artist_list(request):
    search = request.GET.get("search", "")
    sql = "SELECT artist_id::text, name, genre FROM ARTIST"
    params = []
    if search:
        sql += " WHERE name ILIKE %s OR genre ILIKE %s"
        params = [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY name"
    artists = fetch_all(sql, params)

    total_artists = fetch_one("SELECT COUNT(*) AS count FROM ARTIST")
    total_genres = fetch_one(
        "SELECT COUNT(DISTINCT genre) AS count FROM ARTIST WHERE genre IS NOT NULL"
    )
    total_in_events = fetch_one(
        "SELECT COUNT(DISTINCT artist_id) AS count FROM EVENT_ARTIST"
    )

    return render(request, "events/artist_list.html", {
        "artists": artists,
        "search": search,
        "total_artists": total_artists["count"] if total_artists else 0,
        "total_genres": total_genres["count"] if total_genres else 0,
        "total_in_events": total_in_events["count"] if total_in_events else 0,
    })


def artist_partial(request):
    artists = fetch_all("SELECT artist_id::text, name, genre FROM ARTIST ORDER BY name")
    return render(request, "events/partials/artist_table.html", {"artists": artists})


@role_required("administrator")
def artist_create(request):
    error = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        genre = request.POST.get("genre", "").strip()
        if not name:
            error = "Nama artist wajib diisi."
        else:
            try:
                execute_query(
                    "INSERT INTO ARTIST (artist_id, name, genre) VALUES (%s, %s, %s)",
                    [str(uuid.uuid4()), name, genre or None],
                )
                return redirect("events:artist_list")
            except DatabaseError as e:
                error = str(e).split("\n")[0]
    return render(request, "events/artist_form.html", {"action": "create", "error": error})


@role_required("administrator")
def artist_edit(request, artist_id):
    artist = fetch_one(
        "SELECT artist_id::text, name, genre FROM ARTIST WHERE artist_id = %s", [artist_id]
    )
    if not artist:
        return redirect("events:artist_list")

    error = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        genre = request.POST.get("genre", "").strip()
        if not name:
            error = "Nama artist wajib diisi."
        else:
            try:
                execute_query(
                    "UPDATE ARTIST SET name=%s, genre=%s WHERE artist_id=%s",
                    [name, genre or None, artist_id],
                )
                return redirect("events:artist_list")
            except DatabaseError as e:
                error = str(e).split("\n")[0]
    return render(request, "events/artist_form.html", {
        "action": "edit",
        "artist": artist,
        "error": error,
    })


@role_required("administrator")
def artist_delete(request, artist_id):
    artist = fetch_one(
        "SELECT artist_id::text, name FROM ARTIST WHERE artist_id = %s", [artist_id]
    )
    if not artist:
        return redirect("events:artist_list")

    error = None
    if request.method == "POST":
        try:
            execute_query("DELETE FROM ARTIST WHERE artist_id = %s", [artist_id])
            return redirect("events:artist_list")
        except DatabaseError as e:
            error = str(e).split("\n")[0]
    return render(request, "events/artist_confirm_delete.html", {
        "artist": artist,
        "error": error,
    })
