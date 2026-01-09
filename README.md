# Punto Clave - Sistema Integral de Punto de Venta

Sistema completo de Punto de Venta empresarial para Punto Clave con arquitectura PostgreSQL avanzada, optimizado para pantallas táctiles y gestión integral de ventas, inventario, y finanzas.

## 🚀 Características Principales

### 💳 Sistema de Ventas Avanzado
- ✅ Punto de venta táctil optimizado
- ✅ Carrito de compras en tiempo real con previsualizaciones
- ✅ Múltiples métodos de pago (efectivo, tarjeta débito/crédito, transferencia bancaria, cheques, depósitos, vale/cupón, crédito, pago mixto)
- ✅ Búsqueda rápida de productos por código de barras, código interno o nombre
- ✅ Gestión de descuentos a nivel línea y general
- ✅ Ventas a crédito con pagos parciales
- ✅ Histórico de ventas completo con filtros avanzados
- ✅ Cancelación de ventas con auditoría
- ✅ Reembolsos y devoluciones
- ✅ Clasificación de ventas (producto, mixta, servicio)
- ✅ Seguimiento de cambio de efectivo

### 📦 Gestión Integral de Inventario
- ✅ Catálogo maestro de productos (varios, suplementos, accesorios, bebidas, alimentos, servicios)
- ✅ Control de stock en tiempo real por ubicación
- ✅ Múltiples unidades de medida (pieza, kg, g, litro, ml, caja, paquete, onza, libra, galón, metro, servicio)
- ✅ Movimientos de inventario completos (entrada, venta, merma, ajuste, devolución, transferencia)
- ✅ Alertas de stock bajo y máximo
- ✅ Control FIFO/FEFO con lotes y fechas de caducidad
- ✅ Grid editable para gestión masiva
- ✅ 8 ubicaciones de almacenamiento (Lockers, Recepción, Bodegas, Mostrador, Almacén, Refrigeradores, Área de Ventas)
- ✅ Trazabilidad completa de movimientos
- ✅ Control de productos perecederos
- ✅ Costos promedio y análisis de rentabilidad
- ✅ Productos con precios mayoreo

### 👥 Gestión Completa de Clientes
- ✅ Registro detallado de clientes con RFC
- ✅ Seguimiento de compras y saldo de favor
- ✅ Crédito disponible por cliente
- ✅ Contacto de emergencia
- ✅ Historial completo de transacciones
- ✅ Búsqueda avanzada por nombre, teléfono, email
- ✅ Foto de perfil del cliente

### 💰 Sistema de Cuentas por Cobrar (CxC)
- ✅ Gestión de ventas a crédito con plazos configurables
- ✅ Pagos parciales con seguimiento
- ✅ Estados: activa, pagada, vencida, cancelada
- ✅ Cálculo automático de días vencidos
- ✅ Reportes de CxC vencidas
- ✅ Alertas de vencimiento
- ✅ Múltiples métodos de pago por cuota

### 📋 Sistema de Cuentas por Pagar (CxP) Empresarial
- ✅ Gestión unificada de compras, servicios y gastos
- ✅ Categorías de CxP: compras, servicios, gastos, nómina, impuestos, otros
- ✅ Múltiples tipos de cuenta: productos, servicios, renta, utilidades, nómina, impuestos
- ✅ Control de pagos parciales
- ✅ Estados: activa, pagada, vencida, cancelada, parcial
- ✅ Recepción de productos con cantidad recibida vs. solicitada
- ✅ Integración con inventario (movimientos automáticos)
- ✅ Alertas de cuentas vencidas
- ✅ Análisis de saldo con proveedores

### 🏢 Gestión Avanzada de Proveedores
- ✅ Catálogo completo de proveedores
- ✅ Información comercial detallada (RFC, contacto, teléfono, email)
- ✅ Límites de crédito y saldo actual
- ✅ Días de crédito configurables
- ✅ Historial de compras
- ✅ Control de estado activo/inactivo

### 💳 Caja y Turnos de Trabajo
- ✅ Apertura y cierre de turnos por cajero
- ✅ Monto inicial configurable
- ✅ Control de movimientos de caja (retiros, depósitos, ajustes)
- ✅ Resumen por método de pago (efectivo, tarjeta débito, tarjeta crédito, transferencia)
- ✅ Conteo de efectivo con diferencia calculada
- ✅ Cierre Z con reportes detallados
- ✅ Estadísticas del turno (número de ventas, ticket promedio)
- ✅ Un solo turno abierto por usuario (validación)
- ✅ Auditoría completa de operaciones

### 🔐 Sistema de Usuarios y Control de Acceso
- ✅ Roles: recepcionista, administrador, sistemas
- ✅ Autenticación segura (hash bcrypt/argon2)
- ✅ Gestión de sesiones con tokens
- ✅ Control de intentos fallidos y bloqueos
- ✅ Auditoría de último acceso
- ✅ Activación/desactivación de usuarios

### 📊 Análisis y Reportes
- ✅ Vista de productos con stock bajo
- ✅ Vista de ventas del día
- ✅ Vista de CxC vencidas
- ✅ Vista de CxP vencidas
- ✅ Vista de productos más vendidos (últimos 30 días)
- ✅ Resumen de turno actual
- ✅ Inventario valorizado con márgenes
- ✅ Análisis de rentabilidad por producto
- ✅ Rotación de inventario

### 📱 Interfaz Optimizada para Táctil
- ✅ **TouchNumericInput**: Campos numéricos sin flechas (cantidad, stock)
- ✅ **TouchMoneyInput**: Campos monetarios con formato automático
- ✅ Botones grandes tipo Windows Phone Tiles
- ✅ Altura de 50px en campos para mejor usabilidad táctil
- ✅ Sistema de diseño coherente y homologado
- ✅ Navegación intuitiva con tiles de colores
- ✅ Soporte para pantallas táctiles múltiples

### 🔄 Base de Datos Empresarial
- ✅ **PostgreSQL 12+**: Base de datos relacional empresarial
- ✅ **Supabase**: Sincronización con app móvil y gestión en la nube
- ✅ Row Level Security (RLS) configurado
- ✅ Triggers PostgreSQL para validaciones y sincronización
- ✅ LISTEN/NOTIFY para notificaciones en tiempo real
- ✅ Vistas optimizadas para reportes
- ✅ Índices de rendimiento en tablas críticas

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
│   ├── movimiento_inventario_window.py # Movimientos de inventario
│   ├── historial_movimientos_window.py # Historial de movimientos
│   ├── historial_turnos_window.py  # Historial de turnos
│   ├── historial_ventas_window.py  # Historial de ventas
│   ├── asignacion_turnos_window.py # Asignación de turnos de caja
│   ├── abrir_turno_dialog.py       # Diálogo de apertura de turno
│   ├── admin_auth_dialog.py        # Diálogo de autenticación admin
│   ├── escanear_codigo_dialogo.py  # Escaneo de códigos de barras
│   ├── editable_catalog_grid.py    # Grid editable de catálogo
│   ├── ubicaciones_window.py       # Gestión de ubicaciones de almacén
│   ├── ventas/
│   │   ├── cierre_caja.py          # Cierre Z de caja
│   │   ├── historial.py            # Historial de ventas
│   │   ├── nueva_venta.py          # Creación de nuevas ventas
│   │   └── ventas_dia.py           # Ventas del día
│   └── __pycache__/
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

## 📋 Módulos Principales del Sistema

### 1. Módulo de Ventas (POS)
El corazón del sistema con funcionalidades de punto de venta:
- **Nueva Venta**: Búsqueda de productos, carrito dinámico, cálculo automático de impuestos
- **Métodos de Pago**: 9 opciones incluyendo pago mixto y crédito
- **Descuentos**: Por línea o general, con validación de autorización
- **Ventas a Crédito**: Con generación automática de CxC y pagos parciales
- **Cancelación**: Reversión completa con trazabilidad
- **Historial**: Búsqueda por ticket, cliente, fecha, vendedor
- **Cierre Z**: Reporte detallado por método de pago

### 2. Módulo de Inventario
Gestión completa del inventario con múltiples ubicaciones:
- **Catálogo**: ABM de productos con precios, impuestos, costos
- **Stock Control**: Alertas de mínimo/máximo, stock reservado
- **Movimientos**: Registro completo (entrada, salida, merma, ajuste)
- **Lotes/Caducidades**: Control FIFO/FEFO para perecederos
- **Ubicaciones**: 8 posiciones de almacenamiento configurable
- **Análisis**: Rentabilidad, rotación, valor de inventario
- **Reportes**: Productos lentos, exceso de stock, valor total

### 3. Módulo de Clientes y Crédito
Gestión integral de clientes y cuentas por cobrar:
- **Clientes**: RFC, contacto, límite de crédito, saldo de favor
- **Cuentas por Cobrar**: Seguimiento de ventas a crédito
- **Pagos Parciales**: Registro de abonos con métodos flexibles
- **Cobranza**: Alertas de vencimiento, reportes de deuda
- **Historial**: Todas las transacciones por cliente

### 4. Módulo de Caja y Turnos
Control completo de movimientos de efectivo:
- **Apertura**: Monto inicial configurable por cajero
- **Operaciones**: Retiros, depósitos, ajustes durante el turno
- **Resumen**: Totales por método de pago (efectivo, tarjeta, etc.)
- **Cierre**: Conteo de efectivo, diferencia calculada automáticamente
- **Reportes**: Ticket promedio, número de ventas, estadísticas
- **Auditoría**: Historial completo con usuario y timestamp

### 5. Módulo de Proveedores y Compras
Gestión de cuentas por pagar y compras:
- **Proveedores**: Información comercial, RFC, límites de crédito
- **Cuentas por Pagar**: Unificación de compras, servicios, gastos
- **Categorías**: 15 tipos predefinidos (compras, servicios, renta, nómina, etc.)
- **Recepción**: Partial receipt tracking vs. solicitud
- **Pagos**: Múltiples pagos parciales con registro detallado
- **Vencimientos**: Alertas de cuentas vencidas

### 6. Módulo de Usuarios y Acceso
Control de seguridad y permisos:
- **Roles**: Recepcionista, Administrador, Sistemas
- **Autenticación**: Hash seguro (bcrypt/argon2)
- **Sesiones**: Tokens con expiración configurable
- **Bloqueos**: Control de intentos fallidos
- **Auditoría**: Registro de acceso y último login

### 7. Módulo de Reportes y Análisis
Vistas y reportes para la toma de decisiones:
- **Stock Bajo**: Productos por debajo del mínimo
- **Más Vendidos**: Top 10 productos últimos 30 días
- **Ventas del Día**: Resumen completo con detalles
- **CxC/CxP Vencidas**: Alertas de cobro/pago urgentes
- **Turno Actual**: Estadísticas en tiempo real
- **Inventario Valorizado**: Valor total, márgenes por producto
- **Rentabilidad**: Análisis por producto y período

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

### Base de Datos Empresarial PostgreSQL
La base de datos implementa un esquema relacional completo con validaciones, triggers y vistas optimizadas.

#### Tipos de Datos Personalizados (ENUM)
- `tipo_rol_usuario`: recepcionista, administrador, sistemas
- `tipo_producto_detalle`: varios, suplemento, membresia, digital
- `tipo_movimiento_inventario`: entrada, venta, merma, ajuste, devolucion, transferencia
- `tipo_metodo_pago`: efectivo, tarjeta_debito, tarjeta_credito, transferencia, mixto
- `tipo_estado_venta`: completada, cancelada, reembolsada, pendiente
- `tipo_venta`: producto, mixta, servicio
- `tipo_producto_fisico`: varios, suplemento, accesorio, bebida, alimento
- `tipo_estado_cxc`: activa, pagada, vencida, cancelada
- `tipo_estado_cxp`: activa, pagada, vencida, cancelada, parcial

#### Tablas Principales

**Catálogos Base:**
- `ca_ubicaciones` - 8 ubicaciones de almacenamiento
- `ca_unidades_medida` - 12 unidades de medida predefinidas
- `ca_tipo_pago` - 9 tipos de pago (efectivo, tarjetas, transferencia, cheques, etc.)
- `ca_categorias_producto` - Categorías jerárquicas de productos
- `ca_proveedores` - Información completa de proveedores
- `ca_tipo_cuenta_pagar` - 15 tipos de cuentas por pagar

**Usuarios y Clientes:**
- `usuarios` - Control de acceso, sesiones y auditoría
- `clientes` - Información detallada con RFC, saldo de favor, límite de crédito

**Productos e Inventario:**
- `ca_productos` - Catálogo maestro con precios, impuestos, costos
- `inventario` - Control de stock por producto y ubicación
- `movimientos_inventario` - Trazabilidad completa de movimientos
- `lotes_inventario` - Control FIFO/FEFO para productos perecederos
- `costos_productos` - Historial de costos y análisis de variación
- `analisis_rentabilidad` - Métricas de rentabilidad por producto

**Caja y Turnos:**
- `turnos_caja` - Apertura, cierre y estadísticas por cajero
- `movimientos_caja` - Retiros, depósitos y ajustes de caja

**Ventas:**
- `ventas` - Transacciones completas con múltiples métodos de pago
- `detalles_venta` - Líneas de detalle con impuestos y descuentos
- `pagos_venta` - Pagos parciales para ventas a crédito
- `cuentas_por_cobrar` - Gestión de crédito a clientes
- `cxc_detalle_pagos` - Registro de pagos parciales de CxC

**Compras y Servicios:**
- `cuentas_por_pagar` - Unificación de compras, servicios y gastos
- `cxp_detalle_productos` - Productos en compras con recepción parcial
- `cxp_pagos` - Registro de pagos a proveedores

#### Índices de Rendimiento
Más de 50 índices optimizados en:
- Búsquedas de productos (nombre, código, barras)
- Filtros de inventario (stock bajo, disponible, valor)
- Movimientos históricos (por fecha, tipo, usuario)
- Gestión de crédito (vencimiento, cliente, saldo)
- Reportes de ventas (fecha, vendedor, método pago)
- Análisis de caja (turnos activos, movimientos)

#### Vistas Optimizadas
- `v_productos_stock_bajo` - Productos con stock crítico
- `v_ventas_del_dia` - Resumen de ventas actuales
- `v_cxc_vencidas` - Cuentas por cobrar vencidas
- `v_cxp_vencidas` - Cuentas por pagar vencidas
- `v_productos_mas_vendidos` - Top products últimos 30 días
- `v_resumen_turno_actual` - Estadísticas del turno abierto
- `v_inventario_valorizado` - Inventario con márgenes y valores

### Stack Tecnológico Empresarial
- **Framework UI**: PySide6 (Qt6 para Python) - Interfaz nativa Windows
- **Base de Datos**: PostgreSQL 13+ - Base principal relacional
- **Sincronización Cloud**: Supabase - Replicación y app móvil
- **ORM/Queries**: psycopg2 - Driver nativo PostgreSQL de alto rendimiento
- **Empaquetado**: PyInstaller - Distribución ejecutable sin dependencias
- **Sistema de Diseño**: Windows Phone inspired tiles optimizado para táctil
- **Seguridad**: Row Level Security (RLS), bcrypt/argon2 hashing
- **Análisis**: SQL Views avanzadas con índices de rendimiento

### Funcionalidades Avanzadas Empresariales
- 🔔 **Notificaciones en tiempo real** con LISTEN/NOTIFY PostgreSQL
- 📊 **Reportes complejos** con análisis de rentabilidad e inventario
- 💳 **Gestión financiera** integral (CxC, CxP, caja)
- 🔐 **Auditoría completa** de todas las operaciones
- 📈 **Análisis de rotación** de inventario y márgenes
- 🎯 **Cálculo de impuestos** (IEPS, IVA) automático
- 🏪 **Multi-ubicación** de almacenamiento con trazabilidad
- ⚙️ **Control de proveedores** con crédito y límites
- 📱 **Sincronización** bidireccional POS ↔ App Móvil
- 🔄 **Pagos parciales** en ventas y compras

## 📚 Documentación Adicional

- `POS_sql.txt` - Script SQL completo con 70+ tablas, vistas e índices
- `INICIAR_DEMO.bat` - Script para iniciar la aplicación rápidamente
- `setup_postgres_trigger.sql` - Triggers para validaciones y sincronización
- `GUIA_USUARIO_IMPRESORA.txt` - Configuración de impresora térmica ESCPOS
- `TABLA_COMPARATIVA.txt` - Comparativa de esquemas DB (PostgreSQL vs Supabase)
- `RESUMEN_INTEGRACION.txt` - Detalles de integración con Supabase
- `MIGRACION_POSTGRES.md` - Documentación de migración a PostgreSQL
- `ACTUALIZACION_POSTGRES.md` - Guía de actualizaciones de versiones

## 🚀 Características Destacadas

1. **Sistema Integral Empresarial**: No solo POS, sino gestión completa de finanzas (CxC, CxP, caja)
2. **Pantalla Táctil**: Optimizado desde el inicio para tablets y touch screens con componentes especializados
3. **Base de Datos Robusta**: PostgreSQL con 70+ tablas, 50+ índices y 8+ vistas optimizadas
4. **Sin Conexión**: Funciona completamente offline con PostgreSQL local, sin dependencias de internet
5. **Sincronización Optional**: Puede sincronizar con Supabase para app móvil y reportes remotos
6. **Control de Inventario Avanzado**: FIFO/FEFO, lotes, caducidades, ubicaciones múltiples
7. **Gestión de Crédito**: Cuentas por cobrar y pagar con pagos parciales, vencimientos, alertas
8. **Análisis Financiero**: Rentabilidad por producto, rotación de inventario, márgenes
9. **Auditoría Completa**: Registro de todas las operaciones con usuario, fecha y detalles
10. **Modular y Escalable**: Arquitectura limpia separada por módulos funcionales

## 📦 Distribución

El ejecutable `HTF_Gimnasio_POS.exe` incluye:
- ✅ Todas las dependencias empaquetadas (PySide6, psycopg2, supabase-client)
- ✅ PySide6 (Qt6) embebido con temas Windows nativos
- ✅ PostgreSQL driver de alto rendimiento
- ✅ Supabase client para sincronización
- ✅ Componentes táctiles optimizados y vistas personalizadas
- ✅ Sistema de diseño completo Windows Phone inspired
- ✅ Todas las vistas SQL y procedimientos

**Tamaño**: 85.65 MB  
**Plataforma**: Windows 10/11 (64 bits recomendado)  
**Requisitos**: PostgreSQL local instalado y configurado  
**Instalación**: Descarga y ejecuta - No requiere Python ni instalación adicional

## 🤝 Contribuir

Este proyecto está en constante evolución. Las áreas de desarrollo futuro incluyen:
- 📲 API REST para integraciones externas
- 📊 Reportes avanzados con gráficas (Matplotlib, Plotly)
- 🌐 Portal web de administración
- 🏪 Soporte multi-sucursal con consolidación
- 💹 Análisis predictivo de inventario
- 🎫 Integración con más métodos de pago
- 📧 Notificaciones por correo y WhatsApp
- 🔗 Integraciones contables (SAT, CFDI)

## 📄 Licencia

Proyecto propietario para Punto Clave. Todos los derechos reservados.

---

## 📞 Soporte y Contacto

Para reportar errores, sugerencias o soporte técnico, contacta al equipo de desarrollo de Punto Clave.

---

**Diseñado y desarrollado con ❤️ para Punto Clave**  
*Sistema POS empresarial, moderno, táctil y completamente funcional*  
**Versión 5.0** - PostgreSQL 12+ Ready