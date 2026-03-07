"""
Seed script to populate the meals database with sample data.
Run: python backend/seed.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from models.database import get_db_connection
from pull import init_db

def seed_database():
    """Load seed.sql file and execute it against the database."""
    
    # Initialize the database schema first
    print("📋 Initializing database schema...")
    init_db()
    
    # Get path to seed.sql file
    seed_file = os.path.join(os.path.dirname(__file__), "data", "seed.sql")
    
    if not os.path.exists(seed_file):
        print(f"❌ Seed file not found: {seed_file}")
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Read and execute seed.sql
            with open(seed_file, 'r') as f:
                sql_script = f.read()
            
            cursor.executescript(sql_script)
            conn.commit()
            
            # Verify data was inserted
            cursor.execute("SELECT COUNT(*) as count FROM meals")
            count = cursor.fetchone()['count']
        
        print(f"✅ Database seeded successfully!")
        print(f"📊 Total meals in database: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
