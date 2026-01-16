from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

# Insert officers
officers = [
    (1, 'Officer North', 'North'),
    (2, 'Officer South', 'South'),
    (3, 'Officer East', 'East'),
    (4, 'Officer West', 'West'),
    (5, 'Admin Officer', 'Admin')
]

for officer in officers:
    try:
        cursor.execute("INSERT INTO officers (officer_id, officer_name, zone) VALUES (%s, %s, %s)", officer)
    except Exception as e:
        pass

conn.commit()
print("✅ Officers added/verified")
cursor.close()
conn.close()
