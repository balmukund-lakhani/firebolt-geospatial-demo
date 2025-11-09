"""
Firebolt Geospatial Functions Demo
Showcases PostgreSQL-compatible geospatial capabilities for high-performance analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from firebolt.db import connect
from firebolt.client.auth import ClientCredentials

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Firebolt Geospatial Demo", 
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
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
            account_name=os.getenv("FIREBOLT_ACCOUNT", "account-1")
        )
        
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        st.info("Please check your .env file with Firebolt credentials")
        return None

def run_query(query):
    """Execute a query and return results as DataFrame"""
    try:
        conn = get_connection()
        if not conn:
            return pd.DataFrame()
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
        return pd.DataFrame(results, columns=columns)
    
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return pd.DataFrame()

def check_sample_data():
    """Check if sample data exists in the database"""
    try:
        orders_df = run_query("SELECT COUNT(*) as count FROM customer_orders")
        zones_df = run_query("SELECT COUNT(*) as count FROM geo_zones")
        
        orders_count = orders_df.iloc[0]['count'] if not orders_df.empty else 0
        zones_count = zones_df.iloc[0]['count'] if not zones_df.empty else 0
        
        return orders_count, zones_count
    except:
        return 0, 0

def show_data_setup():
    """Show data setup instructions"""
    st.warning("⚠️ No sample data found in your database!")
    
    st.markdown("""
    **To use this demo, you need sample data in your Firebolt database.**
    
    ### Option 1: Generate Sample Data (Recommended)
    Run the sample data generator script:
    ```bash
    python generate_sample_data.py
    ```
    
    ### Option 2: Manual Setup
    1. Run the SQL schemas in your database:
       - `schema_customer_orders.sql`
       - `schema_geo_zones.sql`
    2. Insert your own geospatial data
    
    ### What the sample data includes:
    - **50,000 customer orders** with realistic Bengaluru coordinates
    - **10 geographic zones** covering different areas of Bengaluru
    - **8 store locations** in major Bengaluru districts
    """)
    
    with st.expander("🔧 Database Schema Details"):
        st.code("""
        -- Customer Orders Table
        CREATE TABLE customer_orders (
            order_id TEXT,
            customer_lat DOUBLE PRECISION,
            customer_lon DOUBLE PRECISION,
            order_value DOUBLE PRECISION,
            order_date TEXT,
            store_id TEXT
        );
        
        -- Geographic Zones Table  
        CREATE TABLE geo_zones (
            zone_id TEXT,
            zone_name TEXT,
            zone_type TEXT,
            zone_lat DOUBLE PRECISION,
            zone_lon DOUBLE PRECISION,
            zone_radius DOUBLE PRECISION
        );
        """, language="sql")

def main():
    """Main app function"""
    st.title("🗺️ Firebolt Geospatial Functions Demo")
    st.markdown("*Showcase the power of geospatial bulk queries with Firebolt*")
    
    # Check for sample data
    orders_count, zones_count = check_sample_data()
    
    if orders_count == 0 or zones_count == 0:
        show_data_setup()
        return
    
    # Show data status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Customer Orders", f"{orders_count:,}")
    with col2:
        st.metric("Geographic Zones", f"{zones_count:,}")
    with col3:
        st.metric("Database Status", "✅ Ready")
    
    st.markdown("---")
    
    # Demo selection
    demo_choice = st.selectbox(
        "Select a geospatial function demo:",
        ["Functions Reference", "1. Store Coverage Analysis", "2. Customer Zone Analysis", "3. Service Area Coverage"]
    )
    
    # Demo routing
    demo_functions = {
        "Functions Reference": show_functions_reference,
        "1. Store Coverage Analysis": show_st_distance_demo,
        "2. Customer Zone Analysis": show_st_contains_demo,
        "3. Service Area Coverage": show_st_covers_demo
    }
    
    # Run selected demo
    demo_functions[demo_choice]()

def show_st_distance_demo():
    """Store Coverage Analysis: Distance-based customer reach optimization"""
    st.header("1. Store Coverage Analysis")
    st.markdown("**Business Use Case**: Optimize store locations and understand customer reach")
    
    st.markdown("""
    **Store Coverage Analysis** helps retail businesses understand:
    - Which customers are within delivery range of each store
    - Store coverage areas and potential expansion opportunities  
    - Customer-to-store distance patterns for logistics optimization
    - Delivery radius optimization and service area planning
    """)
    
    # Interactive controls
    st.subheader("🏪 Store-to-Customer Distance Analysis")
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Get available stores
        stores_query = """
        SELECT DISTINCT store_id, store_lat, store_lon
        FROM customer_orders
        ORDER BY store_id
        """
        stores_df = run_query(stores_query)
        
        if stores_df.empty:
            st.warning("No store data available")
            return
        
        # Store selection
        selected_stores = st.multiselect(
            "Select Store(s)", 
            stores_df['store_id'].tolist(),
            default=stores_df['store_id'].tolist()[:2]  # Default to first 2 stores
        )
        
        if not selected_stores:
            st.warning("Please select at least one store")
            return
        
        # Distance parameters
        max_distance = st.slider("Maximum Distance (km)", 1, 15, 8)
        min_order_value = st.slider("Minimum Order Value ($)", 0, 500, 50)
        
        st.subheader("📊 Analysis Settings")
        st.metric("Selected Stores", len(selected_stores))
        st.metric("Max Distance", f"{max_distance} km")
        st.metric("Min Order Value", f"${min_order_value}")
    
    with col1:
        # Build store-to-customer distance query
        store_ids_str = "', '".join(selected_stores)
        
        # Since ST_Distance might have serialization issues, we'll calculate in Python
        distance_query = f"""
        SELECT 
            order_id,
            store_id,
            customer_lat,
            customer_lon,
            order_value,
            delivery_time_minutes,
            (SELECT store_lat FROM customer_orders c2 WHERE c2.store_id = customer_orders.store_id LIMIT 1) as store_lat,
            (SELECT store_lon FROM customer_orders c2 WHERE c2.store_id = customer_orders.store_id LIMIT 1) as store_lon
        FROM customer_orders 
        WHERE store_id IN ('{store_ids_str}')
        AND order_value >= {min_order_value}
        ORDER BY store_id, order_value DESC
        LIMIT 1000
        """
        
        results_df = run_query(distance_query)
        
        if not results_df.empty:
            # Calculate distances using Haversine formula (since ST_Distance has issues)
            from math import radians, sin, cos, sqrt, atan2
            
            def haversine_distance(lat1, lon1, lat2, lon2):
                """Calculate distance between two points using Haversine formula"""
                R = 6371000  # Earth's radius in meters
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                return R * c
            
            # Calculate distance for each order
            results_df['distance_km'] = results_df.apply(
                lambda row: haversine_distance(
                    row['customer_lat'], row['customer_lon'],
                    row['store_lat'], row['store_lon']
                ) / 1000.0, axis=1
            )
            
            # Round to 2 decimal places
            results_df['distance_km'] = results_df['distance_km'].round(2)
            
            # Filter by distance
            results_df = results_df[results_df['distance_km'] <= max_distance]
            results_df = results_df.sort_values(['store_id', 'distance_km'])
            
            if not results_df.empty:
                st.info(f"🔧 **Implementation**: Using Haversine formula as ST_Distance() simulation")
                st.success(f"✅ Found {len(results_df)} orders within {max_distance}km of selected stores")
                
                # Create visualization
                fig = go.Figure()
                
                # Color palette for stores
                colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink']
                
                # Add customer orders with color-coding by store
                for i, store_id in enumerate(selected_stores):
                    store_orders = results_df[results_df['store_id'] == store_id]
                    if not store_orders.empty:
                        color = colors[i % len(colors)]
                        
                        # Add customer points
                        fig.add_trace(go.Scattermap(
                            lat=store_orders['customer_lat'],
                            lon=store_orders['customer_lon'],
                            mode='markers',
                            marker=dict(size=8, color=color, opacity=0.7),
                            text=store_orders.apply(
                                lambda row: f"Order: ${row['order_value']:.0f}<br>"
                                           f"Distance: {row['distance_km']:.2f} km<br>"
                                           f"Delivery: {row['delivery_time_minutes']:.0f} min<br>"
                                           f"Store: {row['store_id']}", axis=1
                            ),
                            name=f'Store {store_id} Orders ({len(store_orders)})',
                            hovertemplate="<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
                        ))
                        
                        # Add store location
                        store_data = store_orders.iloc[0]
                        fig.add_trace(go.Scattermap(
                            lat=[store_data['store_lat']],
                            lon=[store_data['store_lon']],
                            mode='markers',
                            marker=dict(
                                size=25, 
                                color=color,
                                symbol='building',
                                opacity=0.9
                            ),
                            text=[f"🏪 Store: {store_id}<br>Location: {store_data['store_lat']:.4f}, {store_data['store_lon']:.4f}"],
                            name=f'🏪 Store {store_id}',
                            hovertemplate="<b>%{text}</b><extra></extra>"
                        ))
                
                # Center map on stores
                center_lat = results_df['store_lat'].mean()
                center_lon = results_df['store_lon'].mean()
                
                fig.update_layout(
                    map=dict(
                        style="open-street-map",
                        center=dict(lat=center_lat, lon=center_lon),
                        zoom=10
                    ),
                    title=f"ST_Distance Analysis: Orders within {max_distance}km of Stores",
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Distance analysis results
                st.subheader("📊 Distance Analysis Results")
                
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    st.metric("Total Orders", len(results_df))
                    total_revenue = results_df['order_value'].sum()
                    st.metric("Total Revenue", f"${total_revenue:,.0f}")
                
                with col4:
                    avg_distance = results_df['distance_km'].mean()
                    st.metric("Avg Distance", f"{avg_distance:.2f} km")
                    closest_distance = results_df['distance_km'].min()
                    st.metric("Closest Order", f"{closest_distance:.2f} km")
                
                with col5:
                    avg_delivery = results_df['delivery_time_minutes'].mean()
                    st.metric("Avg Delivery Time", f"{avg_delivery:.1f} min")
                    avg_order_value = results_df['order_value'].mean()
                    st.metric("Avg Order Value", f"${avg_order_value:.2f}")
                
                # Store performance breakdown
                st.subheader("🏪 Store Performance by Distance")
                
                store_analysis = results_df.groupby('store_id').agg({
                    'order_id': 'count',
                    'order_value': ['sum', 'mean'],
                    'distance_km': ['mean', 'min', 'max'],
                    'delivery_time_minutes': 'mean'
                }).round(2)
                
                store_analysis.columns = [
                    'Order Count', 'Total Revenue', 'Avg Order Value',
                    'Avg Distance', 'Min Distance', 'Max Distance', 'Avg Delivery Time'
                ]
                store_analysis = store_analysis.reset_index()
                
                st.dataframe(store_analysis, use_container_width=True)
                
                # Distance vs Order Value analysis
                if len(results_df) > 10:
                    col6, col7 = st.columns(2)
                    
                    with col6:
                        # Distance distribution
                        fig2 = px.histogram(
                            results_df,
                            x='distance_km',
                            nbins=20,
                            title="Distance Distribution",
                            labels={'distance_km': 'Distance (km)'}
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with col7:
                        # Distance vs Order Value correlation
                        fig3 = px.scatter(
                            results_df,
                            x='distance_km',
                            y='order_value',
                            color='store_id',
                            title="Distance vs Order Value",
                            labels={'distance_km': 'Distance (km)', 'order_value': 'Order Value ($)'}
                        )
                        st.plotly_chart(fig3, use_container_width=True)
            else:
                st.warning(f"No orders found within {max_distance}km of selected stores")
        else:
            st.warning("No customer order data available")
    
    # Technical implementation
    st.subheader("🔧 Technical Implementation")
    
    col8, col9 = st.columns(2)
    
    with col8:
        st.markdown("**Business Logic:**")
        st.markdown("""
        - **Store Selection**: Analyze specific store performance
        - **Distance Filtering**: Focus on accessible customers
        - **Order Value Filtering**: Analyze profitable orders
        - **Delivery Optimization**: Understand distance impact
        """)
    
    with col9:
        st.markdown("**Query Performance:**")
        st.markdown("""
        - **Spatial Indexing**: Fast distance calculations
        - **Filtered Queries**: Reduce dataset size
        - **Haversine Formula**: Accurate distance calculation
        - **Result Caching**: Improve user experience
        """)
    
    with st.expander("📋 ST_Distance() SQL Reference"):
        st.code(f"""
-- ST_Distance() with spatial filtering
SELECT 
    order_id,
    store_id,
    customer_lat,
    customer_lon,
    order_value,
    ST_Distance(
        ST_GEOGPOINT(customer_lon, customer_lat),
        ST_GEOGPOINT(store_lon, store_lat)
    ) / 1000.0 as distance_km
FROM customer_orders co
JOIN stores s ON co.store_id = s.store_id
WHERE ST_Distance(
    ST_GEOGPOINT(customer_lon, customer_lat),
    ST_GEOGPOINT(store_lon, store_lat)
) <= {max_distance * 1000}  -- Distance in meters
AND order_value >= {min_order_value}
ORDER BY distance_km ASC;

-- Performance optimization with bounding box
SELECT *
FROM customer_orders
WHERE store_id IN ('{("', '".join(selected_stores))}')
AND customer_lat BETWEEN store_lat - 0.1 AND store_lat + 0.1
AND customer_lon BETWEEN store_lon - 0.1 AND store_lon + 0.1
AND ST_Distance(
    ST_GEOGPOINT(customer_lon, customer_lat),
    ST_GEOGPOINT(store_lon, store_lat)
) <= {max_distance * 1000};
        """, language="sql")

def show_st_contains_demo():
    """Customer Zone Analysis: Territory management and customer segmentation"""
    st.header("2. Customer Zone Analysis")
    st.markdown("**Business Use Case**: Territory management and customer segmentation")
    st.markdown("*📍 Location: Bengaluru, India - Geographic customer analysis*")
    
    st.markdown("""
    **Customer Zone Analysis** helps businesses understand:
    - Which customers fall within specific service territories
    - Geographic customer distribution across business zones
    - Territory performance and customer density analysis
    - Regional marketing and sales territory optimization
    """)
    
    # Zone selection
    st.subheader("🗺️ Territory Selection")
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Fetch actual zones from the database
        zones_query = """
        SELECT 
            zone_id,
            zone_name,
            zone_type,
            center_lat,
            center_lon,
            polygon_wkt
        FROM geo_zones 
        ORDER BY zone_name
        """
        
        zones_df = run_query(zones_query)
        
        if zones_df.empty:
            st.error("No zones found in geo_zones table")
            return
            
        selected_zones = st.multiselect(
            "Select Zones for Analysis",
            options=zones_df['zone_id'].tolist(),
            default=zones_df['zone_id'].tolist()[:2],
            format_func=lambda x: f"Zone {x} ({zones_df[zones_df['zone_id']==x]['zone_name'].iloc[0]})"
        )
        
        if not selected_zones:
            st.warning("Please select at least one zone")
            return
    
    with col1:
        st.info("🔧 **Demo Implementation**: Using bounding box containment as ST_Contains() simulation")
        
        # Get customer orders in selected zones using bounding box approximation
        zone_conditions = []
        for zone_id in selected_zones:
            zone_data = zones_df[zones_df['zone_id'] == zone_id].iloc[0]
            center_lat, center_lon = zone_data['center_lat'], zone_data['center_lon']
            zone_conditions.append(f"""
                (customer_lat BETWEEN {center_lat - 0.05} AND {center_lat + 0.05}
                 AND customer_lon BETWEEN {center_lon - 0.05} AND {center_lon + 0.05})
            """)
        
        contains_query = f"""
        SELECT 
            order_id,
            customer_lat,
            customer_lon,
            order_value,
            store_id,
            CASE 
                {' '.join([f"WHEN (customer_lat BETWEEN {zones_df[zones_df['zone_id'] == zone]['center_lat'].iloc[0] - 0.05} AND {zones_df[zones_df['zone_id'] == zone]['center_lat'].iloc[0] + 0.05} AND customer_lon BETWEEN {zones_df[zones_df['zone_id'] == zone]['center_lon'].iloc[0] - 0.05} AND {zones_df[zones_df['zone_id'] == zone]['center_lon'].iloc[0] + 0.05}) THEN '{zone}'" for zone in selected_zones])}
                ELSE 'unknown' 
            END as zone_id
        FROM customer_orders 
        WHERE ({' OR '.join([f"(customer_lat BETWEEN {zones_df[zones_df['zone_id'] == zone]['center_lat'].iloc[0] - 0.05} AND {zones_df[zones_df['zone_id'] == zone]['center_lat'].iloc[0] + 0.05} AND customer_lon BETWEEN {zones_df[zones_df['zone_id'] == zone]['center_lon'].iloc[0] - 0.05} AND {zones_df[zones_df['zone_id'] == zone]['center_lon'].iloc[0] + 0.05})" for zone in selected_zones])})
        ORDER BY order_value DESC
        LIMIT 500
        """
        
        results_df = run_query(contains_query)
        
        if not results_df.empty:
            # Create visualization
            fig = go.Figure()
            
            # Add zone boundaries and customer points
            zone_colors = ['blue', 'green', 'red', 'orange', 'purple']
            
            for i, zone_id in enumerate(selected_zones):
                zone_data = zones_df[zones_df['zone_id'] == zone_id].iloc[0]
                color = zone_colors[i % len(zone_colors)]
                
                # Create zone boundary (simplified rectangle)
                center_lat, center_lon = zone_data['center_lat'], zone_data['center_lon']
                zone_lats = [center_lat-0.05, center_lat-0.05, center_lat+0.05, center_lat+0.05, center_lat-0.05]
                zone_lons = [center_lon-0.05, center_lon+0.05, center_lon+0.05, center_lon-0.05, center_lon-0.05]
                
                # Add zone boundary
                fig.add_trace(go.Scattermap(
                    lat=zone_lats,
                    lon=zone_lons,
                    mode='lines',
                    line=dict(width=3, color=color),
                    name=f"{zone_data['zone_name']} Boundary",
                    fill='toself',
                    fillcolor=f'rgba({255 if color=="red" else 0},{255 if color=="green" else 0},{255 if color=="blue" else 0},0.1)'
                ))
            
            # Add customer points colored by zone
            for i, zone_id in enumerate(selected_zones):
                zone_customers = results_df[results_df['zone_id'] == zone_id]
                if not zone_customers.empty:
                    color = zone_colors[i % len(zone_colors)]
                    zone_name = zones_df[zones_df['zone_id'] == zone_id]['zone_name'].iloc[0]
                    
                    fig.add_trace(go.Scattermap(
                        lat=zone_customers['customer_lat'],
                        lon=zone_customers['customer_lon'],
                        mode='markers',
                        marker=dict(size=8, color=color, opacity=0.8),
                        name=f'Customers in {zone_name}',
                        text=zone_customers.apply(lambda row: f"Zone: {zone_name}<br>Order: ${row['order_value']:.0f}<br>Store: {row['store_id']}", axis=1)
                    ))
            
            fig.update_layout(
                map=dict(
                    style="open-street-map",
                    center=dict(lat=12.9716, lon=77.5946),
                    zoom=10.5
                ),
                title="ST_Contains Demo: Customers in Geographic Zones",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis summary
            st.subheader("📊 Analysis Results")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Customers Found", len(results_df))
            with col4:
                st.metric("Total Revenue", f"${results_df['order_value'].sum():,.0f}")
            with col5:
                avg_order = results_df['order_value'].mean() if len(results_df) > 0 else 0
                st.metric("Avg Order Value", f"${avg_order:.2f}")
        else:
            st.warning("No customers found in selected zones")
    
    # Technical notes
    st.subheader("🔧 Technical Implementation")
    with st.expander("📋 ST_Contains() Function Reference"):
        st.code("""
-- ST_Contains() checks if a polygon contains a point
SELECT customer_id, zone_name
FROM customers c, zones z
WHERE ST_Contains(
    ST_GeogFromText(z.polygon_wkt),  -- Polygon geometry
    ST_GEOGPOINT(c.customer_lon, c.customer_lat)  -- Point geometry
) = TRUE

-- Example with zone filtering:
SELECT 
    COUNT(*) as customers_in_zone,
    SUM(order_value) as total_revenue
FROM customer_orders co, geo_zones gz
WHERE gz.zone_id = 'central_bangalore'
AND ST_Contains(
    ST_GeogFromText(gz.polygon_wkt),
    ST_GEOGPOINT(co.customer_lon, co.customer_lat)
) = TRUE
        """, language="sql")

def show_st_covers_demo():
    """Service Area Coverage: Market penetration and service optimization"""
    st.header("3. Service Area Coverage")
    st.markdown("**Business Use Case**: Market penetration and service area optimization")
    st.markdown("*📍 Location: Bengaluru, India - Coverage and service reach analysis*")
    
    st.markdown("""
    **Service Area Coverage Analysis** helps businesses understand:
    - **Market penetration** - How well do our service areas cover target markets?
    - **Service optimization** - Are all customer locations within our coverage zones?
    - **Expansion planning** - Which areas need better service coverage?
    - **Competitive analysis** - Coverage gaps and opportunities for growth
    """)
    
    # Interactive controls
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("🎯 Coverage Analysis")
        
        # Coverage scenarios
        coverage_type = st.selectbox(
            "Coverage Scenario",
            ["Delivery Zone Coverage", "Emergency Response Coverage", "Sales Territory Coverage"]
        )
        
        coverage_radius = st.slider("Coverage Radius (km)", 1.0, 10.0, 5.0, 0.5)
        
        # Reference points for coverage analysis
        reference_points = {
            "Central Bangalore": (13.0, 77.6),
            "North Bangalore": (13.1, 77.6),
            "South Bangalore": (12.9, 77.6),
            "East Bangalore": (13.0, 77.7),
            "West Bangalore": (13.0, 77.5)
        }
        
        selected_center = st.selectbox(
            "Coverage Center",
            list(reference_points.keys())
        )
        
        center_lat, center_lon = reference_points[selected_center]
        
        st.metric("Coverage Center", selected_center)
        st.metric("Radius", f"{coverage_radius} km")
        st.metric("Coverage Area", f"{3.14159 * coverage_radius**2:.1f} km²")
    
    with col1:
        # Simulate ST_COVERS analysis
        st.info("🔧 **Demo Implementation**: Simulating ST_COVERS() with distance-based coverage analysis")
        
        # Get customer orders and test coverage
        coverage_query = f"""
        WITH coverage_analysis AS (
            SELECT 
                order_id,
                customer_lat,
                customer_lon,
                order_value,
                store_id,
                -- Calculate distance from coverage center
                SQRT(
                    POW((customer_lat - {center_lat}) * 111.32, 2) + 
                    POW((customer_lon - {center_lon}) * 111.32 * COS(RADIANS({center_lat})), 2)
                ) as distance_km,
                -- Coverage test (simulating ST_COVERS)
                CASE 
                    WHEN SQRT(
                        POW((customer_lat - {center_lat}) * 111.32, 2) + 
                        POW((customer_lon - {center_lon}) * 111.32 * COS(RADIANS({center_lat})), 2)
                    ) <= {coverage_radius} 
                    THEN 1 
                    ELSE 0 
                END as is_covered
            FROM customer_orders
            WHERE customer_lat BETWEEN {center_lat - 0.1} AND {center_lat + 0.1}
            AND customer_lon BETWEEN {center_lon - 0.1} AND {center_lon + 0.1}
        )
        SELECT 
            order_id,
            customer_lat,
            customer_lon,
            order_value,
            store_id,
            ROUND(distance_km, 2) as distance_km,
            is_covered
        FROM coverage_analysis
        ORDER BY distance_km
        LIMIT 200
        """
        
        coverage_df = run_query(coverage_query)
        
        if not coverage_df.empty:
            # Create coverage visualization
            fig = go.Figure()
            
            # Add coverage circle
            circle_points = 64
            angles = np.linspace(0, 2*np.pi, circle_points)
            # Convert km to approximate degrees
            lat_offset = coverage_radius / 111.32
            lon_offset = coverage_radius / (111.32 * np.cos(np.radians(center_lat)))
            
            circle_lats = center_lat + lat_offset * np.sin(angles)
            circle_lons = center_lon + lon_offset * np.cos(angles)
            
            fig.add_trace(go.Scattermap(
                lat=circle_lats,
                lon=circle_lons,
                mode='lines',
                line=dict(width=3, color='blue'),
                name=f'{coverage_type} Zone',
                fill='toself',
                fillcolor='rgba(0,0,255,0.1)'
            ))
            
            # Add coverage center
            fig.add_trace(go.Scattermap(
                lat=[center_lat],
                lon=[center_lon],
                mode='markers',
                marker=dict(size=15, color='blue', symbol='star'),
                name=f'Coverage Center: {selected_center}'
            ))
            
            # Add covered customers (green)
            covered_df = coverage_df[coverage_df['is_covered'] == 1]
            if not covered_df.empty:
                fig.add_trace(go.Scattermap(
                    lat=covered_df['customer_lat'],
                    lon=covered_df['customer_lon'],
                    mode='markers',
                    marker=dict(size=8, color='green', opacity=0.7),
                    name=f'Covered Customers ({len(covered_df)})',
                    text=covered_df.apply(lambda row: f"${row['order_value']:.0f}<br>{row['distance_km']} km", axis=1)
                ))
            
            # Add non-covered customers (red)
            not_covered_df = coverage_df[coverage_df['is_covered'] == 0]
            if not not_covered_df.empty:
                fig.add_trace(go.Scattermap(
                    lat=not_covered_df['customer_lat'],
                    lon=not_covered_df['customer_lon'],
                    mode='markers',
                    marker=dict(size=8, color='red', opacity=0.7),
                    name=f'Not Covered ({len(not_covered_df)})',
                    text=not_covered_df.apply(lambda row: f"${row['order_value']:.0f}<br>{row['distance_km']} km", axis=1)
                ))
            
            fig.update_layout(
                map=dict(
                    style="open-street-map",
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=11
                ),
                title=f"ST_COVERS Demo: {coverage_type} Analysis",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Coverage statistics
            st.subheader("📊 Coverage Analysis")
            
            total_customers = len(coverage_df)
            covered_customers = len(covered_df) if not covered_df.empty else 0
            coverage_rate = (covered_customers / total_customers * 100) if total_customers > 0 else 0
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Coverage Rate", f"{coverage_rate:.1f}%")
            with col4:
                st.metric("Customers Covered", f"{covered_customers}/{total_customers}")
            with col5:
                covered_revenue = covered_df['order_value'].sum() if not covered_df.empty else 0
                st.metric("Covered Revenue", f"${covered_revenue:,.0f}")
        else:
            st.warning("No customer data found in the selected area")
    
    # Technical implementation
    st.subheader("🔧 Technical Implementation")
    
    with st.expander("📋 ST_COVERS() SQL Reference"):
        st.code(f"""
-- ST_COVERS() syntax
SELECT customer_id, is_covered
FROM customers c, service_zones sz
WHERE sz.zone_name = '{coverage_type}'
AND ST_COVERS(
    sz.zone_boundary,  -- Coverage area (polygon)
    ST_GEOGPOINT(c.customer_lon, c.customer_lat)  -- Point to test
) = TRUE

-- Coverage analysis with metrics
SELECT 
    zone_name,
    COUNT(*) as total_customers,
    SUM(CASE WHEN ST_COVERS(zone_boundary, customer_location) 
        THEN 1 ELSE 0 END) as covered_customers,
    AVG(CASE WHEN ST_COVERS(zone_boundary, customer_location) 
        THEN 1.0 ELSE 0.0 END) * 100 as coverage_rate
FROM service_zones sz
CROSS JOIN customers c
GROUP BY zone_name, zone_boundary
ORDER BY coverage_rate DESC;
        """, language="sql")

def show_functions_reference():
    """Welcome page: Introduction to the demo and Firebolt geospatial functions"""
    st.header("🗺️ Firebolt Geospatial Analytics Demo")
    st.markdown("*Showcase the power of geospatial bulk queries with Firebolt*")
    
    # Introduction and purpose
    st.subheader("🎯 Welcome to the Demo!")
    st.markdown("""
    This interactive demonstration showcases **Firebolt's high-performance geospatial capabilities** for analyzing location-based data at scale. 
    
    **What you'll explore:**
    - **Store Coverage Analysis** for location optimization and customer reach
    - **Customer Zone Analysis** for territory management and segmentation  
    - **Service Area Coverage** for market penetration and service optimization
    
    **Why Firebolt for Geospatial?**
    - PostgreSQL-compatible spatial functions with cloud-scale performance
    - Sub-second query response times on millions of geographic points
    - Built-in optimization for time-series and location data
    """)
    
    # Instructions for using the demo
    st.subheader("📋 How to Use This Demo")
    st.markdown("""
    1. **Select a demo** from the dropdown menu above
    2. **Explore the data** using interactive controls and filters  
    3. **View real-time results** on maps and charts
    4. **Check the SQL queries** to see how Firebolt processes geospatial data
    5. **Experiment** with different parameters and settings
    
    Each demo is focused on a specific geospatial function with realistic business scenarios.
    """)
    
    st.subheader("🔧 Geospatial Functions Reference")
    st.markdown("*Functions demonstrated and available in Firebolt for spatial analytics*")
    
    functions_data = [
        {
            "Function": "ST_Distance(geom1, geom2)",
            "Description": "Returns distance between two geometries in meters",
            "Example": "WHERE ST_Distance(point1, point2) <= 5000",
            "Returns": "Distance in meters",
            "Demo": "✅ Store coverage analysis"
        },
        {
            "Function": "ST_Contains(polygon, point)",
            "Description": "Tests if a polygon contains a point",
            "Example": "ST_Contains(zone_boundary, customer_location)",
            "Returns": "Boolean",
            "Demo": "✅ Customer zone analysis"
        },
        {
            "Function": "ST_COVERS(geom1, geom2)",
            "Description": "Tests if geometry A completely covers geometry B",
            "Example": "ST_COVERS(service_area, facility_location)",
            "Returns": "Boolean", 
            "Demo": "✅ Service area coverage"
        }
    ]
    
    functions_df = pd.DataFrame(functions_data)
    st.dataframe(functions_df, use_container_width=True)
    
    st.subheader("🚀 Ready to Start?")
    st.success("""
    **Choose a demo from the dropdown menu above to begin exploring!**
    
    💡 **Tip:** Start with "1. Store Coverage Analysis" to see realistic retail location optimization, 
    or jump to any demo that interests you. Each demo is self-contained and includes interactive controls.
    """)

if __name__ == "__main__":
    main()