
from sqlalchemy import create_engine, column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_File = 'Comandas.db'
engine = create_engine('sqlite:///' + DB_File, echo=True)

Base = declarative_base()

session_L = sessionmaker(bind=engine)
session = session_L()

