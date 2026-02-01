import streamlit as st
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico

st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="📊")

st.title("🧠 IA Finanzas Psicométricas")
st.markdown("Analizando el costo emocional de tus gastos.")

if st.button('Generar Mapa de Valor'):
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos = motor.preparar_datos_burbujas()
    db.close()

    if not datos:
        st.warning('No hay datos suficientes en la base de datos de Supabase.')
    else:
        # Lógica de tu gráfico original adaptada a Streamlit
        fig, ax = plt.subplots(figsize=(10, 6))
        montos = [d['monto'] for d in datos]
        satisfacciones = [d['satisfaccion'] for d in datos]
        descripciones = [d['descripcion'] for d in datos]
        tamanos = [d['peso'] * 100 for d in datos] 

        scatter = ax.scatter(montos, satisfacciones, s=tamanos, alpha=0.5, c=satisfacciones, cmap='RdYlGn')
        
        for i, txt in enumerate(descripciones):
            ax.annotate(txt, (montos[i], satisfacciones[i]))

        ax.set_title('Monto vs. Satisfacción')
        ax.set_xlabel('Monto ($)')
        ax.set_ylabel('Satisfacción (1-10)')
        
        # Mostrar en Streamlit
        st.pyplot(fig)