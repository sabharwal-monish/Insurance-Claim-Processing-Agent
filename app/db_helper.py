import pymysql
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_db_connection(max_retries=3):
    """
    Establishes a PyMySQL connection to Aiven MySQL with SSL.
    Includes retry logic with exponential backoff for resilience.
    
    Args:
        max_retries (int): Maximum number of connection attempts
        
    Returns:
        pymysql.Connection or None: Database connection object or None on failure
    """
    # Validate required environment variables
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return None
    
    # Resolve SSL certificate path dynamically
    ssl_ca_path = os.path.join(os.path.dirname(__file__), 'ca.pem')
    
    if not os.path.exists(ssl_ca_path):
        print(f"❌ SSL certificate not found at: {ssl_ca_path}")
        return None
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", 15215)),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                ssl={'ca': ssl_ca_path},
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10,
                read_timeout=10,
                write_timeout=10
            )
            
            # Test the connection with a simple query
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            print(f"✅ Database connection established (attempt {attempt + 1}/{max_retries})")
            return conn
            
        except pymysql.err.OperationalError as e:
            error_code = e.args[0] if e.args else 'unknown'
            print(f"⚠️  Connection attempt {attempt + 1}/{max_retries} failed: {error_code} - {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Database connection failed after {max_retries} attempts")
                return None
                
        except Exception as e:
            print(f"❌ Unexpected database error: {type(e).__name__} - {str(e)}")
            return None
    
    return None
