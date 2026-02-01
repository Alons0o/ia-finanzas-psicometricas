import streamlit as st
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
# Importamos los modelos para poder guardar datos
from app.db.models import Movimiento, MetricaSatisfaccion 

st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠")

st.title("🧠 IA Finanzas Psicométricas")
st.markdown("Analizando el costo emocional de tus gastos.")

# --- SECCIÓN 1: FORMULARIO PARA INGRESAR DATOS ---
st.subheader("📝 Registrar nuevo gasto")
with st.form("formulario_gastos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        descripcion = st.text_input("¿En qué gastaste?", placeholder="Ej. Cena con amigos")
        monto = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    with col2:
        tipo = st.selectbox("Tipo", ["Gasto", "Inversión", "Ocio", "Necesidad"])
        satisfaccion = st.slider("Satisfacción (1 al 10)", 1, 10, 5)
    
    comentario = st.text_area("Comentario emocional", placeholder="¿Cómo te sentiste después de este gasto?")
    
    boton_guardar = st.form_submit_button("Guardar en Base de Datos")

if boton_guardar:
    if descripcion and monto > 0:
        db = SessionLocal()
        try:
            # 1. Crear el movimiento
            nuevo_movimiento = Movimiento(tipo=tipo, descripcion=descripcion, monto=monto)
            db.add(nuevo_movimiento)
            db.flush() # Para obtener el ID antes de hacer commit
            
            # 2. Crear la métrica vinculada
            nueva_metrica = MetricaSatisfaccion(
                movimiento_id=nuevo_movimiento.id, 
                nivel_satisfaccion=satisfaccion,
                comentario=comentario
            )
            db.add(nueva_metrica)
            db.commit()
            st.success(f"✅ ¡Gasto '{descripcion}' guardado correctamente!")
        except Exception as e:
            db.rollback()
            st.error(f"Error al guardar: {e}")
        finally:
            db.close()
    else:
        st.warning("Por favor, completa el nombre y el monto.")

st.divider()

# --- SECCIÓN 2: GENERAR EL GRÁFICO ---
st.subheader("📊 Tu Mapa de Valor")
if st.button('Actualizar y Generar Mapa'):
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos = motor.preparar_datos_burbujas()
    db.close()

    if not datos:
        st.warning('No hay datos suficientes. ¡Registra tu primer gasto arriba! 👆')
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extraer datos para el gráfico
        montos = [d['monto'] for d in datos]
        satisfacciones = [d['satisfaccion'] for d in datos]
        descripciones = [d['descripcion'] for d in datos]
        tamanos = [max(d['peso'] * 500, 100) for d in datos] # Ajuste de tamaño para que se vea mejor

        # Crear el scatter plot
        scatter = ax.scatter(montos, satisfacciones, s=tamanos, alpha=0.6, c=satisfacciones, cmap='RdYlGn', edgecolors="black")
        
        # Etiquetas de cada punto
        for i, txt in enumerate(descripciones):
            ax.annotate(txt, (montos[i], satisfacciones[i]), xytext=(5,5), textcoords='offset points')

        # Estética del gráfico
        ax.set_title('Relación Monto vs. Bienestar Emocional', fontsize=14)
        ax.set_xlabel('Inversión Económica ($)', fontsize=12)
        ax.set_ylabel('Nivel de Satisfacción (1-10)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Líneas de cuadrantes (promedios)
        ax.axhline(y=5.5, color='gray', linestyle='--', alpha=0.5)
        
        st.pyplot(fig)