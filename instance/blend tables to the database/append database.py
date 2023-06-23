import pandas as pd
from sqlalchemy import create_engine
import sqlite3

class DatabaseAppender:
    def __init__(self, file_name, table_name):
        self.file_name = file_name
        self.table_name = table_name
        self.engine = create_engine('sqlite://', echo=False)
        try:
            self.conn = sqlite3.connect("database.db")
        except Exception as e:
            print(e)
    
    def append_to_database(self):
        df = pd.read_csv(self.file_name, index_col=False)
        df.columns = [column.strip() for column in df.columns]  # Remove leading/trailing spaces from column names
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Remove the existing table if it exists
        c.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        
        # Create the table using the DataFrame columns and their corresponding types
        self.create_table_from_dataframe(df, conn)
        
        # Insert the data from the DataFrame into the table
        df.to_sql(self.table_name, conn, if_exists='append', index=False)

    def create_table_from_dataframe(self, df, conn):
        c = conn.cursor()
        
        # Get the column types based on the DataFrame data
        column_types = self.get_column_types(df)
        
        # Create the table using the DataFrame columns and their corresponding types
        columns_with_types = ', '.join([f"{column} {column_types[column]}" for column in df.columns])
        create_table_query = f"CREATE TABLE {self.table_name} ({columns_with_types})"
        c.execute(create_table_query)

    def get_column_types(self, df):
        column_types = {}
        for column in df.columns:
            dtype = df[column].dtype
            if dtype == 'int64':
                column_types[column] = 'INTEGER'
            elif dtype == 'float64':
                column_types[column] = 'REAL'
            else:
                column_types[column] = 'TEXT'
        return column_types

# Example usage:
appender = DatabaseAppender("MLSBuilds_20230522_Clean.csv", "builds_table")
appender.append_to_database()
appender = DatabaseAppender("InventoryVirginBatch_20230622.csv", "inventory_virgin_batch")
appender.append_to_database()
appender = DatabaseAppender("PowderMaterial_20230622.csv", "materials_table")
appender.append_to_database()
appender = DatabaseAppender("PowderBlendPart_20230622.csv", "Powder_Blend_Parts")
appender.append_to_database()
appender = DatabaseAppender("PowderBlend_20230622.csv", "powder_blends")
appender.append_to_database()
appender = DatabaseAppender("PowderBlendCalc_20230606_.csv", "Powder_Blend_Calc")
appender.append_to_database()
