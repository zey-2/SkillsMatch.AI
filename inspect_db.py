#!/usr/bin/env python3
"""
Inspect SQLite database structure and contents
"""
import sqlite3
import os
from pathlib import Path

def inspect_database(db_path):
    """Inspect SQLite database structure and contents"""
    print(f"🔍 Inspecting database: {db_path}")
    print(f"📍 Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    # Get file size
    file_size = os.path.getsize(db_path)
    print(f"📊 Database size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables found: {len(tables)}")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗂️  Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("   Columns:")
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                pk_indicator = " (PK)" if pk else ""
                print(f"     - {name}: {data_type}{pk_indicator}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   📊 Rows: {count}")
            
            # Show sample data for key tables
            if table_name in ['jobs', 'user_profiles'] and count > 0:
                print("   📋 Sample data:")
                if table_name == 'jobs':
                    cursor.execute(f"SELECT job_id, title, company_name FROM {table_name} LIMIT 3;")
                elif table_name == 'user_profiles':
                    cursor.execute(f"SELECT user_id, name, title FROM {table_name} LIMIT 3;")
                
                sample_rows = cursor.fetchall()
                for row in sample_rows:
                    print(f"     {row}")
        
        conn.close()
        print("\n✅ Database inspection complete!")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function to inspect both database files"""
    base_path = Path(__file__).parent
    
    # Check both potential database locations
    db_files = [
        base_path / "web" / "data" / "skillsmatch.db",
        base_path / "web" / "skillsmatch.db"
    ]
    
    for db_path in db_files:
        if db_path.exists():
            inspect_database(str(db_path))
            print("\n" + "="*70 + "\n")
        else:
            print(f"⚠️  Database not found: {db_path}")

if __name__ == "__main__":
    main()