from app.db.session import engine, Base, SessionLocal
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

def ejecutar_todo():
    # PASO A: Crear las tablas en SQL Server
    print("--- 1. Sincronizando Tablas ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas listas en GestorFinanzas.")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return

    # PASO B: Insertar datos de prueba
    print("\n--- 2. Insertando Datos de Prueba ---")
    db = SessionLocal()
    try:
        # Creamos un gasto de baja satisfacción (para probar la IA luego)
        gasto = Movimiento(
            tipo="GASTO", 
            descripcion="Suscripción olvidada", 
            monto=19.99
        )
        db.add(gasto)
        db.commit()
        db.refresh(gasto)

        sat = MetricaSatisfaccion(
            movimiento_id=gasto.id,
            nivel=2,
            comentario="No lo uso nunca, es un desperdicio."
        )
        db.add(sat)
        db.commit()

        print(f"✅ ÉXITO: Registrado '{gasto.descripcion}' con satisfacción {sat.nivel}/10")
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ejecutar_todo()
    