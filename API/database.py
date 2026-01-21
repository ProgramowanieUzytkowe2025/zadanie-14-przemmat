from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse

# Parametry połączenia
driver = 'ODBC Driver 17 for SQL Server'
server = r'(localdb)\MSSQLLocalDB' 
database = 'Garaz'

# TWORZENIE CONNECTION STRINGA PRZEZ URLLIB (To jest kluczowe dla MSSQL!)
params = urllib.parse.quote_plus(
    f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Tworzenie silnika
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()