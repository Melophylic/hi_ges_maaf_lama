-- Trigger 2: Venue integrity rules
-- (a) Prevent duplicate venue name in the same city (case-insensitive)
-- (b) Prevent deletion of a venue that has at least one active (future) event

-- ── (a) Duplicate venue name + city check ────────────────────────────────────

CREATE OR REPLACE FUNCTION trg_venue_no_duplicate_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM VENUE
        WHERE LOWER(venue_name) = LOWER(NEW.venue_name)
          AND LOWER(city)       = LOWER(NEW.city)
          AND venue_id          <> NEW.venue_id
    ) THEN
        RAISE EXCEPTION 'Venue "%" sudah terdaftar di kota %.', NEW.venue_name, NEW.city;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_venue_no_duplicate ON VENUE;
CREATE TRIGGER trg_venue_no_duplicate
BEFORE INSERT OR UPDATE ON VENUE
FOR EACH ROW EXECUTE FUNCTION trg_venue_no_duplicate_fn();


-- ── (b) Prevent delete if venue has future events ────────────────────────────

CREATE OR REPLACE FUNCTION trg_venue_no_delete_active_fn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM EVENT
        WHERE venue_id = OLD.venue_id
          AND event_datetime >= NOW()
    ) THEN
        RAISE EXCEPTION 'Venue "%" tidak dapat dihapus karena masih memiliki event aktif.', OLD.venue_name;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_venue_no_delete_active ON VENUE;
CREATE TRIGGER trg_venue_no_delete_active
BEFORE DELETE ON VENUE
FOR EACH ROW EXECUTE FUNCTION trg_venue_no_delete_active_fn();
