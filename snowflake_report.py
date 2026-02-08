import os
import logging
from datetime import datetime
import snowflake.connector
import pandas as pd

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_FILE = f"snowflake_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
EMPTY_COLUMNS = ['Notes', 'Status', 'Follow_Up_Date', 'Assigned_To']

# SQL Query
SQL_QUERY = """
    SELECT *
    FROM VW_CLIENT_CAREGIVER_RELATIONSHIP
    ORDER BY MONTH_YEAR DESC
"""

# -----------------------------
# 1. Connect to Snowflake
# -----------------------------
def connect_to_snowflake():
    """Create Snowflake connection from environment variables"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Connecting to Snowflake...")
        logger.info(f"   Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
        logger.info(f"   User: {os.getenv('SNOWFLAKE_USER')}")
        logger.info(f"   Database: {os.getenv('SNOWFLAKE_DATABASE')}")
        logger.info(f"   Schema: {os.getenv('SNOWFLAKE_SCHEMA')}")
        
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            role=os.getenv('SNOWFLAKE_ROLE') if os.getenv('SNOWFLAKE_ROLE') else None
        )
        
        logger.info("✅ Connected successfully!")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {str(e)}")
        raise

# -----------------------------
# 2. Execute Query
# -----------------------------
def execute_query(conn, query):
    """Run SQL query and return DataFrame"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Executing SQL query...")
        logger.info(f"   Query preview: {query[:80]}...")
        
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Fetch results
        logger.info("   Fetching results...")
        results = cursor.fetchall()
        
        # Get column names
        columns = [col[0] for col in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        cursor.close()
        
        logger.info("✅ Query completed successfully!")
        logger.info(f"   📊 Rows: {len(df):,}")
        logger.info(f"   📋 Columns: {len(df.columns)}")
        logger.info(f"   📝 Column names: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise

# -----------------------------
# 3. Create Excel File
# -----------------------------
def create_excel(df, filename=OUTPUT_FILE):
    """Save DataFrame to Excel with additional empty columns"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Creating Excel file...")
        
        # Show original structure
        logger.info(f"   Original columns: {len(df.columns)}")
        
        # Add empty columns
        logger.info(f"   Adding {len(EMPTY_COLUMNS)} empty columns:")
        for col in EMPTY_COLUMNS:
            logger.info(f"      - {col}")
            df[col] = ''
        
        logger.info(f"   Final columns: {len(df.columns)}")
        
        # Save to Excel
        logger.info(f"   Writing to: {filename}")
        df.to_excel(filename, index=False, engine='openpyxl')
        
        # File info
        file_size = os.path.getsize(filename) / 1024
        
        logger.info("✅ Excel file created successfully!")
        logger.info(f"   📁 Filename: {filename}")
        logger.info(f"   💾 Size: {file_size:.2f} KB")
        logger.info(f"   📊 Rows: {len(df):,}")
        logger.info(f"   📋 Columns: {len(df.columns)}")
        
        return filename
        
    except Exception as e:
        logger.error(f"❌ Excel creation failed: {str(e)}")
        raise

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def main():
    """Execute the complete workflow"""
    conn = None
    
    try:
        logger.info("=" * 60)
        logger.info("🚀 SNOWFLAKE REPORT GENERATION STARTED")
        logger.info("=" * 60)
        
        # Step 1: Connect
        conn = connect_to_snowflake()
        
        # Step 2: Query
        df = execute_query(conn, SQL_QUERY)
        
        # Step 3: Create Excel
        filename = create_excel(df)
        
        logger.info("=" * 60)
        logger.info("🎉 SUCCESS! Report generation completed")
        logger.info(f"   📊 Total records: {len(df):,}")
        logger.info(f"   📁 Output file: {filename}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"💥 PROCESS FAILED")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 60)
        raise
        
    finally:
        if conn:
            conn.close()
            logger.info("🔌 Snowflake connection closed")

if __name__ == "__main__":
    main()
