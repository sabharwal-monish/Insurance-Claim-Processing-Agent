import mysql.connector
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DYNAMIC PATH CONFIGURATION ---
# Locally: looks in /certs/ca.pem
# On Render: looks in /etc/secrets/ca.pem (Render's default secret path)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_CA_PATH = os.path.join(BASE_DIR, "certs", "ca.pem")
RENDER_CA_PATH = "/etc/secrets/ca.pem"

CA_PATH = RENDER_CA_PATH if os.path.exists(RENDER_CA_PATH) else LOCAL_CA_PATH

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 15215)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "defaultdb"),
            ssl_ca=CA_PATH,
            ssl_verify_cert=True,
            use_pure=True 
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"❌ Connection Failed: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                claimant_name VARCHAR(255),
                policy_number VARCHAR(255),
                date_time_of_incident VARCHAR(255),
                vehicle_info TEXT,
                incident_description TEXT,
                photo_uploaded BOOLEAN DEFAULT FALSE,
                status VARCHAR(50) DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Database verified using certificate at: {CA_PATH}")

if __name__ == "__main__":
    init_db()