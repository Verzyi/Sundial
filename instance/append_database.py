import os
import pandas as pd
from sqlalchemy import create_engine, inspect

class DatabaseAppender:
    def __init__(self, file_name, table_name):
        self.file_name = file_name
        self.table_name = table_name
        self.engine = create_engine('sqlite:///database.db', echo=False)
        self.conn = None

    def OpenConnection(self):
        try:
            self.conn = self.engine.connect()
        except Exception as e:
            print('Connection error!')
            print(e)
            os.system('pause')

    def CloseConnection(self):
        if self.conn:
            self.conn.close()
    
    def AppendToDatabase(self):
        file_path = os.path.join('tables', self.file_name)
        if self.file_name.endswith(('csv')):
            df = pd.read_csv(file_path)
        elif self.file_name.endswith(('ftr', 'feather')):
            df = pd.read_feather(file_path)
        elif self.file_name.endswith(('pqt', 'parquet')):
            df = pd.read_parquet(file_path)
        df.columns = [column.strip() for column in df.columns]  # Remove leading/trailing spaces from column names
        # Cast datetime64 columns to strings
        for column in df.select_dtypes(include=['datetime64']):
            df[column] = df[column].astype(str)
        # Open database connection
        self.OpenConnection()
        # Check if the table already exists in the database
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        if self.table_name in table_names:
            # Retrieve the existing table's schema
            existing_df = pd.read_sql(self.table_name, self.conn)
            # Check for schema compatibility
            if not existing_df.columns.equals(df.columns) or not existing_df.dtypes.equals(df.dtypes):
                self.CloseConnection()
                raise ValueError(f'Schema mismatch for table "{self.table_name}". Existing schema: {existing_df.dtypes}, New schema: {df.dtypes}')
        # Create or replace the table in the database and insert the data
        df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)
        self.CloseConnection()

    def GetColumnTypes(self, df):
        column_types = {}
        for column, dtype in df.dtypes.iteritems():
            if dtype in ['int64', 'Int64', 'bool']:
                column_types[column] = 'INTEGER'
            elif dtype == 'float64':
                column_types[column] = 'REAL'
            else:
                column_types[column] = 'TEXT'
        return column_types

# Dictionary of tables and filename prefixes:
prefix_dict = {'users': 'Users_', 
              'inventory_virgin_batch': 'InventoryVirginBatch_', 
              'builds_table': 'MLSBuilds_',
              'powder_blends': 'PowderBlends_',
              'powder_blend_calc': 'PowderBlendCalc_',
              'powder_blend_parts': 'PowderBlendParts_',
              'material_products': 'MaterialProducts_',
              'material_alloys': 'MaterialAlloys_',
              }

def FindTables(prefix_dict):
    table_dict = {}
    # Define a dictionary to keep track of the prefixes and their corresponding filenames
    prefix_files = {prefix: [] for prefix in prefix_dict}
    # Directory containing the tables
    table_directory = 'tables'
    # Loop through the files in the directory
    for filename in os.listdir(table_directory):
        # Check if the file has a matching prefix
        for prefix, prefix_value in prefix_dict.items():
            if filename.startswith(prefix_value):
                # If a file with the same prefix already exists, raise an error
                if prefix_files[prefix]:
                    raise ValueError(f'Multiple files found for prefix "{prefix}": {prefix_files[prefix][-1]} and {filename}')
                # Add the filename to the dictionary
                prefix_files[prefix].append(filename)
                table_dict[prefix] = filename
    return table_dict

def main():
    # for loop to append all tables in `table_dict`
    for table, file in FindTables(prefix_dict).items():
        appender = DatabaseAppender(file, table)
        appender.AppendToDatabase()
        print(f'{file} appended to database!\n')

    print('All tables successfully appended to database!')
    os.system('pause')

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print('Error:')
        print(e, '\n')
        os.system('pause')
    