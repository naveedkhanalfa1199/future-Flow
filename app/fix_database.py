import sqlite3

db_path = r'C:\Users\SAUK-119 NA\OneDrive\Desktop\sauk119-complete\app\database_backups\sauk119.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE university_fields ADD COLUMN general_max_study_gap VARCHAR(20)')
    conn.commit()
    print("Column added successfully!")
except Exception as e:
    print(f"Error: {e}")

conn.close()