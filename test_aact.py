import psycopg2
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

def test_aact_connection():
    """Test connection to AACT database"""
    try:
        conn = psycopg2.connect(
            dbname="aact",
            user=os.getenv("AACT_USER"),
            password=os.getenv("AACT_PASSWORD"),
            host="aact-db.ctti-clinicaltrials.org",
            port=5432
        )
        print("✅ Successfully connected to AACT database!")
        
        # Test a simple query
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM ctgov.studies;")
        count = cur.fetchone()[0]
        print(f"Total studies in database: {count}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_aact_connection()