from numpy import genfromtxt
from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd


def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=',', skip_header=1)
    return data.tolist()

Base = declarative_base()

class PowderBlends(Base):
    #Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
    __tablename__ = 'PowderBlends'
    __table_args__ = {'sqlite_autoincrement': True}
    #tell SQLAlchemy the name of column and its attributes:
    PowderBlendPartID = Column(Integer, primary_key=True) 
    PowderBlendID = Column(Float)
    OldPowderBlendID = Column(Float)
    AddedWeight = Column(Float)
    DateAdded = Column(Date)
    PowderInventoryBatchID = Column(Float)



if __name__ == "__main__":
    t = time()

    #Create the database
    engine = create_engine('sqlite:///PowderBlends.db')
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    try:
        file_name = "PowderBlendPart_20230406.csv" #input data from this file 
        print("loaded")
        data = Load_Data(file_name) 

        #using pandas so that the dates will work 
        df = pd.read_csv(data)

        # establish connection with the database
        engine = create_engine(
            "dialect+driver//username:password@hostname:portnumber/databasename")
          
        # read the pandas dataframe
        data = pandas.read_csv("path to dataset")
          
        # connect the pandas dataframe with postgresql table
        data.to_sql('loan_data', engine, if_exists='replace')






    #     for i in data:
    #         print(i)
    #         record = PowderBlends(**{
    #             'PowderBlendPartID' : i[0],
    #             'PowderBlendID' : i[1],
    #             'OldPowderBlendID' : i[2],
    #             'AddedWeight' : i[3],
    #             'DateAdded' : datetime.strptime(str(i[4]), "%m/%d/%Y").date(),
    #             'PowderInventoryBatchID' : i[5]
    #         })
    #         print("trying to add record")
    #         s.add(record) #Add all the records

    #     s.commit() #Attempt to commit all the records
    #     print("commit")
    # except Exception as e:
    #     s.rollback() #Rollback the changes on error
    #     print("rollback \n",e)
    # finally:
    #     s.close() #Close the connection
    #     print("close")
    # print("Time elapsed: " + str(time() - t) + " s.") #0.091s