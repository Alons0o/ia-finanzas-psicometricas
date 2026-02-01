import streamlit as st
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠", layout="wide")

st.title("🧠 IA Finanzas Psicométricas")
st.markdown("Analizando el costo emocional de tus gastos.")

# --- INICIALIZACIÓN DE ESTADOS (Para persistencia de botones) ---
if 'ver_graficos' not in st.session_state:
    st.session_state.ver_graficos = False
if 'ver_ia' not in st.session_state:
    st.session_state.ver_ia = False

# --- FUNCIONES DE CONTROL (Callbacks) ---
def activar_graficos():
    st.session_state.ver_graficos = True

def activar_ia():
    st.session_state.ver_ia = True

# --- SECCIÓN 1: FORMULARIO DE REGISTRO ---
st.subheader("📝 Registrar nuevo gasto")
with st.form("formulario_gastos", clear_on_submit=True):
    col1, col2 = st.columns(2)
    # En la Sección 1: Formulario
with col1:
    descripcion = st.text_input("¿En qué gastaste?", placeholder="Ej. Café, Netflix...")
    
    # CAMBIO AQUÍ: value=None hace que el campo aparezca vacío
    monto = st.number_input("Monto ($)", value=None, placeholder="0.00", step=0.01)
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
                nivel=satisfaccion_nivel,
                comentario=comentario
            )
            db.add(nueva_metrica)
            db.commit()
            st.success("✅ ¡Guardado con éxito!")
            st.session_state.ver_graficos = False # Resetear para forzar actualización
        except Exception as e:
            db.rollback()
            st.error(f"Error: {e}")
        finally:
            db.close()

st.divider()

# --- SECCIÓN 2: BOTONES DE ACCIÓN ---
col_acc1, col_acc2 = st.columns(2)
with col_acc1:
    # Usamos on_click para que el cambio sea permanente
    st.button('📊 Generar Visualizaciones', on_click=activar_graficos, use_container_width=True)

with col_acc2:
    st.button('🤖 Obtener Recomendaciones', on_click=activar_ia, use_container_width=True)

# --- LÓGICA DE VISUALIZACIONES ACTUALIZADA ---
if st.session_state.ver_graficos:
    st.subheader("📊 Resumen Financiero Detallado")
    db = SessionLocal()
    movimientos_db = db.query(Movimiento).all()
    db.close()

    if not movimientos_db:
        st.warning('No hay datos suficientes para calcular el saldo.')
    else:
        # Separar datos
        gastos = [m for m in movimientos_db if m.tipo == "GASTO"]
        ingresos = [m for m in movimientos_db if m.tipo == "INGRESO"]
        
        total_gastos = sum(g.monto for g in gastos)
        total_ingresos = sum(i.monto for i in ingresos)
        saldo_final = total_ingresos - total_gastos

        # --- MÉTRICAS SUPERIORES ---
        c1, c2, c3 = st.columns(3)
        c1.metric("📥 Total Ingresos", f"${total_ingresos:,.2f}")
        c2.metric("📤 Total Gastos", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
        c3.metric("💰 Saldo Final", f"${saldo_final:,.2f}")

        st.divider()

        # --- FUNCIÓN MEJORADA PARA COLORES DISTINTOS ---
        def dibujar_pastel_mejorado(ax, datos, titulo, mapa_color_base):
            if not datos:
                ax.text(0.5, 0.5, "Sin registros", ha='center', va='center')
                ax.axis('off')
                return
            
            # Agrupar montos por descripción para no repetir etiquetas
            resumen = {}
            for d in datos:
                resumen[d.descripcion] = resumen.get(d.descripcion, 0) + d.monto
            
            labels = list(resumen.keys())
            sizes = list(resumen.values())
            
            # Generar colores distintos usando una paleta cualitativa (Set3, Paired, etc)
            # O una escala de colores bien distribuida
            n = len(labels)
            colores = plt.get_cmap(mapa_color_base)([i/(n if n > 1 else 1) for i in range(n)])

            wedges, texts, autotexts = ax.pie(
                sizes, 
                autopct=lambda p: f'${p*sum(sizes)/100:,.1f}',
                startangle=140, 
                colors=colores,
                textprops={'color':"w", 'weight':'bold', 'fontsize':9},
                pctdistance=0.75 # Mueve el texto del monto un poco hacia afuera
            )
            ax.set_title(titulo, pad=20, fontweight='bold')
            ax.legend(wedges, labels, title="Categorías", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)

        col_ing, col_gas = st.columns(2)

        with col_ing:
            st.write("### 📥 Mis Ingresos")
            fig_ing, ax_ing = plt.subplots(figsize=(6, 5))
            # Usamos 'viridis' o 'summer' para ingresos (tonos verdes/amarillos distintos)
            dibujar_pastel_mejorado(ax_ing, ingresos, "Distribución de Ingresos", "viridis")
            st.pyplot(fig_ing)

        with col_gas:
            st.write("### 📤 Mis Gastos")
            fig_gas, ax_gas = plt.subplots(figsize=(6, 5))
            # Usamos 'Set3' o 'tab20' para gastos (muchos colores distintos)
            dibujar_pastel_mejorado(ax_gas, gastos, "Distribución de Gastos", "tab20")
            st.pyplot(fig_gas)
# --- LÓGICA DE DIAGNÓSTICO IA ---
if st.session_state.ver_ia:
    st.divider()
    st.subheader("🤖 Diagnóstico de la IA Financiera")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    analisis = motor.calcular_costo_insatisfaccion()
    
    if analisis["total_ineficiente"] > 0:
        st.error(f"⚠️ He detectado {analisis['cantidad_gastos']} gasto(s) que no te hacen feliz.")
        st.markdown("### 📋 Gastos Detectados:")
        for detalle in analisis["detalles"]:
            st.warning(f"👉 **{detalle['desc']}**: Costó **${detalle['monto']}** (Satisfacción: {detalle['nivel']}/10)")
        
        st.info(f"Si eliminas estos gastos, recuperarías **${analisis['total_ineficiente']}** mensuales.")
        simulacion = motor.simular_alcance_meta(monto_meta=1000, ahorro_mensual_base=100)
        st.success(f"📈 **Plan de Optimización:** Alcanzarías tu meta en **{simulacion['meses_optimizado']} meses**.")
    else:
        st.balloons()
        st.success("✨ ¡Increíble! Todos tus gastos actuales te generan bienestar.")
    db.close()

# --- SECCIÓN 4: GESTIÓN DE HISTORIAL ---
st.divider()
st.subheader("🗑️ Gestionar Historial")
db = SessionLocal()
historial = db.query(Movimiento).join(MetricaSatisfaccion).order_by(Movimiento.fecha.desc()).all()

if historial:
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

    col_edit, col_del = st.columns(2)
    
    with col_del:
        with st.expander("❌ Eliminar un registro"):
            id_a_eliminar = st.number_input("ID a borrar", min_value=1, step=1)
            if st.button("Confirmar Eliminación"):
                try:
                    db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id == id_a_eliminar).delete()
                    db.query(Movimiento).filter(Movimiento.id == id_a_eliminar).delete()
                    db.commit()
                    st.success(f"Registro {id_a_eliminar} borrado.")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")

    with col_edit:
        with st.expander("📝 Editar un registro"):
            id_a_editar = st.number_input("ID a editar", min_value=1, step=1, key="edit_id")
            mov_edit = db.query(Movimiento).filter(Movimiento.id == id_a_editar).first()
            if mov_edit:
                with st.form("form_edicion"):
                    nueva_desc = st.text_input("Descripción", value=mov_edit.descripcion)
                    nuevo_monto = st.number_input("Monto", value=float(mov_edit.monto))
                    nuevo_nivel = st.slider("Satisfacción", 1, 10, int(mov_edit.satisfaccion.nivel))
                    if st.form_submit_button("Guardar Cambios"):
                        mov_edit.descripcion = nueva_desc
                        mov_edit.monto = nuevo_monto
                        mov_edit.satisfaccion.nivel = nuevo_nivel
                        db.commit()
                        st.success("Actualizado.")
                        st.rerun()
else:
    st.write("No hay registros.")
db.close()