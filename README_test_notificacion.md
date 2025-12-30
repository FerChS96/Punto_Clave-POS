# Script de Prueba para Notificación de Entrada

Este script permite probar el widget `NotificacionEntradaWidget` que se muestra cuando un miembro registra su entrada en el sistema.

## Cómo usar

1. Ejecuta el script:
   ```bash
   python test_notificacion_widget.py
   ```

2. Se mostrará una ventana emergente con la información del miembro de ejemplo.

3. La ventana se puede cerrar haciendo clic en el botón "✕ CERRAR".

## Personalización

Para cambiar los datos del miembro, edita el diccionario `miembro_data` en el script:

```python
miembro_data = {
    'id_miembro': 12345,
    'nombres': 'Juan Carlos',
    'apellido_paterno': 'Pérez',
    'apellido_materno': 'García',
    'telefono': '+52 55 1234 5678',
    'fecha_registro': '2023-01-15',
    'foto': 'ruta/a/la/foto.jpg'  # Opcional
}
```

## Características del Widget

- **Ventana emergente**: Se muestra sin bloquear la aplicación principal
- **Siempre visible**: Se mantiene encima de otras ventanas
- **Sin marco**: Apariencia moderna sin bordes de ventana
- **Arrastrable**: Se puede mover arrastrando el encabezado
- **Foto del miembro**: Muestra foto circular o iniciales si no hay foto
- **Información completa**: ID, nombre, teléfono, fecha de registro
- **Botones de acción**: Asignar cargo o cerrar
- **Animaciones**: Efectos de opacidad al abrir/cerrar

## Campos requeridos

- `id_miembro`: Número de identificación del miembro
- `nombres`: Nombres del miembro
- `apellido_paterno`: Apellido paterno
- `apellido_materno`: Apellido materno

## Campos opcionales

- `telefono`: Número de teléfono
- `fecha_registro`: Fecha de registro en formato YYYY-MM-DD
- `foto`: Ruta absoluta a la imagen del miembro