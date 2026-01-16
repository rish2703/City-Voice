"""
Check if complaints are being saved to the database
Run this script to verify your complaints are in the database
"""

from database.db import get_connection
import pandas as pd

def check_all_complaints():
    """Check all complaints in the database"""
    print("=" * 60)
    print("Checking Complaints in Database")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        print("❌ Failed to connect to database!")
        print("\nTroubleshooting:")
        print("1. Check if MySQL is running")
        print("2. Verify credentials in database/db.py")
        print("3. Ensure 'cityvoice' database exists")
        return
    
    try:
        # Get all complaints
        query = "SELECT * FROM complaints ORDER BY complaint_id DESC"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("\n⚠️ No complaints found in the database!")
            print("\nPossible reasons:")
            print("- No complaints have been submitted yet")
            print("- Database connection issue")
            print("- Wrong database being accessed")
        else:
            print(f"\n✅ Found {len(df)} complaint(s) in the database!")
            print("\n" + "=" * 60)
            print("Recent Complaints:")
            print("=" * 60)
            
            # Display recent complaints
            for idx, row in df.head(10).iterrows():
                print(f"\nComplaint ID: #{row['complaint_id']}")
                print(f"  Name: {row['citizen_name']}")
                print(f"  Location: {row['location']}")
                print(f"  Category: {row['category']}")
                print(f"  Priority: {row['priority']}")
                print(f"  Status: {row['status']}")
                print(f"  Zone: {row['zone']}")
                print(f"  Submitted: {row['created_at']}")
                print(f"  Description: {row['complaint_text'][:50]}...")
                print("-" * 60)
            
            if len(df) > 10:
                print(f"\n... and {len(df) - 10} more complaint(s)")
            
            # Summary statistics
            print("\n" + "=" * 60)
            print("Summary Statistics:")
            print("=" * 60)
            print(f"Total Complaints: {len(df)}")
            print(f"By Status:")
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            print(f"\nBy Category:")
            category_counts = df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  {category}: {count}")
            
            print(f"\nBy Priority:")
            priority_counts = df['priority'].value_counts()
            for priority, count in priority_counts.items():
                print(f"  {priority}: {count}")
            
            print(f"\nBy Zone:")
            zone_counts = df['zone'].value_counts()
            for zone, count in zone_counts.items():
                print(f"  {zone}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if 'complaints' table exists")
        print("2. Run: python database/setup_database.sql")
        print("3. Check database connection")

if __name__ == "__main__":
    check_all_complaints()

