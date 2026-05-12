-- Trigger 3: EVENT_ARTIST integrity + stored procedure for ticket quota

-- ── (a) Prevent artist from being added to an event they're already in ────────
--       (Adds a friendly error on top of the PK constraint)

CREATE OR REPLACE FUNCTION trg_event_artist_no_dup_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM EVENT_ARTIST
        WHERE event_id  = NEW.event_id
          AND artist_id = NEW.artist_id
    ) THEN
        RAISE EXCEPTION 'Artist sudah terdaftar di event ini.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_event_artist_no_dup ON EVENT_ARTIST;
CREATE TRIGGER trg_event_artist_no_dup
BEFORE INSERT ON EVENT_ARTIST
FOR EACH ROW EXECUTE FUNCTION trg_event_artist_no_dup_fn();


-- ── (b) Stored procedure: get remaining quota for a ticket category ────────────

CREATE OR REPLACE FUNCTION get_remaining_quota(p_category_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_quota    INTEGER;
    v_sold     INTEGER;
BEGIN
    SELECT quota INTO v_quota
    FROM TICKET_CATEGORY
    WHERE category_id = p_category_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Kategori tiket tidak ditemukan.';
    END IF;

    SELECT COUNT(*) INTO v_sold
    FROM TICKET
    WHERE tcategory_id = p_category_id;

    RETURN v_quota - v_sold;
END;
$$ LANGUAGE plpgsql;
