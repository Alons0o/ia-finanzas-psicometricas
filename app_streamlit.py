import os
import streamlit as st
import base64
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from app.db.session import SessionLocal
from app.ia.analisis_psicometrico import MotorPsicometrico
from app.models.movimiento import Movimiento
from app.models.satisfaccion import MetricaSatisfaccion

# 1. Función de carga ultra-rápida con caché de objeto completo
def get_base64_image(path):
    with open(path, "rb") as img_file:
        # El .decode('utf-8') es vital para que sea texto y no bytes
        return base64.b64encode(img_file.read()).decode('utf-8')

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
    
    col_input, col_emocion = st.columns([1, 1.2])
    
    with col_input:
        descripcion = st.text_input("Descripción", placeholder="Ej. Sueldo, Alquiler, Comida...")
        monto = st.number_input("Monto ($)", value=0.0, step=0.01)
        tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"])

    with col_emocion:
        st.write("### ¿Cómo te sientes con este movimiento?")
        
        # 1. Inicializar el estado si no existe
        if "satisfaccion_select" not in st.session_state:
            st.session_state.satisfaccion_select = 5

        # 2. Generar el HTML del carrete
        iconos_html = ""
        for i in range(1, 11):
            try:
                # Importante: Verifica que la ruta sea exacta a tu estructura de carpetas
                img_path = f"assets/caritas/carita{i}.PNG"
                img_b64 = get_base64_image(img_path)
            
                # Lógica de resaltado
                es_activa = (st.session_state.satisfaccion_select == i)
                
                # Estilos dinámicos
                opacidad = "1" if es_activa else "0.3"
                escala = "scale(1.2)" if es_activa else "scale(0.85)"
                filtro = "grayscale(0%)" if es_activa else "grayscale(100%)"
                borde = "4px solid #ff4b4b" if es_activa else "4px solid transparent"

                iconos_html += f'''
                    <div style="
                        flex: 0 0 auto; 
                        width: 70px; 
                        margin: 10px; 
                        text-align: center; 
                        transition: all 0.4s ease;
                    ">
                        <img src="data:image/png;base64,{img_b64}" 
                             style="
                                width: 60px; 
                                height: 60px; 
                                object-fit: contain;
                                opacity: {opacidad}; 
                                filter: {filtro}; 
                                transform: {escala}; 
                                border-radius: 50%;
                                border-bottom: {borde};
                                padding: 5px;
                             ">
                        <p style="
                            font-size: 14px; 
                            font-weight: {'bold' if es_activa else 'normal'}; 
                            color: {'#ff4b4b' if es_activa else '#666'}; 
                            margin-top: 5px;
                        ">{i}</p>
                    </div>
                '''
            except Exception as e:
                iconos_html += f"<div style='flex: 0 0 auto; width: 70px;'>⚠️ {i}</div>"

        # 3. Renderizar el contenedor tipo "Carrete"
        st.markdown(f'''
            <div style="
                display: flex; 
                flex-wrap: nowrap; 
                overflow-x: auto; 
                padding: 10px 5px; 
                background-color: #f8f9fa; 
                border-radius: 15px; 
                box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
                scrollbar-width: thin;
                justify-content: flex-start;
                align-items: center;
                margin-bottom: 10px;
            ">
                {iconos_html}
            </div>
            <style>
                /* Estilo para la barra de desplazamiento en Chrome/Safari */
                ::-webkit-scrollbar {{ height: 6px; }}
                ::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 10px; }}
            </style>
        ''', unsafe_allow_html=True)
        
        # 4. Control deslizante (Slider) que sincroniza el carrete
        nuevo_nivel = st.select_slider(
            "Desliza para seleccionar tu emoción",
            options=range(1, 11),
            value=st.session_state.satisfaccion_select,
            key="slider_emociones",
            label_visibility="collapsed"
        )
    
    # --- EL FORMULARIO DEBE ESTAR AQUÍ (FUERA DE LAS COLUMNAS) ---
    with st.form("formulario_final", clear_on_submit=True):
        comentario = st.text_area("Comentario (¿Cómo te sentiste?)")
        
        # Botón de envío
        enviar = st.form_submit_button("Guardar Registro")
        
        if enviar:
            if descripcion and monto > 0:
                db = SessionLocal()
                try:
                    nuevo_mov = Movimiento(tipo=tipo, descripcion=descripcion, monto=monto)
                    db.add(nuevo_mov)
                    db.flush()
                    
                    nueva_metrica = MetricaSatisfaccion(
                        movimiento_id=nuevo_mov.id, 
                        nivel=st.session_state.satisfaccion_select, 
                        comentario=comentario
                    )
                    db.add(nueva_metrica)
                    db.commit()
                    st.success("✅ ¡Movimiento registrado!")
                    st.balloons()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
                finally:
                    db.close()
            else:
                st.warning("⚠️ Completa descripción y monto.")

elif opcion == "Visualizaciones":
    st.title("Análisis de Datos")
    db = SessionLocal()
    motor = MotorPsicometrico(db)
    datos_burbujas = motor.preparar_datos_burbujas()
    db.close()

    if not movimientos_db:
        st.warning("Sin datos suficientes.")
    else:
        # --- CONFIGURACIÓN DE COLORES SINCRONIZADOS ---
        descripciones_unicas = list(set(d['descripcion'] for d in datos_burbujas))
        color_palette = plt.get_cmap("tab20")
        color_map = {desc: color_palette(i / len(descripciones_unicas)) for i, desc in enumerate(descripciones_unicas)}

        col_ing, col_gas = st.columns(2)
        
        def dibujar_pastel(ax, datos_lista, titulo, es_gasto=False):
            resumen = {}
            for d in datos_lista:
                resumen[d.descripcion] = resumen.get(d.descripcion, 0) + d.monto
            
            if not resumen:
                ax.text(0.5, 0.5, "Sin datos", ha='center')
                ax.axis('off')
                return
            
            labels, sizes = list(resumen.keys()), list(resumen.values())
            
            if es_gasto:
                colores = [color_map.get(label, "#cccccc") for label in labels]
            else:
                colores = plt.get_cmap("viridis")([i/len(labels) for i in range(len(labels))])

            def format_monto(pct, allvals):
                absolute = pct/100.*sum(allvals)
                return f"${absolute:,.0f}"

            # --- CORRECCIÓN AQUÍ: Eliminamos el duplicado en textprops ---
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=None, 
                autopct=lambda pct: format_monto(pct, sizes), 
                startangle=140, 
                colors=colores,
                pctdistance=0.75,
                textprops={'color': "w", 'fontweight': 'bold', 'size': 10} 
            )
            
            ax.legend(
                wedges, 
                [f"{l} ({ (s/sum(sizes))*100:.1f}%)" for l, s in zip(labels, sizes)],
                title="Categorías",
                loc="center left",
                bbox_to_anchor=(0.9, 0, 0.5, 1),
                fontsize=8
            )
            
            ax.set_title(titulo, fontweight='bold', pad=20)

        with col_ing:
            fig_ing, ax_ing = plt.subplots()
            dibujar_pastel(ax_ing, [m for m in movimientos_db if m.tipo=="INGRESO"], "Ingresos")
            st.pyplot(fig_ing)

        with col_gas:
            fig_gas, ax_gas = plt.subplots()
            dibujar_pastel(ax_gas, [m for m in movimientos_db if m.tipo=="GASTO"], "Gastos", es_gasto=True)
            st.pyplot(fig_gas)

        st.divider()
        st.write("### Mapa de Valor (Gastos)")
        
        if datos_burbujas:
            fig_b, ax_b = plt.subplots(figsize=(10, 5))
            for d in datos_burbujas:
                c_burbuja = color_map.get(d['descripcion'], "blue")
                ax_b.scatter(d['monto'], d['satisfaccion'], s=d['peso']*15, alpha=0.7, color=c_burbuja, edgecolors="white")
                ax_b.annotate(f" {d['descripcion']}", (d['monto'], d['satisfaccion']), fontsize=9, fontweight='bold')
            
            ax_b.set_xlabel("Monto Invertido ($)")
            ax_b.set_ylabel("Nivel de Satisfacción")
            ax_b.grid(True, linestyle='--', alpha=0.5)
            st.pyplot(fig_b)

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