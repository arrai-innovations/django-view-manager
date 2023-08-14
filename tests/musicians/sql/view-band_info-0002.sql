DROP VIEW IF EXISTS musicians_bandinfo;
CREATE VIEW musicians_bandinfo AS
SELECT
    B.id,
    B.name
FROM
    musicians_bands B
;
