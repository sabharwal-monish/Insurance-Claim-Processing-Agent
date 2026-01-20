"""
Database Initialization Script for Insurance Claim Processing Agent
Connects to Aiven MySQL and creates the insurance_sessions table
"""
import pymysql
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the database schema"""
    conn = None
    try:
        # Resolve SSL certificate path
        ssl_ca_path = os.path.join(os.path.dirname(__file__), 'ca.pem')
        
        if not os.path.exists(ssl_ca_path):
            print(f"❌ SSL certificate not found at: {ssl_ca_path}")
            return False
        
        print("🔐 Connecting to Aiven MySQL with SSL...")
        
        # Connect to database
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 15215)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl={'ca': ssl_ca_path},
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connected successfully!")
        
        # Read schema file
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'sql', 
            'schema.sql'
        )
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        with conn.cursor() as cursor:
            # Remove comments and split by semicolon
            statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    print(f"📝 Executing: {statement[:50]}...")
                    cursor.execute(statement)
            
            conn.commit()
            print("✅ Schema created successfully!")
            
            # Verify table exists
            cursor.execute("SHOW TABLES LIKE 'insurance_sessions'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Table 'insurance_sessions' verified!")
                
                # Show table structure
                cursor.execute("DESCRIBE insurance_sessions")
                columns = cursor.fetchall()
                print("\n📋 Table Structure:")
                for col in columns:
                    print(f"  - {col['Field']}: {col['Type']} ({col['Null']}, {col['Key']})")
                
                return True
            else:
                print("❌ Table verification failed!")
                return False
                
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn and conn.open:
            conn.close()
            print("🔒 Connection closed.")

def verify_schema():
    """Verify the database schema without modifying it"""
    conn = None
    try:
        ssl_ca_path = os.path.join(os.path.dirname(__file__), 'ca.pem')
        
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 15215)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl={'ca': ssl_ca_path},
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'insurance_sessions'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Table 'insurance_sessions' exists!")
                cursor.execute("DESCRIBE insurance_sessions")
                columns = cursor.fetchall()
                
                required_columns = [
                    'session_id', 'policy_number', 'claimant_name', 
                    'date_time_of_incident', 'vehicle_info', 
                    'incident_description', 'photo_uploaded'
                ]
                
                existing_columns = [col['Field'] for col in columns]
                missing = [c for c in required_columns if c not in existing_columns]
                
                if missing:
                    print(f"⚠️  Missing columns: {missing}")
                    return False
                else:
                    print("✅ All required columns present!")
                    return True
            else:
                print("❌ Table 'insurance_sessions' does not exist!")
                return False
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
        
    finally:
        if conn and conn.open:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        print("🔍 Verifying database schema...")
        success = verify_schema()
    else:
        print("🚀 Initializing database schema...")
        success = init_database()
    
    sys.exit(0 if success else 1)
