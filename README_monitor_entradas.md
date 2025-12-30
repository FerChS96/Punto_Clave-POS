# Monitor de Entradas - Supabase Realtime

Este documento explica el nuevo sistema de monitoreo de entradas que utiliza **Supabase Realtime** en lugar de PostgreSQL LISTEN/NOTIFY.

## 🚀 Inicio Rápido

### 1. Configurar credenciales
```bash
python setup_supabase.py
```

### 2. Probar conexión
```bash
python test_supabase_connection.py
```

### 3. Probar monitor
```bash
python test_monitor_entradas.py
```

## 📋 Configuración Detallada

### Instalar dependencias
```bash
pip install supabase
```

### Configurar credenciales de Supabase
Obtén tus credenciales desde: https://supabase.com/dashboard/project/_/settings/api

**Variables de entorno permanentes:**
```bash
# En PowerShell
$env:SUPABASE_URL = "https://tu-proyecto.supabase.co"
$env:SUPABASE_KEY = "tu-service-role-key"
```

## ¿Qué cambió?

### Antes (PostgreSQL LISTEN/NOTIFY)
- Se conectaba directamente a la base de datos PostgreSQL del torniquete
- Usaba el comando `LISTEN` para recibir notificaciones
- Dependía de triggers en la base de datos del torniquete

### Ahora (Supabase Realtime)
- Se conecta a Supabase usando WebSockets
- Escucha cambios en tiempo real en la tabla `registro_entradas`
- Es más simple y no requiere configuración adicional en PostgreSQL

## Cómo funciona

1. **Conexión**: El monitor se conecta a Supabase usando la librería oficial
2. **Suscripción**: Se suscribe al evento `INSERT` en la tabla `registro_entradas`
3. **Detección**: Cuando se inserta un nuevo registro, Supabase envía el evento por WebSocket
4. **Procesamiento**: El monitor recibe los datos y consulta información adicional del miembro
5. **Notificación**: Se muestra la ventana de notificación con toda la información

## Requisitos

### En Supabase
- La tabla `registro_entradas` debe tener habilitado Realtime
- El usuario debe tener permisos para suscribirse a cambios
- Las tablas `registro_entradas` y `miembros` deben estar relacionadas

### En el código
- Conexión válida a Supabase
- La librería `supabase` debe estar instalada

## Configuración

No se requiere configuración adicional. El monitor se inicializa automáticamente cuando se abre la ventana principal del POS.

```python
# En main_pos_window.py
self.monitor_entradas = MonitorEntradas(
    self.pg_manager,
    supabase_service=self.supabase_service
)
```

## Ventajas del nuevo sistema

1. **Más simple**: No requiere configuración de PostgreSQL adicional
2. **Más confiable**: Supabase maneja la conexión WebSocket
3. **Centralizado**: Todo pasa por Supabase, no por múltiples bases de datos
4. **Escalable**: Supabase puede manejar múltiples suscriptores

## Prueba del sistema

Para probar que funciona correctamente:

1. Ejecuta el script de prueba:
   ```bash
   python test_monitor_entradas.py
   ```

2. En otra terminal o aplicación, inserta un registro en la tabla `registro_entradas` de Supabase

3. Deberías ver en la consola que se detecta la nueva entrada

## Estructura de datos

Cuando se detecta una nueva entrada, se emite una señal con este formato:

```python
{
    'id_entrada': 123,
    'id_miembro': 456,
    'tipo_acceso': 'miembro',
    'fecha_entrada': '2025-12-29T10:30:00Z',
    'area_accedida': 'Gimnasio Principal',
    'dispositivo_registro': 'Torniquete Principal',
    'notas': 'Entrada normal',
    'nombres': 'Juan Carlos',
    'apellido_paterno': 'Pérez',
    'apellido_materno': 'García',
    'telefono': '+52 55 1234 5678',
    'email': 'juan.perez@email.com',
    'codigo_qr': 'ABC123',
    'activo': True,
    'fecha_registro': '2023-01-15',
    'fecha_nacimiento': '1990-05-20',
    'foto': None  # Opcional
}
```

## Solución de problemas

### El monitor no se inicia
- Verifica que Supabase esté conectado
- Revisa los logs para errores de conexión

### No se detectan entradas
- Verifica que la tabla `registro_entradas` tenga Realtime habilitado en Supabase
- Asegúrate de que los inserts se hagan en Supabase, no en PostgreSQL local

### Error de permisos
- El usuario de Supabase debe tener permisos para suscribirse a cambios
- Verifica las políticas RLS en Supabase</content>
<parameter name="filePath">c:\Users\ferch\Desktop\HTF_gimnasio\POS_HTF\README_monitor_entradas.md