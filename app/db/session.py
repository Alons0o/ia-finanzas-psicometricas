from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Definimos la URL de conexión a Supabase (Cloud)
# IMPORTANTE: Reemplaza TU_PASSWORD por la contraseña que creaste en Supabase.
# Si tu contraseña tiene caracteres especiales como @ o #, dímelo para ayudarte a codificarla.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:TU_PASSWORD@db.skdhjekqmikfvydennng.supabase.co:5432/postgres"

# 2. Creamos el motor de conexión para PostgreSQL
# Usamos 'pool_pre_ping' para asegurar que la conexión esté viva siempre
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 3. Configuramos la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Definimos la Clase Base
Base = declarative_base()