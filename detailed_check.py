import pandas as pd
import numpy as np

def detailed_excel_check():
    """Revisar detalladamente todas las hojas para encontrar el presupuesto de 25 millones"""
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    try:
        print("🔍 BÚSQUEDA DETALLADA DEL PRESUPUESTO DE 25 MILLONES")
        print("="*60)
        
        # Obtener todas las hojas
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"📋 Hojas disponibles: {sheet_names}")
        
        for sheet_name in sheet_names:
            print(f"\n📊 ANALIZANDO HOJA: {sheet_name}")
            print("-" * 40)
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Dimensiones: {df.shape}")
            
            # Buscar valores grandes (cerca de 25 millones)
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) > 0:
                print(f"Columnas numéricas: {list(numeric_columns)}")
                
                for col in numeric_columns:
                    max_val = df[col].max()
                    sum_val = df[col].sum()
                    
                    # Buscar valores grandes
                    if max_val > 1000000:  # Mayor a 1 millón
                        print(f"   📈 {col}:")
                        print(f"      Máximo: Q {max_val:,.2f}")
                        print(f"      Suma total: Q {sum_val:,.2f}")
                        
                        # Mostrar valores únicos grandes
                        large_values = df[df[col] > 1000000][col].unique()
                        if len(large_values) > 0:
                            print(f"      Valores > 1M: {[f'Q {v:,.2f}' for v in large_values[:10]]}")
                        
                        # Verificar si la suma está cerca de 25 millones
                        if 20000000 <= sum_val <= 30000000:
                            print(f"   🎯 POSIBLE PRESUPUESTO DE ~25M: Q {sum_val:,.2f}")
            
            # Buscar texto que mencione totales o presupuestos
            text_columns = df.select_dtypes(include=['object']).columns
            for col in text_columns:
                if df[col].dtype == 'object':
                    text_values = df[col].dropna().astype(str)
                    total_mentions = text_values[text_values.str.contains('total|Total|TOTAL|presupuesto|Presupuesto|PRESUPUESTO', case=False, na=False)]
                    
                    if len(total_mentions) > 0:
                        print(f"   📝 Menciones de 'total/presupuesto' en {col}:")
                        for mention in total_mentions.unique()[:5]:
                            print(f"      - {mention}")
        
        # Análisis específico de RESUMEN
        print(f"\n🎯 ANÁLISIS ESPECÍFICO DE RESUMEN")
        print("-" * 40)
        
        resumen = pd.read_excel(file_path, sheet_name='Resumen')
        
        # Buscar todas las filas con datos numéricos
        print("Filas con totales significativos:")
        for i in range(len(resumen)):
            row = resumen.iloc[i]
            numeric_values = []
            
            for j, val in enumerate(row):
                if pd.notna(val) and isinstance(val, (int, float)) and val > 1000000:
                    numeric_values.append(f"Col{j}: Q {val:,.2f}")
            
            if numeric_values:
                area_name = row.iloc[1] if pd.notna(row.iloc[1]) else f"Fila {i}"
                print(f"   {area_name}: {' | '.join(numeric_values)}")
        
        # Calcular total de todas las áreas
        print(f"\n💰 CÁLCULO TOTAL DE TODAS LAS ÁREAS:")
        data_rows = resumen.iloc[2:10]  # Ampliar rango para asegurar
        
        total_anual_general = 0
        total_ene_jun_general = 0
        
        for idx, row in data_rows.iterrows():
            if pd.notna(row.iloc[1]) and isinstance(row.iloc[1], str) and row.iloc[1] != 'AREA':
                area = row.iloc[1]
                
                # Total anual (columna 14)
                total_anual = row.iloc[14] if pd.notna(row.iloc[14]) else 0
                total_anual_general += total_anual
                
                # Total enero-junio
                ene_jun = []
                for i in range(2, 8):  # Columnas enero-junio
                    val = row.iloc[i] if pd.notna(row.iloc[i]) else 0
                    ene_jun.append(val)
                
                total_ene_jun = sum(ene_jun)
                total_ene_jun_general += total_ene_jun
                
                print(f"   {area}:")
                print(f"      Ene-Jun: Q {total_ene_jun:,.2f}")
                print(f"      Anual: Q {total_anual:,.2f}")
        
        print(f"\n🎯 TOTALES GENERALES:")
        print(f"   Total Ene-Jun todas las áreas: Q {total_ene_jun_general:,.2f}")
        print(f"   Total Anual todas las áreas: Q {total_anual_general:,.2f}")
        
        if 20000000 <= total_anual_general <= 30000000:
            print(f"   ✅ ENCONTRADO: El presupuesto de ~25M es Q {total_anual_general:,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    detailed_excel_check()