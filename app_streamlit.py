import os
import streamlit as st
import streamlit.components.v1 as components
import base64
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

if 'satisfaccion' not in st.session_state:
    st.session_state.satisfaccion = 10 # Empezamos en 10 por defecto

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except: return ""

# 1. Función de carga ultra-rápida con caché de objeto completo
def get_base64_image(path):
    with open(path, "rb") as img_file:
        # El .decode('utf-8') es vital para que sea texto y no bytes
        return base64.b64encode(img_file.read()).decode('utf-8')
# --- FUNCIÓN AUXILIAR PARA CARGAR IMÁGENES LOCALES ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception:
        return ""
# Función para convertir tus caritas locales a formato que el navegador entienda
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception:
        return ""
    
# Función para dibujar las barras de movimientos (Reutilizable)
def renderizar_fila_movimiento(m, valor_max):
    es_ingreso = (m.tipo.upper() == "INGRESO")
    color_hex = "#28a745" if es_ingreso else "#dc3545"
    emoji = "💰" if es_ingreso else "💸"
    porcentaje_relativo = (m.monto / valor_max * 100)
    
    st.markdown(f"""
        <div style="margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: bold; font-size: 16px;">{emoji} {m.descripcion}</span>
                <span style="color: {color_hex}; font-weight: bold; font-size: 16px;">${m.monto:,.2f}</span>
            </div>
            <div style="width: 100%; background-color: #f0f0f0; border-radius: 12px; height: 26px; border: 1px solid #e0e0e0; overflow: hidden;">
                <div style="width: {porcentaje_relativo}%; background-color: {color_hex}; height: 100%; border-radius: 10px; display: flex; align-items: center; justify-content: center; min-width: 40px;">
                    <span style="color: white; font-size: 11px; font-weight: bold;">{porcentaje_relativo:.1f}%</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
        
# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Finanzas Psicométricas", page_icon="🧠", layout="wide")

# --- BARRA LATERAL (MENÚ MODERNO) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'> Menú</h2>", unsafe_allow_html=True)
    
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

# --- NAVEGACIÓN PRINCIPAL ---

# --- NAVEGACIÓN PRINCIPAL ---

if opcion == "Inicio":
    st.title("Dashboard de Inicio")
    st.markdown("### Estado Financiero Actual")
    
    # 1. Métricas (Esto se mantiene igual)
    c1, c2, c3 = st.columns(3)
    c1.metric("📥 Total Ingresos", f"${total_ingresos:,.2f}")
    c2.metric("📤 Total Gastos", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
    
    color_saldo = "normal" if saldo_final >= 0 else "inverse"
    c3.metric("Dinero Restante", f"${saldo_final:,.2f}", 
                delta="POSITIVO" if saldo_final >= 0 else "DÉFICIT", 
                delta_color=color_saldo)
    
    st.divider()
    st.subheader("📊 Última Actividad (Impacto Proporcional)")
    
    if not movimientos_db:
        st.info("No hay registros aún.")
    else:
        # Configuración del estado de expansión
        if "mostrar_todo_inicio" not in st.session_state:
            st.session_state.mostrar_todo_inicio = False

        valor_maximo_global = max([m.monto for m in movimientos_db]) if movimientos_db else 1
        todos_reversa = movimientos_db[::-1]
        
        # Seleccionamos qué mostrar (5 o todos)
        movimientos_a_mostrar = todos_reversa if st.session_state.mostrar_todo_inicio else todos_reversa[:5]
        
        # Renderizado de la lista (EL ÚNICO QUE DEBE QUEDAR)
        for m in movimientos_a_mostrar:
            renderizar_fila_movimiento(m, valor_maximo_global)

        # Botón dinámico al final
        st.write("")
        if not st.session_state.mostrar_todo_inicio and len(todos_reversa) > 5:
            if st.button("🔽 Mostrar todos los movimientos", use_container_width=True):
                st.session_state.mostrar_todo_inicio = True
                st.rerun()
        elif st.session_state.mostrar_todo_inicio:
            if st.button("🔼 Mostrar menos", use_container_width=True):
                st.session_state.mostrar_todo_inicio = False
                st.rerun()



elif opcion == "Registrar Movimiento":
    st.title("Registrar Movimiento")
    
    col_input, col_emocion = st.columns([1, 1.5])
    
    with col_input:
        descripcion = st.text_input("Descripción", placeholder="Ej. Sueldo, Alquiler...", key="reg_desc")
        monto = st.number_input("Monto ($)", value=0.0, step=0.01, key="reg_monto")
        tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"], key="reg_tipo")
        comentario = st.text_area("Comentario (Opcional)", key="reg_com")

    with col_emocion:
        # 1. Generar el HTML de las 10 caritas
        caritas_html_list = ""
        for i in range(1, 11):
            img_path = f"assets/caritas/carita{i}.PNG"
            img_base64 = get_base64_image(img_path)
            
            # Sincronizar visualmente con el session_state
            # Si no hay valor, usamos 10 por defecto
            val_actual = st.session_state.get('satisfaccion', 10)
            active_class = "active" if i == val_actual else ""
            
            caritas_html_list += f"""
                <div class="emoji-card {active_class}" id="card-{i}" onclick="selectEmoji({i})">
                    <img src="{img_base64}" class="emoji-img">
                    <div class="emoji-num">{i}</div>
                </div>
            """

        emoji_component_html = f"""
        <style>
            .carrete {{ display: flex; flex-wrap: wrap; gap: 10px; background: #f8f9fb; padding: 20px; border-radius: 15px; border: 1px solid #e6e9ef; justify-content: center; }}
            .emoji-card {{ cursor: pointer; text-align: center; opacity: 0.4; filter: grayscale(100%); min-width: 45px; transition: 0.3s; }}
            .emoji-card:hover {{ transform: scale(1.1); opacity: 0.7; }}
            .emoji-card.active {{ opacity: 1; filter: grayscale(0%); border-bottom: 3px solid #f39c12; transform: scale(1.1); }}
            .emoji-img {{ width: 100%; max-width: 40px; height: auto; }}
            .emoji-num {{ font-weight: bold; font-size: 0.8rem; color: #444; margin-top: 5px; }}
        </style>
        <div class="main-container">
            <div style="font-weight: bold; margin-bottom: 15px; font-family: sans-serif;">¿Cómo te sientes con este movimiento?</div>
            <div class="carrete">{caritas_html_list}</div>
        </div>
        <script>
            function selectEmoji(val) {{
                document.querySelectorAll('.emoji-card').forEach(c => c.classList.remove('active'));
                document.getElementById('card-' + val).classList.add('active');
                window.parent.postMessage({{
                    isStreamlitMessage: true,
                    type: "streamlit:setComponentValue",
                    value: val
                }}, "*");
            }}
        </script>
        """
        
        # 2. Renderizar y capturar. 
        # IMPORTANTE: No uses 'valor_capturado' directamente en el éxito/DB.
        res = components.html(emoji_component_html, height=230)
        
        # Si 'res' trae un número, actualizamos el estado
        if res is not None:
            st.session_state.satisfaccion = int(res)

    st.divider()

    # --- BOTÓN DE GUARDADO ---
    if st.button("🚀 Guardar Registro", use_container_width=True):
        if descripcion and monto > 0:
            db = SessionLocal()
            try:
                # Extraemos el valor del estado para asegurar que sea un INT y no un objeto
                nivel_final = int(st.session_state.get('satisfaccion', 10))

                nuevo_mov = Movimiento(tipo=tipo, descripcion=descripcion, monto=monto)
                db.add(nuevo_mov)
                db.flush() 
                
                nueva_metrica = MetricaSatisfaccion(
                    movimiento_id=nuevo_mov.id, 
                    nivel=nivel_final, 
                    comentario=comentario
                )
                db.add(nueva_metrica)
                db.commit()
                
                st.success(f"✅ ¡Movimiento registrado! Nivel de satisfacción: {nivel_final}")
                st.balloons()
            except Exception as e:
                db.rollback()
                # Aquí es donde antes fallaba porque intentaba imprimir el objeto HTML en el mensaje de error
                st.error(f"Error al guardar: {str(e)}")
            finally:
                db.close()
        else:
            st.warning("⚠️ Por favor completa la descripción y el monto.")
            
elif opcion == "Recomendaciones":
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
    st.title("Gestión de Historial")
    db = SessionLocal()
    
    # Inicializar estados si no existen
    if "modo_borrado" not in st.session_state:
        st.session_state.modo_borrado = False
    if "modo_edicion" not in st.session_state:
        st.session_state.modo_edicion = False

    # 1. Obtener datos
    historial = db.query(Movimiento).join(MetricaSatisfaccion).order_by(Movimiento.fecha.desc()).all()
    
    if not historial:
        st.info("Aún no tienes movimientos registrados.")
    else:
        import pandas as pd
        datos_lista = []
        for h in historial:
            datos_lista.append({
                "ID": h.id,
                "Fecha": h.fecha.strftime("%Y-%m-%d"),
                "Descripción": h.descripcion,
                "Monto": h.monto,
                "Tipo": h.tipo,
                "Satisfacción": h.satisfaccion.nivel if hasattr(h.satisfaccion, 'nivel') else h.satisfaccion.level
            })
        df_historial = pd.DataFrame(datos_lista)

        # 2. Botonera de control
        col_tit, col_edit, col_del = st.columns([2, 1, 1])
        with col_tit:
            st.subheader("Registros Actuales")
        
        with col_edit:
            if not st.session_state.modo_borrado:
                label_edit = "❌ Cancelar Edición" if st.session_state.modo_edicion else "📝 Editar Datos"
                if st.button(label_edit, use_container_width=True):
                    st.session_state.modo_edicion = not st.session_state.modo_edicion
                    st.rerun()

        with col_del:
            if not st.session_state.modo_edicion:
                label_del = "❌ Cancelar" if st.session_state.modo_borrado else "🗑️ Eliminar"
                if st.button(label_del, use_container_width=True):
                    st.session_state.modo_borrado = not st.session_state.modo_borrado
                    st.rerun()

        # --- LÓGICA DE EDICIÓN ---
        if st.session_state.modo_edicion:
            st.info("💡 Haz doble clic en una celda para modificarla. Al terminar, presiona el botón 'Guardar Cambios'.")
            
            # Configuramos el editor para que ciertas columnas sean editables
            df_editado = st.data_editor(
                df_historial,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", disabled=True),
                    "Fecha": st.column_config.TextColumn("Fecha", disabled=True),
                    "Tipo": st.column_config.SelectboxColumn("Tipo", options=["GASTO", "INGRESO"]),
                    "Satisfacción": st.column_config.NumberColumn("Satisfacción", min_value=1, max_value=10, step=1),
                },
                use_container_width=True,
                key="editor_global"
            )

            # Detectar si hay cambios comparando DataFrames
            if st.button("💾 Guardar Cambios en Base de Datos", type="primary"):
                try:
                    cambios_realizados = False
                    for index, row in df_editado.iterrows():
                        original = df_historial.iloc[index]
                        # Si la fila actual es distinta a la original, actualizamos
                        if not row.equals(original):
                            # Actualizar Movimiento
                            mov = db.query(Movimiento).filter(Movimiento.id == int(row["ID"])).first()
                            mov.descripcion = row["Descripción"]
                            mov.monto = float(row["Monto"])
                            mov.tipo = row["Tipo"]
                            
                            # Actualizar Satisfacción
                            metrica = db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id == mov.id).first()
                            metrica.nivel = int(row["Satisfacción"])
                            
                            cambios_realizados = True
                    
                    if cambios_realizados:
                        db.commit()
                        st.success("✅ Cambios guardados correctamente.")
                        st.session_state.modo_edicion = False
                        st.rerun()
                    else:
                        st.warning("No se detectaron cambios para guardar.")
                except Exception as e:
                    db.rollback()
                    st.error(f"Error al actualizar: {e}")

        # --- LÓGICA DE BORRADO (Tu código original mejorado) ---
        elif st.session_state.modo_borrado:
            df_historial.insert(0, "Seleccionar", False)
            edicion_borrado = st.data_editor(
                df_historial,
                hide_index=True,
                column_config={"Seleccionar": st.column_config.CheckboxColumn("Seleccionar", default=False)},
                use_container_width=True
            )
            ids_a_eliminar = edicion_borrado[edicion_borrado["Seleccionar"] == True]["ID"].tolist()

            if ids_a_eliminar:
                if st.button(f"🗑️ Confirmar eliminación de {len(ids_a_eliminar)} registros"):
                    try:
                        db.query(MetricaSatisfaccion).filter(MetricaSatisfaccion.movimiento_id.in_(ids_a_eliminar)).delete(synchronize_session=False)
                        db.query(Movimiento).filter(Movimiento.id.in_(ids_a_eliminar)).delete(synchronize_session=False)
                        db.commit()
                        st.session_state.modo_borrado = False
                        st.success("Registros eliminados.")
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error: {e}")
        
        # --- VISTA NORMAL ---
        else:
            st.dataframe(df_historial, hide_index=True, use_container_width=True)

    db.close()
    