import json
import sqlite3

# Connect to SQLite (creates the database file if it doesn't exist)
conn = sqlite3.connect('rapport.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS Rapport')

# Create the table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Rapport (
    RapportID INTEGER PRIMARY KEY AUTOINCREMENT,
    Sammenlagt_Pris FLOAT,
    Antal_Udlejede_Biler INTEGER,
    RapportDato DATE
)
''')

conn.commit()
# Insert dummy data into the table
cursor.execute('''
INSERT INTO Rapport (RapportID, Sammenlagt_Pris, Antal_Udlejede_Biler, RapportDato)
VALUES
(1, 1000000, 80, '2022-01-01'),
(2, 1400000, 100, '2023-02-15'),
(3, 1600000, 120, '2024-03-10')
''')

conn.commit()
conn.close()