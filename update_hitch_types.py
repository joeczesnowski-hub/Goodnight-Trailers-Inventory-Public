import sqlite3
import re

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Update Hitch Type from Description
cursor.execute("UPDATE inventory SET hitch_type = 'Gooseneck' WHERE hitch_type IS NULL AND (Description LIKE '%Gooseneck%' OR Description LIKE '%Goose neck%' OR Description LIKE '%GN%' OR Description LIKE '%G/N%')")
cursor.execute("UPDATE inventory SET hitch_type = 'Gooseneck' WHERE hitch_type IS NULL AND (type LIKE '%Gooseneck%' OR type LIKE '%Goose neck%' OR type LIKE '%GN%' OR type LIKE '%G/N%')")
cursor.execute("UPDATE inventory SET hitch_type = 'Bumper-pull' WHERE hitch_type IS NULL AND (Description LIKE '%BP%' OR Description LIKE '%Bumperpull%' OR Description LIKE '%Bumper Pull%' OR Description LIKE '%B/P%')")
cursor.execute("UPDATE inventory SET hitch_type = 'Bumper-pull' WHERE hitch_type IS NULL AND (type LIKE '%BP%' OR type LIKE '%Bumperpull%' OR type LIKE '%Bumper Pull%' OR type LIKE '%Bumper-pull%' OR type LIKE '%B/P%')")
cursor.execute("UPDATE inventory SET hitch_type = 'Bumper-pull' WHERE hitch_type IS NULL")

# Clean Description
cursor.execute("UPDATE inventory SET Description = REPLACE(Description, 'Gooseneck', '') WHERE Description LIKE '%Gooseneck%'")
cursor.execute("UPDATE inventory SET Description = REPLACE(Description, 'Goose neck', '') WHERE Description LIKE '%Goose neck%'")
cursor.execute("UPDATE inventory SET Description = REPLACE(Description, 'G/N', '') WHERE Description LIKE '%G/N%'")
cursor.execute("UPDATE inventory SET Description = REPLACE(Description, 'Bumper Pull', '') WHERE Description LIKE '%Bumper Pull%'")
cursor.execute("UPDATE inventory SET Description = REPLACE(Description, 'B/P', '') WHERE Description LIKE '%B/P%'")

# Clean Type - remove hitch indicators
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Gooseneck', '') WHERE type LIKE '%Gooseneck%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'G/N', '') WHERE type LIKE '%G/N%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Bumper Pull', '') WHERE type LIKE '%Bumper Pull%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Bumper-pull', '') WHERE type LIKE '%Bumper-pull%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'B/P', '') WHERE type LIKE '%B/P%'")

# Replace DT with Dump Trailer
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'DT', 'Dump Trailer') WHERE type LIKE '%DT%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'D T', 'Dump Trailer') WHERE type LIKE '%D T%'")

# Standardize all Car Hauler variations to CAR HAULER (all caps)
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Car Hauler', 'CAR HAULER') WHERE type LIKE '%Car Hauler%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Carhauler', 'CAR HAULER') WHERE type LIKE '%Carhauler%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'CarHauler', 'CAR HAULER') WHERE type LIKE '%CarHauler%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'car hauler', 'CAR HAULER') WHERE type LIKE '%car hauler%'")

# Standardize all Deckover variations to DECK OVER (all caps with space)
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'DECKOVER', 'DECK OVER') WHERE type LIKE '%DECKOVER%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Deckover', 'DECK OVER') WHERE type LIKE '%Deckover%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'DeckOver', 'DECK OVER') WHERE type LIKE '%DeckOver%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'deckover', 'DECK OVER') WHERE type LIKE '%deckover%'")
cursor.execute("UPDATE inventory SET type = REPLACE(type, 'Deck Over', 'DECK OVER') WHERE type LIKE '%Deck Over%'")

# Get all rows and clean up spaced abbreviations
cursor.execute("SELECT id, type FROM inventory WHERE type IS NOT NULL")
rows = cursor.fetchall()

for row_id, type_val in rows:
    if type_val:
        # Remove spaced single letters (H D -> HD, D T -> DT, etc)
        cleaned = re.sub(r'([A-Z])\s+([A-Z])(?=\s|$)', r'\1\2', type_val)
        # Remove duplicate consecutive words
        cleaned = re.sub(r'\b(\w+)\s+\1\b', r'\1', cleaned)
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if cleaned != type_val:
            cursor.execute("UPDATE inventory SET type = ? WHERE id = ?", (cleaned, row_id))

conn.commit()
conn.close()
print("Hitch type update completed successfully!")