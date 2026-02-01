from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. URL de conexión optimizada para la nube
# Usamos el puerto 6543 (Transaction Pooler) para evitar errores de red IPv4
# Se incluye 'sslmode=require' para garantizar la seguridad de la conexión
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.skdhjekqmikfvydennng:Diego23060523060@aws-0-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require"

# 2. Creamos el motor de conexión
# 'pool_pre_ping=True' ayuda a reestablecer la conexión si Supabase la cierra por inactividad
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600
)

# 3. Configuramos la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Definimos la Clase Base
Base = declarative_base()