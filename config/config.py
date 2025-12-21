
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os   
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("A variável DATABASE_URL não foi encontrada no arquivo .env")

engine = create_engine(DATABASE_URL, echo=True,connect_args={"options": "-c client_encoding=utf8"})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


