import pandas as pd
import numpy as np

def check_excel_numbers():
    """Verificar los números del Excel y comparar con lo que está en MongoDB"""
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"  # Archivo en la misma carpeta
    
    try:
        print("🔍 VERIFICANDO NÚMEROS DEL EXCEL")
        print("="*50)
        
        # Cargar hoja Resumen
        print("\n📊 HOJA RESUMEN:")
        resumen = pd.read_excel(file_path, sheet_name='Resumen')
        
        # Mostrar estructura de resumen
        print("Primeras 10 filas de Resumen:")
        for i in range(min(10, len(resumen))):
            row_values = []
            for j, val in enumerate(resumen.iloc[i]):
                if pd.notna(val):
                    row_values.append(f"Col{j}: {val}")
            print(f"Fila {i}: {' | '.join(row_values) if row_values else 'VACÍA'}")
        
        # Verificar totales por área
        print("\n📈 ANÁLISIS DE ÁREAS Y TOTALES:")
        data_rows = resumen.iloc[2:9]  # Filas con datos de áreas
        
        for idx, row in data_rows.iterrows():
            if pd.notna(row.iloc[1]) and row.iloc[1] != 'AREA':
                area = row.iloc[1]
                
                # Valores mensuales (enero a junio)
                ene_jun_values = []
                for i in range(2, 8):  # Columnas enero-junio
                    val = row.iloc[i] if pd.notna(row.iloc[i]) else 0
                    ene_jun_values.append(val)
                
                total_ene_jun = sum(ene_jun_values)
                total_anual = row.iloc[14] if pd.notna(row.iloc[14]) else 0
                freeze = row.iloc[15] if pd.notna(row.iloc[15]) else 0
                
                print(f"\n🏢 {area}:")
                print(f"   Ene-Jun individual: {ene_jun_values}")
                print(f"   Total Ene-Jun: Q {total_ene_jun:,.2f}")
                print(f"   Total Anual: Q {total_anual:,.2f}")
                print(f"   Freeze: Q {freeze:,.2f}")
        
        # Cargar hoja PPTO
        print("\n\n📊 HOJA PPTO:")
        ppto = pd.read_excel(file_path, sheet_name='PPTO')
        
        print("Estructura de PPTO (filas 0-10):")
        for i in range(min(11, len(ppto))):
            row_values = []
            for j, val in enumerate(ppto.iloc[i]):
                if pd.notna(val):
                    row_values.append(f"Col{j}: {val}")
            print(f"Fila {i}: {' | '.join(row_values) if row_values else 'VACÍA'}")
        
        # Verificar totales de PPTO
        print("\n📈 ANÁLISIS DE TOTALES PPTO:")
        total_ppto = 0
        
        for i in range(5, len(ppto)):
            row = ppto.iloc[i]
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[12]):  # Si hay centro de coste y total
                centro = str(int(row.iloc[1])) if pd.notna(row.iloc[1]) else ''
                denominacion = row.iloc[2] if pd.notna(row.iloc[2]) else ''
                total_row = row.iloc[12] if pd.notna(row.iloc[12]) else 0
                total_ppto += total_row
                
                # Mostrar solo los primeros 5 para no saturar
                if i <= 9:
                    print(f"   {centro} - {denominacion}: Q {total_row:,.2f}")
        
        print(f"\n💰 TOTAL GENERAL PPTO: Q {total_ppto:,.2f}")
        
        # Verificar última fila que debería tener el total
        last_row = ppto.iloc[-1]
        if 'Total general' in str(last_row.iloc[0]):
            total_excel = last_row.iloc[12] if pd.notna(last_row.iloc[12]) else 0
            print(f"💰 TOTAL SEGÚN EXCEL (última fila): Q {total_excel:,.2f}")
        
        # Cargar hoja Data para verificar transacciones
        print("\n\n📊 HOJA DATA (TRANSACCIONES):")
        data = pd.read_excel(file_path, sheet_name='Data')
        
        total_transacciones = data['Valor/Moneda objeto'].sum() if 'Valor/Moneda objeto' in data.columns else 0
        count_transacciones = len(data)
        
        print(f"📋 Total registros: {count_transacciones}")
        print(f"💰 Total valor transacciones: Q {total_transacciones:,.2f}")
        
        # Verificar por mes
        if 'Fe.contabilización' in data.columns:
            data['Fe.contabilización'] = pd.to_datetime(data['Fe.contabilización'], errors='coerce')
            data['mes'] = data['Fe.contabilización'].dt.strftime('%B').str.lower()
            
            monthly_totals = data.groupby('mes')['Valor/Moneda objeto'].sum()
            print("\n📅 Totales por mes:")
            for mes, total in monthly_totals.items():
                print(f"   {mes.capitalize()}: Q {total:,.2f}")
        
        print("\n" + "="*50)
        print("✅ VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_excel_numbers()