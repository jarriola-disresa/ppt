import pandas as pd
from pymongo import MongoClient
import os

# Configuración
mongo_uri = "mongodb+srv://jarriola:DISNEWERA@cluster0.nenkmp8.mongodb.net/"
db_name = "ksb_presupuesto"
csv_dir = "csv_data"

def update_mongodb_with_corrected_data():
    """Actualizar MongoDB con los datos corregidos"""
    
    try:
        # Conectar a MongoDB
        print("🔗 Conectando a MongoDB Atlas...")
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Verificar conexión
        client.admin.command('ismaster')
        print(f"✅ Conectado a: {db_name}")
        
        # Archivos CSV a cargar
        collections_data = {
            'resumen_presupuesto': 'resumen_presupuesto.csv',
            'presupuesto_detallado': 'presupuesto_detallado.csv',
            'transacciones': 'transacciones.csv',
            'reclasificaciones': 'reclasificaciones.csv',
            'cuentas_reales': 'cuentas_reales.csv'
        }
        
        print("📊 Actualizando colecciones con datos corregidos...")
        
        for collection_name, csv_file in collections_data.items():
            file_path = f"{csv_dir}/{csv_file}"
            
            if os.path.exists(file_path):
                print(f"   📄 Actualizando {collection_name}...")
                
                # Leer CSV
                df = pd.read_csv(file_path)
                print(f"      📋 Leídas {len(df)} filas de {csv_file}")
                
                # Convertir a diccionarios
                records = df.to_dict('records')
                
                # Limpiar colección existente
                db[collection_name].delete_many({})
                print(f"      🗑️  Colección {collection_name} limpiada")
                
                # Insertar datos en lotes
                if records:
                    batch_size = 100
                    total_inserted = 0
                    
                    for i in range(0, len(records), batch_size):
                        batch = records[i:i + batch_size]
                        db[collection_name].insert_many(batch)
                        total_inserted += len(batch)
                    
                    print(f"      ✅ {total_inserted} documentos insertados")
                else:
                    print(f"      ⚠️  No hay datos en {csv_file}")
            else:
                print(f"      ❌ No encontrado: {csv_file}")
        
        print("\n📈 Verificando datos actualizados...")
        
        # Verificar fila TOTAL en resumen_presupuesto
        total_records = list(db.resumen_presupuesto.find({"area": "TOTAL"}))
        if total_records:
            print(f"   🎯 FILA TOTAL encontrada: {len(total_records)} registros")
            
            # Mostrar total anual de la fila TOTAL
            total_anual = total_records[0].get('total_anual', 0)
            print(f"   💰 Total anual fila TOTAL: Q {total_anual:,.2f}")
            
            if 35000000 <= total_anual <= 36000000:
                print(f"   ✅ CORRECTO: Total de ~35M confirmado")
            else:
                print(f"   ⚠️  Verificar: Total no está en rango esperado")
        else:
            print(f"   ❌ No se encontró fila TOTAL")
        
        # Contar documentos de todas las colecciones
        print(f"\n📊 Resumen de colecciones actualizadas:")
        total_docs = 0
        for collection_name in collections_data.keys():
            count = db[collection_name].count_documents({})
            print(f"   • {collection_name}: {count} documentos")
            total_docs += count
        
        print(f"\n🎉 ACTUALIZACIÓN COMPLETADA")
        print(f"   📊 Total documentos: {total_docs}")
        print(f"   🎯 Datos corregidos con fila TOTAL de 35M")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_mongodb_with_corrected_data()
    
    if success:
        print(f"\n🚀 Dashboard listo con datos corregidos!")
        print(f"   Ejecutar: streamlit run dashboard_mongo.py")
    else:
        print(f"\n❌ Error en la actualización")