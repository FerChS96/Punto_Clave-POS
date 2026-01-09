#!/usr/bin/env python3
"""
Script para insertar 50 productos de ejemplo en la base de datos
"""

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config
from decimal import Decimal
import psycopg2.extras

# Configuración
config = Config()
db = PostgresManager(config.get_postgres_config())

# Datos de ejemplo: codigo, barcode, nombre, descripcion, precio_venta, precio_mayoreo, cantidad_mayoreo, costo_promedio, es_inventariable
productos = [
    # Proteínas
    ("PROT001", "4580001234567", "Proteína Whey Vainilla 2kg", "Suplemento proteico premium", Decimal("45.99"), Decimal("40.00"), 5, Decimal("20.00"), True),
    ("PROT002", "4580001234568", "Proteína Whey Chocolate 2kg", "Suplemento proteico premium", Decimal("45.99"), Decimal("40.00"), 5, Decimal("20.00"), True),
    ("PROT003", "4580001234569", "Proteína Whey Fresa 2kg", "Suplemento proteico premium", Decimal("45.99"), Decimal("40.00"), 5, Decimal("20.00"), True),
    ("PROT004", "4580001234570", "Proteína Caseína 1kg", "Proteína de absorción lenta", Decimal("35.99"), Decimal("30.00"), 3, Decimal("15.00"), True),
    ("PROT005", "4580001234571", "Proteína Isolada 1kg", "Proteína sin lactosa", Decimal("55.99"), Decimal("50.00"), 8, Decimal("25.00"), True),
    
    # Creatina y aminoácidos
    ("CREA001", "4580002234567", "Creatina Monohidratada 300g", "Mejora la fuerza muscular", Decimal("19.99"), Decimal("17.00"), 3, Decimal("8.00"), True),
    ("BCAA001", "4580003234567", "BCAA 2:1:1 500g", "Aminoácidos ramificados", Decimal("29.99"), Decimal("25.00"), 4, Decimal("12.00"), True),
    ("BCAA002", "4580003234568", "Glutamina Pura 500g", "Aminoácido aislado", Decimal("24.99"), Decimal("20.00"), 3, Decimal("10.00"), True),
    ("CITR001", "4580004234567", "Citrulina Malato 250g", "Pre-entrenamiento", Decimal("22.99"), Decimal("19.00"), 3, Decimal("9.00"), True),
    ("BETA001", "4580005234567", "Beta-Alanina 250g", "Resistencia muscular", Decimal("19.99"), Decimal("17.00"), 2, Decimal("8.00"), True),
    
    # Pre-entrenamientos
    ("PREH001", "4580006234567", "Pre-Entreno Explosión 300g", "Energía y concentración", Decimal("32.99"), Decimal("28.00"), 5, Decimal("14.00"), True),
    ("PREH002", "4580006234568", "Pre-Entreno Premium 500g", "Fórmula avanzada", Decimal("49.99"), Decimal("45.00"), 7, Decimal("20.00"), True),
    ("CAFF001", "4580007234567", "Cafeína Pura 100 cápsulas", "Potenciador energético", Decimal("14.99"), Decimal("13.00"), 2, Decimal("5.00"), True),
    
    # Vitaminas y minerales
    ("VITM001", "4580008234567", "Multivitamínico 100 cápsulas", "Completo de vitaminas", Decimal("24.99"), Decimal("21.00"), 4, Decimal("10.00"), True),
    ("VITD001", "4580009234567", "Vitamina D3 5000 IU 120 cápsulas", "Salud ósea", Decimal("16.99"), Decimal("14.00"), 3, Decimal("6.00"), True),
    ("ZINC001", "4580010234567", "Zinc + Magnesio 100 cápsulas", "Mineral esencial", Decimal("18.99"), Decimal("16.00"), 2, Decimal("7.00"), True),
    
    # Equipos de entrenamiento
    ("EQUI001", "4580011234567", "Mancuerna Ajustable 10kg", "Par de mancuernas", Decimal("89.99"), Decimal("80.00"), 1, Decimal("30.00"), True),
    ("EQUI002", "4580011234568", "Mancuerna Ajustable 20kg", "Par de mancuernas", Decimal("149.99"), Decimal("135.00"), 1, Decimal("50.00"), True),
    ("EQUI003", "4580011234569", "Barra Olímpica 20kg", "Barra profesional", Decimal("199.99"), Decimal("180.00"), 1, Decimal("70.00"), True),
    ("EQUI004", "4580012234567", "Disco de Peso 20kg", "Para barra olímpica", Decimal("89.99"), Decimal("80.00"), 2, Decimal("35.00"), True),
    ("EQUI005", "4580012234568", "Disco de Peso 10kg", "Para barra olímpica", Decimal("49.99"), Decimal("45.00"), 2, Decimal("18.00"), True),
    
    # Accesorios
    ("ACCE001", "4580013234567", "Cinturón de Pesas Cuero", "Soporte lumbar", Decimal("34.99"), Decimal("30.00"), 1, Decimal("12.00"), True),
    ("ACCE002", "4580013234568", "Guantes de Levantamiento", "Protección de manos", Decimal("24.99"), Decimal("21.00"), 3, Decimal("9.00"), True),
    ("ACCE003", "4580014234567", "Muñequeras de Neopreno", "Soporte articular", Decimal("19.99"), Decimal("17.00"), 2, Decimal("7.00"), True),
    ("ACCE004", "4580014234568", "Rodilleras Profesionales", "Soporte rodillas", Decimal("29.99"), Decimal("26.00"), 2, Decimal("10.00"), True),
    ("ACCE005", "4580015234567", "Chalk Block (Magnesio)", "Agarre mejorado", Decimal("9.99"), Decimal("8.00"), 1, Decimal("3.00"), True),
    
    # Botellas y accesorios
    ("BOTE001", "4580016234567", "Botella Agua 1L Acero Inoxidable", "Aislada térmica", Decimal("34.99"), Decimal("30.00"), 2, Decimal("12.00"), True),
    ("BOTE002", "4580016234568", "Botella Agua 500ml Plástico", "Ligera y resistente", Decimal("12.99"), Decimal("11.00"), 1, Decimal("4.00"), True),
    ("SHAK001", "4580017234567", "Shaker Botella 600ml", "Mezcla proteínas", Decimal("14.99"), Decimal("13.00"), 2, Decimal("5.00"), True),
    
    # Recuperación
    ("RECO001", "4580018234567", "Gel Recuperador Muscular 500ml", "Masaje recuperativo", Decimal("22.99"), Decimal("20.00"), 2, Decimal("9.00"), True),
    ("RECO002", "4580018234568", "Bálsamo Calor 50ml", "Alivio muscular", Decimal("16.99"), Decimal("14.00"), 2, Decimal("6.00"), True),
    ("RECO003", "4580019234567", "Rollo Masaje Foam 45cm", "Auto-masaje", Decimal("29.99"), Decimal("26.00"), 2, Decimal("11.00"), True),
    
    # Snacks saludables
    ("SNAC001", "4580020234567", "Barrita Proteica Chocolate", "15g proteína por barra", Decimal("2.99"), Decimal("2.50"), 10, Decimal("0.80"), True),
    ("SNAC002", "4580020234568", "Barrita Proteica Almendras", "14g proteína por barra", Decimal("2.99"), Decimal("2.50"), 10, Decimal("0.80"), True),
    ("SNAC003", "4580021234567", "Mix de Nueces 250g", "Naturales sin sal", Decimal("12.99"), Decimal("11.00"), 3, Decimal("4.50"), True),
    ("SNAC004", "4580021234568", "Frutos Secos Mix 200g", "Energía natural", Decimal("11.99"), Decimal("10.00"), 2, Decimal("4.00"), True),
    
    # Ropa deportiva
    ("ROPA001", "4580022234567", "Camiseta Entrenamiento", "Tela transpirable", Decimal("29.99"), Decimal("26.00"), 3, Decimal("11.00"), True),
    ("ROPA002", "4580022234568", "Pantalón Deportivo", "Flexible y resistente", Decimal("39.99"), Decimal("35.00"), 2, Decimal("14.00"), True),
    ("ROPA003", "4580023234567", "Shorts Entrenamiento", "Secado rápido", Decimal("24.99"), Decimal("21.00"), 2, Decimal("9.00"), True),
    ("ROPA004", "4580023234568", "Sudadera Capucha", "Algodón premium", Decimal("49.99"), Decimal("45.00"), 2, Decimal("18.00"), True),
    
    # Accesorios electrónicos
    ("ELEC001", "4580024234567", "Banda Cardio Inteligente", "Monitor de ritmo cardíaco", Decimal("79.99"), Decimal("72.00"), 1, Decimal("30.00"), True),
    ("ELEC002", "4580024234568", "Reloj Deportivo GPS", "Seguimiento de actividad", Decimal("199.99"), Decimal("180.00"), 1, Decimal("70.00"), True),
    ("ELEC003", "4580025234567", "Auriculares Deportivos", "Impermeables Bluetooth", Decimal("79.99"), Decimal("72.00"), 1, Decimal("28.00"), True),
]

try:
    print("🔄 Conectando a la base de datos...")
    
    # Obtener conexión con RealDictCursor
    conn = db.connection
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Obtener ubicaciones disponibles
    cursor.execute("SELECT id_ubicacion, nombre FROM ca_ubicaciones WHERE activa = TRUE LIMIT 1")
    ubicacion = cursor.fetchone()
    
    if not ubicacion:
        print("❌ No hay ubicaciones disponibles. Crea una ubicación primero.")
        cursor.close()
        sys.exit(1)
    
    ubicacion_id = ubicacion['id_ubicacion']
    print(f"✓ Usando ubicación: {ubicacion['nombre']}")
    print(f"\n🆕 Insertando {len(productos)} productos de ejemplo...\n")
    
    insertados = 0
    
    for codigo, barcode, nombre, descripcion, precio_venta, precio_mayoreo, cantidad_mayoreo, costo_promedio, es_inventariable in productos:
        try:
            # Asegurar que cantidad_mayoreo sea >= 2 (por constraint)
            cant_mayoreo = max(cantidad_mayoreo, 2)
            
            # Insertar producto
            cursor.execute("""
                INSERT INTO ca_productos (
                    codigo_interno, codigo_barras, nombre, descripcion,
                    precio_venta, precio_mayoreo, cantidad_mayoreo, costo_promedio,
                    es_inventariable, activo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id_producto
            """, (codigo, barcode, nombre, descripcion, precio_venta, precio_mayoreo, 
                  cant_mayoreo, costo_promedio, es_inventariable))
            
            id_producto = cursor.fetchone()['id_producto']
            
            # Insertar en inventario con stock inicial
            stock_inicial = cant_mayoreo * 10  # Multiplicar por 10 para tener buen stock
            stock_minimo = cant_mayoreo
            stock_maximo = cant_mayoreo * 50
            
            cursor.execute("""
                INSERT INTO inventario (
                    id_producto, id_ubicacion, stock_actual, stock_minimo,
                    stock_maximo, costo_promedio, activo
                ) VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, (id_producto, ubicacion_id, stock_inicial, stock_minimo, 
                  stock_maximo, costo_promedio))
            
            conn.commit()
            insertados += 1
            print(f"  ✓ {insertados:2d}. {codigo:12s} - {nombre:40s} (${precio_venta})")
        
        except Exception as e:
            conn.rollback()
            print(f"  ❌ Error insertando {codigo}: {e}")
            continue
    
    cursor.close()
    print(f"\n✅ {insertados}/{len(productos)} productos insertados correctamente")
    print(f"📊 Base de datos lista para pruebas de venta\n")
    
except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
