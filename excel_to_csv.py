import pandas as pd
import numpy as np
from datetime import datetime
import os

def process_excel_to_csv():
    """Procesar Excel y convertir a archivos CSV para MongoDB"""
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    # Crear directorio para CSVs
    csv_dir = "csv_data"
    os.makedirs(csv_dir, exist_ok=True)
    
    # Cargar todas las hojas
    print("Cargando datos del Excel...")
    resumen = pd.read_excel(file_path, sheet_name='Resumen')
    ppto = pd.read_excel(file_path, sheet_name='PPTO')
    data = pd.read_excel(file_path, sheet_name='Data')
    reclasificacion = pd.read_excel(file_path, sheet_name='Reclasificación de gastos')
    cuentas = pd.read_excel(file_path, sheet_name='Cuentas')
    
    # ========== PROCESAR RESUMEN ==========
    print("Procesando hoja Resumen...")
    resumen_list = []
    
    # Extraer datos de presupuesto por área y mes (filas 2-10, incluyendo TOTAL)
    data_rows = resumen.iloc[2:11]  # Filas 2-10 (incluye fila TOTAL)
    months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    for idx, row in data_rows.iterrows():
        area_name = row.iloc[1] if pd.notna(row.iloc[1]) else ''
        
        # Incluir solo áreas con datos válidos (excluyendo headers)
        if pd.notna(row.iloc[1]) and area_name != 'AREA' and area_name != '':
            area = str(area_name).strip()
            
            # Crear un registro por mes
            for i, month in enumerate(months):
                value = row.iloc[i + 2] if pd.notna(row.iloc[i + 2]) else 0
                total_anual = row.iloc[14] if pd.notna(row.iloc[14]) else 0
                freeze = row.iloc[15] if pd.notna(row.iloc[15]) else 0
                
                # Convertir valores a float de forma segura
                try:
                    value_float = float(value) if pd.notna(value) else 0
                    total_anual_float = float(total_anual) if pd.notna(total_anual) else 0
                    freeze_float = float(freeze) if pd.notna(freeze) else 0
                    
                    resumen_list.append({
                        'area': area,
                        'mes': month,
                        'year': 2025,
                        'presupuesto_mensual': value_float,
                        'total_anual': total_anual_float,
                        'freeze': freeze_float,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'EXPORT KSB 1 ene a jun para ppto.xlsx'
                    })
                except (ValueError, TypeError):
                    # En caso de error, usar 0
                    resumen_list.append({
                        'area': area,
                        'mes': month,
                        'year': 2025,
                        'presupuesto_mensual': 0,
                        'total_anual': 0,
                        'freeze': 0,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'EXPORT KSB 1 ene a jun para ppto.xlsx'
                    })
    
    resumen_df = pd.DataFrame(resumen_list)
    resumen_df.to_csv(f"{csv_dir}/resumen_presupuesto.csv", index=False, encoding='utf-8')
    print(f"✅ Guardado: resumen_presupuesto.csv ({len(resumen_df)} filas)")
    
    # ========== PROCESAR PPTO ==========
    print("Procesando hoja PPTO...")
    ppto_list = []
    
    for i in range(5, len(ppto)):
        row = ppto.iloc[i]
        if pd.notna(row.iloc[1]):  # Si hay centro de coste
            
            # Crear un registro por mes
            months_data = {
                'enero': row.iloc[6],
                'febrero': row.iloc[7], 
                'marzo': row.iloc[8],
                'abril': row.iloc[9],
                'mayo': row.iloc[10],
                'junio': row.iloc[11]
            }
            
            for month, value in months_data.items():
                if pd.notna(value) and value != 0:
                    ppto_list.append({
                        'moneda': row.iloc[0] if pd.notna(row.iloc[0]) else 'GTQ',
                        'centro_coste': str(int(row.iloc[1])) if pd.notna(row.iloc[1]) else '',
                        'denominacion_objeto': row.iloc[2] if pd.notna(row.iloc[2]) else '',
                        'mes': month,
                        'presupuesto': float(value),
                        'total_anual': float(row.iloc[12]) if pd.notna(row.iloc[12]) else 0,
                        'year': 2025,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'EXPORT KSB 1 ene a jun para ppto.xlsx'
                    })
    
    ppto_df = pd.DataFrame(ppto_list)
    ppto_df.to_csv(f"{csv_dir}/presupuesto_detallado.csv", index=False, encoding='utf-8')
    print(f"✅ Guardado: presupuesto_detallado.csv ({len(ppto_df)} filas)")
    
    # ========== PROCESAR DATA ==========
    print("Procesando hoja Data...")
    
    # Limpiar y preparar datos
    data_clean = data.copy()
    
    # Convertir fechas
    if 'Fe.contabilización' in data_clean.columns:
        data_clean['Fe.contabilización'] = pd.to_datetime(data_clean['Fe.contabilización'], errors='coerce')
        data_clean['fecha_contabilizacion'] = data_clean['Fe.contabilización'].dt.strftime('%Y-%m-%d')
        data_clean['mes'] = data_clean['Fe.contabilización'].dt.strftime('%B').str.lower()
        data_clean['año'] = data_clean['Fe.contabilización'].dt.year
    
    # Seleccionar y renombrar columnas principales
    columns_mapping = {
        'Centro de coste': 'centro_coste',
        'Clase de coste': 'clase_coste',
        'Denom.clase de coste': 'denom_clase_coste',
        'Nº docum.refer.': 'num_documento',
        'Valor/Moneda objeto': 'valor_moneda_objeto',
        'Moneda del objeto': 'moneda_objeto',
        'Texto de cabecera de documento': 'texto_cabecera',
        'Documento compras': 'documento_compras',
        'Usuario': 'usuario',
        'Ejercicio': 'ejercicio',
        'Denominación del objeto': 'denominacion_objeto',
        'Descrip.clases coste': 'descrip_clases_coste',
        'Valor variable/MI': 'valor_variable_mi',
        'Merca': 'merca'
    }
    
    # Crear DataFrame final
    data_final = pd.DataFrame()
    for old_col, new_col in columns_mapping.items():
        if old_col in data_clean.columns:
            data_final[new_col] = data_clean[old_col]
    
    # Agregar columnas adicionales
    data_final['fecha_contabilizacion'] = data_clean.get('fecha_contabilizacion', '')
    data_final['mes'] = data_clean.get('mes', '')
    data_final['año'] = data_clean.get('año', 2025)
    data_final['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_final['source'] = 'EXPORT KSB 1 ene a jun para ppto.xlsx'
    
    # Limpiar NaN
    data_final = data_final.fillna('')
    
    data_final.to_csv(f"{csv_dir}/transacciones.csv", index=False, encoding='utf-8')
    print(f"✅ Guardado: transacciones.csv ({len(data_final)} filas)")
    
    # ========== PROCESAR RECLASIFICACIÓN ==========
    print("Procesando hoja Reclasificación...")
    
    # Procesar igual que data pero marcando como reclasificación
    reclasif_clean = reclasificacion.copy()
    
    # Convertir fechas
    if 'Fe.contabilización' in reclasif_clean.columns:
        reclasif_clean['Fe.contabilización'] = pd.to_datetime(reclasif_clean['Fe.contabilización'], errors='coerce')
        reclasif_clean['fecha_contabilizacion'] = reclasif_clean['Fe.contabilización'].dt.strftime('%Y-%m-%d')
        reclasif_clean['mes'] = reclasif_clean['Fe.contabilización'].dt.strftime('%B').str.lower()
        reclasif_clean['año'] = reclasif_clean['Fe.contabilización'].dt.year
    
    # Crear DataFrame final
    reclasif_final = pd.DataFrame()
    for old_col, new_col in columns_mapping.items():
        if old_col in reclasif_clean.columns:
            reclasif_final[new_col] = reclasif_clean[old_col]
    
    # Agregar columnas adicionales
    reclasif_final['fecha_contabilizacion'] = reclasif_clean.get('fecha_contabilizacion', '')
    reclasif_final['mes'] = reclasif_clean.get('mes', '')
    reclasif_final['año'] = reclasif_clean.get('año', 2025)
    reclasif_final['tipo_operacion'] = 'reclasificacion'
    reclasif_final['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reclasif_final['source'] = 'EXPORT KSB 1 ene a jun para ppto.xlsx'
    
    # Limpiar NaN
    reclasif_final = reclasif_final.fillna('')
    
    reclasif_final.to_csv(f"{csv_dir}/reclasificaciones.csv", index=False, encoding='utf-8')
    print(f"✅ Guardado: reclasificaciones.csv ({len(reclasif_final)} filas)")
    
    # ========== PROCESAR CUENTAS ==========
    print("Procesando hoja Cuentas...")
    
    # Limpiar datos de cuentas (remover headers)
    cuentas_clean = cuentas.dropna(subset=[cuentas.columns[-1]]).iloc[1:]
    
    cuentas_list = []
    for idx, row in cuentas_clean.iterrows():
        area = row.iloc[1] if pd.notna(row.iloc[1]) else ''
        sub_area = row.iloc[2] if pd.notna(row.iloc[2]) else ''
        responsable = row.iloc[3] if pd.notna(row.iloc[3]) else ''
        cuenta = str(int(row.iloc[4])) if pd.notna(row.iloc[4]) else ''
        descripcion = row.iloc[5] if pd.notna(row.iloc[5]) else ''
        merca = row.iloc[6] if pd.notna(row.iloc[6]) else ''
        mes = row.iloc[9] if pd.notna(row.iloc[9]) else ''
        valor_real = float(row.iloc[10]) if pd.notna(row.iloc[10]) else 0
        
        if area and mes:  # Solo si tiene área y mes
            cuentas_list.append({
                'area': area,
                'sub_area': sub_area,
                'responsable': responsable,
                'cuenta': cuenta,
                'descripcion_cuenta': descripcion,
                'merca': merca,
                'mes': mes.lower(),
                'valor_real': valor_real,
                'year': 2025,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'EXPORT KSB 1 ene a jun para ppto.xlsx'
            })
    
    cuentas_df = pd.DataFrame(cuentas_list)
    cuentas_df.to_csv(f"{csv_dir}/cuentas_reales.csv", index=False, encoding='utf-8')
    print(f"✅ Guardado: cuentas_reales.csv ({len(cuentas_df)} filas)")
    
    # ========== CREAR RESUMEN ==========
    print("Creando archivo de resumen...")
    
    summary = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_file': 'EXPORT KSB 1 ene a jun para ppto.xlsx',
        'output_directory': csv_dir,
        'files_generated': [
            {'filename': 'resumen_presupuesto.csv', 'rows': len(resumen_df), 'description': 'Presupuesto por área y mes'},
            {'filename': 'presupuesto_detallado.csv', 'rows': len(ppto_df), 'description': 'Presupuesto detallado por centro de coste'},
            {'filename': 'transacciones.csv', 'rows': len(data_final), 'description': 'Transacciones detalladas'},
            {'filename': 'reclasificaciones.csv', 'rows': len(reclasif_final), 'description': 'Reclasificaciones de gastos'},
            {'filename': 'cuentas_reales.csv', 'rows': len(cuentas_df), 'description': 'Valores reales por cuenta'}
        ]
    }
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(f"{csv_dir}/summary.csv", index=False, encoding='utf-8')
    
    print("\n" + "="*60)
    print("✅ PROCESAMIENTO CSV COMPLETADO")
    print("="*60)
    print(f"📁 Directorio: {csv_dir}")
    print("📊 Archivos CSV generados:")
    for file_info in summary['files_generated']:
        print(f"   • {file_info['filename']}: {file_info['rows']} filas - {file_info['description']}")
    print("   • summary.csv: Resumen de la generación")
    print("="*60)
    print("🔧 Para cargar en MongoDB:")
    print("   mongoimport --db ksb_budget --collection resumen_presupuesto --type csv --headerline --file resumen_presupuesto.csv")
    print("   mongoimport --db ksb_budget --collection presupuesto_detallado --type csv --headerline --file presupuesto_detallado.csv")
    print("   mongoimport --db ksb_budget --collection transacciones --type csv --headerline --file transacciones.csv")
    print("   mongoimport --db ksb_budget --collection reclasificaciones --type csv --headerline --file reclasificaciones.csv")
    print("   mongoimport --db ksb_budget --collection cuentas_reales --type csv --headerline --file cuentas_reales.csv")
    print("="*60)

if __name__ == "__main__":
    process_excel_to_csv()