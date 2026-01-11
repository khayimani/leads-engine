import sqlite3
import pandas as pd

conn = sqlite3.connect("leads_database.db")
df = pd.read_sql_query("SELECT * FROM leads", conn)
print(df)
conn.close()