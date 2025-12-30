# Integración de Impresora Térmica ESC/POS en HTF POS

## ✅ COMPLETADO

Se ha integrado exitosamente la impresión térmica ESC/POS en la ventana de ventas.

## 📁 Archivos Creados/Modificados

### 1. **escpos_printer.py** (NUEVO)
- Módulo principal de impresión ESC/POS
- Clases: `EscPosDriver` y `TicketPrinter`
- Soporte para impresoras como **EC-PM-58110-USB**
- Funciones:
  - Conexión por puerto Serial/USB
  - Formateo de texto (alineación, tamaño, negrita)
  - Impresión de tickets completos
  - Control de caja registradora
  - Corte automático de papel

### 2. **config_impresora.py** (NUEVO)
- Gestor de configuración de impresora
- Detección automática de puertos COM disponibles
- Prueba de conexión
- Guardado de configuración en JSON
- Clase: `ConfiguradorImpresora`

### 3. **ui/ventas/nueva_venta.py** (MODIFICADO)
- Agregado import de `TicketPrinter`
- Botón "Imprimir Térmica" en el diálogo de ticket
- Nuevo método: `imprimir_ticket_escpos()`
- Mantiene botón "Imprimir Sistema" para impresoras normales

### 4. **requirements.txt** (ACTUALIZADO)
- `openpyxl>=3.11.0` - Gestión de Excel
- `pandas>=2.0.0` - Manipulación de datos
- `xlsxwriter>=3.1.2` - Formato avanzado Excel
- `pyserial` y `escpos` ya estaban

## 🖨️ USO EN VENTANA DE VENTAS

### Paso 1: Realizar Venta
- Usuario escanea productos o busca manualmente
- Agrega items al carrito
- Define cantidad y confirma

### Paso 2: Finalizar Venta
- Presiona botón "Pagar" o "Finalizar"
- Se abre diálogo con 3 opciones:

```
┌─────────────────────────────┐
│    TICKET DE VENTA #001234  │
├─────────────────────────────┤
│ [Imprimir Térmica]          │  ← ESC/POS (Impresora térmica)
│ [Imprimir Sistema]          │  ← Impresora del sistema
│ [Cerrar]                    │
└─────────────────────────────┘
```

## 🔧 CONFIGURACIÓN

### Puerto COM predeterminado: **COM3**

Para cambiar el puerto, editar en `nueva_venta.py`:

```python
# Línea ~1040
puerto = "COM3"  # Cambiar a COM1, COM2, etc.
```

O crear archivo `config_impresora.json`:

```json
{
    "puerto_impresora": "COM3",
    "baudrate": 115200,
    "abrir_caja_automaticamente": true,
    "cortar_papel_automaticamente": true
}
```

## 🔍 DETECTAR PUERTO CORRECTO

```python
from config_impresora import ConfiguradorImpresora

# Listar puertos disponibles
puertos = ConfiguradorImpresora.obtener_puertos_disponibles()
for puerto in puertos:
    print(f"{puerto['puerto']}: {puerto['descripcion']}")

# Probar conexión
if ConfiguradorImpresora.probar_conexion("COM3"):
    print("✅ Impresora conectada")
```

## 📋 FUNCIONALIDADES DE IMPRESORA

### EscPosDriver (Clase base)
```python
- conectar()           # Conectar a puerto COM
- desconectar()        # Cerrar conexión
- alinear_centro()     # Alinear texto al centro
- alinear_izquierda()  # Alinear a izquierda
- fuente_grande()      # Aumentar tamaño fuente
- negrita_on/off()     # Activar negrita
- linea_punteada()     # Línea decorativa
- cortar_papel()       # Cortar papel
- abrir_caja_registradora()  # Abrir caja
```

### TicketPrinter (Especializado)
```python
- imprimir_titulo_tienda()      # Encabezado
- imprimir_encabezado_ticket()  # Info del ticket
- imprimir_producto()           # Línea de producto
- imprimir_total()              # Total y método de pago
- imprimir_pie()                # Cierre del ticket
- imprimir_ticket(datos)        # Ticket completo
```

## 📦 DATOS DEL TICKET

```python
datos_ticket = {
    'tienda': 'HTF GIMNASIO',
    'subtitulo': 'PUNTO DE VENTA',
    'numero_ticket': 1001,
    'fecha_hora': '19/12/2025 15:30',
    'cajero': 'Juan Pérez',
    'productos': [
        {
            'nombre': 'Bebida Energética',
            'cantidad': 2,
            'precio': 5.00,
            'subtotal': 10.00
        },
        # ... más productos
    ],
    'total': 33.50,
    'metodo_pago': 'EFECTIVO',
    'abrir_caja': True,      # Abre caja registradora
    'cortar': True           # Corta papel automático
}
```

## ⚠️ POSIBLES PROBLEMAS Y SOLUCIONES

### "No se pudo conectar a la impresora"
1. Verificar que la impresora está conectada
2. Comprobar puerto COM correcto (Device Manager)
3. Revisar que los drivers están instalados
4. Probar con otro cable USB

### Impresión cortada o deforme
1. Ajustar `timeout_conexion` en config
2. Reducir velocidad baudrate
3. Verificar compatibilidad ESC/POS de la impresora

### Caja registradora no abre
1. Verificar conexión del cable de caja
2. Configurar `'abrir_caja': False` temporalmente
3. Probar apertura manual de caja

## 🚀 PRÓXIMAS MEJORAS

1. **GUI de Configuración**
   - Interfaz visual para seleccionar puerto COM
   - Test de conexión en tiempo real
   - Guardar configuración automáticamente

2. **Múltiples Copias**
   - Imprimir múltiples copias del ticket
   - Copias para cliente y tienda

3. **Cupones Promocionales**
   - Imprimir descuentos
   - Ofertas especiales

4. **Historial de Tickets**
   - Reimprimir tickets anteriores
   - Exportar a PDF

5. **Control de Caja**
   - Reporte de apertura/cierre de caja
   - Registro de transacciones

## 📞 TÉCNICAS

- **Protocolo**: ESC/POS (EPSON Standard Code for Point Of Sale)
- **Interfaz**: Serial (COM) USB a Serial
- **Baudrate**: 115200 bps (configurable)
- **Ancho papel**: 58mm (42 caracteres por línea)
- **Codificación**: UTF-8

## ✨ ESTADO

**INTEGRACIÓN: ✅ COMPLETA**
- Botones agregados ✅
- Lógica de impresión ✅
- Manejo de errores ✅
- Configuración ✅
- Documentación ✅

Listo para usar en producción. Solo requiere instalación de drivers de la impresora.
