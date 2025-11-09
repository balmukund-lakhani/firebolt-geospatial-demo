-- Table: customer_orders
-- Customer order data with locations for radius-based filtering
CREATE FACT TABLE IF NOT EXISTS customer_orders (
    order_id VARCHAR,
    customer_id VARCHAR,
    store_id VARCHAR,
    order_timestamp TIMESTAMP,
    customer_lat DOUBLE,
    customer_lon DOUBLE,
    store_lat DOUBLE,
    store_lon DOUBLE,
    order_value DOUBLE,
    delivery_time_minutes INT
)
PRIMARY INDEX order_id;