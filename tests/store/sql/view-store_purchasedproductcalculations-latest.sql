/*
    This file was generated using django-view-manager 1.0.4.
    Modify the SQL for this view and then commit the changes.
    You can remove this comment before committing.

    When you have changes to make to this sql, you need to run the makeviewmigration command
    before altering the sql, so the historical sql file is created with the correct contents.
*/
DROP VIEW IF EXISTS store_purchasedproductcalculations;
CREATE VIEW store_purchasedproductcalculations AS
SELECT
    PP.id,
    PP.id AS order_item_id,
    (PC.markup_price - P.price) * PP.quantity AS profit
FROM
    store_purchasedproducts PP
    JOIN store_productcalculations PC ON PP.purchased_product_id = PC.product_id
    JOIN store_products P ON P.id = PP.product_id
;
