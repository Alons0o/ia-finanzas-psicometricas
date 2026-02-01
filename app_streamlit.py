import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠", layout="wide")

# --- BARRA LATERAL (Menú de botones grandes) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 Menú Principal</h2>", unsafe_allow_html=True)
    
    # Este componente sustituye a los círculos de selección por botones elegantes
    opcion = option_menu(
        menu_title=None, 
        options=["Inicio", "Registrar Movimiento", "Visualizaciones", "Recomendaciones IA", "Gestionar Historial"],
        icons=["house", "pencil-square", "bar-chart", "robot", "gear"], 
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#ff4b4b", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "10px", 
                "font-weight": "500",
                "border-radius": "10px"
            },
            "nav-link-selected": {"background-color": "#ff4b4b", "color": "white"},
        }
    )

# --- LÓGICA DE DATOS ---
db = SessionLocal()
movimientos_db = db.query(Movimiento).all()
total_gastos = sum(m.monto for m in movimientos_db if m.tipo == "GASTO")
total_ingresos = sum(m.monto for m in movimientos_db if m.tipo == "INGRESO")
saldo_final = total_ingresos - total_gastos
db.close()

# --- NAVEGACIÓN POR SECCIONES ---

if opcion == "Inicio":
    st.title("🏠 Dashboard de Inicio")
    c1, c2, c3 = st.columns(3)
    c1.metric("📥 Ingresos", f"${total_ingresos:,.2f}")
    c2.metric("📤 Gastos", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
    c3.metric("💰 Saldo Neto", f"${saldo_final:,.2f}", delta="Ahorro" if saldo_final >= 0 else "Déficit")
    st.divider()
    st.subheader("📝 Actividad Reciente")
    for m in reversed(movimientos_db[-5:]):
        st.write(f"{'✅' if m.tipo == 'INGRESO' else '💸'} **{m.descripcion}**: ${m.monto:,.2f}")

elif opcion == "Registrar Movimiento":
    st.title("📝 Nuevo Registro")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descripcion = st.text_input("Concepto", placeholder="Ej. Alquiler, Salario...")
            # 'value=None' asegura que el campo inicie vacío sin el 0,00 molesto
            monto = st.number_input("Importe ($)", value=None, placeholder="Ingresa el monto", step=0.01)
        with col2:
            tipo = st.selectbox("Categoría", ["GASTO", "INGRESO"])
            satisfaccion = st.slider("Satisfacción Emocional", 1, 10, 5)
        
        if st.form_submit_button("Guardar en la Nube"):
            if descripcion and monto and monto > 0:
                # ... (Lógica de guardado que ya tienes)
                st.success("¡Registro guardado exitosamente!")
                st.rerun()

# (Las demás secciones mantienen su lógica pero bajo las etiquetas del nuevo menú)

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
    st.title("🤖 Diagnóstico de la IA")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    analisis = motor.calcular_costo_insatisfaccion()
    if analisis["total_ineficiente"] > 0:
        st.error(f"⚠️ Detectados {analisis['cantidad_gastos']} gastos ineficientes.")
        for d in analisis["detalles"]:
            st.warning(f"👉 **{d['desc']}**: ${d['monto']} (Nivel: {d['nivel']}/10)")
    else:
        st.success("✨ ¡Todo bien! Tus gastos te traen felicidad.")
    db.close()

elif opcion == "Gestionar Historial":
    st.title("⚙️ Gestión de Historial")
    db = SessionLocal()
    historial = db.query(Movimiento).all()
    if historial:
        st.table([{"ID": h.id, "Fecha": h.fecha.strftime("%Y-%m-%d"), "Descripción": h.descripcion, "Monto": h.monto, "Tipo": h.tipo} for h in historial])
        # Aquí puedes dejar tu lógica de editar/eliminar...
    db.close()