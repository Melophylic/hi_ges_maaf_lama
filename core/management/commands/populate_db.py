import uuid
from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.db import execute_query, fetch_one


class Command(BaseCommand):
    help = 'Populate database with dummy data meeting minimum requirements'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        self._clear()

        self.stdout.write('Seeding roles...')
        roles = self._seed_roles()

        self.stdout.write('Seeding users...')
        users = self._seed_users()

        self.stdout.write('Seeding account roles...')
        self._seed_account_roles(users, roles)

        self.stdout.write('Seeding venues...')
        venues = self._seed_venues()

        self.stdout.write('Seeding seats...')
        seats = self._seed_seats(venues)

        self.stdout.write('Seeding artists...')
        artists = self._seed_artists()

        self.stdout.write('Seeding events...')
        events = self._seed_events(venues, users['organizer_ids'])

        self.stdout.write('Seeding event artists...')
        self._seed_event_artists(events, artists)

        self.stdout.write('Seeding ticket categories...')
        categories = self._seed_ticket_categories(events)

        self.stdout.write('Seeding promotions...')
        promotions = self._seed_promotions()

        self.stdout.write('Seeding orders...')
        orders = self._seed_orders(users['customer_ids'])

        self.stdout.write('Seeding order promotions...')
        self._seed_order_promotions(orders, promotions)

        self.stdout.write('Seeding tickets...')
        tickets = self._seed_tickets(orders, categories)

        self.stdout.write('Seeding seat-ticket relationships...')
        self._seed_has_relationships(tickets, seats)

        self.stdout.write(self.style.SUCCESS(
            '\nDatabase populated successfully!\n'
            'Login credentials (all passwords: password123):\n'
            '  Admin     -> username: admin\n'
            '  Organizer -> username: organizer1\n'
            '  Customer  -> username: customer1\n'
        ))

    # ------------------------------------------------------------------ helpers

    def _uid(self):
        return str(uuid.uuid4())

    def _clear(self):
        tables = [
            'has_relationship', 'ticket', 'order_promotion',
            '"order"', 'promotion', 'ticket_category',
            'event_artist', 'event', 'artist', 'seat',
            'venue', 'account_role', 'customer', 'organizer',
            'user_account', 'role',
        ]
        for t in tables:
            execute_query(f'DELETE FROM {t}')

    # ------------------------------------------------------------------ seeds

    def _seed_roles(self):
        roles = {
            'administrator': self._uid(),
            'organizer': self._uid(),
            'customer': self._uid(),
        }
        for name, rid in roles.items():
            execute_query(
                "INSERT INTO role (role_id, role_name) VALUES (%s, %s)",
                [rid, name]
            )
        return roles

    def _seed_users(self):
        hashed = make_password('password123')
        admins, organizers, customers = [], [], []

        # 2 admins
        for i in range(1, 3):
            uid = self._uid()
            execute_query(
                "INSERT INTO user_account (user_id, username, password) VALUES (%s, %s, %s)",
                [uid, f'admin{i}' if i > 1 else 'admin', hashed]
            )
            admins.append(uid)

        # 4 organizers
        for i in range(1, 5):
            uid = self._uid()
            execute_query(
                "INSERT INTO user_account (user_id, username, password) VALUES (%s, %s, %s)",
                [uid, f'organizer{i}', hashed]
            )
            organizers.append(uid)

        # 6 customers
        for i in range(1, 7):
            uid = self._uid()
            execute_query(
                "INSERT INTO user_account (user_id, username, password) VALUES (%s, %s, %s)",
                [uid, f'customer{i}', hashed]
            )
            customers.append(uid)

        # Insert customer profiles (6)
        customer_names = [
            ('Budi Santoso', '081234567890'),
            ('Siti Rahayu', '082345678901'),
            ('Ahmad Fauzi', '083456789012'),
            ('Dewi Lestari', '084567890123'),
            ('Rizky Pratama', '085678901234'),
            ('Nurul Hidayah', '086789012345'),
        ]
        customer_ids = []
        for uid, (name, phone) in zip(customers, customer_names):
            cid = self._uid()
            execute_query(
                "INSERT INTO customer (customer_id, full_name, phone_number, user_id) VALUES (%s, %s, %s, %s)",
                [cid, name, phone, uid]
            )
            customer_ids.append(cid)

        # Insert organizer profiles (4)
        organizer_names = [
            ('Promotor Nusantara', 'promo.nusantara@email.com'),
            ('Event Spektakuler', 'event.spektakuler@email.com'),
            ('Konser Indonesia', 'konser.id@email.com'),
            ('Entertainment Pro', 'entertain.pro@email.com'),
        ]
        organizer_ids = []
        for uid, (name, email) in zip(organizers, organizer_names):
            oid = self._uid()
            execute_query(
                "INSERT INTO organizer (organizer_id, organizer_name, contact_email, user_id) VALUES (%s, %s, %s, %s)",
                [oid, name, email, uid]
            )
            organizer_ids.append(oid)

        return {
            'admin_uids': admins,
            'organizer_uids': organizers,
            'customer_uids': customers,
            'organizer_ids': organizer_ids,
            'customer_ids': customer_ids,
        }

    def _seed_account_roles(self, users, roles):
        # 2 admins → 2 entries
        for uid in users['admin_uids']:
            execute_query(
                "INSERT INTO account_role (role_id, user_id) VALUES (%s, %s)",
                [roles['administrator'], uid]
            )
        # 4 organizers → 4 entries
        for uid in users['organizer_uids']:
            execute_query(
                "INSERT INTO account_role (role_id, user_id) VALUES (%s, %s)",
                [roles['organizer'], uid]
            )
        # 6 customers → 6 entries
        for uid in users['customer_uids']:
            execute_query(
                "INSERT INTO account_role (role_id, user_id) VALUES (%s, %s)",
                [roles['customer'], uid]
            )
        # 3 dual-role: first 3 organizers also get customer role → 3 more = total 15
        for uid in users['organizer_uids'][:3]:
            execute_query(
                "INSERT INTO account_role (role_id, user_id) VALUES (%s, %s)",
                [roles['customer'], uid]
            )

    def _seed_venues(self):
        data = [
            ('Gelora Bung Karno', 80000, 'Jl. Pintu Satu Senayan', 'Jakarta', True),
            ('Trans Studio Bandung', 10000, 'Jl. Gatot Subroto No.289', 'Bandung', True),
            ('Istora Senayan', 7500, 'Jl. Pintu VI Senayan', 'Jakarta', False),
            ('Tennis Indoor Senayan', 5000, 'Jl. Pintu IX Senayan', 'Jakarta', True),
            ('Balai Sarbini', 3000, 'Jl. Jenderal Sudirman Kav.1', 'Jakarta', False),
        ]
        ids = []
        for name, cap, addr, city, _ in data:
            vid = self._uid()
            execute_query(
                "INSERT INTO venue (venue_id, venue_name, capacity, address, city) VALUES (%s, %s, %s, %s, %s)",
                [vid, name, cap, addr, city]
            )
            ids.append(vid)
        return ids

    def _seed_seats(self, venues):
        seats = []
        sections = ['VIP', 'CAT1', 'CAT2']
        count = 0
        for vid in venues:
            for section in sections:
                for row in ['A', 'B']:
                    for num in range(1, 4):
                        if count >= 30:
                            break
                        sid = self._uid()
                        execute_query(
                            "INSERT INTO seat (seat_id, section, seat_number, row_number, venue_id) VALUES (%s, %s, %s, %s, %s)",
                            [sid, section, str(num), row, vid]
                        )
                        seats.append({'id': sid, 'venue_id': vid})
                        count += 1
                    if count >= 30:
                        break
                if count >= 30:
                    break
            if count >= 30:
                break
        return seats

    def _seed_artists(self):
        data = [
            ('Raisa', 'Pop'),
            ('Tulus', 'Pop'),
            ('Dewa 19', 'Rock'),
            ('Noah', 'Pop Rock'),
            ('Coldplay', 'Alternative Rock'),
            ('Ed Sheeran', 'Pop'),
            ('Sheila on 7', 'Pop'),
            ('Payung Teduh', 'Folk'),
        ]
        ids = []
        for name, genre in data:
            aid = self._uid()
            execute_query(
                "INSERT INTO artist (artist_id, name, genre) VALUES (%s, %s, %s)",
                [aid, name, genre]
            )
            ids.append(aid)
        return ids

    def _seed_events(self, venues, organizer_ids):
        data = [
            ('Konser Raisa - Hati yang Sejuk', 0, 0),
            ('Tulus Live in Concert', 1, 1),
            ('Dewa 19 Reunion Tour', 2, 2),
            ('Noah - 10 Tahun Bersama', 0, 3),
            ('Coldplay Music of the Spheres', 3, 0),
            ('Ed Sheeran Mathematics Tour', 4, 1),
        ]
        ids = []
        base_date = datetime(2026, 5, 1, 19, 0)
        for i, (title, v_idx, o_idx) in enumerate(data):
            eid = self._uid()
            event_dt = base_date + timedelta(days=i * 14)
            execute_query(
                "INSERT INTO event (event_id, event_datetime, event_title, venue_id, organizer_id) VALUES (%s, %s, %s, %s, %s)",
                [eid, event_dt, title, venues[v_idx], organizer_ids[o_idx]]
            )
            ids.append(eid)
        return ids

    def _seed_event_artists(self, events, artists):
        pairs = [
            (0, 0, 'Headliner'), (0, 6, 'Opening Act'),
            (1, 1, 'Headliner'), (1, 7, 'Opening Act'),
            (2, 2, 'Headliner'), (2, 3, 'Supporting'),
            (3, 3, 'Headliner'), (3, 6, 'Opening Act'),
            (4, 4, 'Headliner'), (4, 5, 'Supporting'),
            (5, 5, 'Headliner'), (5, 0, 'Opening Act'),
        ]
        for e_idx, a_idx, role in pairs:
            execute_query(
                "INSERT INTO event_artist (event_id, artist_id, role) VALUES (%s, %s, %s)",
                [events[e_idx], artists[a_idx], role]
            )

    def _seed_ticket_categories(self, events):
        tiers = [
            ('WVIP', 2500000, 50),
            ('VIP', 1500000, 100),
            ('CAT1', 750000, 200),
        ]
        ids = []
        count = 0
        for eid in events:
            for name, price, quota in tiers:
                if count >= 14:
                    break
                cid = self._uid()
                execute_query(
                    "INSERT INTO ticket_category (category_id, category_name, quota, price, tevent_id) VALUES (%s, %s, %s, %s, %s)",
                    [cid, name, quota, price, eid]
                )
                ids.append({'id': cid, 'event_id': eid, 'price': price})
                count += 1
            if count >= 14:
                break
        return ids

    def _seed_promotions(self):
        data = [
            ('EARLYBIRD', 'PERCENTAGE', 20, date(2026, 4, 1), date(2026, 4, 30), 100),
            ('DISKON50K', 'NOMINAL', 50000, date(2026, 4, 1), date(2026, 5, 31), 200),
            ('VIP25OFF', 'PERCENTAGE', 25, date(2026, 4, 15), date(2026, 5, 15), 50),
            ('FLASH100K', 'NOMINAL', 100000, date(2026, 4, 21), date(2026, 4, 22), 30),
            ('STUDENT10', 'PERCENTAGE', 10, date(2026, 4, 1), date(2026, 6, 30), 500),
            ('WELCOMENEW', 'NOMINAL', 75000, date(2026, 4, 1), date(2026, 12, 31), 1000),
        ]
        ids = []
        for code, dtype, dval, start, end, limit in data:
            pid = self._uid()
            execute_query(
                "INSERT INTO promotion (promotion_id, promo_code, discount_type, discount_value, start_date, end_date, usage_limit) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [pid, code, dtype, dval, start, end, limit]
            )
            ids.append(pid)
        return ids

    def _seed_orders(self, customer_ids):
        statuses = ['Pending', 'Paid', 'Cancelled']
        ids = []
        base_date = datetime(2026, 4, 1, 10, 0)
        for i in range(12):
            oid = self._uid()
            cid = customer_ids[i % len(customer_ids)]
            status = statuses[i % 3]
            order_date = base_date + timedelta(days=i * 2)
            total = 750000 * (1 + i % 3)
            execute_query(
                "INSERT INTO \"order\" (order_id, order_date, payment_status, total_amount, customer_id) VALUES (%s, %s, %s, %s, %s)",
                [oid, order_date, status, total, cid]
            )
            ids.append(oid)
        return ids

    def _seed_order_promotions(self, orders, promotions):
        pairs = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        for o_idx, p_idx in pairs:
            opid = self._uid()
            execute_query(
                "INSERT INTO order_promotion (order_promotion_id, promotion_id, order_id) VALUES (%s, %s, %s)",
                [opid, promotions[p_idx], orders[o_idx]]
            )

    def _seed_tickets(self, orders, categories):
        ids = []
        count = 0
        for i, oid in enumerate(orders):
            cat = categories[i % len(categories)]
            for j in range(2):
                if count >= 20:
                    break
                tid = self._uid()
                code = f'TTT-{count+1:04d}-{tid[:8].upper()}'
                execute_query(
                    "INSERT INTO ticket (ticket_id, ticket_code, tcategory_id, torder_id) VALUES (%s, %s, %s, %s)",
                    [tid, code, cat['id'], oid]
                )
                ids.append(tid)
                count += 1
            if count >= 20:
                break
        return ids

    def _seed_has_relationships(self, tickets, seats):
        for i in range(min(10, len(tickets), len(seats))):
            execute_query(
                "INSERT INTO has_relationship (seat_id, ticket_id) VALUES (%s, %s)",
                [seats[i]['id'], tickets[i]]
            )
