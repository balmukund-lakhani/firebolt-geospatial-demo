# Firebolt Geospatial Analytics Demo

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Firebolt](https://img.shields.io/badge/Firebolt-FF6900?style=flat&logo=firebolt&logoColor=white)](https://www.firebolt.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)](https://python.org)

An interactive Streamlit application showcasing the power of **Firebolt's geospatial functions** for large-scale location analytics. Experience sub-second query performance on millions of geographic data points with PostgreSQL-compatible spatial functions.

## 🌟 Features

### **Business-Focused Geospatial Analytics**
- **🏪 Store Coverage Analysis** - Location optimization using `ST_DISTANCE` 
- **🎯 Customer Zone Analysis** - Territory management with `ST_CONTAINS`
- **📍 Service Area Coverage** - Market penetration using `ST_COVERS`
- **📚 Functions Reference** - Complete spatial functions documentation

### **Technical Highlights**
- **Cloud-Scale Performance**: Sub-second queries on millions of coordinates
- **PostgreSQL Compatible**: Standard PostGIS spatial functions
- **Real-Time Visualization**: Interactive maps with Plotly
- **Production Ready**: Configurable database connections
- **Sample Data Included**: Realistic Bengaluru geospatial dataset

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Firebolt account with database access
- Streamlit (installed via requirements)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd FBDemo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebolt credentials
   ```

4. **Generate sample data**
   ```bash
   python generate_sample_data.py
   ```

5. **Run the demo**
   ```bash
   streamlit run app_geospatial_demo.py
   ```

## 📊 Sample Data

The demo includes a sample data generator that creates realistic geospatial data for Bengaluru:

### **Customer Orders Dataset (50,000 records)**
- Realistic customer coordinates across Bengaluru
- Order values with exponential distribution
- 8 store locations in major districts
- 90 days of transaction history

### **Geographic Zones Dataset (10 zones)**
- Commercial districts (CBD, tech hubs)
- Residential areas (JP Nagar, HSR Layout)
- Mixed-use zones (Koramangala, Marathahalli)
- Industrial areas (North Bengaluru)

### **Store Locations**
| Store ID | Location | District |
|----------|----------|----------|
| STORE_001 | Koramangala | Central |
| STORE_002 | Indiranagar | East |
| STORE_003 | Whitefield | East |
| STORE_004 | Electronic City | South |
| STORE_005 | JP Nagar | South |
| STORE_006 | Marathahalli | East |
| STORE_007 | HSR Layout | South |
| STORE_008 | Rajajinagar | West |

## 🗄️ Database Schema

### Required Tables

#### `customer_orders`
Customer transaction data with geographic coordinates:
```sql
CREATE TABLE customer_orders (
    order_id TEXT,
    customer_lat DOUBLE PRECISION,
    customer_lon DOUBLE PRECISION,
    order_value DOUBLE PRECISION,
    order_date TEXT,
    store_id TEXT
);
```

#### `geo_zones` 
Geographic zones and boundaries:
```sql
CREATE TABLE geo_zones (
    zone_id TEXT,
    zone_name TEXT,
    zone_type TEXT,
    zone_lat DOUBLE PRECISION,
    zone_lon DOUBLE PRECISION,
    zone_radius DOUBLE PRECISION
);
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with your Firebolt credentials:

```env
FIREBOLT_CLIENT_ID=your_client_id
FIREBOLT_CLIENT_SECRET=your_client_secret
FIREBOLT_ACCOUNT_NAME=your_account_name
FIREBOLT_DATABASE=your_database_name
FIREBOLT_ENGINE=your_engine_name
```

### Customization
- **Geographic Focus**: Update coordinate bounds in demo functions
- **Data Size**: Modify `num_orders` in `generate_sample_data.py`
- **Styling**: Customize colors and map settings in Plotly configurations

## 🎯 Demo Walkthroughs

### 1. Store Coverage Analysis
- **Purpose**: Optimize store locations and analyze customer reach
- **Function**: `ST_DISTANCE` for proximity calculations
- **Business Value**: Identify coverage gaps and expansion opportunities
- **Sample Query**: Find customers within 5km of each store

### 2. Customer Zone Analysis  
- **Purpose**: Territory management and customer segmentation
- **Function**: `ST_CONTAINS` for point-in-polygon analysis
- **Business Value**: Understand market penetration by geographic zones
- **Sample Query**: Analyze customer distribution across zones

### 3. Service Area Coverage
- **Purpose**: Market analysis and service optimization
- **Function**: `ST_COVERS` for area coverage analysis  
- **Business Value**: Validate service boundaries and capacity planning
- **Sample Query**: Check if service areas cover customer locations

## 🔧 Development

### Project Structure
```
FBDemo/
├── app_geospatial_demo.py     # Main Streamlit application
├── generate_sample_data.py    # Sample data generator
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── setup.py                 # Quick setup script
├── schema_customer_orders.sql # Customer orders table schema
├── schema_geo_zones.sql      # Geographic zones table schema
└── README.md                # This documentation
```

### Key Dependencies
- **streamlit** ≥1.28.0 - Web application framework
- **firebolt-sdk** ≥1.4.0 - Firebolt database connector
- **plotly** ≥5.15.0 - Interactive visualizations
- **pandas** ≥2.0.0 - Data manipulation
- **python-dotenv** ≥1.0.0 - Environment configuration
- **numpy** ≥1.24.0 - Numerical operations

## 📊 Performance Insights

**Firebolt Advantages for Geospatial Analytics:**
- **Speed**: Sub-second response times on millions of coordinates
- **Scale**: Built for cloud-scale data processing
- **Compatibility**: PostgreSQL spatial functions without migration
- **Optimization**: Native support for time-series and location data
- **Simplicity**: Standard SQL with spatial extensions

## 🛠️ Troubleshooting

### Common Issues

**Connection Problems:**
```bash
# Verify your .env file has correct credentials
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Account:', os.getenv('FIREBOLT_ACCOUNT_NAME'))"
```

**No Sample Data:**
```bash
# Run the data generator
python generate_sample_data.py
```

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Firebolt Documentation**: [docs.firebolt.io](https://docs.firebolt.io)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Issues**: Open an issue in this repository

## 🏷️ Tags

`geospatial` `analytics` `firebolt` `streamlit` `postgis` `location-intelligence` `spatial-analysis` `data-visualization` `bengaluru` `sample-data`

---

**Built with ❤️ using Firebolt and Streamlit**