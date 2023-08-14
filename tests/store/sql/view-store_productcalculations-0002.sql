DROP VIEW IF EXISTS store_purchasedproductcalculations;
DROP VIEW IF EXISTS store_productcalculations;
CREATE VIEW store_productcalculations AS
SELECT
    P.id,
    P.id AS product_id,
    P.price * (1 + (P.markup_percentage / 100)) AS markup_price
FROM
    store_products P
;
