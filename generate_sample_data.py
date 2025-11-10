"""
Sample Data Generator for Firebolt Geospatial Demo
Generates realistic customer orders and geographic zones data for Bengaluru
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from firebolt.db import connect
from firebolt.client.auth import ClientCredentials

# Load environment variables
load_dotenv()

def get_connection():
    """Get Firebolt database connection"""
    try:
        auth = ClientCredentials(
            client_id=os.getenv("FIREBOLT_CLIENT_ID"),
            client_secret=os.getenv("FIREBOLT_CLIENT_SECRET")
        )
        
        connection = connect(
            auth=auth,
            database=os.getenv("FIREBOLT_DATABASE", "playstats"),
            engine_name=os.getenv("FIREBOLT_ENGINE", "my_engine"),
            account_name=os.getenv("FIREBOLT_ACCOUNT_NAME", "account-1")
        )
        return connection
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def generate_customer_orders(num_orders=50000):
    """Generate sample customer orders data for Bengaluru"""
    
    # Bengaluru coordinate bounds
    bengaluru_bounds = {
        'lat_min': 12.8, 'lat_max': 13.2,
        'lon_min': 77.4, 'lon_max': 77.8
    }
    
    # Store locations (realistic Bengaluru areas)
    stores = [
        {'id': 'STORE_001', 'name': 'Koramangala', 'lat': 12.9279, 'lon': 77.6271},
        {'id': 'STORE_002', 'name': 'Indiranagar', 'lat': 12.9784, 'lon': 77.6408},
        {'id': 'STORE_003', 'name': 'Whitefield', 'lat': 12.9698, 'lon': 77.7500},
        {'id': 'STORE_004', 'name': 'Electronic City', 'lat': 12.8456, 'lon': 77.6603},
        {'id': 'STORE_005', 'name': 'JP Nagar', 'lat': 12.9083, 'lon': 77.5833},
        {'id': 'STORE_006', 'name': 'Marathahalli', 'lat': 12.9591, 'lon': 77.6974},
        {'id': 'STORE_007', 'name': 'HSR Layout', 'lat': 12.9116, 'lon': 77.6473},
        {'id': 'STORE_008', 'name': 'Rajajinagar', 'lat': 12.9915, 'lon': 77.5632}
    ]
    
    print(f"🏪 Generating {num_orders:,} customer orders...")
    
    orders = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(num_orders):
        store = random.choice(stores)
        
        # Generate customer location near store (with some spread)
        lat_offset = np.random.normal(0, 0.02)  # ~2km radius
        lon_offset = np.random.normal(0, 0.02)
        
        customer_lat = max(bengaluru_bounds['lat_min'], 
                          min(bengaluru_bounds['lat_max'], 
                              store['lat'] + lat_offset))
        customer_lon = max(bengaluru_bounds['lon_min'], 
                          min(bengaluru_bounds['lon_max'], 
                              store['lon'] + lon_offset))
        
        # Generate order details
        order_value = round(np.random.exponential(500) + 50, 2)  # Exponential distribution
        order_date = base_date + timedelta(days=random.randint(0, 90))
        
        # Generate realistic delivery time based on distance to store
        distance_factor = np.sqrt(lat_offset**2 + lon_offset**2)  # Approximate distance
        base_delivery_time = 20  # Base delivery time in minutes
        distance_delivery_time = distance_factor * 1000  # Distance-based time
        delivery_time = int(base_delivery_time + distance_delivery_time + np.random.normal(0, 5))
        delivery_time = max(10, min(90, delivery_time))  # Clamp between 10-90 minutes
        
        orders.append({
            'order_id': f'ORD_{i+1:06d}',
            'customer_lat': round(customer_lat, 6),
            'customer_lon': round(customer_lon, 6),
            'order_value': order_value,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'store_id': store['id'],
            'store_lat': store['lat'],
            'store_lon': store['lon'],
            'delivery_time_minutes': delivery_time
        })
        
        if (i + 1) % 10000 == 0:
            print(f"   Generated {i+1:,} orders...")
    
    return pd.DataFrame(orders)

def generate_geo_zones():
    """Generate sample geographic zones for Bengaluru"""
    
    zones = [
        # City center zones
        {'zone_id': 'ZONE_001', 'zone_name': 'Central Business District', 'zone_type': 'commercial', 
         'zone_lat': 12.9716, 'zone_lon': 77.5946, 'zone_radius': 2.0},
        
        {'zone_id': 'ZONE_002', 'zone_name': 'Koramangala District', 'zone_type': 'mixed', 
         'zone_lat': 12.9279, 'zone_lon': 77.6271, 'zone_radius': 1.5},
        
        {'zone_id': 'ZONE_003', 'zone_name': 'Indiranagar District', 'zone_type': 'residential', 
         'zone_lat': 12.9784, 'zone_lon': 77.6408, 'zone_radius': 1.2},
        
        # Tech hubs
        {'zone_id': 'ZONE_004', 'zone_name': 'Whitefield Tech Hub', 'zone_type': 'technology', 
         'zone_lat': 12.9698, 'zone_lon': 77.7500, 'zone_radius': 2.5},
        
        {'zone_id': 'ZONE_005', 'zone_name': 'Electronic City', 'zone_type': 'technology', 
         'zone_lat': 12.8456, 'zone_lon': 77.6603, 'zone_radius': 3.0},
        
        # Residential areas
        {'zone_id': 'ZONE_006', 'zone_name': 'JP Nagar Residential', 'zone_type': 'residential', 
         'zone_lat': 12.9083, 'zone_lon': 77.5833, 'zone_radius': 1.8},
        
        {'zone_id': 'ZONE_007', 'zone_name': 'HSR Layout', 'zone_type': 'residential', 
         'zone_lat': 12.9116, 'zone_lon': 77.6473, 'zone_radius': 1.5},
        
        {'zone_id': 'ZONE_008', 'zone_name': 'Marathahalli Area', 'zone_type': 'mixed', 
         'zone_lat': 12.9591, 'zone_lon': 77.6974, 'zone_radius': 2.0},
        
        # Outer zones
        {'zone_id': 'ZONE_009', 'zone_name': 'North Bengaluru', 'zone_type': 'industrial', 
         'zone_lat': 13.1500, 'zone_lon': 77.6000, 'zone_radius': 4.0},
        
        {'zone_id': 'ZONE_010', 'zone_name': 'South Bengaluru', 'zone_type': 'residential', 
         'zone_lat': 12.8500, 'zone_lon': 77.6000, 'zone_radius': 3.5}
    ]
    
    print(f"🗺️ Generating {len(zones)} geographic zones...")
    return pd.DataFrame(zones)

def create_tables_if_not_exist(connection):
    """Create tables if they don't exist"""
    
    customer_orders_sql = """
    CREATE TABLE IF NOT EXISTS customer_orders (
        order_id TEXT,
        customer_lat DOUBLE PRECISION,
        customer_lon DOUBLE PRECISION,
        order_value DOUBLE PRECISION,
        order_date TEXT,
        store_id TEXT,
        store_lat DOUBLE PRECISION,
        store_lon DOUBLE PRECISION,
        delivery_time_minutes INT
    ) PRIMARY INDEX order_id
    """
    
    geo_zones_sql = """
    CREATE TABLE IF NOT EXISTS geo_zones (
        zone_id TEXT,
        zone_name TEXT,
        zone_type TEXT,
        zone_lat DOUBLE PRECISION,
        zone_lon DOUBLE PRECISION,
        zone_radius DOUBLE PRECISION
    ) PRIMARY INDEX zone_id
    """
    
    cursor = connection.cursor()
    print("📋 Creating tables if they don't exist...")
    
    try:
        cursor.execute(customer_orders_sql)
        print("   ✅ customer_orders table ready")
        
        cursor.execute(geo_zones_sql)
        print("   ✅ geo_zones table ready")
        
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
    
    cursor.close()

def insert_data_batch(connection, table_name, df, batch_size=1000):
    """Insert data in batches for better performance"""
    
    cursor = connection.cursor()
    total_rows = len(df)
    
    print(f"📤 Inserting {total_rows:,} rows into {table_name}...")
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        
        if table_name == 'customer_orders':
            values = []
            for _, row in batch.iterrows():
                values.append(f"('{row['order_id']}', {row['customer_lat']}, {row['customer_lon']}, "
                            f"{row['order_value']}, '{row['order_date']}', '{row['store_id']}', "
                            f"{row['store_lat']}, {row['store_lon']}, {row['delivery_time_minutes']})")
            
            sql = f"INSERT INTO customer_orders VALUES " + ", ".join(values)
            
        elif table_name == 'geo_zones':
            values = []
            for _, row in batch.iterrows():
                values.append(f"('{row['zone_id']}', '{row['zone_name']}', '{row['zone_type']}', "
                            f"{row['zone_lat']}, {row['zone_lon']}, {row['zone_radius']})")
            
            sql = f"INSERT INTO geo_zones VALUES " + ", ".join(values)
        
        try:
            cursor.execute(sql)
            print(f"   Inserted batch {i//batch_size + 1} ({min(i+batch_size, total_rows):,}/{total_rows:,} rows)")
        
        except Exception as e:
            print(f"   ❌ Error inserting batch: {e}")
            break
    
    cursor.close()

def check_existing_data(connection):
    """Check if data already exists in tables"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM customer_orders")
        orders_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geo_zones") 
        zones_count = cursor.fetchone()[0]
        
        cursor.close()
        return orders_count, zones_count
        
    except Exception as e:
        print(f"❌ Error checking existing data: {e}")
        cursor.close()
        return 0, 0

def main():
    """Main data generation function"""
    print("🚀 Firebolt Geospatial Demo - Sample Data Generator")
    print("=" * 60)
    
    # Get database connection
    connection = get_connection()
    if not connection:
        print("❌ Failed to connect to Firebolt. Please check your .env configuration.")
        return
    
    print("✅ Connected to Firebolt database")
    
    # Check existing data
    orders_count, zones_count = check_existing_data(connection)
    
    if orders_count > 0 or zones_count > 0:
        print(f"📊 Existing data found:")
        print(f"   customer_orders: {orders_count:,} rows")
        print(f"   geo_zones: {zones_count:,} rows")
        
        response = input("\n🤔 Do you want to add more sample data? (y/n): ").lower()
        if response != 'y':
            print("⏭️ Skipping data generation.")
            connection.close()
            return
    
    # Create tables
    create_tables_if_not_exist(connection)
    
    # Generate and insert customer orders
    orders_df = generate_customer_orders(50000)
    insert_data_batch(connection, 'customer_orders', orders_df)
    
    # Generate and insert geo zones  
    zones_df = generate_geo_zones()
    insert_data_batch(connection, 'geo_zones', zones_df)
    
    # Verify data
    final_orders, final_zones = check_existing_data(connection)
    
    print("\n" + "=" * 60)
    print("🎉 Sample data generation complete!")
    print(f"📊 Final data counts:")
    print(f"   customer_orders: {final_orders:,} rows")
    print(f"   geo_zones: {final_zones:,} rows")
    print("\n🚀 You can now run the demo with: streamlit run app_geospatial_demo.py")
    
    connection.close()

if __name__ == "__main__":
    main()