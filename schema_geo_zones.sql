-- Table: geo_zones
-- Polygon zones for region-level aggregation
CREATE FACT TABLE IF NOT EXISTS geo_zones (
    zone_id VARCHAR,
    zone_name VARCHAR,
    zone_type VARCHAR, -- 'postal_code', 'district', 'commercial'
    polygon_wkt TEXT, -- Well-Known Text format for polygon
    center_lat DOUBLE,
    center_lon DOUBLE
)
PRIMARY INDEX zone_id;