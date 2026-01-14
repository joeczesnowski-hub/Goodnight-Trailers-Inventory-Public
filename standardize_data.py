import sqlite3
import re

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Get all text columns to search and replace ALUIM/ALIUM/ALUMN with ALUM
text_columns = ['type', 'description', 'dimensions', 'capacity', 'condition', 'color', 'make', 'vin']

for column in text_columns:
    cursor.execute(f"SELECT id, {column} FROM inventory WHERE {column} IS NOT NULL")
    rows = cursor.fetchall()
    
    for row_id, col_val in rows:
        if col_val:
            # Replace ALUIM, ALIUM, and ALUMN with ALUM (case insensitive)
            cleaned = re.sub(r'ALUIM', 'ALUM', str(col_val), flags=re.IGNORECASE)
            cleaned = re.sub(r'ALIUM', 'ALUM', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'ALUMN', 'ALUM', cleaned, flags=re.IGNORECASE)
            
            if cleaned != col_val:
                cursor.execute(f"UPDATE inventory SET {column} = ? WHERE id = ?", (cleaned, row_id))