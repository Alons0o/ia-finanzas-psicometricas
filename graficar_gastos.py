import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico

def generar_grafico():
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos = motor.preparar_datos_burbujas()
    db.close()

    if not datos:
        print('No hay datos suficientes para graficar.')
        return

    descripciones = [d['descripcion'] for d in datos]
    montos = [d['monto'] for d in datos]
    satisfacciones = [d['satisfaccion'] for d in datos]
    tamanos = [d['peso'] * 15 for d in datos] 

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(montos, satisfacciones, s=tamanos, alpha=0.5, c=satisfacciones, cmap='RdYlGn')
    
    for i, txt in enumerate(descripciones):
        plt.annotate(txt, (montos[i], satisfacciones[i]), fontsize=9, ha='right')

    plt.axhline(y=5, color='gray', linestyle='--', alpha=0.3)
    plt.title('Mapa de Valor: Monto vs. Satisfaccion', fontsize=14)
    plt.xlabel('Monto Gastado ($)', fontsize=12)
    plt.ylabel('Nivel de Satisfaccion (1-10)', fontsize=12)
    plt.colorbar(scatter, label='Escala de Felicidad')
    plt.grid(True, linestyle=':', alpha=0.6)

    print('Generando grafico... revisa tu barra de tareas.')
    print('📊 Generando gráfico...')
    plt.savefig('reporte_psicometrico.png', dpi=300) # Guarda la imagen en alta calidad
    print('✅ Imagen guardada como: reporte_psicometrico.png')
    plt.show()


if __name__ == '__main__':
    generar_grafico()
