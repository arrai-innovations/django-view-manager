DROP VIEW IF EXISTS musicians_bandinfo;
CREATE VIEW musicians_bandinfo AS
SELECT
    B.id,
    B.name,
    count(M.name) as member_count
FROM
    musicians_bands B
    LEFT JOIN musicians_bandmembers M
    ON M.band_id = B.id
;
