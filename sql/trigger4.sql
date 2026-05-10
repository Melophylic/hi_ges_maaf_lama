-- Trigger 4: Validate promotion when applied to an order
-- Fires BEFORE INSERT on ORDER_PROMOTION and checks:
--   (a) Promotion exists
--   (b) Current date is within the promotion's active period
--   (c) Usage limit has not been reached

CREATE OR REPLACE FUNCTION trg_order_promotion_validate_fn()
RETURNS TRIGGER AS $$
DECLARE
    v_promo    PROMOTION%ROWTYPE;
    v_usage    INTEGER;
BEGIN
    SELECT * INTO v_promo FROM PROMOTION WHERE promotion_id = NEW.promotion_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Kode promo tidak ditemukan.';
    END IF;

    IF CURRENT_DATE < v_promo.start_date OR CURRENT_DATE > v_promo.end_date THEN
        RAISE EXCEPTION 'Kode promo "%" sudah kadaluarsa atau belum aktif.', v_promo.promo_code;
    END IF;

    SELECT COUNT(*) INTO v_usage
    FROM ORDER_PROMOTION
    WHERE promotion_id = NEW.promotion_id;

    IF v_usage >= v_promo.usage_limit THEN
        RAISE EXCEPTION 'Kode promo "%" sudah mencapai batas penggunaan (%%).', v_promo.promo_code, v_promo.usage_limit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_order_promotion_validate ON ORDER_PROMOTION;
CREATE TRIGGER trg_order_promotion_validate
BEFORE INSERT ON ORDER_PROMOTION
FOR EACH ROW EXECUTE FUNCTION trg_order_promotion_validate_fn();
