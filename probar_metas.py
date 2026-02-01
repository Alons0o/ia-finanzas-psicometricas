from app.db.session import engine, Base, SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.meta import MetaAhorro

def probar_simulacion():
    # 1. Crear tabla de metas si no existe
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    
    # Supongamos que quieres ahorrar para una Laptop de $1200
    # y puedes ahorrar $100 al mes por tu cuenta.
    laptop_precio = 1200.0
    ahorro_base = 100.0
    
    proyeccion = motor.simular_alcance_meta(laptop_precio, ahorro_base)
    
    print("\n" + "Target: LAPTOP GAMER ($1200)".center(40, "-"))
    print(f"Plan Normal: {proyeccion['meses_normal']} meses")
    print(f"🚀 Plan Optimizado (IA): {proyeccion['meses_optimizado']} meses")
    print(f"✨ ¡Llegarás {proyeccion['tiempo_ahorrado']} meses antes si cortas tus gastos ineficientes!")
    print("-" * 40)
    
    db.close()

if __name__ == "__main__":
    probar_simulacion()