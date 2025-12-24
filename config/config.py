import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()


""" Conexão com o banco de dados remoto, deve esta comentado para rodar localmente"""
DATABASE_URL = st.secrets.get("DATABASE_URL") 
if not DATABASE_URL:

    st.error("DATABASE_URL não configurada!")
    st.stop()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True
)


""" Conexão com o banco de dados local precisa esta comentado para o uso remoto"""
# DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True
# )

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()