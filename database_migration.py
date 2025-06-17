# migrate_database.py - Add login system columns to existing database
"""
Run this script to add the new login system columns to your existing database.
Usage: python migrate_database.py
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = 'fire_alerts.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Run your Flask app first to create it.")
        return
    
    print("🔄 Migrating database for login system...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns in user table
        cursor.execute("PRAGMA table_info(user)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Add email column if it doesn't exist
        if 'email' not in existing_columns:
            print("➕ Adding email column...")
            cursor.execute('ALTER TABLE user ADD COLUMN email VARCHAR(120)')
            
        # Add password_hash column if it doesn't exist
        if 'password_hash' not in existing_columns:
            print("➕ Adding password_hash column...")
            cursor.execute('ALTER TABLE user ADD COLUMN password_hash VARCHAR(128)')
            
        # Add last_login column if it doesn't exist
        if 'last_login' not in existing_columns:
            print("➕ Adding last_login column...")
            cursor.execute('ALTER TABLE user ADD COLUMN last_login DATETIME')
            
        # Add is_admin column if it doesn't exist
        if 'is_admin' not in existing_columns:
            print("➕ Adding is_admin column...")
            cursor.execute('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0')
            
        # Add created_at column if it doesn't exist
        if 'created_at' not in existing_columns:
            print("➕ Adding created_at column...")
            cursor.execute('ALTER TABLE user ADD COLUMN created_at DATETIME')
            # Update existing users with current timestamp
            cursor.execute('UPDATE user SET created_at = ? WHERE created_at IS NULL', (datetime.utcnow(),))
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(user)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns: {updated_columns}")
        
        # Show existing users
        cursor.execute("SELECT id, name, phone, email FROM user")
        users = cursor.fetchall()
        if users:
            print(f"\n👥 Existing users ({len(users)}):")
            for user in users:
                print(f"  - ID: {user[0]}, Name: {user[1]}, Phone: {user[2]}, Email: {user[3] or 'None'}")
        else:
            print("\n👥 No existing users found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrate_database()