from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect

from core.auth import role_required
from core.db import fetch_all, fetch_one, execute_query
from venues.views import DUMMY_VENUES

DUMMY_ORGANIZERS = [
    {
        "organizer_id": "40000000-0000-0000-0000-000000000001",
        "organizer_name": "PT Nada Penuh Cerita",
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2",
    },
    {
        "organizer_id": "40000000-0000-0000-0000-000000000002",
        "organizer_name": "Sunset Wave Organizer",
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6",
    },
    {
        "organizer_id": "40000000-0000-0000-0000-000000000003",
        "organizer_name": "Ruang Bunyi",
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa9",
    },
    {
        "organizer_id": "40000000-0000-0000-0000-000000000004",
        "organizer_name": "Bright Stage ID",
        "user_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12",
    },
]

DUMMY_EVENTS = [
    {
        "event_id": "60000000-0000-0000-0000-000000000001",
        "event_title": "Jakarta Music Fest 2026",
        "event_datetime": datetime(2026, 5, 10, 19, 0),
        "venue_id": "11111111-1111-1111-1111-111111111112",
        "venue_name": "Istora Senayan",
        "organizer_id": "40000000-0000-0000-0000-000000000001",
        "organizer_name": "PT Nada Penuh Cerita",
        "performers": ["NOAH", "Tulus", "RAN"],
        "ticket_categories": [
            {"name": "WVIP", "price": 1500000},
            {"name": "VIP", "price": 900000},
            {"name": "Regular", "price": 350000},
        ],
        "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=1200&q=80",
        "description": "Festival musik malam hari dengan line up besar.",
    },
    {
        "event_id": "60000000-0000-0000-0000-000000000002",
        "event_title": "Bali Summer Sound",
        "event_datetime": datetime(2026, 6, 1, 18, 30),
        "venue_id": "11111111-1111-1111-1111-111111111113",
        "venue_name": "Bali Nusa Dua Convention Center",
        "organizer_id": "40000000-0000-0000-0000-000000000002",
        "organizer_name": "Sunset Wave Organizer",
        "performers": ["Nadin Amizah", "Pamungkas"],
        "ticket_categories": [
            {"name": "VIP", "price": 1250000},
            {"name": "Festival", "price": 500000},
        ],
        "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
        "description": "Konser santai di suasana tropis Bali.",
    },
    {
        "event_id": "60000000-0000-0000-0000-000000000003",
        "event_title": "Indie Night Medan",
        "event_datetime": datetime(2026, 6, 12, 20, 0),
        "venue_id": "11111111-1111-1111-1111-111111111114",
        "venue_name": "Lapangan Merdeka Medan",
        "organizer_id": "40000000-0000-0000-0000-000000000003",
        "organizer_name": "Ruang Bunyi",
        "performers": ["Hindia", "Juicy Luicy"],
        "ticket_categories": [
            {"name": "Early Bird", "price": 175000},
            {"name": "Festival", "price": 250000},
        ],
        "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1200&q=80",
        "description": "Panggung musik indie untuk penikmat lagu malam.",
    },
    {
        "event_id": "60000000-0000-0000-0000-000000000004",
        "event_title": "Classic Harmony Jakarta",
        "event_datetime": datetime(2026, 7, 3, 18, 0),
        "venue_id": "11111111-1111-1111-1111-111111111115",
        "venue_name": "Gedung Kesenian Jakarta",
        "organizer_id": "40000000-0000-0000-0000-000000000001",
        "organizer_name": "PT Nada Penuh Cerita",
        "performers": ["Maliq & D'Essentials"],
        "ticket_categories": [
            {"name": "Premium", "price": 1100000},
            {"name": "Regular", "price": 450000},
        ],
        "image": "https://images.unsplash.com/photo-1487180144351-b8472da7d491?auto=format&fit=crop&w=1200&q=80",
        "description": "Acara musik elegan dengan atmosfer intim.",
    },
    {
        "event_id": "60000000-0000-0000-0000-000000000005",
        "event_title": "Campus Festival Purwokerto",
        "event_datetime": datetime(2026, 7, 20, 16, 0),
        "venue_id": "11111111-1111-1111-1111-111111111111",
        "venue_name": "Jakarta Convention Center",
        "organizer_id": "40000000-0000-0000-0000-000000000004",
        "organizer_name": "Bright Stage ID",
        "performers": ["RAN", "Nadin Amizah"],
        "ticket_categories": [
            {"name": "Festival", "price": 200000},
            {"name": "VIP", "price": 600000},
        ],
        "image": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=1200&q=80",
        "description": "Festival kampus dengan energi penuh dan harga ramah mahasiswa.",
    },
    {
        "event_id": "60000000-0000-0000-0000-000000000006",
        "event_title": "Road To Year End Concert",
        "event_datetime": datetime(2026, 12, 20, 19, 30),
        "venue_id": "11111111-1111-1111-1111-111111111112",
        "venue_name": "Istora Senayan",
        "organizer_id": "40000000-0000-0000-0000-000000000002",
        "organizer_name": "Sunset Wave Organizer",
        "performers": ["Tulus", "Pamungkas", "NOAH"],
        "ticket_categories": [
            {"name": "Platinum", "price": 1750000},
            {"name": "Regular", "price": 400000},
        ],
        "image": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1200&q=80",
        "description": "Penutup tahun dengan konser besar dan panggung megah.",
    },
]


def _can_manage(request):
    user_data = request.session.get("user", {})
    role = user_data.get("role", "")
    return role in ["administrator", "organizer"]


def _find_event(event_id):
    for event in DUMMY_EVENTS:
        if str(event["event_id"]) == str(event_id):
            return event
    return None


def event_list(request):
    q = request.GET.get("q", "").strip().lower()
    venue = request.GET.get("venue", "").strip().lower()

    events = DUMMY_EVENTS[:]

    if q:
        events = [
            e for e in events
            if q in e["event_title"].lower()
            or any(q in p.lower() for p in e["performers"])
            or q in e["description"].lower()
        ]

    if venue:
        events = [e for e in events if e["venue_name"].lower() == venue]

    return render(request, "events/event_list.html", {
        "events": sorted(events, key=lambda x: x["event_datetime"]),
        "venues": sorted({v["venue_name"] for v in DUMMY_VENUES}),
        "q": request.GET.get("q", ""),
        "selected_venue": request.GET.get("venue", ""),
        "can_manage": _can_manage(request),
    })


def event_partial(request):
    return render(request, "events/partials/event_cards.html", {"events": DUMMY_EVENTS})


def event_detail(request, event_id):
    event = _find_event(event_id)
    if not event:
        messages.error(request, "Event tidak ditemukan.")
        return redirect("events:event_list")

    return render(request, "events/event_detail.html", {
        "event": event,
        "can_manage": _can_manage(request),
    })


def event_create(request):
    if not _can_manage(request):
        messages.error(request, "Kamu tidak punya akses untuk membuat event.")
        return redirect("events:event_list")

    if request.method == "POST":
        messages.success(request, "Event berhasil dibuat. Ini masih dummy frontend.")
        return redirect("events:event_list")

    return render(request, "events/partials/event_modal.html", {
        "mode": "create",
        "event": None,
        "venues": DUMMY_VENUES,
        "organizers": DUMMY_ORGANIZERS,
        "performers_text": "",
        "ticket_categories_text": "",
    })


def event_edit(request, event_id):
    if not _can_manage(request):
        messages.error(request, "Kamu tidak punya akses untuk mengubah event.")
        return redirect("events:event_list")

    event = _find_event(event_id)
    if not event:
        messages.error(request, "Event tidak ditemukan.")
        return redirect("events:event_list")

    if request.method == "POST":
        messages.success(request, "Event berhasil diperbarui. Ini masih dummy frontend.")
        return redirect("events:event_list")

    return render(request, "events/partials/event_modal.html", {
        "mode": "edit",
        "event": event,
        "venues": DUMMY_VENUES,
        "organizers": DUMMY_ORGANIZERS,
        "performers_text": ", ".join(event["performers"]),
        "ticket_categories_text": ", ".join([c["name"] for c in event["ticket_categories"]]),
    })


def artist_list(request):
    search = request.GET.get('search', '')
    sql = "SELECT * FROM artist"
    params = []
    if search:
        sql += " WHERE name ILIKE %s OR genre ILIKE %s"
        params = [f'%{search}%', f'%{search}%']
    sql += " ORDER BY name"
    artists = fetch_all(sql, params)
    total_artists = fetch_one("SELECT COUNT(*) as count FROM artist")
    total_genres = fetch_one("SELECT COUNT(DISTINCT genre) as count FROM artist WHERE genre IS NOT NULL")
    total_in_events = fetch_one("SELECT COUNT(DISTINCT artist_id) as count FROM event_artist")
    return render(request, 'events/artist_list.html', {
        'artists': artists,
        'search': search,
        'total_artists': total_artists['count'] if total_artists else 0,
        'total_genres': total_genres['count'] if total_genres else 0,
        'total_in_events': total_in_events['count'] if total_in_events else 0,
    })


def artist_partial(request):
    artists = fetch_all("SELECT * FROM artist ORDER BY name")
    return render(request, 'events/partials/artist_table.html', {'artists': artists})


@role_required('administrator')
def artist_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        genre = request.POST.get('genre', '').strip()
        if not name:
            messages.error(request, 'Nama artist wajib diisi.')
        else:
            execute_query(
                "INSERT INTO artist (artist_id, name, genre) VALUES (gen_random_uuid(), %s, %s)",
                [name, genre or None]
            )
            messages.success(request, 'Artist berhasil ditambahkan.')
            return redirect('artist_list')
    return render(request, 'events/artist_form.html', {'action': 'create'})


@role_required('administrator')
def artist_edit(request, artist_id):
    artist = fetch_one("SELECT * FROM artist WHERE artist_id = %s", [artist_id])
    if not artist:
        return redirect('artist_list')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        genre = request.POST.get('genre', '').strip()
        if not name:
            messages.error(request, 'Nama artist wajib diisi.')
        else:
            execute_query(
                "UPDATE artist SET name=%s, genre=%s WHERE artist_id=%s",
                [name, genre or None, artist_id]
            )
            messages.success(request, 'Artist berhasil diperbarui.')
            return redirect('artist_list')
    return render(request, 'events/artist_form.html', {'action': 'edit', 'artist': artist})


@role_required('administrator')
def artist_delete(request, artist_id):
    artist = fetch_one("SELECT * FROM artist WHERE artist_id = %s", [artist_id])
    if not artist:
        return redirect('artist_list')
    if request.method == 'POST':
        execute_query("DELETE FROM artist WHERE artist_id = %s", [artist_id])
        messages.success(request, 'Artist berhasil dihapus.')
        return redirect('artist_list')
    return render(request, 'events/artist_confirm_delete.html', {'artist': artist})
