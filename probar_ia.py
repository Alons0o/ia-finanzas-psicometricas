from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico

def ejecutar_diagnostico():
    db = SessionLocal()
    try:
        motor = MotorPsicometrico(db)
        
        print("\n" + "="*40)
        print("🧠  DIAGNÓSTICO DE INTELIGENCIA PSICOMÉTRICA")
        print("="*40)
        
        resultado = motor.calcular_costo_insatisfaccion()
        
        print(f"Análisis completo. Gastos detectados: {resultado['cantidad_gastos']}")
        print(f"💰 DINERO MAL GASTADO: ${resultado['total_ineficiente']:.2f}")
        
        if resultado['detalles']:
            print("\nDetalle de ineficiencias encontradas:")
            for item in resultado['detalles']:
                print(f"❌ {item['desc']} | Monto: ${item['monto']} | Satisfacción: {item['nivel']}/10")
            
            print("\n💡 IA INSIGHT: Si eliminas estos gastos, podrías ahorrar "
                  f"${resultado['total_ineficiente']:.2f} adicionales por mes.")
        else:
            print("\n✅ ¡Felicidades! No se detectaron gastos con satisfacción baja.")

    except Exception as e:
        print(f"❌ Error al ejecutar el motor: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ejecutar_diagnostico()