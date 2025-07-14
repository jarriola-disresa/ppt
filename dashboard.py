import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard KSB - Presupuesto 2025",
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

@st.cache_data
def load_data():
    """Cargar y procesar todos los datos del Excel"""
    file_path = "/home/jarriola/mercadeo/EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    # Cargar cada hoja
    resumen = pd.read_excel(file_path, sheet_name='Resumen')
    ppto = pd.read_excel(file_path, sheet_name='PPTO')
    data = pd.read_excel(file_path, sheet_name='Data')
    reclasificacion = pd.read_excel(file_path, sheet_name='Reclasificación de gastos')
    cuentas = pd.read_excel(file_path, sheet_name='Cuentas')
    
    return resumen, ppto, data, reclasificacion, cuentas

def process_resumen_data(resumen_df):
    """Procesar datos de la hoja Resumen para gráficas"""
    # Extraer datos de presupuesto por área y mes
    data_rows = resumen_df.iloc[2:9].copy()  # Filas con datos de áreas
    
    areas = []
    monthly_data = []
    
    for idx, row in data_rows.iterrows():
        if pd.notna(row.iloc[1]) and row.iloc[1] != 'AREA':  # Verificar que hay área
            area = row.iloc[1]
            areas.append(area)
            
            # Extraer datos mensuales (columnas 2-13 corresponden a ene-dic)
            monthly_values = []
            months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            
            for i in range(2, 14):  # Columnas ene-dic
                value = row.iloc[i] if pd.notna(row.iloc[i]) else 0
                monthly_values.append(value)
            
            monthly_data.append(monthly_values)
    
    # Crear DataFrame estructurado
    budget_df = pd.DataFrame(monthly_data, columns=months, index=areas)
    return budget_df

def create_resumen_charts(budget_df):
    """Crear gráficas para la hoja Resumen"""
    
    # Gráfica 1: Presupuesto por área (Enero-Junio)
    fig1 = go.Figure()
    
    months_jan_jun = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    
    for i, area in enumerate(budget_df.index):
        fig1.add_trace(go.Scatter(
            x=months_jan_jun,
            y=budget_df.loc[area, months_jan_jun].values,
            mode='lines+markers',
            name=area,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8)
        ))
    
    fig1.update_layout(
        title="<b>Presupuesto por Área - Enero a Junio 2025</b>",
        xaxis_title="Mes",
        yaxis_title="Presupuesto (GTQ)",
        template="plotly_white",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    # Gráfica 2: Comparación total por área
    total_by_area = budget_df[months_jan_jun].sum(axis=1)
    
    fig2 = px.bar(
        x=total_by_area.index,
        y=total_by_area.values,
        title="<b>Presupuesto Total por Área (Enero-Junio)</b>",
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
        title="<b>Distribución Porcentual del Presupuesto por Área</b>",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig3.update_layout(height=500)
    
    return fig1, fig2, fig3, total_by_area

def main():
    # Header principal
    st.markdown('<h1 class="main-header">📊 Dashboard KSB - Presupuesto 2025</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner('Cargando datos...'):
        resumen, ppto, data, reclasificacion, cuentas = load_data()
    
    # Sidebar para navegación
    st.sidebar.markdown("## 🎛️ Panel de Control")
    page = st.sidebar.selectbox(
        "Seleccionar Vista",
        ["📈 Resumen Ejecutivo", "💰 Datos Detallados", "📋 Presupuesto", "🔄 Reclasificaciones", "📊 Cuentas"]
    )
    
    if page == "📈 Resumen Ejecutivo":
        st.header("📈 Resumen Ejecutivo - Presupuesto por Área")
        
        # Procesar datos de resumen
        budget_df = process_resumen_data(resumen)
        fig1, fig2, fig3, total_by_area = create_resumen_charts(budget_df)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        total_budget = total_by_area.sum()
        max_area = total_by_area.idxmax()
        max_value = total_by_area.max()
        avg_budget = total_by_area.mean()
        
        with col1:
            st.metric("💰 Presupuesto Total", f"Q {total_budget:,.0f}")
        with col2:
            st.metric("🏆 Área Principal", max_area)
        with col3:
            st.metric("📊 Mayor Presupuesto", f"Q {max_value:,.0f}")
        with col4:
            st.metric("📊 Promedio por Área", f"Q {avg_budget:,.0f}")
        
        # Gráficas
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
            
            # Tabla resumen
            st.subheader("📋 Resumen por Área")
            summary_table = pd.DataFrame({
                'Área': total_by_area.index,
                'Presupuesto Total': total_by_area.values,
                'Porcentaje': (total_by_area.values / total_budget * 100).round(1)
            })
            summary_table['Presupuesto Total'] = summary_table['Presupuesto Total'].apply(lambda x: f"Q {x:,.0f}")
            summary_table['Porcentaje'] = summary_table['Porcentaje'].apply(lambda x: f"{x}%")
            st.dataframe(summary_table, use_container_width=True)
    
    elif page == "💰 Datos Detallados":
        st.header("💰 Análisis de Datos Detallados")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Denominación del objeto' in data.columns:
                denominaciones = ['Todos'] + list(data['Denominación del objeto'].dropna().unique())
                selected_denom = st.selectbox("Denominación del Objeto", denominaciones)
        
        with col2:
            if 'Denom.clase de coste' in data.columns:
                clases = ['Todas'] + list(data['Denom.clase de coste'].dropna().unique())
                selected_clase = st.selectbox("Clase de Coste", clases)
        
        with col3:
            if 'Fe.contabilización' in data.columns:
                data['Fe.contabilización'] = pd.to_datetime(data['Fe.contabilización'], errors='coerce')
                meses = ['Todos'] + list(data['Fe.contabilización'].dt.strftime('%Y-%m').dropna().unique())
                selected_month = st.selectbox("Mes", meses)
        
        # Aplicar filtros
        filtered_data = data.copy()
        
        if selected_denom != 'Todos':
            filtered_data = filtered_data[filtered_data['Denominación del objeto'] == selected_denom]
        if selected_clase != 'Todas':
            filtered_data = filtered_data[filtered_data['Denom.clase de coste'] == selected_clase]
        if selected_month != 'Todos':
            filtered_data = filtered_data[filtered_data['Fe.contabilización'].dt.strftime('%Y-%m') == selected_month]
        
        # Métricas filtradas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Registros", len(filtered_data))
        with col2:
            if 'Valor/Moneda objeto' in filtered_data.columns:
                total_valor = filtered_data['Valor/Moneda objeto'].sum()
                st.metric("💰 Valor Total", f"Q {total_valor:,.0f}")
        with col3:
            centros_unicos = filtered_data['Centro de coste'].nunique()
            st.metric("🏢 Centros de Coste", centros_unicos)
        with col4:
            if 'Valor/Moneda objeto' in filtered_data.columns and len(filtered_data) > 0:
                valor_promedio = filtered_data['Valor/Moneda objeto'].mean()
                st.metric("📊 Valor Promedio", f"Q {valor_promedio:,.0f}")
        
        # Gráfica de valores por mes
        if len(filtered_data) > 0 and 'Fe.contabilización' in filtered_data.columns:
            monthly_values = filtered_data.groupby(filtered_data['Fe.contabilización'].dt.strftime('%Y-%m'))['Valor/Moneda objeto'].sum()
            
            fig = px.bar(
                x=monthly_values.index,
                y=monthly_values.values,
                title="Valores por Mes",
                color=monthly_values.values,
                color_continuous_scale="Blues"
            )
            fig.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        st.subheader("📋 Datos Filtrados")
        if len(filtered_data) > 0:
            display_cols = ['Centro de coste', 'Denom.clase de coste', 'Valor/Moneda objeto', 'Fe.contabilización', 'Denominación del objeto']
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            st.dataframe(filtered_data[display_cols].head(100), use_container_width=True)
        else:
            st.warning("No se encontraron datos con los filtros seleccionados.")
    
    elif page == "📋 Presupuesto":
        st.header("📋 Análisis de Presupuesto Detallado")
        
        # Procesar datos de PPTO correctamente
        try:
            # Extraer headers correctos de la fila 2 y 4
            months_header = ['Moneda', 'Centro de coste', 'Denominación del objeto', 'Clase de coste', 'Denom.clase de coste', 'Texto de cabecera', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Total']
            
            # Datos empiezan en fila 5 (índice 5)
            ppto_data = []
            for i in range(5, len(ppto)):
                row = ppto.iloc[i]
                if pd.notna(row.iloc[1]):  # Si hay centro de coste
                    row_data = {
                        'Moneda': row.iloc[0] if pd.notna(row.iloc[0]) else 'GTQ',
                        'Centro de coste': str(int(row.iloc[1])) if pd.notna(row.iloc[1]) else '',
                        'Denominación del objeto': row.iloc[2] if pd.notna(row.iloc[2]) else '',
                        'Ene': row.iloc[6] if pd.notna(row.iloc[6]) else 0,
                        'Feb': row.iloc[7] if pd.notna(row.iloc[7]) else 0,
                        'Mar': row.iloc[8] if pd.notna(row.iloc[8]) else 0,
                        'Abr': row.iloc[9] if pd.notna(row.iloc[9]) else 0,
                        'May': row.iloc[10] if pd.notna(row.iloc[10]) else 0,
                        'Jun': row.iloc[11] if pd.notna(row.iloc[11]) else 0,
                        'Total': row.iloc[12] if pd.notna(row.iloc[12]) else 0
                    }
                    ppto_data.append(row_data)
            
            if ppto_data:
                ppto_df = pd.DataFrame(ppto_data)
                
                # Filtros
                col1, col2 = st.columns(2)
                
                with col1:
                    denominaciones = ['Todas'] + list(ppto_df['Denominación del objeto'].unique())
                    selected_denom = st.selectbox("Denominación del Objeto", denominaciones)
                
                with col2:
                    monedas = ['Todas'] + list(ppto_df['Moneda'].unique())
                    selected_moneda = st.selectbox("Moneda", monedas)
                
                # Aplicar filtros
                filtered_ppto = ppto_df.copy()
                if selected_denom != 'Todas':
                    filtered_ppto = filtered_ppto[filtered_ppto['Denominación del objeto'] == selected_denom]
                if selected_moneda != 'Todas':
                    filtered_ppto = filtered_ppto[filtered_ppto['Moneda'] == selected_moneda]
                
                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Centros de Coste", len(filtered_ppto))
                with col2:
                    total_presupuesto = filtered_ppto['Total'].sum()
                    st.metric("💰 Total Presupuesto", f"Q {total_presupuesto:,.0f}")
                with col3:
                    total_ene_jun = filtered_ppto[['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']].sum().sum()
                    st.metric("📊 Ene-Jun Total", f"Q {total_ene_jun:,.0f}")
                with col4:
                    promedio_mensual = total_ene_jun / 6
                    st.metric("📊 Promedio Mensual", f"Q {promedio_mensual:,.0f}")
                
                # Gráfica de presupuesto por mes
                monthly_totals = filtered_ppto[['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']].sum()
                
                fig = px.bar(
                    x=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
                    y=monthly_totals.values,
                    title="Presupuesto Mensual Total",
                    color=monthly_totals.values,
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Gráfica por centro de coste (top 10)
                if len(filtered_ppto) > 0:
                    top_centers = filtered_ppto.nlargest(10, 'Total')
                    
                    fig2 = px.bar(
                        x=top_centers['Total'],
                        y=top_centers['Denominación del objeto'],
                        orientation='h',
                        title="Top 10 Centros por Presupuesto Total",
                        color=top_centers['Total'],
                        color_continuous_scale="Blues"
                    )
                    fig2.update_layout(template="plotly_white", height=500)
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tabla de datos
                st.subheader("📋 Datos de Presupuesto")
                
                # Formatear números para display
                display_df = filtered_ppto.copy()
                numeric_cols = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Total']
                for col in numeric_cols:
                    display_df[col] = display_df[col].apply(lambda x: f"Q {x:,.0f}" if x != 0 else "-")
                
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No se pudieron procesar los datos de presupuesto.")
                
        except Exception as e:
            st.error(f"Error procesando datos de presupuesto: {e}")
            st.subheader("Datos raw de PPTO (para debug)")
            st.dataframe(ppto, use_container_width=True)
    
    elif page == "🔄 Reclasificaciones":
        st.header("🔄 Análisis de Reclasificaciones")
        
        if len(reclasificacion) > 0:
            # Métricas de reclasificación
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total Reclasificaciones", len(reclasificacion))
            with col2:
                if 'Valor/Moneda objeto' in reclasificacion.columns:
                    total_reclas = reclasificacion['Valor/Moneda objeto'].sum()
                    st.metric("💰 Valor Total", f"Q {total_reclas:,.0f}")
            with col3:
                centros_reclas = reclasificacion['Centro de coste'].nunique()
                st.metric("🏢 Centros Involucrados", centros_reclas)
            
            # Gráfica de reclasificaciones por centro
            if 'Centro de coste' in reclasificacion.columns and 'Valor/Moneda objeto' in reclasificacion.columns:
                reclas_by_center = reclasificacion.groupby('Centro de coste')['Valor/Moneda objeto'].sum().head(10)
                
                fig = px.bar(
                    x=reclas_by_center.values,
                    y=reclas_by_center.index.astype(str),
                    orientation='h',
                    title="Top 10 Centros de Coste por Valor de Reclasificación",
                    color=reclas_by_center.values,
                    color_continuous_scale="Reds"
                )
                fig.update_layout(template="plotly_white", height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Datos de Reclasificación")
            display_cols = ['Centro de coste', 'Denom.clase de coste', 'Valor/Moneda objeto', 'Fe.contabilización']
            display_cols = [col for col in display_cols if col in reclasificacion.columns]
            st.dataframe(reclasificacion[display_cols], use_container_width=True)
        else:
            st.warning("No hay datos de reclasificación para mostrar.")
    
    elif page == "📊 Cuentas":
        st.header("📊 Análisis de Cuentas")
        
        # Procesar datos de cuentas
        cuentas_clean = cuentas.dropna(subset=[cuentas.columns[-1]]).iloc[1:]  # Remover header y filas sin datos
        
        if len(cuentas_clean) > 0:
            # Renombrar columnas basado en el análisis
            cuentas_clean.columns = ['ID', 'AREA', 'SUB_AREA', 'Responsable', 'Cuenta', 'Descripción', 'Merca', 'Col7', 'Col8', 'Mes', 'REAL']
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                areas_cuentas = ['Todas'] + list(cuentas_clean['AREA'].dropna().unique())
                selected_area = st.selectbox("Área", areas_cuentas)
            
            with col2:
                meses_cuentas = ['Todos'] + list(cuentas_clean['Mes'].dropna().unique())
                selected_mes = st.selectbox("Mes", meses_cuentas)
            
            with col3:
                responsables = ['Todos'] + list(cuentas_clean['Responsable'].dropna().unique())
                selected_resp = st.selectbox("Responsable", responsables)
            
            # Aplicar filtros
            filtered_cuentas = cuentas_clean.copy()
            if selected_area != 'Todas':
                filtered_cuentas = filtered_cuentas[filtered_cuentas['AREA'] == selected_area]
            if selected_mes != 'Todos':
                filtered_cuentas = filtered_cuentas[filtered_cuentas['Mes'] == selected_mes]
            if selected_resp != 'Todos':
                filtered_cuentas = filtered_cuentas[filtered_cuentas['Responsable'] == selected_resp]
            
            # Convertir REAL a numérico
            filtered_cuentas['REAL'] = pd.to_numeric(filtered_cuentas['REAL'], errors='coerce')
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Registros", len(filtered_cuentas))
            with col2:
                total_real = filtered_cuentas['REAL'].sum()
                st.metric("💰 Total Real", f"Q {total_real:,.2f}")
            with col3:
                areas_unicas = filtered_cuentas['AREA'].nunique()
                st.metric("🏢 Áreas Únicas", areas_unicas)
            with col4:
                promedio_real = filtered_cuentas['REAL'].mean()
                st.metric("📊 Promedio Real", f"Q {promedio_real:,.2f}")
            
            # Gráfica por área
            if len(filtered_cuentas) > 0:
                real_by_area = filtered_cuentas.groupby('AREA')['REAL'].sum()
                
                fig = px.pie(
                    values=real_by_area.values,
                    names=real_by_area.index,
                    title="Distribución de Valores Reales por Área",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Datos de Cuentas")
            display_cols = ['AREA', 'Responsable', 'Cuenta', 'Descripción', 'Mes', 'REAL']
            st.dataframe(filtered_cuentas[display_cols], use_container_width=True)
        else:
            st.warning("No hay datos de cuentas para mostrar.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Dashboard KSB - Presupuesto 2025** | Generado con Streamlit y Plotly")

if __name__ == "__main__":
    main()