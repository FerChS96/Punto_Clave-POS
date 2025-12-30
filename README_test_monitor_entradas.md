# Scripts de Prueba - Monitor de Entradas con Supabase Realtime

Esta carpeta contiene scripts para probar el sistema de monitoreo de entradas en tiempo real usando Supabase.

## 📋 Scripts Disponibles

### 1. `test_supabase_connection.py`
**Propósito:** Verificar la conexión a Supabase y las credenciales.

**Uso:**
```bash
python test_supabase_connection.py
```

**Qué hace:**
- Carga variables de entorno desde `.env`
- Verifica conexión a Supabase
- Prueba una consulta básica a la tabla `usuarios`

### 2. `test_monitor_entradas.py`
**Propósito:** Probar el monitor de entradas con timeout automático.

**Uso:**
```bash
python test_monitor_entradas.py
```

**Qué hace:**
- Inicia el monitor de entradas usando Supabase Realtime
- Escucha por nuevas entradas en la tabla `registro_entradas`
- Se detiene automáticamente después de 10 segundos
- Muestra información de cualquier entrada detectada

### 3. `test_insertar_entrada.py`
**Propósito:** Insertar una entrada de prueba con un miembro aleatorio.

**Uso:**
```bash
python test_insertar_entrada.py
```

**Qué hace:**
- Consulta todos los miembros de la tabla `miembros`
- Selecciona un miembro aleatoriamente
- Pide confirmación antes de insertar
- Inserta una nueva entrada en `registro_entradas`
- El monitor debería detectar esta entrada automáticamente

### 4. `test_insertar_multiples_entradas.py`
**Propósito:** Insertar múltiples entradas automáticamente para testing continuo.

**Uso:**
```bash
python test_insertar_multiples_entradas.py
```

**Qué hace:**
- Consulta todos los miembros disponibles
- Pide cantidad de entradas a insertar (default: 3)
- Pide intervalo entre inserciones (default: 2 segundos)
- Inserta entradas automáticamente con miembros aleatorios
- Útil para probar el monitor con múltiples eventos

### 6. `test_monitor_completo.py`
**Propósito:** Probar el monitor completo con una interfaz Qt simplificada.

**Uso:**
```bash
python test_monitor_completo.py
```

**Qué hace:**
- Crea una ventana Qt simplificada que simula el POS
- Inicializa el monitor de entradas con Supabase Realtime
- Muestra notificaciones cuando se detectan nuevas entradas
- Incluye un botón para probar notificaciones manualmente
- Útil para probar el sistema completo sin ejecutar todo el POS

**Ventana de prueba:**
- Muestra estado de conexión y monitor
- Botón para probar notificaciones manualmente
- Maneja múltiples notificaciones activas

## 🔧 Configuración

### Variables de Entorno (.env)
Asegúrate de tener un archivo `.env` en la raíz del proyecto con:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_service_role_key
```

### Requisitos de Supabase
Para que el realtime funcione correctamente:

1. **Habilitar Realtime:** Ve a Supabase Dashboard > Database > Publications
2. **Asegurarse de que `supabase_realtime` incluya la tabla `registro_entradas`**
3. **Verificar permisos:** La service role key debe tener permisos para INSERT en `registro_entradas`

## 🧪 Flujo de Prueba Completo

Para probar todo el sistema de monitoreo:

### Paso 1: Verificar conexión
```bash
python test_supabase_connection.py
```

### Paso 2: Iniciar monitor (en terminal separada)
```bash
python test_monitor_entradas.py
```

### Paso 3: Insertar entradas de prueba
```bash
# Para una entrada
python test_insertar_entrada.py

# Para múltiples entradas
python test_insertar_multiples_entradas.py
```

### Paso 4: Verificar notificaciones en la app principal
```bash
python main.py
```

## 📊 Estructura de Datos

### Tabla `registro_entradas`
Campos requeridos para inserción:
- `id_miembro`: ID del miembro (de tabla `miembros`)
- `tipo_acceso`: Enum ('miembro', 'personal', 'visitante')
- `area_accedida`: Texto (opcional, default: 'General')
- `dispositivo_registro`: Texto (opcional)
- `notas`: Texto (opcional)
- `autorizado_por`: Texto (opcional)
- `fecha_entrada`: Timestamp (generado automáticamente)

### Tabla `miembros`
Campos consultados:
- `id_miembro`: ID único
- `nombres`: Nombre(s)
- `apellido_paterno`: Apellido paterno
- `apellido_materno`: Apellido materno (opcional)

## 🔍 Troubleshooting

### Error: "invalid input value for enum tipo_acceso_registro"
- **Solución:** Usar valores en minúsculas: 'miembro', 'personal', 'visitante'

### Error: "Realtime no funciona"
- **Solución:** Verificar que la tabla esté en la publicación `supabase_realtime`
- **Solución:** Usar service role key en lugar de anon key

### Error: "No se encontraron miembros"
- **Solución:** Verificar que la tabla `miembros` tenga registros
- **Solución:** Verificar permisos de lectura en la tabla

### Error: "Variables de entorno no configuradas"
- **Solución:** Crear archivo `.env` con las credenciales correctas
- **Solución:** Instalar `python-dotenv`: `pip install python-dotenv`

## 📝 Notas

- Los scripts cargan automáticamente las variables desde `.env`
- El monitor usa cliente async de Supabase para realtime
- Las notificaciones se muestran tanto en consola como en la UI
- Los scripts de inserción incluyen timestamps para tracking
- El sistema es compatible con el POS principal y funciona en background