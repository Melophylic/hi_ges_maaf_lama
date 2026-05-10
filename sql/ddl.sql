-- TikTakTuk DDL
-- PostgreSQL schema — run once on a fresh database

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- DROP (reverse dependency order)
-- ============================================================
DROP TABLE IF EXISTS HAS_RELATIONSHIP  CASCADE;
DROP TABLE IF EXISTS TICKET            CASCADE;
DROP TABLE IF EXISTS ORDER_PROMOTION   CASCADE;
DROP TABLE IF EXISTS "ORDER"           CASCADE;
DROP TABLE IF EXISTS TICKET_CATEGORY   CASCADE;
DROP TABLE IF EXISTS EVENT_ARTIST      CASCADE;
DROP TABLE IF EXISTS EVENT             CASCADE;
DROP TABLE IF EXISTS ARTIST            CASCADE;
DROP TABLE IF EXISTS SEAT              CASCADE;
DROP TABLE IF EXISTS VENUE             CASCADE;
DROP TABLE IF EXISTS PROMOTION         CASCADE;
DROP TABLE IF EXISTS ORGANIZER         CASCADE;
DROP TABLE IF EXISTS CUSTOMER          CASCADE;
DROP TABLE IF EXISTS ACCOUNT_ROLE      CASCADE;
DROP TABLE IF EXISTS ROLE              CASCADE;
DROP TABLE IF EXISTS USER_ACCOUNT      CASCADE;
DROP TABLE IF EXISTS django_session    CASCADE;

-- ============================================================
-- DJANGO SESSION (required by session middleware)
-- ============================================================
CREATE TABLE django_session (
    session_key  VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT        NOT NULL,
    expire_date  TIMESTAMPTZ NOT NULL
);
CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);

-- ============================================================
-- USERS & ROLES
-- ============================================================
CREATE TABLE USER_ACCOUNT (
    user_id  UUID         PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE ROLE (
    role_id   UUID        PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE ACCOUNT_ROLE (
    role_id UUID NOT NULL,
    user_id UUID NOT NULL,
    PRIMARY KEY (role_id, user_id),
    CONSTRAINT fk_accountrole_role FOREIGN KEY (role_id) REFERENCES ROLE(role_id)    ON DELETE CASCADE,
    CONSTRAINT fk_accountrole_user FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id) ON DELETE CASCADE
);

CREATE TABLE CUSTOMER (
    customer_id  UUID         PRIMARY KEY,
    full_name    VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    user_id      UUID         NOT NULL,
    CONSTRAINT fk_useracc FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE ORGANIZER (
    organizer_id   UUID         PRIMARY KEY,
    organizer_name VARCHAR(100) NOT NULL,
    contact_email  VARCHAR(100),
    user_id        UUID         NOT NULL UNIQUE,
    CONSTRAINT fk_organizer_user FOREIGN KEY (user_id) REFERENCES USER_ACCOUNT(user_id)
);

-- ============================================================
-- VENUE & SEAT
-- ============================================================
CREATE TABLE VENUE (
    venue_id   UUID         PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    capacity   INTEGER      NOT NULL CHECK (capacity > 0),
    address    TEXT         NOT NULL,
    city       VARCHAR(100) NOT NULL
);

CREATE TABLE SEAT (
    seat_id     UUID        PRIMARY KEY,
    section     VARCHAR(50) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    row_number  VARCHAR(10) NOT NULL,
    venue_id    UUID        NOT NULL,
    CONSTRAINT fk_venue         FOREIGN KEY (venue_id) REFERENCES VENUE(venue_id) ON DELETE RESTRICT,
    CONSTRAINT uq_seat_position UNIQUE (venue_id, section, row_number, seat_number)
);

-- ============================================================
-- ARTIST & EVENT
-- ============================================================
CREATE TABLE ARTIST (
    artist_id UUID         PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    genre     VARCHAR(100)
);

CREATE TABLE EVENT (
    event_id       UUID         PRIMARY KEY,
    event_datetime TIMESTAMP    NOT NULL,
    event_title    VARCHAR(200) NOT NULL,
    venue_id       UUID         NOT NULL,
    organizer_id   UUID         NOT NULL,
    CONSTRAINT fk_event_venue     FOREIGN KEY (venue_id)     REFERENCES VENUE(venue_id),
    CONSTRAINT fk_event_organizer FOREIGN KEY (organizer_id) REFERENCES ORGANIZER(organizer_id)
);

CREATE TABLE EVENT_ARTIST (
    event_id  UUID         NOT NULL,
    artist_id UUID         NOT NULL,
    role      VARCHAR(100),
    PRIMARY KEY (event_id, artist_id),
    CONSTRAINT fk_eventartist_event  FOREIGN KEY (event_id)  REFERENCES EVENT(event_id)   ON DELETE CASCADE,
    CONSTRAINT fk_eventartist_artist FOREIGN KEY (artist_id) REFERENCES ARTIST(artist_id) ON DELETE CASCADE
);

-- ============================================================
-- TICKET
-- ============================================================
CREATE TABLE TICKET_CATEGORY (
    category_id   UUID          PRIMARY KEY,
    category_name VARCHAR(50)   NOT NULL,
    quota         INTEGER       NOT NULL CHECK (quota > 0),
    price         NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    tevent_id     UUID          NOT NULL,
    CONSTRAINT fk_ticketcat_event FOREIGN KEY (tevent_id) REFERENCES EVENT(event_id) ON DELETE RESTRICT
);

-- ============================================================
-- PROMOTION & ORDER
-- ============================================================
CREATE TABLE PROMOTION (
    promotion_id   UUID          PRIMARY KEY,
    promo_code     VARCHAR(50)   UNIQUE NOT NULL,
    discount_type  VARCHAR(20)   NOT NULL CHECK (discount_type IN ('NOMINAL', 'PERCENTAGE')),
    discount_value NUMERIC(12,2) NOT NULL CHECK (discount_value > 0),
    start_date     DATE          NOT NULL,
    end_date       DATE          NOT NULL,
    usage_limit    INTEGER       NOT NULL CHECK (usage_limit > 0)
);

CREATE TABLE "ORDER" (
    order_id       UUID          PRIMARY KEY,
    order_date     TIMESTAMP     NOT NULL,
    payment_status VARCHAR(20)   NOT NULL,
    total_amount   NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    customer_id    UUID          NOT NULL,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE ORDER_PROMOTION (
    order_promotion_id UUID PRIMARY KEY,
    promotion_id       UUID NOT NULL,
    order_id           UUID NOT NULL,
    CONSTRAINT fk_promotion FOREIGN KEY (promotion_id) REFERENCES PROMOTION(promotion_id),
    CONSTRAINT fk_order     FOREIGN KEY (order_id)     REFERENCES "ORDER"(order_id)
);

CREATE TABLE TICKET (
    ticket_id    UUID         PRIMARY KEY,
    ticket_code  VARCHAR(100) UNIQUE NOT NULL,
    tcategory_id UUID         NOT NULL,
    torder_id    UUID         NOT NULL,
    CONSTRAINT fk_tcategory FOREIGN KEY (tcategory_id) REFERENCES TICKET_CATEGORY(category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_torder    FOREIGN KEY (torder_id)    REFERENCES "ORDER"(order_id)             ON DELETE RESTRICT
);

CREATE TABLE HAS_RELATIONSHIP (
    seat_id   UUID NOT NULL,
    ticket_id UUID NOT NULL,
    PRIMARY KEY (seat_id, ticket_id),
    CONSTRAINT fk_seat   FOREIGN KEY (seat_id)   REFERENCES SEAT(seat_id)     ON DELETE CASCADE,
    CONSTRAINT fk_ticket FOREIGN KEY (ticket_id) REFERENCES TICKET(ticket_id) ON DELETE CASCADE,
    CONSTRAINT uq_has_relationship_seat   UNIQUE (seat_id),
    CONSTRAINT uq_has_relationship_ticket UNIQUE (ticket_id)
);

-- ============================================================
-- DUMMY DATA
-- ============================================================

-- ROLE
INSERT INTO ROLE (role_id, role_name) VALUES
    ('00000000-0000-0000-0000-000000000101', 'administrator'),
    ('00000000-0000-0000-0000-000000000102', 'organizer'),
    ('00000000-0000-0000-0000-000000000103', 'customer');

-- USER_ACCOUNT
INSERT INTO USER_ACCOUNT (user_id, username, password) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'syafiq',     'panjangpanjangin'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'nadzim',     'programmerhandal'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'elizabeth',  'artisdepok'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'rashika',    'kalimantan'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'jebungsz',   'bungamawar'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6', 'gilangbiru', 'bluespax'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa7', 'putri',      'lastname'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa8', 'momotwice',  'blondehair'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa9', 'jihyotwice', 'mantandaniel'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', 'kahitna',    'lagulampau'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', 'tulus',      'gongisme'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12', 'raisa',      'aquagalon');

-- ACCOUNT_ROLE
INSERT INTO ACCOUNT_ROLE (role_id, user_id) VALUES
    -- administrator
    ('00000000-0000-0000-0000-000000000101', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa7'),
    -- organizers
    ('00000000-0000-0000-0000-000000000102', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
    ('00000000-0000-0000-0000-000000000102', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'),
    ('00000000-0000-0000-0000-000000000102', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa9'),
    ('00000000-0000-0000-0000-000000000102', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12'),
    -- customers
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa8'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa9'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10'),
    ('00000000-0000-0000-0000-000000000103', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11');

-- CUSTOMER
INSERT INTO CUSTOMER (customer_id, full_name, phone_number, user_id) VALUES
    ('dddddddd-dddd-dddd-dddd-ddddddddddd1', 'Syafiq Faqih',      '08123456789', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
    ('dddddddd-dddd-dddd-dddd-ddddddddddd2', 'Nadzim',            '08122222222', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
    ('dddddddd-dddd-dddd-dddd-ddddddddddd3', 'Elizabeth Meilanny','08133333333', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'),
    ('dddddddd-dddd-dddd-dddd-ddddddddddd4', 'Rashika Maharani',  '08144444444', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4'),
    ('dddddddd-dddd-dddd-dddd-ddddddddddd5', 'Jenisa Bunga',      '08155555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa5'),
    ('dddddddd-dddd-dddd-dddd-ddddddddddd6', 'Gilang Adjie',      '08166666666', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6');

-- ORGANIZER
INSERT INTO ORGANIZER (organizer_id, organizer_name, contact_email, user_id) VALUES
    ('40000000-0000-0000-0000-000000000001', 'PT Nada Penuh Cerita', 'hello@nadapenuhcerta.com', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
    ('40000000-0000-0000-0000-000000000002', 'Sunset Wave Organizer','contact@sunsetwave.id',    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa6'),
    ('40000000-0000-0000-0000-000000000003', 'Ruang Bunyi',          'info@ruangbunyi.id',       'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa9'),
    ('40000000-0000-0000-0000-000000000004', 'Bright Stage ID',      'admin@brightstage.id',     'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12');

-- VENUE
INSERT INTO VENUE (venue_id, venue_name, capacity, address, city) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Jakarta Convention Center',       5000,  'Jl. Gatot Subroto, Jakarta',          'Jakarta'),
    ('11111111-1111-1111-1111-111111111112', 'Istora Senayan',                  12000, 'Jl. Pintu Satu Senayan, Gelora',      'Jakarta'),
    ('11111111-1111-1111-1111-111111111113', 'Bali Nusa Dua Convention Center', 8000,  'Kawasan Pariwisata Nusa Dua',         'Bali'),
    ('11111111-1111-1111-1111-111111111114', 'Lapangan Merdeka Medan',          15000, 'Jl. Pulau Pinang',                    'Medan'),
    ('11111111-1111-1111-1111-111111111115', 'Gedung Kesenian Jakarta',         2000,  'Jl. Gedung Kesenian No.1',            'Jakarta');

-- SEAT
INSERT INTO SEAT (seat_id, section, seat_number, row_number, venue_id) VALUES
    ('00000000-0000-0000-0000-000000000001', 'WVIP',    '1',  'A', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000002', 'WVIP',    '2',  'A', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000003', 'WVIP',    '3',  'A', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000004', 'WVIP',    '4',  'A', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000005', 'WVIP',    '5',  'A', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000006', 'VIP',     '1',  'B', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000007', 'VIP',     '2',  'B', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000008', 'VIP',     '3',  'B', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000009', 'VIP',     '4',  'B', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000010', 'VIP',     '5',  'B', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000011', 'REGULER', '1',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000012', 'REGULER', '2',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000013', 'REGULER', '3',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000014', 'REGULER', '4',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000015', 'REGULER', '5',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000016', 'REGULER', '6',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000017', 'REGULER', '7',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000018', 'REGULER', '8',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000019', 'REGULER', '9',  'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000020', 'REGULER', '10', 'C', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000021', 'FESTIVAL','1',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000022', 'FESTIVAL','2',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000023', 'FESTIVAL','3',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000024', 'FESTIVAL','4',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000025', 'FESTIVAL','5',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000026', 'FESTIVAL','6',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000027', 'FESTIVAL','7',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000028', 'FESTIVAL','8',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000029', 'FESTIVAL','9',  'D', '11111111-1111-1111-1111-111111111111'),
    ('00000000-0000-0000-0000-000000000030', 'FESTIVAL','10', 'D', '11111111-1111-1111-1111-111111111111');

-- ARTIST
INSERT INTO ARTIST (artist_id, name, genre) VALUES
    ('00000000-0000-0000-0000-000000000201', 'Fourtwnty',    'Indie Folk'),
    ('00000000-0000-0000-0000-000000000202', 'Hindia',       'Indie Pop'),
    ('00000000-0000-0000-0000-000000000203', 'Tulus',        'Pop'),
    ('00000000-0000-0000-0000-000000000204', 'Raisa',        'Pop'),
    ('00000000-0000-0000-0000-000000000205', 'Pamungkas',    'Singer-Songwriter'),
    ('00000000-0000-0000-0000-000000000206', 'Nadin Amizah', 'Folk'),
    ('00000000-0000-0000-0000-000000000207', 'Sheila On 7',  'Rock'),
    ('00000000-0000-0000-0000-000000000208', 'Dewa 19',      'Rock');

-- EVENT
INSERT INTO EVENT (event_id, event_datetime, event_title, venue_id, organizer_id) VALUES
    ('60000000-0000-0000-0000-000000000001', '2026-05-10 19:00:00', 'Jakarta Music Fest 2026',     '11111111-1111-1111-1111-111111111112', '40000000-0000-0000-0000-000000000001'),
    ('60000000-0000-0000-0000-000000000002', '2026-06-01 18:30:00', 'Bali Summer Sound',           '11111111-1111-1111-1111-111111111113', '40000000-0000-0000-0000-000000000002'),
    ('60000000-0000-0000-0000-000000000003', '2026-06-12 20:00:00', 'Indie Night Medan',           '11111111-1111-1111-1111-111111111114', '40000000-0000-0000-0000-000000000003'),
    ('60000000-0000-0000-0000-000000000004', '2026-07-03 18:00:00', 'Classic Harmony Jakarta',     '11111111-1111-1111-1111-111111111115', '40000000-0000-0000-0000-000000000001'),
    ('60000000-0000-0000-0000-000000000005', '2026-07-20 16:00:00', 'Campus Festival Purwokerto',  '11111111-1111-1111-1111-111111111111', '40000000-0000-0000-0000-000000000004'),
    ('60000000-0000-0000-0000-000000000006', '2026-12-20 19:30:00', 'Road To Year End Concert',    '11111111-1111-1111-1111-111111111112', '40000000-0000-0000-0000-000000000002');

-- EVENT_ARTIST
INSERT INTO EVENT_ARTIST (event_id, artist_id, role) VALUES
    ('60000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000201', 'Performer'),
    ('60000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000202', 'Performer'),
    ('60000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000203', 'Headliner'),
    ('60000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000204', 'Headliner'),
    ('60000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000205', 'Performer'),
    ('60000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000201', 'Performer'),
    ('60000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000206', 'Headliner'),
    ('60000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000203', 'Headliner'),
    ('60000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000204', 'Performer'),
    ('60000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000202', 'Performer'),
    ('60000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000205', 'Headliner'),
    ('60000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000207', 'Headliner'),
    ('60000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000208', 'Performer');

-- TICKET_CATEGORY
INSERT INTO TICKET_CATEGORY (category_id, category_name, quota, price, tevent_id) VALUES
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'WVIP',    50,    2000000.00, '60000000-0000-0000-0000-000000000005'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'VIP',     150,    750000.00, '60000000-0000-0000-0000-000000000005'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'REGULER', 1000,   150000.00, '60000000-0000-0000-0000-000000000005'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'FESTIVAL',2000,    50000.00, '60000000-0000-0000-0000-000000000005'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb005', 'WVIP',    100,  3000000.00, '60000000-0000-0000-0000-000000000001'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb006', 'VIP',     500,  1500000.00, '60000000-0000-0000-0000-000000000001'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb007', 'REGULER', 3000,  500000.00, '60000000-0000-0000-0000-000000000001'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb008', 'VIP',     300,  1500000.00, '60000000-0000-0000-0000-000000000002'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb009', 'REGULER', 2000,  400000.00, '60000000-0000-0000-0000-000000000002'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb010', 'VIP',     500,   300000.00, '60000000-0000-0000-0000-000000000003'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb011', 'REGULER', 5000,  100000.00, '60000000-0000-0000-0000-000000000003'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb012', 'VIP',     200,   800000.00, '60000000-0000-0000-0000-000000000004'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb013', 'REGULER', 800,   250000.00, '60000000-0000-0000-0000-000000000004'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb014', 'REGULER', 5000,  750000.00, '60000000-0000-0000-0000-000000000006');

-- PROMOTION
INSERT INTO PROMOTION (promotion_id, promo_code, discount_type, discount_value, start_date, end_date, usage_limit) VALUES
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 'PROMO_TAHUN_BARU',   'PERCENTAGE', 25.00,    '2026-01-01', '2026-01-05',  100),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2', 'PROMO_VALENTINE',    'NOMINAL',    14000.00, '2026-02-14', '2026-02-15',  50),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee3', 'LEBARAN_IDUL_FITRI', 'PERCENTAGE', 50.00,    '2026-03-20', '2026-04-05',  200),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee4', 'DISKON_PELAJAR',     'PERCENTAGE', 15.00,    '2026-01-01', '2026-12-31',  500),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee5', 'MEMBER_BARU',        'NOMINAL',    20000.00, '2026-01-01', '2026-12-31',  1000),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee6', 'FLASH_SALE_MANTAP',  'NOMINAL',    100000.00,'2026-04-28', '2026-04-28',  25);

-- ORDER
INSERT INTO "ORDER" (order_id, order_date, payment_status, total_amount, customer_id) VALUES
    ('cccccccc-cccc-cccc-cccc-ccccccccc001', NOW(), 'PAID',      150000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd1'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc002', NOW(), 'PAID',      200000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd2'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc003', NOW(), 'PENDING',    75000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd3'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc004', NOW(), 'PAID',      300000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd4'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc005', NOW(), 'PAID',       50000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd5'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc006', NOW(), 'CANCELLED',      0.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd6'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc007', NOW(), 'PAID',      120000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd1'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc008', NOW(), 'PENDING',    90000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd2'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc009', NOW(), 'PAID',       45000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd3'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc010', NOW(), 'PAID',      250000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd4'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc011', NOW(), 'PAID',      100000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd5'),
    ('cccccccc-cccc-cccc-cccc-ccccccccc012', NOW(), 'PENDING',    30000.00, 'dddddddd-dddd-dddd-dddd-ddddddddddd6');

-- ORDER_PROMOTION
INSERT INTO ORDER_PROMOTION (order_promotion_id, promotion_id, order_id) VALUES
    ('ffffffff-ffff-ffff-ffff-fffffffffff1', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('ffffffff-ffff-ffff-ffff-fffffffffff2', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('ffffffff-ffff-ffff-ffff-fffffffffff3', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee3', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('ffffffff-ffff-ffff-ffff-fffffffffff4', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee4', 'cccccccc-cccc-cccc-cccc-ccccccccc004'),
    ('ffffffff-ffff-ffff-ffff-fffffffffff5', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee5', 'cccccccc-cccc-cccc-cccc-ccccccccc007');

-- TICKET
INSERT INTO TICKET (ticket_id, ticket_code, tcategory_id, torder_id) VALUES
    ('11111111-1111-1111-1111-111111111101', 'TIK-A001', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('11111111-1111-1111-1111-111111111102', 'TIK-A002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('11111111-1111-1111-1111-111111111103', 'TIK-A003', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('11111111-1111-1111-1111-111111111104', 'TIK-A004', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('11111111-1111-1111-1111-111111111105', 'TIK-A005', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('11111111-1111-1111-1111-111111111106', 'TIK-B001', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('11111111-1111-1111-1111-111111111107', 'TIK-B002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'cccccccc-cccc-cccc-cccc-ccccccccc004'),
    ('11111111-1111-1111-1111-111111111108', 'TIK-B003', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'cccccccc-cccc-cccc-cccc-ccccccccc004'),
    ('11111111-1111-1111-1111-111111111109', 'TIK-B004', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('11111111-1111-1111-1111-111111111110', 'TIK-B005', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('11111111-1111-1111-1111-111111111121', 'TIK-C001', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('11111111-1111-1111-1111-111111111122', 'TIK-C002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'cccccccc-cccc-cccc-cccc-ccccccccc004'),
    ('11111111-1111-1111-1111-111111111123', 'TIK-C003', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('11111111-1111-1111-1111-111111111124', 'TIK-C004', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('11111111-1111-1111-1111-111111111125', 'TIK-C005', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('11111111-1111-1111-1111-111111111126', 'TIK-D001', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'cccccccc-cccc-cccc-cccc-ccccccccc004'),
    ('11111111-1111-1111-1111-111111111127', 'TIK-D002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb001', 'cccccccc-cccc-cccc-cccc-ccccccccc001'),
    ('11111111-1111-1111-1111-111111111128', 'TIK-D003', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb002', 'cccccccc-cccc-cccc-cccc-ccccccccc002'),
    ('11111111-1111-1111-1111-111111111129', 'TIK-D004', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb003', 'cccccccc-cccc-cccc-cccc-ccccccccc003'),
    ('11111111-1111-1111-1111-111111111130', 'TIK-D005', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbb004', 'cccccccc-cccc-cccc-cccc-ccccccccc004');

-- HAS_RELATIONSHIP
INSERT INTO HAS_RELATIONSHIP (seat_id, ticket_id) VALUES
    ('00000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111101'),
    ('00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111102'),
    ('00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-111111111103'),
    ('00000000-0000-0000-0000-000000000004', '11111111-1111-1111-1111-111111111104'),
    ('00000000-0000-0000-0000-000000000005', '11111111-1111-1111-1111-111111111105'),
    ('00000000-0000-0000-0000-000000000006', '11111111-1111-1111-1111-111111111106'),
    ('00000000-0000-0000-0000-000000000007', '11111111-1111-1111-1111-111111111107'),
    ('00000000-0000-0000-0000-000000000008', '11111111-1111-1111-1111-111111111108'),
    ('00000000-0000-0000-0000-000000000009', '11111111-1111-1111-1111-111111111109'),
    ('00000000-0000-0000-0000-000000000010', '11111111-1111-1111-1111-111111111110');
