from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

# First, delete any existing
cursor.execute("DELETE FROM officers")

# Insert officers with correct column names (name, department instead of officer_name, zone)
officers = [
    (1, 'Officer North', 'North'),
    (2, 'Officer South', 'South'),
    (3, 'Officer East', 'East'),
    (4, 'Officer West', 'West'),
    (5, 'Admin Officer', 'Admin')
]

for officer in officers:
    cursor.execute("INSERT INTO officers (officer_id, name, department) VALUES (%s, %s, %s)", officer)
    print(f"✅ Inserted: {officer}")

conn.commit()

# Verify
cursor.execute("SELECT * FROM officers")
results = cursor.fetchall()
print(f"\nTotal officers in database: {len(results)}")
for r in results:
    print(f"  Officer ID {r[0]}: {r[1]} - {r[2]} Department")

cursor.close()
conn.close()
