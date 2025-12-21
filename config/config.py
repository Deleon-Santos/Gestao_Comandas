import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Carregar .env apenas para desenvolvimento local
load_dotenv()

# 2. Prioridade: Pegar do st.secrets (Nuvem). Se não houver, pegar do os.getenv (Local)
DATABASE_URL = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.error("Erro: DATABASE_URL não encontrada! Verifique os Secrets ou o arquivo .env.")
    st.stop()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL, 
    connect_args={"sslmode": "require"},
    echo=True, # Mostra os comandos SQL no terminal para debug
    pool_pre_ping=True,
    connect_args={"options": "-c client_encoding=utf8"}
)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()