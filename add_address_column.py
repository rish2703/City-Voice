from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE complaints ADD COLUMN address VARCHAR(255)')
    conn.commit()
    print('✅ Added address column to complaints table')
except Exception as e:
    if 'Duplicate column' in str(e):
        print('⚠️ Address column already exists')
    else:
        print(f'Error: {e}')
finally:
    cursor.close()
    conn.close()
