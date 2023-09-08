import os
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

class DatabaseAppender:
    def __init__(self, file_name, table_name):
        self.file_name = file_name
        self.table_name = table_name
        self.engine = create_engine('sqlite://', echo=False)
        try:
            self.conn = sqlite3.connect('database.db')
        except Exception as e:
            print('Connection error!')
            print(e)
            os.system('pause')
    
    def AppendToDatabase(self):
        df = pd.read_csv('tables/' + self.file_name, index_col=False)
        df.columns = [column.strip() for column in df.columns]  # Remove leading/trailing spaces from column names
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Remove the existing table if it exists
        c.execute(f'DROP TABLE IF EXISTS {self.table_name}')
        # Create the table using the DataFrame columns and their corresponding types
        self.CreateTable(df, conn)
        # Insert the data from the DataFrame into the table
        df.to_sql(self.table_name, conn, if_exists='append', index=False)

    def CreateTable(self, df, conn):
        c = conn.cursor()
        # Get the column types based on the DataFrame data
        column_types = self.GetColumnTypes(df)
        # Create the table using the DataFrame columns and their corresponding types
        columns_with_types = ', '.join([f'{column} {column_types[column]}' for column in df.columns])
        create_table_query = f'CREATE TABLE {self.table_name} ({columns_with_types})'
        c.execute(create_table_query)

    def GetColumnTypes(self, df):
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


# Dictionary of lookup tables:
table_dict = {'users': 'Users_20230908.csv', 
              'inventory_virgin_batch': 'InventoryVirginBatch_20230906_1138.csv', 
              'builds_table': 'MLSBuilds_20230821_Clean.csv',
              'powder_blends': 'PowderBlend_20230908_1337.csv',
              'powder_blend_calc': 'PowderBlendCalc_20230905_1511.csv',
              'powder_blend_parts': 'PowderBlendPart_20230713_1224.csv',
              'material_products': 'MaterialProducts_20230905.csv',
              'material_alloys': 'MaterialAlloys_20230905.csv',
              }

def main():
    # for loop to append all tables in `table_dict`
    for k, v in table_dict.items():
        appender = DatabaseAppender(v, k)
        appender.AppendToDatabase()

    print('Tables successfully appended to database!')
    os.system('pause')

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print('Error:')
        print(e, '\n')
        os.system('pause')
    