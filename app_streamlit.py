import streamlit as st
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠", layout="wide")

# --- BARRA LATERAL (MENÚ DE NAVEGACIÓN) ---
with st.sidebar:
    st.title("🧠 Menú de Control")
    # El radio button controla qué "página" se muestra
    opcion = st.radio(
        "Selecciona una sección:",
        ["🏠 Inicio", "📝 Registrar Movimiento", "📊 Visualizaciones", "🤖 Recomendaciones IA", "⚙️ Gestionar Historial"]
    )
    st.divider()
    st.info("Navega entre las pestañas para gestionar tus finanzas y salud emocional.")

# --- LÓGICA DE DATOS GLOBAL ---
db = SessionLocal()
movimientos_db = db.query(Movimiento).all()
total_gastos = sum(m.monto for m in movimientos_db if m.tipo == "GASTO")
total_ingresos = sum(m.monto for m in movimientos_db if m.tipo == "INGRESO")
saldo_final = total_ingresos - total_gastos
db.close()

# --- 1. SECCIÓN: INICIO ---
if opcion == "🏠 Inicio":
    st.title("🏠 Dashboard de Inicio")
    st.markdown("Bienvenido. Aquí tienes el estado actual de tus cuentas.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Total Ingresos", f"${total_ingresos:,.2f}")
    col2.metric("📤 Total Gastos", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
    
    color_saldo = "normal" if saldo_final >= 0 else "inverse"
    col3.metric("💰 Dinero Restante", f"${saldo_final:,.2f}", 
                delta="POSITIVO" if saldo_final >= 0 else "DÉFICIT", 
                delta_color=color_saldo)
    
    st.divider()
    st.write("### 📜 Resumen de Actividad")
    if not movimientos_db:
        st.write("No hay movimientos registrados aún.")
    else:
        # Mostramos los últimos 5 de forma elegante
        for m in reversed(movimientos_db[-5:]):
            label = "🟢 Ingreso" if m.tipo == "INGRESO" else "🔴 Gasto"
            st.text(f"{label} | {m.fecha.strftime('%d/%m/%Y')} | {m.descripcion}: ${m.monto:,.2f}")

# --- 2. SECCIÓN: REGISTRO ---
elif opcion == "📝 Registrar Movimiento":
    st.title("📝 Registrar nuevo movimiento")
    with st.form("formulario_gastos", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descripcion = st.text_input("¿En qué gastaste o qué ingresó?", placeholder="Ej. Sueldo, Alquiler...")
            monto = st.number_input("Monto ($)", value=None, placeholder="0.00", step=0.01)
        with col2:
            tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"])
            satisfaccion_nivel = st.slider("Satisfacción (1 al 10)", 1, 10, 5)
        
        comentario = st.text_area("Comentario emocional")
        boton_guardar = st.form_submit_button("Guardar en Base de Datos")

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
            st.warning("⚠️ Asegúrate de poner una descripción y un monto válido.")

# --- 3. SECCIÓN: VISUALIZACIONES ---
elif opcion == "📊 Visualizaciones":
    st.title("📊 Análisis de Datos")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos_burbujas = motor.preparar_datos_burbujas()
    db.close()

    if not movimientos_db:
        st.warning("No hay datos para mostrar gráficos.")
    else:
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
            ax.pie(sizes, autopct=lambda p: f'${p*sum(sizes)/100:,.0f}', startangle=140, colors=colores, textprops={'color':"w", 'weight':'bold'})
            ax.set_title(titulo, fontweight='bold')
            ax.legend(labels, title="Categorías", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        with col_ing:
            fig_ing, ax_ing = plt.subplots(figsize=(5, 4))
            dibujar_pastel(ax_ing, [m for m in movimientos_db if m.tipo == "INGRESO"], "Distribución de Ingresos", "viridis")
            st.pyplot(fig_ing)

        with col_gas:
            fig_gas, ax_gas = plt.subplots(figsize=(5, 4))
            dibujar_pastel(ax_gas, [m for m in movimientos_db if m.tipo == "GASTO"], "Distribución de Gastos", "tab20")
            st.pyplot(fig_gas)

        st.divider()
        st.write("### 🫧 Mapa de Valor (Gastos)")
        if datos_burbujas:
            fig_b, ax_b = plt.subplots(figsize=(10, 4))
            for d in datos_burbujas:
                ax_b.scatter(d['monto'], d['satisfaccion'], s=d['peso']*15, alpha=0.6)
                ax_b.annotate(d['descripcion'], (d['monto'], d['satisfaccion']), fontsize=9)
            ax_b.set_xlabel("Monto ($)")
            ax_b.set_ylabel("Satisfacción")
            st.pyplot(fig_b)

# --- 4. SECCIÓN: RECOMENDACIONES ---
elif opcion == "🤖 Recomendaciones IA":
    st.title("🤖 Diagnóstico de la IA")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    analisis = motor.calcular_costo_insatisfaccion()
    
    if analisis["total_ineficiente"] > 0:
        st.error(f"⚠️ He detectado {analisis['cantidad_gastos']} gastos ineficientes.")
        for detalle in analisis["detalles"]:
            st.warning(f"👉 **{detalle['desc']}**: Costó **${detalle['monto']}** (Satisfacción: {detalle['nivel']}/10)")
        st.info(f"Si los eliminas, ahorrarías **${analisis['total_ineficiente']}** mensuales.")
    else:
        st.success("✨ ¡Tus gastos son excelentes para tu bienestar!")
    db.close()

# --- 5. SECCIÓN: GESTIÓN (HISTORIAL) ---
elif opcion == "⚙️ Gestionar Historial":
    st.title("⚙️ Gestión de Historial")
    db = SessionLocal()
    historial = db.query(Movimiento).join(MetricaSatisfaccion).order_by(Movimiento.fecha.desc()).all()
    
    if historial:
        datos_tabla = [{"ID": h.id, "Fecha": h.fecha.strftime("%Y-%m-%d"), "Descripción": h.descripcion, "Monto": f"${h.monto:.2f}", "Tipo": h.tipo} for h in historial]
        st.table(datos_tabla)

        c_edit, c_del = st.columns(2)
        with c_del:
            with st.expander("❌ Eliminar"):
                id_del = st.number_input("ID a borrar", min_value=1, step=1)
                if st.button("Confirmar Borrado"):
                    db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id == id_del).delete()
                    db.query(Movimiento).filter(Movimiento.id == id_del).delete()
                    db.commit()
                    st.success("Registro eliminado.")
                    st.rerun()
        with c_edit:
            with st.expander("📝 Editar"):
                id_edit = st.number_input("ID a editar", min_value=1, step=1)
                mov_edit = db.query(Movimiento).filter(Movimiento.id == id_edit).first()
                if mov_edit:
                    with st.form("edit_f"):
                        n_desc = st.text_input("Descripción", value=mov_edit.descripcion)
                        n_monto = st.number_input("Monto", value=float(mov_edit.monto))
                        n_sat = st.slider("Satisfacción", 1, 10, int(mov_edit.satisfaccion.nivel))
                        if st.form_submit_button("Actualizar"):
                            mov_edit.descripcion = n_desc
                            mov_edit.monto = n_monto
                            mov_edit.satisfaccion.nivel = n_sat
                            db.commit()
                            st.rerun()
    db.close()