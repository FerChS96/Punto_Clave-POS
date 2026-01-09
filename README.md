# Punto Clave - Sistema POS

Sistema de Punto de Venta completo para Punto Clave con arquitectura híbrida PostgreSQL + Supabase, optimizado para pantallas táctiles.

## 🚀 Características Principales

### 💳 Sistema de Ventas
- ✅ Punto de venta táctil optimizado
- ✅ Carrito de compras en tiempo real
- ✅ Múltiples métodos de pago (efectivo, tarjeta, transferencia)
- ✅ Búsqueda rápida de productos por código de barras
- ✅ Gestión de descuentos
- ✅ Histórico de ventas completo
- ✅ Cierre de caja con corte Z

### 📦 Gestión de Inventario
- ✅ Catálogo de productos (varios y suplementos)
- ✅ Control de stock en tiempo real
- ✅ Movimientos de inventario (entradas/salidas)
- ✅ Alertas de stock bajo
- ✅ Grid editable para gestión masiva
- ✅ Ubicaciones de almacenamiento
- ✅ Búsqueda avanzada con filtros múltiples

### 👥 Gestión de Miembros
- ✅ Registro completo de miembros
- ✅ Seguimiento de asistencias
- ✅ Gestión de pagos y mensualidades
- ✅ Historial de compras por miembro
- ✅ Escaneo de QR para entrada rápida
- ✅ Monitor de entradas en tiempo real

### 🏢 Gestión de Proveedores
- ✅ Catálogo completo de proveedores
- ✅ Formulario de registro y edición de proveedores
- ✅ Gestión de estado activo/inactivo
- ✅ Validación de datos (email, teléfono)
- ✅ Integración con base de datos PostgreSQL

### 🏪 Ventas Digitales y Pagos en Efectivo
- ✅ Notificaciones de pagos pendientes
- ✅ Confirmación de pagos en efectivo escaneando código
- ✅ Edge Function para procesar pagos
- ✅ Sistema de códigos de pago (CASH-XXX)
- ✅ Actualización automática de estado de ventas

### 💰 Caja y Turnos
- ✅ Asignación de turnos a empleados
- ✅ Registro de monto inicial
- ✅ Control de movimientos de caja
- ✅ Cierre de turno con reporte detallado
- ✅ Auditoría completa de operaciones

### 📱 Interfaz Optimizada para Táctil
- ✅ **TouchNumericInput**: Campos numéricos sin flechas (cantidad, stock)
- ✅ **TouchMoneyInput**: Campos monetarios con formato automático
- ✅ Botones grandes tipo Windows Phone Tiles
- ✅ Altura de 50px en campos para mejor usabilidad táctil
- ✅ Sistema de diseño coherente y homologado
- ✅ Navegación intuitiva con tiles de colores

### 🔄 Base de Datos Híbrida
- ✅ **PostgreSQL local**: Base de datos principal para operaciones POS
- ✅ **Supabase**: Sincronización con app móvil y gestión en la nube
- ✅ Row Level Security (RLS) configurado
- ✅ Triggers PostgreSQL para notificaciones en tiempo real
- ✅ LISTEN/NOTIFY para entradas de miembros

## 📁 Estructura del Proyecto

```
Punto_Clave/
├── main.py                          # Aplicación principal
├── requirements.txt                 # Dependencias Python
├── .env                            # Variables de entorno (Supabase, PostgreSQL)
├── HTF_Gimnasio_POS.exe            # Ejecutable para Windows (85.65 MB)
│
├── database/
│   ├── postgres_manager.py         # Gestor PostgreSQL principal
│   └── supabase_service.py         # Servicio Supabase para sincronización
│
├── ui/
│   ├── main_pos_window.py          # Ventana principal con navegación
│   ├── components.py               # Sistema de diseño (Tiles, TouchInputs)
│   ├── sales_windows.py            # Módulo de ventas
│   ├── inventario_window.py        # Gestión de inventario
│   ├── nuevo_producto_window.py    # Formulario de productos
│   ├── proveedores_window.py       # Gestión de proveedores
│   ├── movimiento_inventario_window.py
│   ├── miembros_window.py          # Gestión de miembros
│   ├── asignacion_turnos_window.py # Turnos de caja
│   ├── notificaciones_pago_window.py
│   ├── confirmar_pago_efectivo_dialog.py
│   ├── escanear_codigo_dialogo.py
│   ├── editable_catalog_grid.py    # Grid editable de catálogo
│   └── ...
│
├── services/
│   ├── postgres_listener.py        # Listener para notificaciones PostgreSQL
│   └── supabase_sync.py            # Sincronización con Supabase
│
├── utils/
│   └── config.py                   # Configuración general
│
└── assets/
    └── icons/                      # Iconos de la aplicación
```

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.12+
- PostgreSQL 13+
- Cuenta de Supabase (opcional para sincronización)

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` con:

```env
# PostgreSQL Local
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=punto_clave
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password

# Supabase (Opcional)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
```

### 3. Ejecutar la Aplicación

**Desarrollo:**
```bash
python main.py
```

**Producción (Ejecutable):**
```bash
dist\HTF_Gimnasio_POS.exe
```

### 4. Generar Ejecutable

```bash
python build_exe.py
```

## 👤 Credenciales por Defecto

- **Usuario:** admin
- **Contraseña:** admin123

## 🎨 Componentes Táctiles Personalizados

### TouchNumericInput
Campo numérico sin flechas para números enteros (cantidad, stock):

```python
from ui.components import TouchNumericInput

cantidad = TouchNumericInput(
    minimum=1,
    maximum=9999,
    default_value=1
)
```

### TouchMoneyInput
Campo monetario con formato automático y validación:

```python
from ui.components import TouchMoneyInput

precio = TouchMoneyInput(
    minimum=0.01,
    maximum=999999.99,
    decimals=2,
    prefix="$ "
)
```

**Beneficios:**
- 🚫 Sin flechas pequeñas (▲▼)
- 📏 Campos de 50px de altura (fáciles de tocar)
- ⌨️ Teclado numérico automático en tablets
- ✅ Validación automática de rangos
- 🔄 API compatible con QSpinBox/QDoubleSpinBox

## 🔧 Arquitectura Técnica

### Base de Datos
- **PostgreSQL**: Base principal para operaciones del POS
- **Supabase**: Sincronización con app móvil
- **Triggers**: LISTEN/NOTIFY para notificaciones en tiempo real
- **RLS**: Seguridad a nivel de fila habilitada

#### Tablas Principales
- `ca_productos`: Catálogo de productos
- `ca_proveedores`: Gestión de proveedores
  - `id`: SERIAL PRIMARY KEY
  - `nombre`: VARCHAR(255) NOT NULL
  - `telefono`: VARCHAR(20)
  - `email`: VARCHAR(255)
  - `direccion`: TEXT
  - `fecha_creacion`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  - `activo`: BOOLEAN DEFAULT TRUE
- `ventas`: Registro de ventas
- `detalle_venta`: Detalles de productos vendidos
- `inventario`: Control de stock
- `movimientos_inventario`: Historial de movimientos
- `miembros`: Registro de miembros del gimnasio
- `turnos`: Asignación de turnos de caja

### Stack Tecnológico
- **Framework UI**: PySide6 (Qt6 para Python)
- **Base de Datos**: PostgreSQL 13+ / Supabase
- **ORM/Queries**: psycopg2, supabase-py
- **Empaquetado**: PyInstaller
- **Sistema de Diseño**: Windows Phone inspired

### Funcionalidades Avanzadas
- 🔔 **Notificaciones en tiempo real** de entradas de miembros
- 💳 **Edge Functions** para confirmar pagos en efectivo
- 📊 **Reportes** de ventas, inventario y caja
- 🔐 **Seguridad** con RLS y validación de permisos
- 📱 **Sincronización** bidireccional POS ↔ App Móvil

## 📚 Documentación Adicional

- `INICIAR_DEMO.bat` - Script para iniciar la aplicación rápidamente
- `setup_postgres_trigger.sql` - Triggers para notificaciones
- `GUIA_USUARIO_IMPRESORA.txt` - Configuración de impresora térmica
- `TABLA_COMPARATIVA.txt` - Comparativa de esquemas DB
- `RESUMEN_INTEGRACION.txt` - Integración con Supabase

## 🚀 Características Destacadas

1. **Pantalla Táctil**: Optimizado desde el inicio para tablets y touch screens
2. **Sin Conexión**: Funciona completamente offline con PostgreSQL local
3. **Sincronización**: Opcionalmente sincroniza con Supabase para app móvil
4. **Modular**: Arquitectura limpia y escalable
5. **Producción**: Ejecutable .exe listo para distribuir (no requiere Python)

## 📦 Distribución

El ejecutable `HTF_Gimnasio_POS.exe` incluye:
- ✅ Todas las dependencias empaquetadas
- ✅ PySide6 (Qt6) embebido
- ✅ PostgreSQL driver (psycopg2)
- ✅ Supabase client
- ✅ Componentes táctiles optimizados
- ✅ Sistema de diseño completo

**Tamaño**: 85.65 MB  
**Plataforma**: Windows 10/11  
**Instalación**: No requiere Python ni dependencias

## 🤝 Contribuir

Este proyecto está en constante evolución. Las áreas de desarrollo futuro incluyen:
- Integración con más métodos de pago
- Reportes avanzados con gráficas
- App de administración web
- Soporte multi-sucursal
- API REST para integraciones

## 📄 Licencia

Proyecto privado para Punto Clave.

---

**Diseñado y desarrollado con ❤️ para Punto Clave**  
Sistema POS moderno, táctil y completamente funcional.