import os
import logging
import snowflake.connector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_access():
    """Check what databases, schemas, and tables you can access"""
    try:
        logger.info("Connecting to Snowflake...")
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE') if os.getenv('SNOWFLAKE_ROLE') else None
        )
        
        cursor = conn.cursor()
        
        # Check current context
        logger.info("=" * 60)
        logger.info("CURRENT SESSION INFO:")
        logger.info("=" * 60)
        cursor.execute("""
            SELECT 
                CURRENT_USER() as user,
                CURRENT_ROLE() as role,
                CURRENT_WAREHOUSE() as warehouse,
                CURRENT_DATABASE() as database,
                CURRENT_SCHEMA() as schema
        """)
        result = cursor.fetchone()
        logger.info(f"User: {result[0]}")
        logger.info(f"Role: {result[1]}")
        logger.info(f"Warehouse: {result[2]}")
        logger.info(f"Database: {result[3]}")
        logger.info(f"Schema: {result[4]}")
        
        # List available databases
        logger.info("=" * 60)
        logger.info("AVAILABLE DATABASES:")
        logger.info("=" * 60)
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        for db in databases:
            logger.info(f"  - {db[1]}")  # database name is in column 1
        
        # Try to find your table
        logger.info("=" * 60)
        logger.info("SEARCHING FOR 'FACT_VISIT_MERGED' TABLE:")
        logger.info("=" * 60)
        
        for db in databases:
            db_name = db[1]
            try:
                cursor.execute(f"SHOW SCHEMAS IN DATABASE {db_name}")
                schemas = cursor.fetchall()
                
                for schema in schemas:
                    schema_name = schema[1]
                    try:
                        cursor.execute(f"SHOW TABLES IN {db_name}.{schema_name}")
                        tables = cursor.fetchall()
                        
                        for table in tables:
                            table_name = table[1]
                            if 'FACT_VISIT_MERGED' in table_name:
                                logger.info(f"✅ FOUND: {db_name}.{schema_name}.{table_name}")
                    except:
                        pass
            except:
                pass
        
        # Check the specific database from secrets
        secret_db = os.getenv('SNOWFLAKE_DATABASE')
        secret_schema = os.getenv('SNOWFLAKE_SCHEMA')
        
        logger.info("=" * 60)
        logger.info(f"CHECKING CONFIGURED DATABASE: {secret_db}")
        logger.info("=" * 60)
        
        try:
            cursor.execute(f"USE DATABASE {secret_db}")
            cursor.execute(f"USE SCHEMA {secret_schema}")
            
            logger.info(f"✅ Can access {secret_db}.{secret_schema}")
            
            cursor.execute(f"SHOW TABLES IN {secret_db}.{secret_schema}")
            tables = cursor.fetchall()
            
            logger.info(f"Tables in {secret_db}.{secret_schema}:")
            for table in tables[:10]:  # Show first 10
                logger.info(f"  - {table[1]}")
            
            if len(tables) > 10:
                logger.info(f"  ... and {len(tables) - 10} more")
                
        except Exception as e:
            logger.error(f"❌ Cannot access {secret_db}.{secret_schema}: {str(e)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    check_access()
