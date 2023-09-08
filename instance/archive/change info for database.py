from sqlalchemy import create_engine
engine = create_engine('sqlite://', echo=False)

import sqlite3
import sqlalchemy 
try:

	conn = sqlite3.connect('database.db')
	c = conn.cursor()
	c.execute(
	"""
	ALTER TABLE Users
	RENAME COLUMN userID TO id;

	""")
	conn.commit()
	conn.close()
	print('name changed')
except Exception as e:
	print(e)
