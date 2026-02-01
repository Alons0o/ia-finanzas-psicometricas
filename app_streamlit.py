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

# --- SECCIÓN 2: VISUALIZACIONES (Burbujas y Pastel) ---
if st.button('Generar Visualizaciones'):
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos = motor.preparar_datos_burbujas()
    db.close()

    if not datos:
        st.warning('No hay datos suficientes (necesitas registros tipo "GASTO").')
    else:
        # Creamos dos columnas: una para cada gráfico
        col_izq, col_der = st.columns(2)

        with col_izq:
            st.write("### 🫧 Mapa de Valor")
            fig_burbuja, ax_burbuja = plt.subplots(figsize=(6, 5))
            for d in datos:
                # Dibujamos cada burbuja
                ax_burbuja.scatter(d['monto'], d['satisfaccion'], s=d['peso']*10, alpha=0.6)
                ax_burbuja.annotate(d['descripcion'], (d['monto'], d['satisfaccion']), fontsize=8)
            
            ax_burbuja.set_xlabel('Monto ($)')
            ax_burbuja.set_ylabel('Satisfacción (1-10)')
            st.pyplot(fig_burbuja)

        # ... (código previo del gráfico de burbujas en col_izq)

        with col_der:
            st.write("### 🍰 Distribución de Gastos")
            labels = [d['descripcion'] for d in datos]
            sizes = [d['monto'] for d in datos]
            
            def func_monto(val):
                actual_val = val/100.*sum(sizes)
                return f"${actual_val:,.1f}"

            fig_pastel, ax_pastel = plt.subplots(figsize=(6, 5))
            colores = plt.cm.Paired(range(len(labels)))

            wedges, texts, autotexts = ax_pastel.pie(
                sizes, 
                autopct=func_monto, 
                startangle=140, 
                colors=colores,
                textprops={'color':"w", 'weight':'bold', 'fontsize':8}
            )

            ax_pastel.legend(
                wedges, labels,
                title="Gastos",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=8
            )
            ax_pastel.axis('equal')
            st.pyplot(fig_pastel)

            # --- LA MÉTRICA AHORA AQUÍ ---
            total_dinero = sum(d['monto'] for d in datos)
            st.metric(label="💰 Gasto Total Registrado", value=f"${total_dinero:,.2f}")
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
# --- SECCIÓN 4: GESTIÓN DE HISTORIAL (EDITAR/ELIMINAR) ---
st.divider()
st.subheader("🗑️ Gestionar Historial")

db = SessionLocal()
# Consultamos todos los movimientos con su satisfacción
historial = (
    db.query(Movimiento)
    .join(MetricaSatisfaccion)
    .order_by(Movimiento.fecha.desc())
    .all()
)

if historial:
    # Creamos una lista de datos para mostrar en una tabla
    datos_tabla = []
    for h in historial:
        datos_tabla.append({
            "ID": h.id,
            "Fecha": h.fecha.strftime("%Y-%m-%d"),
            "Descripción": h.descripcion,
            "Monto": f"${h.monto:.2f}",
            "Satisfacción": h.satisfaccion.nivel
        })
    
    st.table(datos_tabla)

    # Formulario pequeño para eliminar por ID
    with st.expander("❌ Eliminar un registro"):
        id_a_eliminar = st.number_input("Ingresa el ID del gasto a borrar", min_value=1, step=1)
        confirmar_borrado = st.button("Confirmar Eliminación")

        if confirmar_borrado:
            try:
                # 1. Borrar primero la métrica (por la llave foránea)
                db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id == id_a_eliminar).delete()
                # 2. Borrar el movimiento
                db.query(Movimiento).filter(Movimiento.id == id_a_eliminar).delete()
                
                db.commit()
                st.success(f"✅ Registro {id_a_eliminar} eliminado. ¡Refresca los gráficos!")
                st.rerun() # Recarga la app automáticamente
            except Exception as e:
                db.rollback()
                st.error(f"Error al eliminar: {e}")
else:
    st.write("No hay registros en el historial.")
# --- SUB-SECCIÓN: EDITAR REGISTRO ---
    with st.expander("📝 Editar un registro"):
        id_a_editar = st.number_input("ID del gasto a editar", min_value=1, step=1, key="edit_id")
        
        # Buscamos el registro en la DB
        mov_edit = db.query(Movimiento).filter(Movimiento.id == id_a_editar).first()
        
        if mov_edit:
            st.info(f"Editando: {mov_edit.descripcion}")
            with st.form("form_edicion"):
                nueva_desc = st.text_input("Nueva Descripción", value=mov_edit.descripcion)
                nuevo_monto = st.number_input("Nuevo Monto", value=float(mov_edit.monto))
                nuevo_nivel = st.slider("Nueva Satisfacción", 1, 10, int(mov_edit.satisfaccion.nivel))
                
                boton_actualizar = st.form_submit_button("Guardar Cambios")
                
                if boton_actualizar:
                    try:
                        # Actualizamos Movimiento
                        mov_edit.descripcion = nueva_desc
                        mov_edit.monto = nuevo_monto
                        # Actualizamos Métrica
                        mov_edit.satisfaccion.nivel = nuevo_nivel
                        
                        db.commit()
                        st.success("✅ ¡Registro actualizado!")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error al actualizar: {e}")
        else:
            st.warning("Introduce un ID válido para editar.")
db.close()    