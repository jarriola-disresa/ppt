import pandas as pd

def fix_resumen():
    """Verificar y corregir la lectura de la hoja Resumen"""
    
    file_path = "EXPORT KSB 1 ene a jun para ppto.xlsx"
    
    try:
        print("🔍 VERIFICANDO HOJA RESUMEN PARA CORRECCIÓN")
        print("="*50)
        
        resumen = pd.read_excel(file_path, sheet_name='Resumen')
        
        # Mostrar todas las filas para entender la estructura
        print("Todas las filas de Resumen:")
        for i in range(len(resumen)):
            row = resumen.iloc[i]
            area_name = row.iloc[1] if pd.notna(row.iloc[1]) else 'VACÍA'
            total_anual = row.iloc[14] if pd.notna(row.iloc[14]) else 'N/A'
            
            print(f"Fila {i}: {area_name} | Total anual: {total_anual}")
            
            # Si es la fila TOTAL, mostrar detalles
            if area_name == 'TOTAL':
                print(f"   🎯 FILA TOTAL ENCONTRADA:")
                print(f"      Total anual (Col 14): {total_anual}")
                print(f"      Ene: {row.iloc[2]}")
                print(f"      Feb: {row.iloc[3]}")
                print(f"      Mar: {row.iloc[4]}")
                print(f"      Abr: {row.iloc[5]}")
                print(f"      May: {row.iloc[6]}")
                print(f"      Jun: {row.iloc[7]}")
        
        print("\n✅ VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_resumen()