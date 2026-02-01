from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. URL de conexión con tu nueva contraseña
# Hemos quitado el proceso de 'urllib' porque ya no hay caracteres especiales
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Diego23060523060@db.skdhjekqmikfvydennng.supabase.co:5432/postgres"

# 2. Creamos el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 3. Configuramos la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Definimos la Clase Base
Base = declarative_base()