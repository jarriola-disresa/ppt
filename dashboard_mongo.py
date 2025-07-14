import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from pymongo import MongoClient
import hmac
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard KSB - MongoDB",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para estilo profesional
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f4e79;
        padding-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1f4e79 0%, #2980b9 100%);
    }
    .stSelectbox > div > div > select {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""
 
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
 
    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True
 
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
 
 
if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Clear cache button for debugging
if st.button("🗑️ Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared! Please refresh the page.")
    st.rerun()

@st.cache_resource
def init_mongodb_connection():
    """Inicializar conexión a MongoDB"""
    try:
        # Configuración de conexión
        mongo_uri = st.secrets.get("mongo_uri", "mongodb://localhost:27017/")
        db_name = st.secrets.get("db_name", "ksb_budget")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        client.admin.command('ismaster')
        
        return db, True, f"Conectado a: {db_name}"
    except Exception as e:
        return None, False, f"Error de conexión: {str(e)}"

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data_from_mongo(_db):
    """Cargar datos desde MongoDB"""
    
    try:
        # Cargar cada colección
        resumen_data = list(_db.resumen_presupuesto.find())
        ppto_data = list(_db.presupuesto_detallado.find())
        transacciones_data = list(_db.transacciones.find())
        reclasif_data = list(_db.reclasificaciones.find())
        cuentas_data = list(_db.cuentas_reales.find())
        
        return {
            'resumen': pd.DataFrame(resumen_data),
            'presupuesto': pd.DataFrame(ppto_data),
            'transacciones': pd.DataFrame(transacciones_data),
            'reclasificaciones': pd.DataFrame(reclasif_data),
            'cuentas': pd.DataFrame(cuentas_data)
        }, True, "Datos cargados exitosamente"
        
    except Exception as e:
        return {}, False, f"Error cargando datos: {str(e)}"

def create_resumen_charts_mongo(resumen_df):
    """Crear gráficas para datos de resumen desde MongoDB"""
    
    if resumen_df.empty:
        return None, None, None, None
    
    # Filtrar SOLO áreas (excluir fila TOTAL)
    areas_df = resumen_df[resumen_df['area'] != 'TOTAL'].copy()
    
    # Preparar datos para gráficas (solo áreas, sin TOTAL)
    pivot_data = areas_df.pivot_table(
        values='presupuesto_mensual',
        index='area',
        columns='mes',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ordenar meses correctamente
    month_order = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio']
    available_months = [month for month in month_order if month in pivot_data.columns]
    pivot_data = pivot_data[available_months]
    
    # Gráfica 1: Evolución mensual por área
    fig1 = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    for i, area in enumerate(pivot_data.index):
        fig1.add_trace(go.Scatter(
            x=[month.capitalize() for month in available_months],
            y=pivot_data.loc[area, available_months].values,
            mode='lines+markers',
            name=area,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8)
        ))
    
    fig1.update_layout(
        title="<b>Presupuesto por Área - Evolución Mensual</b>",
        xaxis_title="Mes",
        yaxis_title="Presupuesto (GTQ)",
        template="plotly_white",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    # Gráfica 2: Total por área
    total_by_area = pivot_data.sum(axis=1)
    
    fig2 = px.bar(
        x=total_by_area.index,
        y=total_by_area.values,
        title="<b>Presupuesto Total por Área</b>",
        color=total_by_area.values,
        color_continuous_scale="Viridis"
    )
    
    fig2.update_layout(
        xaxis_title="Área",
        yaxis_title="Presupuesto Total (GTQ)",
        template="plotly_white",
        height=500,
        showlegend=False
    )
    
    # Gráfica 3: Distribución porcentual
    fig3 = px.pie(
        values=total_by_area.values,
        names=total_by_area.index,
        title="<b>Distribución Porcentual del Presupuesto</b>",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig3.update_layout(height=500)
    
    return fig1, fig2, fig3, total_by_area

def main():
    # Header principal
    st.markdown('<h1 class="main-header">📊 Dashboard KSB - MongoDB Edition</h1>', unsafe_allow_html=True)
    
    # Intentar conexión
    db, connection_success, connection_msg = init_mongodb_connection()
    
    if connection_success:
        # Cargar datos
        with st.spinner('Cargando datos desde MongoDB...'):
            data_dict, load_success, load_msg = load_data_from_mongo(db)
        
        if load_success:
            # Navegación principal
            st.sidebar.markdown("## 🎛️ Panel de Control")
            page = st.sidebar.selectbox(
                "Seleccionar Vista",
                ["📈 Resumen Ejecutivo", "💰 Presupuesto Detallado", "📋 Transacciones", "🔄 Reclasificaciones", "📊 Cuentas"]
            )
            
            # Mostrar páginas
            if page == "📈 Resumen Ejecutivo":
                st.header("📈 Resumen Ejecutivo - Presupuesto por Área")
                
                resumen_df = data_dict['resumen']
                
                if not resumen_df.empty:
                    # Crear gráficas
                    fig1, fig2, fig3, total_by_area = create_resumen_charts_mongo(resumen_df)
                    
                    if fig1 is not None:
                        # Obtener el presupuesto total anual (35 millones) y ejecutado Ene-Jun de la fila TOTAL
                        total_records = resumen_df[resumen_df['area'] == 'TOTAL']
                        if len(total_records) > 0:
                            total_anual_record = total_records['total_anual'].iloc[0]
                            # Calcular ejecutado Ene-Jun de la fila TOTAL
                            total_ene_jun_records = total_records[total_records['mes'].isin(['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio'])]
                            ejecutado_ene_jun = total_ene_jun_records['presupuesto_mensual'].sum()
                        else:
                            total_anual_record = 0
                            ejecutado_ene_jun = 0
                        
                        # Métricas principales  
                        col1, col2, col3, col4 = st.columns(4)
                        
                        # Para métricas de áreas (sin TOTAL)
                        max_area = total_by_area.idxmax() if len(total_by_area) > 0 else "N/A"
                        max_value = total_by_area.max() if len(total_by_area) > 0 else 0
                        
                        with col1:
                            st.metric("💰 Presupuesto 2025", f"Q {total_anual_record:,.0f}")
                        with col2:
                            st.metric("📊 Ejecutado Ene-Jun", f"Q {ejecutado_ene_jun:,.0f}")
                        with col3:
                            st.metric("🏆 Área Principal", max_area)
                        with col4:
                            pendiente = total_anual_record - ejecutado_ene_jun
                            st.metric("⏳ Pendiente Jul-Dic", f"Q {pendiente:,.0f}")
                        
                        # Gráficas
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.plotly_chart(fig1, use_container_width=True)
                            st.plotly_chart(fig3, use_container_width=True)
                        
                        with col2:
                            st.plotly_chart(fig2, use_container_width=True)
                            
                            # Tabla resumen por áreas
                            st.subheader("📋 Resumen por Área")
                            summary_table = pd.DataFrame({
                                'Área': total_by_area.index,
                                'Ejecutado Ene-Jun': total_by_area.values,
                                'Porcentaje': (total_by_area.values / ejecutado_ene_jun * 100).round(1) if ejecutado_ene_jun > 0 else 0
                            })
                            summary_table['Ejecutado Ene-Jun'] = summary_table['Ejecutado Ene-Jun'].apply(lambda x: f"Q {x:,.0f}")
                            summary_table['Porcentaje'] = summary_table['Porcentaje'].apply(lambda x: f"{x}%")
                            
                            # Agregar nota del presupuesto total (usando fila TOTAL)
                            porcentaje_ejecutado = (ejecutado_ene_jun/total_anual_record*100) if total_anual_record > 0 else 0
                            st.info(f"💰 **Presupuesto Total 2025: Q {total_anual_record:,.0f}** | Ejecutado Ene-Jun: Q {ejecutado_ene_jun:,.0f} ({porcentaje_ejecutado:.1f}%)")
                            st.dataframe(summary_table, use_container_width=True)
                    else:
                        st.warning("No se pudieron generar las gráficas.")
                else:
                    st.warning("No hay datos de resumen disponibles.")
            
            elif page == "💰 Presupuesto Detallado":
                st.header("💰 Presupuesto Detallado por Centro de Coste")
                
                ppto_df = data_dict['presupuesto']
                
                if not ppto_df.empty:
                    # Filtros
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        denominaciones = ['Todas'] + list(ppto_df['denominacion_objeto'].unique())
                        selected_denom = st.selectbox("Denominación del Objeto", denominaciones)
                    
                    with col2:
                        monedas = ['Todas'] + list(ppto_df['moneda'].unique())
                        selected_moneda = st.selectbox("Moneda", monedas)
                    
                    # Aplicar filtros
                    filtered_df = ppto_df.copy()
                    if selected_denom != 'Todas':
                        filtered_df = filtered_df[filtered_df['denominacion_objeto'] == selected_denom]
                    if selected_moneda != 'Todas':
                        filtered_df = filtered_df[filtered_df['moneda'] == selected_moneda]
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Registros", len(filtered_df))
                    with col2:
                        total_presupuesto = filtered_df['presupuesto'].sum()
                        st.metric("💰 Total Presupuesto", f"Q {total_presupuesto:,.0f}")
                    with col3:
                        centros_unicos = filtered_df['centro_coste'].nunique()
                        st.metric("🏢 Centros de Coste", centros_unicos)
                    with col4:
                        promedio = filtered_df['presupuesto'].mean()
                        st.metric("📊 Promedio", f"Q {promedio:,.0f}")
                    
                    # Gráficas
                    if len(filtered_df) > 0:
                        # Por mes
                        monthly_data = filtered_df.groupby('mes')['presupuesto'].sum().reset_index()
                        
                        fig = px.bar(
                            monthly_data,
                            x='mes',
                            y='presupuesto',
                            title="Presupuesto por Mes",
                            color='presupuesto',
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(template="plotly_white", height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Top centros
                        top_centers = filtered_df.groupby('centro_coste')['presupuesto'].sum().nlargest(10)
                        
                        fig2 = px.bar(
                            x=top_centers.values,
                            y=top_centers.index,
                            orientation='h',
                            title="Top 10 Centros de Coste",
                            color=top_centers.values,
                            color_continuous_scale="Blues"
                        )
                        fig2.update_layout(template="plotly_white", height=500)
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Tabla
                    st.subheader("📋 Datos Detallados")
                    display_cols = ['centro_coste', 'denominacion_objeto', 'mes', 'presupuesto', 'moneda']
                    st.dataframe(filtered_df[display_cols], use_container_width=True)
                else:
                    st.warning("No hay datos de presupuesto disponibles.")
            
            elif page == "📋 Transacciones":
                st.header("📋 Análisis de Transacciones")
                
                trans_df = data_dict['transacciones']
                
                if not trans_df.empty:
                    # Filtros
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if 'denominacion_objeto' in trans_df.columns:
                            denominaciones = ['Todas'] + list(trans_df['denominacion_objeto'].dropna().unique())
                            selected_denom = st.selectbox("Denominación", denominaciones)
                    
                    with col2:
                        if 'mes' in trans_df.columns:
                            meses = ['Todos'] + list(trans_df['mes'].dropna().unique())
                            selected_mes = st.selectbox("Mes", meses)
                    
                    with col3:
                        if 'centro_coste' in trans_df.columns:
                            centros = ['Todos'] + list(trans_df['centro_coste'].dropna().unique())[:20]  # Limitar para performance
                            selected_centro = st.selectbox("Centro de Coste", centros)
                    
                    # Aplicar filtros
                    filtered_trans = trans_df.copy()
                    if 'selected_denom' in locals() and selected_denom != 'Todas':
                        filtered_trans = filtered_trans[filtered_trans['denominacion_objeto'] == selected_denom]
                    if 'selected_mes' in locals() and selected_mes != 'Todos':
                        filtered_trans = filtered_trans[filtered_trans['mes'] == selected_mes]
                    if 'selected_centro' in locals() and selected_centro != 'Todos':
                        filtered_trans = filtered_trans[filtered_trans['centro_coste'] == selected_centro]
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Transacciones", len(filtered_trans))
                    with col2:
                        if 'valor_moneda_objeto' in filtered_trans.columns:
                            total_valor = filtered_trans['valor_moneda_objeto'].sum()
                            st.metric("💰 Valor Total", f"Q {total_valor:,.0f}")
                    with col3:
                        if 'centro_coste' in filtered_trans.columns:
                            centros_unicos = filtered_trans['centro_coste'].nunique()
                            st.metric("🏢 Centros Únicos", centros_unicos)
                    with col4:
                        if 'valor_moneda_objeto' in filtered_trans.columns and len(filtered_trans) > 0:
                            promedio = filtered_trans['valor_moneda_objeto'].mean()
                            st.metric("📊 Valor Promedio", f"Q {promedio:,.0f}")
                    
                    # Tabla
                    st.subheader("📋 Transacciones")
                    display_cols = ['centro_coste', 'denom_clase_coste', 'valor_moneda_objeto', 'fecha_contabilizacion', 'mes']
                    available_cols = [col for col in display_cols if col in filtered_trans.columns]
                    if available_cols:
                        st.dataframe(filtered_trans[available_cols].head(100), use_container_width=True)
                    else:
                        st.dataframe(filtered_trans.head(100), use_container_width=True)
                else:
                    st.warning("No hay datos de transacciones disponibles.")
            
            elif page == "🔄 Reclasificaciones":
                st.header("🔄 Análisis de Reclasificaciones")
                
                reclasif_df = data_dict['reclasificaciones']
                
                if not reclasif_df.empty:
                    # Métricas
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Reclasificaciones", len(reclasif_df))
                    with col2:
                        if 'valor_moneda_objeto' in reclasif_df.columns:
                            total_valor = reclasif_df['valor_moneda_objeto'].sum()
                            st.metric("💰 Valor Total", f"Q {total_valor:,.0f}")
                    with col3:
                        if 'centro_coste' in reclasif_df.columns:
                            centros_unicos = reclasif_df['centro_coste'].nunique()
                            st.metric("🏢 Centros Afectados", centros_unicos)
                    
                    # Tabla
                    st.subheader("📋 Reclasificaciones")
                    display_cols = ['centro_coste', 'denom_clase_coste', 'valor_moneda_objeto', 'fecha_contabilizacion']
                    available_cols = [col for col in display_cols if col in reclasif_df.columns]
                    if available_cols:
                        st.dataframe(reclasif_df[available_cols], use_container_width=True)
                    else:
                        st.dataframe(reclasif_df, use_container_width=True)
                else:
                    st.warning("No hay datos de reclasificaciones disponibles.")
            
            elif page == "📊 Cuentas":
                st.header("📊 Análisis de Cuentas Reales")
                
                cuentas_df = data_dict['cuentas']
                
                if not cuentas_df.empty:
                    # Filtros
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        areas = ['Todas'] + list(cuentas_df['area'].unique())
                        selected_area = st.selectbox("Área", areas)
                    
                    with col2:
                        meses = ['Todos'] + list(cuentas_df['mes'].unique())
                        selected_mes_c = st.selectbox("Mes", meses, key="mes_cuentas")
                    
                    # Aplicar filtros
                    filtered_cuentas = cuentas_df.copy()
                    if selected_area != 'Todas':
                        filtered_cuentas = filtered_cuentas[filtered_cuentas['area'] == selected_area]
                    if selected_mes_c != 'Todos':
                        filtered_cuentas = filtered_cuentas[filtered_cuentas['mes'] == selected_mes_c]
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Registros", len(filtered_cuentas))
                    with col2:
                        total_real = filtered_cuentas['valor_real'].sum()
                        st.metric("💰 Total Real", f"Q {total_real:,.2f}")
                    with col3:
                        areas_unicas = filtered_cuentas['area'].nunique()
                        st.metric("🏢 Áreas", areas_unicas)
                    with col4:
                        if len(filtered_cuentas) > 0:
                            promedio_real = filtered_cuentas['valor_real'].mean()
                            st.metric("📊 Promedio", f"Q {promedio_real:,.2f}")
                    
                    # Gráfica por área
                    if len(filtered_cuentas) > 0:
                        real_by_area = filtered_cuentas.groupby('area')['valor_real'].sum()
                        
                        fig = px.pie(
                            values=real_by_area.values,
                            names=real_by_area.index,
                            title="Distribución de Valores Reales por Área",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabla
                    st.subheader("📋 Datos de Cuentas")
                    display_cols = ['area', 'responsable', 'cuenta', 'descripcion_cuenta', 'mes', 'valor_real']
                    st.dataframe(filtered_cuentas[display_cols], use_container_width=True)
                else:
                    st.warning("No hay datos de cuentas disponibles.")
        else:
            st.error(load_msg)
            st.info("Verifica que los datos estén cargados correctamente en MongoDB.")
    else:
        st.error("No se pudo conectar a MongoDB")
        
        # Mostrar instrucciones de configuración
        st.markdown("""
        ## 🔧 Configuración de MongoDB
        
        Para usar este dashboard, necesitas:
        
        1. **MongoDB ejecutándose** (local o en la nube)
        2. **Datos cargados** usando los archivos CSV generados
        3. **Configuración** en Streamlit secrets
        
        ### Archivos disponibles para cargar:
        - `csv_data/resumen_presupuesto.csv`
        - `csv_data/presupuesto_detallado.csv`
        - `csv_data/transacciones.csv`
        - `csv_data/reclasificaciones.csv`
        - `csv_data/cuentas_reales.csv`
        
        ### Comandos para cargar:
        ```bash
        mongoimport --db ksb_budget --collection resumen_presupuesto --type csv --headerline --file csv_data/resumen_presupuesto.csv
        mongoimport --db ksb_budget --collection presupuesto_detallado --type csv --headerline --file csv_data/presupuesto_detallado.csv
        mongoimport --db ksb_budget --collection transacciones --type csv --headerline --file csv_data/transacciones.csv
        mongoimport --db ksb_budget --collection reclasificaciones --type csv --headerline --file csv_data/reclasificaciones.csv
        mongoimport --db ksb_budget --collection cuentas_reales --type csv --headerline --file csv_data/cuentas_reales.csv
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Dashboard KSB - MongoDB Edition** | Conectado a base de datos en tiempo real")

if __name__ == "__main__":
    main()