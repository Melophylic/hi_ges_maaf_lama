from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

PAYMENT_STATUSES = ['PAID', 'PENDING', 'CANCELLED']

ORDERS = [
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc001',
        'order_date': '2026-04-28 10:00',
        'payment_status': 'PAID',
        'total_amount': 150000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd1',
        'customer_name': 'Budi Santoso',
        'event_name': 'Konser Melodi Senja',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc002',
        'order_date': '2026-04-28 10:05',
        'payment_status': 'PAID',
        'total_amount': 200000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd2',
        'customer_name': 'Siti Rahayu',
        'event_name': 'Festival Seni Budaya',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc003',
        'order_date': '2026-04-28 10:10',
        'payment_status': 'PENDING',
        'total_amount': 75000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd3',
        'customer_name': 'Andi Wijaya',
        'event_name': 'Malam Akustik Bandung',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc004',
        'order_date': '2026-04-28 10:15',
        'payment_status': 'PAID',
        'total_amount': 300000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd4',
        'customer_name': 'Dewi Putri',
        'event_name': 'Konser Melodi Senja',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc005',
        'order_date': '2026-04-28 10:20',
        'payment_status': 'PAID',
        'total_amount': 50000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd5',
        'customer_name': 'Reza Firmansyah',
        'event_name': 'Festival Seni Budaya',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc006',
        'order_date': '2026-04-28 10:25',
        'payment_status': 'CANCELLED',
        'total_amount': 0.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd6',
        'customer_name': 'Maya Indira',
        'event_name': 'Malam Akustik Bandung',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc007',
        'order_date': '2026-04-28 10:30',
        'payment_status': 'PAID',
        'total_amount': 120000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd1',
        'customer_name': 'Budi Santoso',
        'event_name': 'Festival Seni Budaya',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc008',
        'order_date': '2026-04-28 10:35',
        'payment_status': 'PENDING',
        'total_amount': 90000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd2',
        'customer_name': 'Siti Rahayu',
        'event_name': 'Konser Melodi Senja',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc009',
        'order_date': '2026-04-28 10:40',
        'payment_status': 'PAID',
        'total_amount': 45000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd3',
        'customer_name': 'Andi Wijaya',
        'event_name': 'Festival Seni Budaya',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc010',
        'order_date': '2026-04-28 10:45',
        'payment_status': 'PAID',
        'total_amount': 250000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd4',
        'customer_name': 'Dewi Putri',
        'event_name': 'Malam Akustik Bandung',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc011',
        'order_date': '2026-04-28 10:50',
        'payment_status': 'PAID',
        'total_amount': 100000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd5',
        'customer_name': 'Reza Firmansyah',
        'event_name': 'Konser Melodi Senja',
    },
    {
        'order_id': 'cccccccc-cccc-cccc-cccc-ccccccccc012',
        'order_date': '2026-04-28 10:55',
        'payment_status': 'PENDING',
        'total_amount': 30000.00,
        'customer_id': 'dddddddd-dddd-dddd-dddd-ddddddddddd6',
        'customer_name': 'Maya Indira',
        'event_name': 'Festival Seni Budaya',
    },
]

MOCK_ROLE = 'admin'
MOCK_CUSTOMER_ID = 'dddddddd-dddd-dddd-dddd-ddddddddddd1'
ORGANIZER_EVENT_NAMES = ['Konser Melodi Senja', 'Festival Seni Budaya']


def get_role(request):
    user = request.session.get("user")

    if user:
        role = user.get("role")

        if role == "administrator":
            return "admin"

        if role == "organizer":
            return "organizer"

        if role == "customer":
            return "customer"

    return request.GET.get("role", MOCK_ROLE)


def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def redirect_with_role(role):
    return redirect(f'/orders/?role={role}')


def format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")


def order_list(request):
    role = get_role(request)

    role_orders = list(ORDERS)

    if role == 'customer':
        role_orders = [o for o in role_orders if o['customer_id'] == MOCK_CUSTOMER_ID]
    elif role == 'organizer':
        role_orders = [o for o in role_orders if o['event_name'] in ORGANIZER_EVENT_NAMES]

    orders = list(role_orders)

    filter_status = request.GET.get('status', 'all')
    if filter_status in PAYMENT_STATUSES:
        orders = [o for o in orders if o['payment_status'] == filter_status]

    search = request.GET.get('q', '').strip().lower()
    if search:
        orders = [
            o for o in orders
            if search in o['order_id'].lower()
            or search in o['customer_name'].lower()
            or search in o['event_name'].lower()
        ]

    total_orders = len(role_orders)
    total_paid = sum(1 for o in role_orders if o['payment_status'] == 'PAID')
    total_pending = sum(1 for o in role_orders if o['payment_status'] == 'PENDING')
    total_revenue = sum(o['total_amount'] for o in role_orders if o['payment_status'] == 'PAID')

    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'role': role,
        'payment_statuses': PAYMENT_STATUSES,
        'filter_status': filter_status,
        'search': search,
        'total_orders': total_orders,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_revenue_display': format_rupiah(total_revenue),
    })


def checkout(request):
    role = get_role(request)

    if request.method == 'POST':
        if is_ajax(request):
            return JsonResponse({
                'success': True,
                'message': 'Order berhasil dibuat! Status pembayaran: PENDING.'
            })

        messages.success(request, 'Order berhasil dibuat! Status pembayaran: PENDING.')
        return redirect_with_role(role)

    event = {
        'event_title': 'Konser Melodi Senja',
        'event_datetime': '2026-05-15 19:00',
        'venue_name': 'Jakarta Convention Center',
        'artists': ['Fourtwnty', 'Hindia'],
        'categories': [
            {'category_id': 'cat-001', 'category_name': 'WVIP', 'price': 1500000, 'quota': 50, 'used': 3},
            {'category_id': 'cat-002', 'category_name': 'VIP', 'price': 750000, 'quota': 150, 'used': 30},
            {'category_id': 'cat-003', 'category_name': 'Category 1', 'price': 450000, 'quota': 300, 'used': 100},
        ],
        'has_reserved_seating': True,
        'seats': [
            {'seat_id': 'seat-001', 'section': 'VIP', 'row_number': 'B', 'seat_number': '1'},
            {'seat_id': 'seat-002', 'section': 'VIP', 'row_number': 'B', 'seat_number': '2'},
            {'seat_id': 'seat-003', 'section': 'Category 1', 'row_number': 'C', 'seat_number': '5'},
        ],
    }

    return render(request, 'orders/checkout.html', {
        'role': role,
        'event': event,
    })


def order_update(request, order_id):
    role = get_role(request)

    if role != 'admin':
        if is_ajax(request):
            return JsonResponse({'success': False, 'message': 'Hanya admin yang dapat update order.'}, status=403)

        messages.error(request, 'Hanya admin yang dapat update order.')
        return redirect_with_role(role)

    if request.method == 'POST':
        new_status = request.POST.get('payment_status')

        found = False
        for order in ORDERS:
            if order['order_id'] == order_id:
                order['payment_status'] = new_status
                found = True
                break

        if not found:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Order tidak ditemukan.'}, status=404)

            messages.error(request, 'Order tidak ditemukan.')
            return redirect_with_role(role)

        if is_ajax(request):
            return JsonResponse({
                'success': True,
                'message': f'Order berhasil diupdate menjadi {new_status}.'
            })

        messages.success(request, f'Order berhasil diupdate menjadi {new_status}.')
        return redirect_with_role(role)

    return redirect_with_role(role)


def order_delete(request, order_id):
    role = get_role(request)

    if role != 'admin':
        if is_ajax(request):
            return JsonResponse({'success': False, 'message': 'Hanya admin yang dapat delete order.'}, status=403)

        messages.error(request, 'Hanya admin yang dapat delete order.')
        return redirect_with_role(role)

    if request.method == 'POST':
        global ORDERS

        before_count = len(ORDERS)
        ORDERS = [order for order in ORDERS if order['order_id'] != order_id]

        if len(ORDERS) == before_count:
            if is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Order tidak ditemukan.'}, status=404)

            messages.error(request, 'Order tidak ditemukan.')
            return redirect_with_role(role)

        if is_ajax(request):
            return JsonResponse({
                'success': True,
                'message': 'Order berhasil dihapus.'
            })

        messages.success(request, 'Order berhasil dihapus.')
        return redirect_with_role(role)

    return redirect_with_role(role)