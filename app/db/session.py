from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Definimos la URL real de tu SQL Server (SQLEXPRESS con autenticación de Windows)
# Usamos doble barra \\ para que Python lea correctamente el nombre de la instancia
DATABASE_URL = "mssql+pyodbc://DESKTOP-28LC7MC\\SQLEXPRESS/GestorFinanzas?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"

# 2. Creamos el motor de conexión
engine = create_engine(DATABASE_URL)

# 3. Configuramos la fábrica de sesiones (SessionLocal es el estándar)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Definimos la Clase Base para que todos los modelos hereden de ella
Base = declarative_base()