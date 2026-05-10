-- Trigger 1 (WAJIB): Username validation on USER_ACCOUNT
-- (a) Case-insensitive uniqueness check
-- (b) Only alphanumeric characters and underscores allowed

CREATE OR REPLACE FUNCTION trg_user_account_validate_fn()
RETURNS TRIGGER AS $$
BEGIN
    -- (a) Case-insensitive duplicate check
    IF EXISTS (
        SELECT 1 FROM USER_ACCOUNT
        WHERE LOWER(username) = LOWER(NEW.username)
          AND user_id <> NEW.user_id
    ) THEN
        RAISE EXCEPTION 'Username "%" sudah digunakan (case-insensitive).', NEW.username;
    END IF;

    -- (b) Only letters, digits, and underscores
    IF NEW.username !~ '^[A-Za-z0-9_]+$' THEN
        RAISE EXCEPTION 'Username hanya boleh mengandung huruf, angka, dan underscore (_).';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_user_account_validate ON USER_ACCOUNT;
CREATE TRIGGER trg_user_account_validate
BEFORE INSERT OR UPDATE ON USER_ACCOUNT
FOR EACH ROW EXECUTE FUNCTION trg_user_account_validate_fn();
