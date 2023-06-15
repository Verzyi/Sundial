from sqlalchemy import create_engine, MetaData, Table, delete

# Create an SQLAlchemy engine
engine = create_engine('sqlite:///database.db', echo=False)

# Create a MetaData object
metadata = MetaData(bind=engine)

# Reflect the table structure from the database
metadata.reflect()

# Get the existing table
powder_blends_table = metadata.tables['PowderBlends']

# Create a delete query to remove records after May
delete_query = delete(powder_blends_table).where(powder_blends_table.c.DateAdded > '2023-05-31')

# Connect to the database
with engine.connect() as conn:
    # Execute the delete query
    conn.execute(delete_query)

print('Records removed successfully.')
