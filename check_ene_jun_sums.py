import pandas as pd
from pymongo import MongoClient

def check_ene_jun_sums():
    """Verificar las sumas de Ene-Jun área por área"""
    
    print("🔍 VERIFICANDO SUMAS ENE-JUN ÁREA POR ÁREA")
    print("="*60)
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    # ===== 1. EXCEL DIRECTO =====
    print("📋 1. SUMAS ENE-JUN DIRECTAS DEL EXCEL")
    print("-" * 40)
    
    resumen = pd.read_excel(file_path, sheet_name='Resumen')
    
    excel_sums = {}
    total_excel_ene_jun = 0
    
    # Verificar cada área (filas 2-10)
    for i in range(2, 11):
        row = resumen.iloc[i]
        area = row.iloc[1] if pd.notna(row.iloc[1]) else f"Fila_{i}"
        
        if pd.notna(row.iloc[1]) and area != '':
            # Calcular suma Ene-Jun manual
            ene_jun_values = []
            ene_jun_sum = 0
            
            for month_col in range(2, 8):  # Columnas Ene-Jun
                val = row.iloc[month_col] if pd.notna(row.iloc[month_col]) else 0
                try:
                    val_float = float(val)
                    ene_jun_values.append(val_float)
                    ene_jun_sum += val_float
                except:
                    ene_jun_values.append(0)
            
            excel_sums[area] = ene_jun_sum
            
            print(f"🏢 {area}:")
            print(f"   Ene: Q {ene_jun_values[0]:,.2f}")
            print(f"   Feb: Q {ene_jun_values[1]:,.2f}")
            print(f"   Mar: Q {ene_jun_values[2]:,.2f}")
            print(f"   Abr: Q {ene_jun_values[3]:,.2f}")
            print(f"   May: Q {ene_jun_values[4]:,.2f}")
            print(f"   Jun: Q {ene_jun_values[5]:,.2f}")
            print(f"   SUMA ENE-JUN: Q {ene_jun_sum:,.2f}")
            print()
            
            if area != 'TOTAL':
                total_excel_ene_jun += ene_jun_sum
    
    print(f"📊 TOTAL MANUAL (sin fila TOTAL): Q {total_excel_ene_jun:,.2f}")
    print(f"📊 FILA TOTAL EXCEL: Q {excel_sums.get('TOTAL', 0):,.2f}")
    print(f"📊 DIFERENCIA: Q {abs(total_excel_ene_jun - excel_sums.get('TOTAL', 0)):,.2f}")
    
    # ===== 2. MONGODB =====
    print(f"\n📊 2. VERIFICANDO MONGODB")
    print("-" * 40)
    
    try:
        mongo_uri = "mongodb+srv://jarriola:DISNEWERA@cluster0.nenkmp8.mongodb.net/"
        client = MongoClient(mongo_uri)
        db = client["ksb_presupuesto"]
        
        mongo_sums = {}
        
        # Obtener todas las áreas
        areas = db.resumen_presupuesto.distinct("area")
        
        for area in areas:
            # Obtener registros Ene-Jun para esta área
            records = list(db.resumen_presupuesto.find({
                "area": area,
                "mes": {"$in": ["enero", "febrero", "marzo", "abril", "mayo", "junio"]}
            }))
            
            monthly_values = {}
            total_ene_jun = 0
            
            for record in records:
                mes = record.get('mes', '')
                valor = record.get('presupuesto_mensual', 0)
                monthly_values[mes] = valor
                total_ene_jun += valor
            
            mongo_sums[area] = total_ene_jun
            
            print(f"🏢 {area} (MongoDB):")
            print(f"   Ene: Q {monthly_values.get('enero', 0):,.2f}")
            print(f"   Feb: Q {monthly_values.get('febrero', 0):,.2f}")
            print(f"   Mar: Q {monthly_values.get('marzo', 0):,.2f}")
            print(f"   Abr: Q {monthly_values.get('abril', 0):,.2f}")
            print(f"   May: Q {monthly_values.get('mayo', 0):,.2f}")
            print(f"   Jun: Q {monthly_values.get('junio', 0):,.2f}")
            print(f"   SUMA ENE-JUN: Q {total_ene_jun:,.2f}")
            print()
        
        # ===== 3. COMPARACIÓN =====
        print(f"\n🔍 3. COMPARACIÓN EXCEL vs MONGODB")
        print("-" * 40)
        
        for area in excel_sums.keys():
            excel_val = excel_sums.get(area, 0)
            mongo_val = mongo_sums.get(area, 0)
            diff = abs(excel_val - mongo_val)
            
            status = "✅" if diff < 1 else "❌"
            print(f"{status} {area}:")
            print(f"   Excel: Q {excel_val:,.2f}")
            print(f"   MongoDB: Q {mongo_val:,.2f}")
            print(f"   Diferencia: Q {diff:,.2f}")
            print()
        
        # ===== 4. VERIFICAR DASHBOARD LOGIC =====
        print(f"\n📊 4. LÓGICA DEL DASHBOARD")
        print("-" * 40)
        
        # Simular lo que hace create_resumen_charts_mongo
        resumen_df = pd.DataFrame(list(db.resumen_presupuesto.find()))
        
        if not resumen_df.empty:
            pivot_data = resumen_df.pivot_table(
                values='presupuesto_mensual',
                index='area',
                columns='mes',
                aggfunc='sum',
                fill_value=0
            )
            
            month_order = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio']
            available_months = [month for month in month_order if month in pivot_data.columns]
            
            if available_months:
                pivot_data_filtered = pivot_data[available_months]
                total_by_area = pivot_data_filtered.sum(axis=1)
                
                print("Dashboard calculará:")
                for area, total in total_by_area.items():
                    print(f"   {area}: Q {total:,.2f}")
                
                dashboard_total = total_by_area.sum()
                print(f"\nDashboard Total Ene-Jun: Q {dashboard_total:,.2f}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error MongoDB: {e}")

if __name__ == "__main__":
    check_ene_jun_sums()