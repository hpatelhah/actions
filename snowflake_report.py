import os
import logging
from datetime import datetime
import snowflake.connector
import pandas as pd

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OUTPUT_FILE = f"snowflake_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
EMPTY_COLUMNS = ['Notes', 'Status', 'Follow_Up_Date', 'Assigned_To']

# SQL Query with FULL table path
SQL_QUERY = """
    SELECT * 
    FROM DW_PROD.INTEGRATION.FACT_VISIT_MERGED 
    LIMIT 5
"""

# Connect to Snowflake (NO database/schema needed)
def connect_to_snowflake():
    """Create Snowflake connection"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Connecting to Snowflake...")
        logger.info(f"   Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
        logger.info(f"   User: {os.getenv('SNOWFLAKE_USER')}")
        logger.info(f"   Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE')}")
        
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE') if os.getenv('SNOWFLAKE_ROLE') else None
            # NOTE: No database or schema specified - using fully qualified names in queries
        )
        
        logger.info("✅ Connected successfully!")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {str(e)}")
        raise

# Execute Query
def execute_query(conn, query):
    """Run SQL query and return DataFrame"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Executing SQL query...")
        logger.info(f"   Query: {query.strip()}")
        
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
        logger.info(f"   📝 Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Query execution failed: {str(e)}")
        raise

# Create Excel File
def create_excel(df, filename=OUTPUT_FILE):
    """Save DataFrame to Excel with additional empty columns"""
    try:
        logger.info("=" * 60)
        logger.info("🔵 Creating Excel file...")
        
        logger.info(f"   Adding {len(EMPTY_COLUMNS)} empty columns: {', '.join(EMPTY_COLUMNS)}")
        for col in EMPTY_COLUMNS:
            df[col] = ''
        
        logger.info(f"   Writing to: {filename}")
        df.to_excel(filename, index=False, engine='openpyxl')
        
        file_size = os.path.getsize(filename) / 1024
        
        logger.info("✅ Excel file created successfully!")
        logger.info(f"   📁 Filename: {filename}")
        logger.info(f"   💾 Size: {file_size:.2f} KB")
        logger.info(f"   📊 Rows: {len(df):,}")
        logger.info(f"   📋 Total columns: {len(df.columns)}")
        
        return filename
        
    except Exception as e:
        logger.error(f"❌ Excel creation failed: {str(e)}")
        raise

# Main Function
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
