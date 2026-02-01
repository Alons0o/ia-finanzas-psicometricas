from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse

# Tu contraseña real de Supabase (la que me pasaste)
password = "Dieg#2230605"

# Esto "traduce" el símbolo # para que la base de datos no dé error
encoded_password = urllib.parse.quote_plus(password)

# Esta es la dirección de tu base de datos en la nube
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@db.skdhjekqmikfvydennng.supabase.co:5432/postgres"

# Creamos la conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()