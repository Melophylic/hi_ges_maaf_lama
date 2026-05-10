from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

PROMOTIONS = [
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1',
        'promo_code': 'PROMO_TAHUN_BARU',
        'discount_type': 'PERCENTAGE',
        'discount_value': 25.00,
        'start_date': '2026-01-01',
        'end_date': '2026-01-05',
        'usage_limit': 100,
        'used': 44,
    },
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2',
        'promo_code': 'PROMO_VALENTINE',
        'discount_type': 'NOMINAL',
        'discount_value': 14000.00,
        'start_date': '2026-02-14',
        'end_date': '2026-02-15',
        'usage_limit': 50,
        'used': 12,
    },
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee3',
        'promo_code': 'LEBARAN_IDUL_FITRI',
        'discount_type': 'PERCENTAGE',
        'discount_value': 50.00,
        'start_date': '2026-03-20',
        'end_date': '2026-04-05',
        'usage_limit': 200,
        'used': 87,
    },
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee4',
        'promo_code': 'DISKON_PELAJAR',
        'discount_type': 'PERCENTAGE',
        'discount_value': 15.00,
        'start_date': '2026-01-01',
        'end_date': '2026-12-31',
        'usage_limit': 500,
        'used': 156,
    },
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee5',
        'promo_code': 'MEMBER_BARU',
        'discount_type': 'NOMINAL',
        'discount_value': 20000.00,
        'start_date': '2026-01-01',
        'end_date': '2026-12-31',
        'usage_limit': 1000,
        'used': 231,
    },
    {
        'promotion_id': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee6',
        'promo_code': 'FLASH_SALE_MANTAP',
        'discount_type': 'NOMINAL',
        'discount_value': 100000.00,
        'start_date': '2026-04-28',
        'end_date': '2026-04-28',
        'usage_limit': 25,
        'used': 19,
    },
]

DISCOUNT_TYPES = ['PERCENTAGE', 'NOMINAL']
MOCK_ROLE = 'admin'


def get_mock_role(request):
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
    return redirect(f'/promotions/?role={role}')


def promotion_list(request):
    role = get_mock_role(request)
    promotions = list(PROMOTIONS)

    search = request.GET.get('q', '').strip().lower()
    filter_type = request.GET.get('type', 'all')

    if search:
        promotions = [p for p in promotions if search in p['promo_code'].lower()]

    if filter_type in DISCOUNT_TYPES:
        promotions = [p for p in promotions if p['discount_type'] == filter_type]

    total_promos = len(PROMOTIONS)
    total_usage = sum(p['used'] for p in PROMOTIONS)
    total_percentage = sum(1 for p in PROMOTIONS if p['discount_type'] == 'PERCENTAGE')

    return render(request, 'promotions/promotion_list.html', {
        'role': role,
        'promotions': promotions,
        'search': search,
        'filter_type': filter_type,
        'discount_types': DISCOUNT_TYPES,
        'total_promos': total_promos,
        'total_usage': total_usage,
        'total_percentage': total_percentage,
    })


def promotion_create(request):
    role = get_mock_role(request)

    if role != 'admin':
        return JsonResponse({'success': False, 'message': 'Hanya admin yang dapat membuat promo.'}, status=403)

    if request.method == 'POST':
        new_promo = {
            'promotion_id': f'promo-{len(PROMOTIONS) + 1}',
            'promo_code': request.POST.get('promo_code'),
            'discount_type': request.POST.get('discount_type'),
            'discount_value': float(request.POST.get('discount_value')),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'usage_limit': int(request.POST.get('usage_limit')),
            'used': 0,
        }

        PROMOTIONS.insert(0, new_promo)

        if is_ajax(request):
            return JsonResponse({'success': True, 'message': 'Promo baru berhasil dibuat!'})

        messages.success(request, 'Promo baru berhasil dibuat!')
        return redirect_with_role(role)

    return redirect_with_role(role)


def promotion_update(request, promotion_id):
    role = get_mock_role(request)

    if role != 'admin':
        return JsonResponse({'success': False, 'message': 'Hanya admin yang dapat update promo.'}, status=403)

    promotion = next((p for p in PROMOTIONS if p['promotion_id'] == promotion_id), None)

    if not promotion:
        return JsonResponse({'success': False, 'message': 'Promo tidak ditemukan.'}, status=404)

    if request.method == 'POST':
        promotion['promo_code'] = request.POST.get('promo_code')
        promotion['discount_type'] = request.POST.get('discount_type')
        promotion['discount_value'] = float(request.POST.get('discount_value'))
        promotion['start_date'] = request.POST.get('start_date')
        promotion['end_date'] = request.POST.get('end_date')
        promotion['usage_limit'] = int(request.POST.get('usage_limit'))

        if is_ajax(request):
            return JsonResponse({'success': True, 'message': 'Promo berhasil diperbarui!'})

        messages.success(request, 'Promo berhasil diperbarui!')
        return redirect_with_role(role)

    return redirect_with_role(role)


def promotion_delete(request, promotion_id):
    role = get_mock_role(request)

    if role != 'admin':
        return JsonResponse({'success': False, 'message': 'Hanya admin yang dapat delete promo.'}, status=403)

    if request.method == 'POST':
        global PROMOTIONS

        before_count = len(PROMOTIONS)
        PROMOTIONS = [p for p in PROMOTIONS if p['promotion_id'] != promotion_id]

        if len(PROMOTIONS) == before_count:
            return JsonResponse({'success': False, 'message': 'Promo tidak ditemukan.'}, status=404)

        if is_ajax(request):
            return JsonResponse({'success': True, 'message': 'Promo berhasil dihapus!'})

        messages.success(request, 'Promo berhasil dihapus!')
        return redirect_with_role(role)

    return redirect_with_role(role)