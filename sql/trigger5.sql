-- Trigger 5: Ticket integrity rules
-- (a) Prevent deletion of a SEAT that is assigned to a ticket (has a HAS_RELATIONSHIP row)
-- (b) Enforce TICKET_CATEGORY quota on TICKET insert

-- ── (a) Prevent seat deletion when assigned ──────────────────────────────────

CREATE OR REPLACE FUNCTION trg_seat_no_delete_if_assigned_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM HAS_RELATIONSHIP WHERE seat_id = OLD.seat_id
    ) THEN
        RAISE EXCEPTION 'Kursi ini sudah di-assign ke tiket dan tidak dapat dihapus.';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_seat_no_delete_if_assigned ON SEAT;
CREATE TRIGGER trg_seat_no_delete_if_assigned
BEFORE DELETE ON SEAT
FOR EACH ROW EXECUTE FUNCTION trg_seat_no_delete_if_assigned_fn();


-- ── (b) Enforce ticket category quota on TICKET insert ───────────────────────

CREATE OR REPLACE FUNCTION trg_ticket_check_quota_fn()
RETURNS TRIGGER AS $$
DECLARE
    v_quota  INTEGER;
    v_sold   INTEGER;
    v_name   VARCHAR;
BEGIN
    SELECT quota, category_name INTO v_quota, v_name
    FROM TICKET_CATEGORY
    WHERE category_id = NEW.tcategory_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Kategori tiket tidak ditemukan.';
    END IF;

    SELECT COUNT(*) INTO v_sold
    FROM TICKET
    WHERE tcategory_id = NEW.tcategory_id;

    IF v_sold >= v_quota THEN
        RAISE EXCEPTION 'Kuota kategori tiket "%" sudah habis (% / %).', v_name, v_sold, v_quota;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ticket_check_quota ON TICKET;
CREATE TRIGGER trg_ticket_check_quota
BEFORE INSERT ON TICKET
FOR EACH ROW EXECUTE FUNCTION trg_ticket_check_quota_fn();
