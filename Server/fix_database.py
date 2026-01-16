"""
Database Migration Script
Fixes the schema by adding missing tenant_id columns or recreating tables

Run this on the server to fix the database schema:
  python fix_database.py

Options:
  --drop   Drop and recreate all tables (WARNING: loses all data)
  --alter  Try to ALTER tables to add missing columns (safer)
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.base import engine, Base, SessionLocal
from db.models import *
from sqlalchemy import text, inspect


def check_schema():
    """Check current schema"""
    inspector = inspect(engine)
    
    print("Current Database Schema:")
    print("=" * 60)
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        print(f"\n📋 Table: {table_name}")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
    
    # Check for tenant_id in spans
    spans_columns = {col['name'] for col in inspector.get_columns('spans')} if 'spans' in inspector.get_table_names() else set()
    
    if 'tenant_id' not in spans_columns:
        print("\n⚠️  WARNING: spans table is missing tenant_id column!")
        return False
    
    print("\n✅ Schema looks correct!")
    return True


def alter_tables():
    """Try to add missing columns with ALTER"""
    print("\n🔧 Attempting to add missing columns...")
    
    with engine.connect() as conn:
        try:
            # Check if tenant_id exists in spans
            result = conn.execute(text("PRAGMA table_info(spans)")).fetchall()
            column_names = [row[1] for row in result]
            
            if 'tenant_id' not in column_names:
                print("   Adding tenant_id to spans table...")
                conn.execute(text("ALTER TABLE spans ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
                conn.commit()
                print("   ✅ Added tenant_id column")
            else:
                print("   ✅ tenant_id already exists in spans")
                
        except Exception as e:
            print(f"   ❌ Failed to alter table: {e}")
            return False
    
    return True


def recreate_tables():
    """Drop and recreate all tables"""
    print("\n⚠️  DROPPING ALL TABLES AND RECREATING...")
    print("   This will DELETE ALL DATA!")
    
    confirm = input("   Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("   Aborted.")
        return False
    
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 Creating all tables with new schema...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables recreated successfully!")
    return True


def main():
    print("=" * 60)
    print("🔧 Nexarch Database Migration Tool")
    print("=" * 60)
    
    if '--drop' in sys.argv:
        recreate_tables()
    elif '--alter' in sys.argv:
        alter_tables()
    else:
        # Check schema first
        if not check_schema():
            print("\n💡 To fix, run one of:")
            print("   python fix_database.py --alter  # Add missing columns (safer)")
            print("   python fix_database.py --drop   # Recreate tables (loses data)")
    
    # Verify final state
    print("\n" + "=" * 60)
    check_schema()


if __name__ == "__main__":
    main()
