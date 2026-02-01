from app.db.session import engine, Base
# Importamos los modelos para que Base "sepa" que existen
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

def inicializar():
    print("--- Iniciando Sincronización de Base de Datos ---")
    try:
        # Esta línea crea las tablas que falten en tu SQL Server
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas o actualizadas correctamente en SQL Server.")
    except Exception as e:
        print(f"❌ Error al conectar o crear tablas: {e}")

if __name__ == "__main__":
    inicializar()