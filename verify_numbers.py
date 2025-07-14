import pandas as pd
from pymongo import MongoClient

def verify_dashboard_numbers():
    """Verificar que los números del dashboard coincidan exactamente con el Excel"""
    
    print("🔍 VERIFICANDO NÚMEROS DASHBOARD VS EXCEL")
    print("="*60)
    
    # 1. VERIFICAR EXCEL DIRECTAMENTE
    print("📊 NÚMEROS DIRECTOS DEL EXCEL:")
    print("-" * 30)
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    resumen = pd.read_excel(file_path, sheet_name='Resumen')
    
    # Mostrar totales reales del Excel
    print("Fila TOTAL (fila 10):")
    total_row = resumen.iloc[10]
    print(f"   Área: {total_row.iloc[1]}")
    print(f"   Ene: Q {total_row.iloc[2]:,.2f}")
    print(f"   Feb: Q {total_row.iloc[3]:,.2f}")
    print(f"   Mar: Q {total_row.iloc[4]:,.2f}")
    print(f"   Abr: Q {total_row.iloc[5]:,.2f}")
    print(f"   May: Q {total_row.iloc[6]:,.2f}")
    print(f"   Jun: Q {total_row.iloc[7]:,.2f}")
    print(f"   Total Anual: Q {total_row.iloc[14]:,.2f}")
    
    # Calcular Ene-Jun del Excel
    ene_jun_excel = sum([
        total_row.iloc[2], total_row.iloc[3], total_row.iloc[4],
        total_row.iloc[5], total_row.iloc[6], total_row.iloc[7]
    ])
    print(f"   ✅ TOTAL ENE-JUN EXCEL: Q {ene_jun_excel:,.2f}")
    
    # 2. VERIFICAR MONGODB
    print(f"\n📊 NÚMEROS EN MONGODB:")
    print("-" * 30)
    
    try:
        mongo_uri = "mongodb+srv://jarriola:DISNEWERA@cluster0.nenkmp8.mongodb.net/"
        client = MongoClient(mongo_uri)
        db = client["ksb_presupuesto"]
        
        # Buscar fila TOTAL en MongoDB
        total_records = list(db.resumen_presupuesto.find({"area": "TOTAL"}))
        
        if total_records:
            print(f"Registros TOTAL encontrados: {len(total_records)}")
            
            # Calcular total por mes
            monthly_totals = {}
            total_anual_mongo = 0
            
            for record in total_records:
                mes = record.get('mes', '')
                valor = record.get('presupuesto_mensual', 0)
                total_anual_mongo = record.get('total_anual', 0)
                
                monthly_totals[mes] = valor
                print(f"   {mes.capitalize()}: Q {valor:,.2f}")
            
            print(f"   Total Anual MongoDB: Q {total_anual_mongo:,.2f}")
            
            # Calcular Ene-Jun de MongoDB
            ene_jun_mongo = sum([
                monthly_totals.get('enero', 0),
                monthly_totals.get('febrero', 0),
                monthly_totals.get('marzo', 0),
                monthly_totals.get('abril', 0),
                monthly_totals.get('mayo', 0),
                monthly_totals.get('junio', 0)
            ])
            print(f"   ✅ TOTAL ENE-JUN MONGODB: Q {ene_jun_mongo:,.2f}")
            
            # 3. COMPARAR
            print(f"\n🔍 COMPARACIÓN:")
            print("-" * 30)
            print(f"Excel Ene-Jun:   Q {ene_jun_excel:,.2f}")
            print(f"MongoDB Ene-Jun: Q {ene_jun_mongo:,.2f}")
            print(f"Diferencia:      Q {abs(ene_jun_excel - ene_jun_mongo):,.2f}")
            
            if abs(ene_jun_excel - ene_jun_mongo) < 1:
                print("✅ NÚMEROS COINCIDEN")
            else:
                print("❌ NÚMEROS NO COINCIDEN")
                
            print(f"\nExcel Total Anual:   Q {total_row.iloc[14]:,.2f}")
            print(f"MongoDB Total Anual: Q {total_anual_mongo:,.2f}")
            
        else:
            print("❌ No se encontró fila TOTAL en MongoDB")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
    
    # 4. VERIFICAR OTRAS HOJAS
    print(f"\n📊 VERIFICAR OTRAS HOJAS:")
    print("-" * 30)
    
    # PPTO
    ppto = pd.read_excel(file_path, sheet_name='PPTO')
    total_ppto_excel = ppto.iloc[-1, 12] if len(ppto) > 0 else 0
    print(f"PPTO Total (Excel): Q {total_ppto_excel:,.2f}")
    
    # DATA  
    data = pd.read_excel(file_path, sheet_name='Data')
    total_data_excel = data['Valor/Moneda objeto'].sum()
    print(f"DATA Total (Excel): Q {total_data_excel:,.2f}")
    
    print(f"\n✅ VERIFICACIÓN COMPLETADA")

if __name__ == "__main__":
    verify_dashboard_numbers()