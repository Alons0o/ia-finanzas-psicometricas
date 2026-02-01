import streamlit as st
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
# IMPORTACIONES CORRECTAS DESDE TUS ARCHIVOS
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠")

st.title("🧠 IA Finanzas Psicométricas")
st.markdown("Analizando el costo emocional de tus gastos.")

# --- SECCIÓN 1: FORMULARIO ---
st.subheader("📝 Registrar nuevo gasto")
with st.form("formulario_gastos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        descripcion = st.text_input("¿En qué gastaste?")
        monto = st.number_input("Monto ($)", min_value=0.0)
    with col2:
        tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"])
        satisfaccion_nivel = st.slider("Satisfacción (1 al 10)", 1, 10, 5)
    
    comentario = st.text_area("Comentario emocional")
    boton_guardar = st.form_submit_button("Guardar en Base de Datos")

if boton_guardar:
    if descripcion and monto > 0:
        db = SessionLocal()
        try:
            nuevo_mov = Movimiento(tipo=tipo, descripcion=descripcion, monto=monto)
            db.add(nuevo_mov)
            db.flush()
            
            nueva_metrica = MetricaSatisfaccion(
                movimiento_id=nuevo_mov.id, 
                nivel=satisfaccion_nivel, # Usamos 'nivel' como pide tu IA
                comentario=comentario
            )
            db.add(nueva_metrica)
            db.commit()
            st.success("✅ ¡Guardado con éxito!")
        except Exception as e:
            db.rollback()
            st.error(f"Error: {e}")
        finally:
            db.close()

st.divider()

# --- SECCIÓN 2: GRÁFICO ---
if st.button('Generar Mapa de Valor'):
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos = motor.preparar_datos_burbujas()
    db.close()

    if not datos:
        st.warning('No hay datos suficientes con tipo "GASTO".')
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Dibujamos las burbujas
        for d in datos:
            ax.scatter(d['monto'], d['satisfaccion'], s=d['peso']*10, alpha=0.6)
            ax.annotate(d['descripcion'], (d['monto'], d['satisfaccion']))

        ax.set_xlabel('Monto ($)')
        ax.set_ylabel('Satisfacción (1-10)')
        ax.set_title('Mapa de Valor Emocional')
        st.pyplot(fig)
# --- SECCIÓN 3: DIAGNÓSTICO DE LA IA ---
st.divider()
st.subheader("🤖 Diagnóstico de la IA Financiera")

if st.button('Obtener Recomendaciones'):
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    
    # 1. Análisis de ineficiencias
    analisis = motor.calcular_costo_insatisfaccion()
    
    if analisis["total_ineficiente"] > 0:
        st.error(f"⚠️ He detectado {analisis['cantidad_gastos']} gasto(s) que no te hacen feliz.")
        
        # MOSTRAR DETALLES ESPECÍFICOS
        st.markdown("### 📋 Gastos Detectados:")
        for detalle in analisis["detalles"]:
            # Aquí imprimimos el nombre y el monto del gasto específico
            st.warning(f"👉 **{detalle['desc']}**: Costó **${detalle['monto']}** y te dio una satisfacción de solo **{detalle['nivel']}/10**.")
        
        st.info(f"Si eliminas estos gastos, recuperarías **${analisis['total_ineficiente']}** mensuales.")
        
        # 2. Simulación de meta
        simulacion = motor.simular_alcance_meta(monto_meta=1000, ahorro_mensual_base=100)
        st.success(f"📈 **Plan de Optimización:** Si dejas de gastar en eso, alcanzarías tu meta en **{simulacion['meses_optimizado']} meses**.")
    else:
        st.balloons()
        st.write("✨ ¡Increíble! Todos tus gastos actuales te generan bienestar.")
    
    db.close()       