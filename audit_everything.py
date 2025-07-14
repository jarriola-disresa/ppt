import pandas as pd
from pymongo import MongoClient

def audit_everything():
    """Auditoría completa de TODOS los números - Excel vs MongoDB vs Dashboard"""
    
    print("🔍 AUDITORÍA COMPLETA - VERIFICANDO TODO")
    print("="*60)
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    # ===== 1. EXCEL RAW DATA =====
    print("📋 1. DATOS EXACTOS DEL EXCEL (SIN PROCESAR)")
    print("-" * 40)
    
    # Cargar hoja Resumen
    resumen = pd.read_excel(file_path, sheet_name='Resumen')
    
    print("TODAS las filas con totales importantes:")
    for i in range(len(resumen)):
        row = resumen.iloc[i]
        area = row.iloc[1] if pd.notna(row.iloc[1]) else f"Fila_{i}"
        total_col14 = row.iloc[14] if pd.notna(row.iloc[14]) else 0
        
        # Mostrar solo filas con totales significativos
        if pd.notna(total_col14) and isinstance(total_col14, (int, float)) and total_col14 > 1000000:  # Mayor a 1 millón
            ene_jun_sum = 0
            monthly_values = []
            
            for month_idx in range(2, 8):  # Ene-Jun
                val = row.iloc[month_idx] if pd.notna(row.iloc[month_idx]) else 0
                monthly_values.append(val)
                ene_jun_sum += val
            
            print(f"\n🏢 {area} (Fila {i}):")
            print(f"   Valores Ene-Jun: {[f'Q{v:,.0f}' for v in monthly_values]}")
            print(f"   Suma Ene-Jun: Q {ene_jun_sum:,.2f}")
            print(f"   Total Anual (Col 14): Q {total_col14:,.2f}")
    
    # ===== 2. CÁLCULO MANUAL TOTAL =====
    print(f"\n📊 2. CÁLCULO MANUAL DEL TOTAL")
    print("-" * 40)
    
    # Sumar TODAS las áreas (filas 2-9)
    total_manual_ene_jun = 0
    total_manual_anual = 0
    
    print("Sumando área por área:")
    for i in range(2, 10):  # Filas de áreas (sin TOTAL)
        row = resumen.iloc[i]
        area = row.iloc[1] if pd.notna(row.iloc[1]) else f"Fila_{i}"
        
        if area != 'TOTAL':  # Excluir la fila TOTAL para evitar doble conteo
            # Ene-Jun
            ene_jun = sum([row.iloc[j] if pd.notna(row.iloc[j]) else 0 for j in range(2, 8)])
            anual = row.iloc[14] if pd.notna(row.iloc[14]) else 0
            
            total_manual_ene_jun += ene_jun
            total_manual_anual += anual
            
            print(f"   {area}: Ene-Jun Q{ene_jun:,.0f} | Anual Q{anual:,.0f}")
    
    print(f"\n🧮 TOTAL CALCULADO MANUALMENTE:")
    print(f"   Ene-Jun: Q {total_manual_ene_jun:,.2f}")
    print(f"   Anual: Q {total_manual_anual:,.2f}")
    
    # Comparar con fila TOTAL del Excel
    total_row = resumen.iloc[10]  # Fila TOTAL
    excel_total_ene_jun = sum([total_row.iloc[j] if pd.notna(total_row.iloc[j]) else 0 for j in range(2, 8)])
    excel_total_anual = total_row.iloc[14] if pd.notna(total_row.iloc[14]) else 0
    
    print(f"\n📋 FILA TOTAL DEL EXCEL:")
    print(f"   Ene-Jun: Q {excel_total_ene_jun:,.2f}")
    print(f"   Anual: Q {excel_total_anual:,.2f}")
    
    print(f"\n🔍 COMPARACIÓN:")
    diff_ene_jun = abs(total_manual_ene_jun - excel_total_ene_jun)
    diff_anual = abs(total_manual_anual - excel_total_anual)
    
    print(f"   Diferencia Ene-Jun: Q {diff_ene_jun:,.2f}")
    print(f"   Diferencia Anual: Q {diff_anual:,.2f}")
    
    if diff_ene_jun < 1 and diff_anual < 1:
        print("   ✅ EXCEL INTERNAMENTE CONSISTENTE")
    else:
        print("   ❌ EXCEL TIENE INCONSISTENCIAS INTERNAS")
    
    # ===== 3. VERIFICAR MONGODB =====
    print(f"\n📊 3. VERIFICANDO MONGODB")
    print("-" * 40)
    
    try:
        mongo_uri = "mongodb+srv://jarriola:DISNEWERA@cluster0.nenkmp8.mongodb.net/"
        client = MongoClient(mongo_uri)
        db = client["ksb_presupuesto"]
        
        # Verificar fila TOTAL
        total_records = list(db.resumen_presupuesto.find({"area": "TOTAL"}))
        if total_records:
            mongo_ene_jun = sum([
                r.get('presupuesto_mensual', 0) for r in total_records 
                if r.get('mes') in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio']
            ])
            mongo_anual = total_records[0].get('total_anual', 0)
            
            print(f"MongoDB TOTAL:")
            print(f"   Ene-Jun: Q {mongo_ene_jun:,.2f}")
            print(f"   Anual: Q {mongo_anual:,.2f}")
            
            # Comparar Excel vs MongoDB
            print(f"\n🔍 EXCEL vs MONGODB:")
            print(f"   Ene-Jun - Excel: Q {excel_total_ene_jun:,.2f} | MongoDB: Q {mongo_ene_jun:,.2f}")
            print(f"   Anual - Excel: Q {excel_total_anual:,.2f} | MongoDB: Q {mongo_anual:,.2f}")
            
            if abs(excel_total_ene_jun - mongo_ene_jun) < 1 and abs(excel_total_anual - mongo_anual) < 1:
                print("   ✅ EXCEL Y MONGODB COINCIDEN")
            else:
                print("   ❌ EXCEL Y MONGODB NO COINCIDEN")
        
        # Verificar todas las áreas individualmente
        print(f"\n📋 VERIFICANDO CADA ÁREA:")
        areas_excel = {}
        for i in range(2, 10):
            row = resumen.iloc[i]
            area = row.iloc[1] if pd.notna(row.iloc[1]) else f"Fila_{i}"
            if area != 'TOTAL':
                ene_jun = sum([row.iloc[j] if pd.notna(row.iloc[j]) else 0 for j in range(2, 8)])
                areas_excel[area] = ene_jun
        
        for area, excel_value in areas_excel.items():
            mongo_records = list(db.resumen_presupuesto.find({"area": area}))
            mongo_value = sum([
                r.get('presupuesto_mensual', 0) for r in mongo_records 
                if r.get('mes') in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio']
            ])
            
            diff = abs(excel_value - mongo_value)
            status = "✅" if diff < 1 else "❌"
            print(f"   {status} {area}: Excel Q{excel_value:,.0f} | MongoDB Q{mongo_value:,.0f}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error MongoDB: {e}")
    
    # ===== 4. VERIFICAR OTRAS HOJAS =====
    print(f"\n📊 4. VERIFICANDO OTRAS HOJAS")
    print("-" * 40)
    
    # PPTO
    ppto = pd.read_excel(file_path, sheet_name='PPTO')
    ppto_total = ppto.iloc[-1, 12] if len(ppto) > 0 else 0
    print(f"PPTO Total: Q {ppto_total:,.2f}")
    
    # DATA
    data = pd.read_excel(file_path, sheet_name='Data')
    data_total = data['Valor/Moneda objeto'].sum()
    print(f"DATA Total: Q {data_total:,.2f}")
    
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   Resumen Total: Q {excel_total_anual:,.2f}")
    print(f"   PPTO Total: Q {ppto_total:,.2f}")
    print(f"   DATA Total: Q {data_total:,.2f}")
    
    print(f"\n✅ AUDITORÍA COMPLETADA")

if __name__ == "__main__":
    audit_everything()