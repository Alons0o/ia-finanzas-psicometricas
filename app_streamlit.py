import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠", layout="wide")

# --- BARRA LATERAL (MENÚ MODERNO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 Menú</h2>", unsafe_allow_html=True)
    
    opcion = option_menu(
        menu_title=None, 
        options=["Inicio", "Registrar Movimiento", "Visualizaciones", "Recomendaciones", "Gestionar Historial"],
        icons=["house", "pencil-square", "bar-chart", "robot", "gear"], 
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#ff4b4b", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "8px", 
                "font-weight": "bold"
            },
            "nav-link-selected": {"background-color": "#ff4b4b", "color": "white"},
        }
    )

# --- LÓGICA DE DATOS GLOBAL ---
db = SessionLocal()
movimientos_db = db.query(Movimiento).all()
total_gastos = sum(m.monto for m in movimientos_db if m.tipo == "GASTO")
total_ingresos = sum(m.monto for m in movimientos_db if m.tipo == "INGRESO")
saldo_final = total_ingresos - total_gastos
db.close()

# --- NAVEGACIÓN ---

if opcion == "Inicio":
    st.title("🏠 Dashboard de Inicio")
    st.markdown("### Estado Financiero Actual")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📥 Total Ingresos", f"${total_ingresos:,.2f}")
    c2.metric("📤 Total Gastos", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
    
    color_saldo = "normal" if saldo_final >= 0 else "inverse"
    c3.metric("💰 Dinero Restante", f"${saldo_final:,.2f}", 
                delta="POSITIVO" if saldo_final >= 0 else "DÉFICIT", 
                delta_color=color_saldo)
    
    st.divider()
    st.subheader("📜 Última Actividad")
    if not movimientos_db:
        st.info("No hay registros. Comienza en 'Registrar Movimiento'.")
    else:
        for m in reversed(movimientos_db[-5:]):
            st.write(f"{'🟢' if m.tipo == 'INGRESO' else '🔴'} **{m.descripcion}**: ${m.monto:,.2f}")

elif opcion == "Registrar Movimiento":
    st.title("📝 Registrar Movimiento")
    with st.form("formulario_gastos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descripcion = st.text_input("Descripción", placeholder="Ej. Sueldo, Netflix...")
            monto = st.number_input("Monto ($)", value=None, placeholder="0.00", step=0.01)
        with col2:
            tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"])
            satisfaccion_nivel = st.slider("Satisfacción (1-10)", 1, 10, 5)
        
        comentario = st.text_area("Comentario emocional")
        boton_guardar = st.form_submit_button("Guardar Registro")

    if boton_guardar:
        if descripcion and monto and monto > 0:
            db = SessionLocal()
            try:
                nuevo_mov = Movimiento(tipo=tipo, descripcion=descripcion, monto=monto)
                db.add(nuevo_mov)
                db.flush()
                nueva_metrica = MetricaSatisfaccion(movimiento_id=nuevo_mov.id, nivel=satisfaccion_nivel, comentario=comentario)
                db.add(nueva_metrica)
                db.commit()
                st.success("✅ ¡Guardado con éxito!")
            except Exception as e:
                db.rollback()
                st.error(f"Error: {e}")
            finally:
                db.close()
        else:
            st.warning("⚠️ Ingresa descripción y monto válido.")

elif opcion == "Visualizaciones":
    st.title("📊 Análisis de Datos")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos_burbujas = motor.preparar_datos_burbujas()
    db.close()

    if not movimientos_db:
        st.warning("Sin datos suficientes.")
    else:
        # Gráficos de Pastel
        col_ing, col_gas = st.columns(2)
        
        def dibujar_pastel(ax, datos_lista, titulo, mapa_color):
            resumen = {}
            for d in datos_lista:
                resumen[d.descripcion] = resumen.get(d.descripcion, 0) + d.monto
            if not resumen:
                ax.text(0.5, 0.5, "Sin datos", ha='center')
                ax.axis('off')
                return
            labels, sizes = list(resumen.keys()), list(resumen.values())
            n = len(labels)
            colores = plt.get_cmap(mapa_color)([i/(n if n > 1 else 1) for i in range(n)])
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colores)
            ax.set_title(titulo, fontweight='bold')

        with col_ing:
            fig_ing, ax_ing = plt.subplots()
            dibujar_pastel(ax_ing, [m for m in movimientos_db if m.tipo=="INGRESO"], "Ingresos", "viridis")
            st.pyplot(fig_ing)

        with col_gas:
            fig_gas, ax_gas = plt.subplots()
            dibujar_pastel(ax_gas, [m for m in movimientos_db if m.tipo=="GASTO"], "Gastos", "tab20")
            st.pyplot(fig_gas)

        st.divider()
        st.write("### 🫧 Mapa de Valor (Gastos)")
        if datos_burbujas:
            fig_b, ax_b = plt.subplots(figsize=(10, 4))
            for d in datos_burbujas:
                ax_b.scatter(d['monto'], d['satisfaccion'], s=d['peso']*15, alpha=0.6)
                ax_b.annotate(d['descripcion'], (d['monto'], d['satisfaccion']))
            st.pyplot(fig_b)

elif opcion == "Recomendaciones IA":
    st.title("🤖 Recomendaciones") # Título actualizado
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    analisis = motor.calcular_costo_insatisfaccion()
    
    if analisis["total_ineficiente"] > 0:
        st.error(f"⚠️ He detectado {analisis['cantidad_gastos']} gasto(s) ineficientes.")
        for detalle in analisis["detalles"]:
            st.warning(f"👉 **{detalle['desc']}**: ${detalle['monto']} (Nivel: {detalle['nivel']}/10)")
        
        st.info(f"Si eliminas estos gastos, podrías recuperar **${analisis['total_ineficiente']}** mensuales.")
        
        # Simulación de meta (puedes ajustar los valores)
        simulacion = motor.simular_alcance_meta(monto_meta=1000, ahorro_mensual_base=100)
        st.success(f"📈 **Plan de Optimización:** Alcanzarías tu meta en **{simulacion['meses_optimizado']} meses**.")
    else:
        # ESTO ES LO QUE FALTABA: El mensaje verde final
        st.balloons()
        st.success("✨ ¡Excelente! Todos tus gastos actuales están alineados con tu bienestar y felicidad.")
    
    db.close()

elif opcion == "Gestionar Historial":
    st.title("⚙️ Gestión de Historial")
    db = SessionLocal()
    
    # Obtenemos los datos uniendo Movimiento con su Satisfacción
    historial = db.query(Movimiento).join(MetricaSatisfaccion).order_by(Movimiento.fecha.desc()).all()
    
    if not historial:
        st.info("Aún no tienes movimientos registrados.")
    else:
        # 1. Mostrar la tabla de datos
        datos_tabla = []
        for h in historial:
            datos_tabla.append({
                "ID": h.id,
                "Fecha": h.fecha.strftime("%Y-%m-%d"),
                "Descripción": h.descripcion,
                "Monto": f"${h.monto:.2f}",
                "Tipo": h.tipo,
                "Satisfacción": h.satisfaccion.level if hasattr(h.satisfaccion, 'level') else h.satisfaccion.nivel
            })
        st.table(datos_tabla)

        st.divider()
        st.subheader("🛠️ Acciones de historial")

        # 2. Columnas para Editar y Eliminar
        col_edit, col_del = st.columns(2)

        with col_edit:
            with st.expander("📝 Editar un registro"):
                id_a_editar = st.number_input("Ingresa el ID para editar", min_value=1, step=1, key="edit_id")
                mov_edit = db.query(Movimiento).filter(Movimiento.id == id_a_editar).first()
                
                if mov_edit:
                    with st.form("form_edicion"):
                        nueva_desc = st.text_input("Nueva Descripción", value=mov_edit.descripcion)
                        nuevo_monto = st.number_input("Nuevo Monto", value=float(mov_edit.monto))
                        
                        # Manejo de si la columna se llama 'level' o 'nivel'
                        val_sat = mov_edit.satisfaccion.level if hasattr(mov_edit.satisfaccion, 'level') else mov_edit.satisfaccion.nivel
                        nuevo_nivel = st.slider("Nueva Satisfacción", 1, 10, int(val_sat))
                        
                        if st.form_submit_button("Guardar Cambios"):
                            mov_edit.descripcion = nueva_desc
                            mov_edit.monto = nuevo_monto
                            if hasattr(mov_edit.satisfaccion, 'level'):
                                mov_edit.satisfaccion.level = nuevo_nivel
                            else:
                                mov_edit.satisfaccion.nivel = nuevo_nivel
                            
                            db.commit()
                            st.success(f"✅ Registro {id_a_editar} actualizado")
                            st.rerun()
                else:
                    st.caption("Introduce un ID válido para ver el formulario de edición.")

        with col_del:
            with st.expander("🗑️ Eliminar un registro"):
                id_a_eliminar = st.number_input("Ingresa el ID para borrar", min_value=1, step=1, key="del_id")
                confirmar = st.checkbox(f"Estoy seguro de que quiero borrar el ID {id_a_eliminar}")
                
                if st.button("Eliminar permanentemente"):
                    if confirmar:
                        try:
                            # Borrar primero la satisfacción (llave foránea) y luego el movimiento
                            db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id == id_a_eliminar).delete()
                            db.query(Movimiento).filter(Movimiento.id == id_a_eliminar).delete()
                            db.commit()
                            st.error(f"Registro {id_a_eliminar} eliminado.")
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Error al eliminar: {e}")
                    else:
                        st.warning("Debes marcar la casilla de confirmación.")
    db.close()