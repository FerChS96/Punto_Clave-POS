"""
Gestor de Base de Datos Supabase para Sistema de Gimnasio
Reemplaza PostgreSQL local con Supabase (PostgreSQL en la nube)
Compatible con el esquema HTF_sql.txt
ACTUALIZADO: Usa Supabase como backend único
"""

import logging
import bcrypt
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
import sys
import io

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase no está instalado. Instala con: pip install supabase")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PostgresManager:
    """Gestor de conexión y operaciones con Supabase"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Inicializar conexión a Supabase
        
        Args:
            db_config: Diccionario con la configuración de conexión
                {
                    'url': 'https://xxxx.supabase.co',
                    'key': 'eyJhbGciOiJIUzI1NiIs...',
                    # Los parámetros de PostgreSQL se ignoran ahora
                    'host': 'ignorado',
                    'port': 'ignorado',
                    'database': 'ignorado',
                    'user': 'ignorado',
                    'password': 'ignorado'
                }
        """
        self.db_config = db_config
        self.client: Optional[Client] = None
        self.is_connected = False
        self.connect()
    
    def connect(self):
        """Establecer conexión con Supabase"""
        try:
            if not SUPABASE_AVAILABLE:
                logging.error("Supabase no está disponible. Instala con: pip install supabase")
                raise ImportError("Supabase library not installed")
            
            # Obtener credenciales de Supabase
            url = self.db_config.get('url') or os.getenv('SUPABASE_URL')
            key = self.db_config.get('key') or os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                logging.error("Credenciales de Supabase no configuradas. Configura SUPABASE_URL y SUPABASE_KEY")
                raise ValueError("Missing Supabase credentials")
            
            # Crear cliente de Supabase
            self.client = create_client(url, key)
            
            # Probar conexión
            response = self.client.table('usuarios').select('id_usuario').limit(1).execute()
            self.is_connected = True
            logging.info("✅ Conexión exitosa a Supabase")
            
        except Exception as e:
            logging.error(f"❌ Error conectando a Supabase: {e}")
            self.is_connected = False
            raise
    
    def close(self):
        """Cerrar conexión (Supabase no requiere cerrar explícitamente)"""
        self.is_connected = False
        logging.info("Conexión a Supabase cerrada")
    
    def close_connection(self):
        """Alias para compatibilidad"""
        self.close()
    
    def __del__(self):
        """Destructor para cerrar conexión"""
        self.close()
    
    def initialize_database(self):
        """Verificar que la base de datos esté disponible en Supabase"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Probar acceso a tabla usuarios
            response = self.client.table('usuarios').select('id_usuario').limit(1).execute()
            logging.info("✅ Base de datos Supabase verificada correctamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error verificando base de datos: {e}")
            return False
    
    # ========== AUTENTICACIÓN ==========
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Autenticar un usuario por nombre de usuario y contraseña.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            dict con información del usuario si la autenticación es exitosa, None si falla
        """
        try:
            if not self.is_connected:
                self.connect()
            
            # Consultar usuario por nombre de usuario
            response = self.client.table('usuarios').select('*').eq('nombre_usuario', username).eq('activo', True).execute()
            
            if not response.data:
                logging.warning(f"Usuario no encontrado o inactivo: {username}")
                return None
            
            user = response.data[0]
            stored_password = user['contrasenia']
            
            # Verificar la contraseña usando bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                logging.info(f"✅ Autenticación exitosa para usuario: {username}")
                
                # Actualizar último acceso
                self.client.table('usuarios').update({'ultimo_acceso': datetime.now().isoformat()}).eq('id_usuario', user['id_usuario']).execute()
                
                return {
                    "id_usuario": user['id_usuario'],
                    "username": user['nombre_usuario'],
                    "nombre_completo": user['nombre_completo'],
                    "rol": user['rol']
                }
            else:
                logging.warning(f"Contraseña incorrecta para usuario: {username}")
                return None
                
        except Exception as e:
            logging.error(f"Error durante la autenticación: {e}")
            return None
    
    def create_user(self, username: str, password: str, nombre_completo: str, rol: str = "recepcionista") -> Optional[int]:
        """
        Crear un nuevo usuario en Supabase.
        
        Args:
            username: Nombre de usuario (mínimo 3 caracteres)
            password: Contraseña en texto plano
            nombre_completo: Nombre completo del usuario
            rol: Rol del usuario (administrador, recepcionista, sistemas)
            
        Returns:
            ID del usuario creado, o None si hay error
        """
        try:
            if not self.is_connected:
                self.connect()
            
            # Validar longitud del nombre de usuario
            if len(username) < 3:
                logging.error("El nombre de usuario debe tener al menos 3 caracteres")
                return None
            
            # Verificar si el usuario ya existe
            response = self.client.table('usuarios').select('id_usuario').eq('nombre_usuario', username).execute()
            
            if response.data:
                logging.warning(f"El usuario '{username}' ya existe")
                return None
            
            # Hashear la contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Insertar nuevo usuario
            user_data = {
                'nombre_usuario': username,
                'contrasenia': hashed_password,
                'nombre_completo': nombre_completo,
                'rol': rol,
                'activo': True
            }
            
            response = self.client.table('usuarios').insert(user_data).execute()
            
            if response.data:
                user_id = response.data[0]['id_usuario']
                logging.info(f"✅ Usuario '{username}' creado exitosamente con ID: {user_id}")
                return user_id
            else:
                logging.error(f"No se pudo crear el usuario '{username}'")
                return None
                
        except Exception as e:
            logging.error(f"Error al crear usuario: {e}")
            return None
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """
        Actualizar la contraseña de un usuario existente.
        
        Args:
            username: Nombre de usuario
            new_password: Nueva contraseña en texto plano
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        try:
            if not self.is_connected:
                self.connect()
            
            # Obtener usuario
            response = self.client.table('usuarios').select('id_usuario').eq('nombre_usuario', username).execute()
            
            if not response.data:
                logging.warning(f"Usuario no encontrado: {username}")
                return False
            
            user_id = response.data[0]['id_usuario']
            
            # Hashear la nueva contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            # Actualizar contraseña
            update_response = self.client.table('usuarios').update({'contrasenia': hashed_password}).eq('id_usuario', user_id).execute()
            
            if update_response.data:
                logging.info(f"✅ Contraseña actualizada para usuario: {username}")
                return True
            else:
                logging.error(f"No se pudo actualizar la contraseña para {username}")
                return False
                    
        except Exception as e:
            logging.error(f"Error al actualizar contraseña: {e}")
            return False
    
    # ========== PRODUCTOS ==========
    
    def get_all_products(self) -> List[Dict]:
        """Obtener todos los productos activos con stock"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Obtener productos varios
            response_varios = self.client.table('ca_productos_varios').select('*, inventario(stock_actual)').eq('activo', True).execute()
            productos = response_varios.data or []
            
            # Obtener suplementos
            response_suplementos = self.client.table('ca_suplementos').select('*, inventario(stock_actual)').eq('activo', True).execute()
            productos.extend(response_suplementos.data or [])
            
            logging.info(f"Obtenidos {len(productos)} productos activos")
            return productos
        
        except Exception as e:
            logging.error(f"Error obteniendo productos: {e}")
            return []
    
    def search_products(self, search_text: str) -> List[Dict]:
        """Buscar productos por código o nombre"""
        try:
            if not self.is_connected:
                self.connect()
            
            search_pattern = f"%{search_text}%"
            productos = []
            
            # Buscar en productos varios
            response_varios = self.client.table('ca_productos_varios').select('*').or_(
                f"nombre.ilike.{search_pattern},codigo_barras.ilike.{search_pattern},codigo_interno.ilike.{search_pattern}"
            ).eq('activo', True).execute()
            
            productos.extend(response_varios.data or [])
            
            # Buscar en suplementos
            response_suplementos = self.client.table('ca_suplementos').select('*').or_(
                f"nombre.ilike.{search_pattern},codigo_barras.ilike.{search_pattern},codigo_interno.ilike.{search_pattern}"
            ).eq('activo', True).execute()
            
            productos.extend(response_suplementos.data or [])
            
            logging.info(f"Encontrados {len(productos)} productos para '{search_text}'")
            return productos
            
        except Exception as e:
            logging.error(f"Error buscando productos: {e}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Buscar producto por código de barras"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Buscar en productos varios
            response_varios = self.client.table('ca_productos_varios').select('*').eq('codigo_barras', barcode).eq('activo', True).execute()
            
            if response_varios.data:
                return response_varios.data[0]
            
            # Buscar en suplementos
            response_suplementos = self.client.table('ca_suplementos').select('*').eq('codigo_barras', barcode).eq('activo', True).execute()
            
            if response_suplementos.data:
                return response_suplementos.data[0]
            
            logging.warning(f"Producto con código de barras {barcode} no encontrado")
            return None
        
        except Exception as e:
            logging.error(f"Error buscando producto por código de barras: {e}")
            return None
    
    def get_product_by_code(self, code: str) -> Optional[Dict]:
        """Buscar producto por código interno"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Buscar en productos varios
            response_varios = self.client.table('ca_productos_varios').select('*').eq('codigo_interno', code).eq('activo', True).execute()
            
            if response_varios.data:
                return response_varios.data[0]
            
            # Buscar en suplementos
            response_suplementos = self.client.table('ca_suplementos').select('*').eq('codigo_interno', code).eq('activo', True).execute()
            
            if response_suplementos.data:
                return response_suplementos.data[0]
            
            logging.warning(f"Producto con código interno {code} no encontrado")
            return None
        
        except Exception as e:
            logging.error(f"Error buscando producto por código interno: {e}")
            return None
    
    # ========== VENTAS ==========
    
    def create_sale(self, venta_data: Dict) -> int:
        """Crear nueva venta con transacción"""
        try:
            if not self.is_connected:
                self.connect()
            
            # Calcular totales
            subtotal = venta_data['total']
            descuento = venta_data.get('descuento', 0)
            impuestos = venta_data.get('impuestos', 0)
            
            # Preparar datos de venta
            venta_insert = {
                'id_usuario': venta_data['id_usuario'],
                'id_miembro': venta_data.get('id_miembro'),
                'fecha': venta_data.get('fecha', datetime.now().isoformat()),
                'subtotal': float(subtotal),
                'descuento': float(descuento),
                'impuestos': float(impuestos),
                'total': float(venta_data['total']),
                'metodo_pago': venta_data.get('metodo_pago', 'efectivo'),
                'tipo_venta': venta_data.get('tipo_venta', 'producto'),
                'estado': 'completada'
            }
            
            # Insertar venta
            response = self.client.table('ventas').insert(venta_insert).execute()
            
            if not response.data:
                logging.error("Error insertando venta")
                return None
            
            venta_id = response.data[0]['id_venta']
            
            # Insertar detalles y actualizar stock
            for item in venta_data.get('productos', []):
                # Obtener información del producto
                producto_response = self.client.table('ca_productos_varios').select('codigo_interno, nombre, descripcion').eq('id_producto', item['id_producto']).execute()
                
                if not producto_response.data:
                    logging.error(f"Producto {item['id_producto']} no encontrado")
                    continue
                
                producto_info = producto_response.data[0]
                codigo_interno = producto_info['codigo_interno']
                
                # Verificar stock
                stock_response = self.client.table('inventario').select('stock_actual').eq('codigo_interno', codigo_interno).eq('tipo_producto', 'varios').execute()
                
                if not stock_response.data or stock_response.data[0]['stock_actual'] < item['cantidad']:
                    logging.error(f"Stock insuficiente para {producto_info['nombre']}")
                    continue
                
                # Insertar detalle
                detalle_data = {
                    'id_venta': venta_id,
                    'codigo_interno': codigo_interno,
                    'tipo_producto': 'varios',
                    'cantidad': item['cantidad'],
                    'precio_unitario': float(item['precio']),
                    'subtotal_linea': float(item['subtotal']),
                    'nombre_producto': producto_info['nombre'],
                    'descripcion_producto': producto_info.get('descripcion')
                }
                
                self.client.table('detalles_venta').insert(detalle_data).execute()
                
                # Actualizar stock
                stock_anterior = stock_response.data[0]['stock_actual']
                stock_nuevo = stock_anterior - item['cantidad']
                
                self.client.table('inventario').update({'stock_actual': stock_nuevo}).eq('codigo_interno', codigo_interno).eq('tipo_producto', 'varios').execute()
                
                # Registrar movimiento
                movimiento_data = {
                    'codigo_interno': codigo_interno,
                    'tipo_producto': 'varios',
                    'tipo_movimiento': 'venta',
                    'cantidad': -item['cantidad'],
                    'stock_anterior': stock_anterior,
                    'stock_nuevo': stock_nuevo,
                    'id_usuario': venta_data['id_usuario'],
                    'id_venta': venta_id
                }
                
                self.client.table('movimientos_inventario').insert(movimiento_data).execute()
            
            logging.info(f"✅ Venta creada: ID {venta_id}, Total: ${venta_data['total']:.2f}")
            return venta_id
            
        except Exception as e:
            logging.error(f"Error creando venta: {e}")
            raise
    
    # ========== MIEMBROS Y ACCESO ==========
    
    def obtener_miembro_por_codigo_qr(self, codigo_qr: str) -> Optional[Dict]:
        """Obtener miembro por código QR"""
        try:
            if not self.is_connected:
                self.connect()
            
            response = self.client.table('miembros').select('*').eq('codigo_qr', codigo_qr).execute()
            
            if response.data:
                return response.data[0]
            
            logging.warning(f"Miembro con código QR {codigo_qr} no encontrado")
            return None
                
        except Exception as e:
            logging.error(f"Error obteniendo miembro: {e}")
            return None
    
    def get_total_members(self) -> int:
        """Obtener total de miembros activos"""
        try:
            if not self.is_connected:
                self.connect()
            
            response = self.client.table('miembros').select('id_miembro', count='exact').eq('activo', True).execute()
            return response.count or 0
        except Exception as e:
            logging.error(f"Error obteniendo total de miembros: {e}")
            return 0
    
    # ========== GESTIÓN DE PRODUCTOS E INVENTARIO ==========
    
    def producto_existe(self, codigo_interno: str) -> bool:
        """
        Verificar si un código interno ya existe en productos varios o suplementos.
        
        Args:
            codigo_interno: Código interno del producto a verificar
            
        Returns:
            True si el código ya existe, False si está disponible
        """
        try:
            if not self.is_connected:
                self.connect()
            
            # Buscar en productos varios
            response_varios = self.client.table('ca_productos_varios').select('id_producto').eq('codigo_interno', codigo_interno).limit(1).execute()
            
            if response_varios.data:
                return True
            
            # Buscar en suplementos
            response_suplementos = self.client.table('ca_suplementos').select('id_suplemento').eq('codigo_interno', codigo_interno).limit(1).execute()
            
            if response_suplementos.data:
                return True
            
            return False
                
        except Exception as e:
            logging.error(f"Error verificando existencia de producto: {e}")
            return False
    
    def insertar_producto_varios(self, producto_data: Dict) -> bool:
        """
        Insertar un nuevo producto normal (varios) en Supabase.
        
        Args:
            producto_data: Diccionario con los datos del producto
                {
                    'codigo_interno': str,
                    'codigo_barras': str (opcional),
                    'nombre': str,
                    'descripcion': str (opcional),
                    'precio_venta': Decimal,
                    'categoria': str,
                    'requiere_refrigeracion': bool,
                    'peso_gr': Decimal (opcional),
                    'activo': bool
                }
                
        Returns:
            True si se insertó correctamente, False en caso de error
        """
        try:
            if not self.is_connected:
                self.connect()
            
            producto_insert = {
                'codigo_interno': producto_data['codigo_interno'],
                'codigo_barras': producto_data.get('codigo_barras'),
                'nombre': producto_data['nombre'],
                'descripcion': producto_data.get('descripcion'),
                'precio_venta': float(producto_data['precio_venta']),
                'categoria': producto_data.get('categoria', 'General'),
                'requiere_refrigeracion': bool(producto_data.get('requiere_refrigeracion', False)),
                'peso_gr': float(producto_data['peso_gr']) if producto_data.get('peso_gr') else None,
                'activo': bool(producto_data.get('activo', True))
            }
            
            response = self.client.table('ca_productos_varios').insert(producto_insert).execute()
            
            if response.data:
                id_producto = response.data[0]['id_producto']
                logging.info(f"✅ Producto varios '{producto_data['nombre']}' insertado con ID: {id_producto}")
                return True
            else:
                logging.error(f"No se pudo insertar el producto '{producto_data['nombre']}'")
                return False
                
        except Exception as e:
            logging.error(f"Error insertando producto varios: {e}")
            return False
                    producto_data['precio_venta'],
                    producto_data.get('categoria', 'General'),
                    producto_data.get('requiere_refrigeracion', False),
                    producto_data.get('peso_gr'),
                    producto_data.get('activo', True)
                ))
                
                id_producto = cursor.fetchone()['id_producto']
                self.connection.commit()
                
                logging.info(f"Producto varios '{producto_data['nombre']}' insertado con ID: {id_producto}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error insertando producto varios: {e}")
            return False
    
    def insertar_suplemento(self, suplemento_data: Dict) -> bool:
        """
        Insertar un nuevo suplemento en la base de datos.
        
        Args:
            suplemento_data: Diccionario con los datos del suplemento
                {
                    'codigo_interno': str,
                    'codigo_barras': str (opcional),
                    'nombre': str,
                    'descripcion': str (opcional),
                    'marca': str,
                    'tipo': str,
                    'peso_neto_gr': Decimal (opcional),
                    'precio_venta': Decimal,
                    'activo': bool,
                    'fecha_vencimiento': str (formato YYYY-MM-DD, opcional)
                }
                
        Returns:
            True si se insertó correctamente, False en caso de error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ca_suplementos (
                        codigo_interno, codigo_barras, nombre, descripcion,
                        marca, tipo, peso_neto_gr, precio_venta,
                        activo, fecha_vencimiento
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id_suplemento
                """, (
                    suplemento_data['codigo_interno'],
                    suplemento_data.get('codigo_barras'),
                    suplemento_data['nombre'],
                    suplemento_data.get('descripcion'),
                    suplemento_data['marca'],
                    suplemento_data['tipo'],
                    suplemento_data.get('peso_neto_gr'),
                    suplemento_data['precio_venta'],
                    suplemento_data.get('activo', True),
                    suplemento_data.get('fecha_vencimiento')
                ))
                
                id_suplemento = cursor.fetchone()['id_suplemento']
                self.connection.commit()
                
                logging.info(f"Suplemento '{suplemento_data['nombre']}' insertado con ID: {id_suplemento}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error insertando suplemento: {e}")
            return False
    
    def crear_inventario(self, inventario_data: Dict) -> bool:
        """
        Crear un registro de inventario para un producto físico.
        
        Args:
            inventario_data: Diccionario con los datos del inventario
                {
                    'codigo_interno': str,
                    'tipo_producto': str ('varios' o 'suplemento'),
                    'stock_actual': int,
                    'stock_minimo': int,
                    'id_ubicacion': int,  # ID del catálogo ca_ubicaciones
                    'activo': bool
                }
                
        Returns:
            True si se creó correctamente, False en caso de error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO inventario (
                        codigo_interno, tipo_producto, stock_actual,
                        stock_minimo, id_ubicacion, activo
                    ) VALUES (
                        %s, %s::tipo_producto_fisico, %s, %s, %s, %s
                    )
                    RETURNING id_inventario
                """, (
                    inventario_data['codigo_interno'],
                    inventario_data['tipo_producto'],
                    inventario_data.get('stock_actual', 0),
                    inventario_data.get('stock_minimo', 5),
                    inventario_data.get('id_ubicacion', 1),  # Default a Zona Lockers (id=1)
                    inventario_data.get('activo', True)
                ))
                
                id_inventario = cursor.fetchone()['id_inventario']
                self.connection.commit()
                
                logging.info(f"Inventario creado para '{inventario_data['codigo_interno']}' con ID: {id_inventario}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except Exception:
                pass
            logging.error(f"Error creando inventario: {e}")
            return False
    
    # ========== UBICACIONES ==========
    
    def get_ubicaciones(self) -> List[Dict]:
        """Obtener todas las ubicaciones activas"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_ubicacion, nombre, descripcion, activa
                    FROM ca_ubicaciones
                    WHERE activa = TRUE
                    ORDER BY nombre
                """)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo ubicaciones: {e}")
            return []
    
    def get_ubicacion_by_id(self, id_ubicacion: int) -> Optional[Dict]:
        """Obtener una ubicación por ID"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_ubicacion, nombre, descripcion, activa
                    FROM ca_ubicaciones
                    WHERE id_ubicacion = %s
                """, (id_ubicacion,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error obteniendo ubicación: {e}")
            return None
    
    # ========== PRODUCTOS DIGITALES ==========
    
    def get_productos_digitales(self) -> List[Dict]:
        """Obtener todos los productos digitales activos"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_producto_digital, codigo_interno, nombre, descripcion,
                        tipo, precio_venta, duracion_dias, aplica_domingo,
                        aplica_festivo, es_unico, requiere_asignacion, activo
                    FROM ca_productos_digitales
                    WHERE activo = TRUE
                    ORDER BY nombre
                """)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo productos digitales: {e}")
            return []
    
    def get_producto_digital_by_id(self, id_producto_digital: int) -> Optional[Dict]:
        """Obtener producto digital por ID"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_producto_digital, codigo_interno, nombre, descripcion,
                        tipo, precio_venta, duracion_dias, aplica_domingo,
                        aplica_festivo, es_unico, requiere_asignacion, activo
                    FROM ca_productos_digitales
                    WHERE id_producto_digital = %s
                """, (id_producto_digital,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error obteniendo producto digital: {e}")
            return None
    
    def insertar_producto_digital(self, producto_data: Dict) -> Optional[int]:
        """
        Insertar un nuevo producto digital.
        
        Args:
            producto_data: {
                'codigo_interno': str,
                'nombre': str,
                'descripcion': str (opcional),
                'tipo': str ('membresia_gym', 'recargo_dia', etc),
                'precio_venta': Decimal,
                'duracion_dias': int (opcional),
                'aplica_domingo': bool,
                'aplica_festivo': bool,
                'es_unico': bool,
                'requiere_asignacion': bool
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ca_productos_digitales (
                        codigo_interno, nombre, descripcion, tipo,
                        precio_venta, duracion_dias, aplica_domingo,
                        aplica_festivo, es_unico, requiere_asignacion, activo
                    ) VALUES (
                        %s, %s, %s, %s::tipo_producto_digital, %s, %s, %s, %s, %s, %s, TRUE
                    )
                    RETURNING id_producto_digital
                """, (
                    producto_data['codigo_interno'],
                    producto_data['nombre'],
                    producto_data.get('descripcion'),
                    producto_data['tipo'],
                    producto_data.get('precio_venta', 0),
                    producto_data.get('duracion_dias'),
                    producto_data.get('aplica_domingo', False),
                    producto_data.get('aplica_festivo', False),
                    producto_data.get('es_unico', False),
                    producto_data.get('requiere_asignacion', False)
                ))
                
                id_producto = cursor.fetchone()['id_producto_digital']
                self.connection.commit()
                logging.info(f"Producto digital '{producto_data['nombre']}' creado con ID: {id_producto}")
                return id_producto
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error insertando producto digital: {e}")
            return None
    
    # ========== LOCKERS ==========
    
    def get_lockers(self) -> List[Dict]:
        """Obtener todos los lockers activos"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_locker, numero, ubicacion, tipo, requiere_llave, activo
                    FROM lockers
                    WHERE activo = TRUE
                    ORDER BY numero
                """)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo lockers: {e}")
            return []
    
    def get_locker_by_id(self, id_locker: int) -> Optional[Dict]:
        """Obtener locker por ID"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_locker, numero, ubicacion, tipo, requiere_llave, activo
                    FROM lockers
                    WHERE id_locker = %s
                """, (id_locker,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error obteniendo locker: {e}")
            return None
    
    def insertar_locker(self, locker_data: Dict) -> Optional[int]:
        """
        Insertar un nuevo locker.
        
        Args:
            locker_data: {
                'numero': str,
                'ubicacion': str,
                'tipo': str (default: 'estándar'),
                'requiere_llave': bool
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO lockers (numero, ubicacion, tipo, requiere_llave, activo)
                    VALUES (%s, %s, %s::tipo_locker, %s, TRUE)
                    RETURNING id_locker
                """, (
                    locker_data['numero'],
                    locker_data.get('ubicacion', 'Zona Lockers'),
                    locker_data.get('tipo', 'estándar'),
                    locker_data.get('requiere_llave', True)
                ))
                
                id_locker = cursor.fetchone()['id_locker']
                self.connection.commit()
                logging.info(f"Locker '{locker_data['numero']}' creado con ID: {id_locker}")
                return id_locker
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error insertando locker: {e}")
            return None
    
    # ========== ASIGNACIONES ACTIVAS ==========
    
    def crear_asignacion_activa(self, asignacion_data: Dict) -> Optional[int]:
        """
        Crear una asignación activa (membresía o locker).
        
        Args:
            asignacion_data: {
                'id_miembro': int,
                'id_producto_digital': int,
                'id_venta': int (opcional),
                'id_locker': int (opcional),
                'fecha_inicio': str (YYYY-MM-DD),
                'fecha_fin': str (YYYY-MM-DD),
                'estado': str (default: 'activa')
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO asignaciones_activas (
                        id_miembro, id_producto_digital, id_venta, id_locker,
                        activa, cancelada, fecha_inicio, fecha_fin, estado
                    ) VALUES (
                        %s, %s, %s, %s, TRUE, FALSE, %s, %s, %s
                    )
                    RETURNING id_asignacion
                """, (
                    asignacion_data['id_miembro'],
                    asignacion_data['id_producto_digital'],
                    asignacion_data.get('id_venta'),
                    asignacion_data.get('id_locker'),
                    asignacion_data['fecha_inicio'],
                    asignacion_data['fecha_fin'],
                    asignacion_data.get('estado', 'activa')
                ))
                
                id_asignacion = cursor.fetchone()['id_asignacion']
                self.connection.commit()
                logging.info(f"Asignación activa creada con ID: {id_asignacion}")
                return id_asignacion
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error creando asignación activa: {e}")
            return None
    
    def get_asignaciones_activas_por_miembro(self, id_miembro: int) -> List[Dict]:
        """Obtener asignaciones activas de un miembro"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_asignacion, id_miembro, id_producto_digital, id_venta,
                        id_locker, activa, cancelada, fecha_inicio, fecha_fin,
                        estado, fecha_cancelacion
                    FROM asignaciones_activas
                    WHERE id_miembro = %s AND activa = TRUE
                    ORDER BY fecha_inicio DESC
                """, (id_miembro,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo asignaciones activas: {e}")
            return []
    
    def cancelar_asignacion(self, id_asignacion: int) -> bool:
        """Cancelar una asignación activa"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE asignaciones_activas
                    SET activa = FALSE, cancelada = TRUE, 
                        estado = 'cancelada', fecha_cancelacion = CURRENT_DATE
                    WHERE id_asignacion = %s
                """, (id_asignacion,))
                
                self.connection.commit()
                logging.info(f"Asignación {id_asignacion} cancelada")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error cancelando asignación: {e}")
            return False
    
    # ========== REGISTRO DE ENTRADAS ==========
    
    def registrar_entrada(self, entrada_data: Dict) -> Optional[int]:
        """
        Registrar una entrada al gimnasio.
        
        Args:
            entrada_data: {
                'id_miembro': int (opcional),
                'id_personal': int (opcional),
                'nombre_visitante': str (opcional),
                'tipo_acceso': str ('miembro', 'personal', 'visitante'),
                'area_accedida': str (default: 'General'),
                'dispositivo_registro': str (opcional),
                'notas': str (opcional),
                'autorizado_por': str (opcional),
                'id_venta_acceso': int (opcional)
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO registro_entradas (
                        id_miembro, id_personal, nombre_visitante, tipo_acceso,
                        area_accedida, dispositivo_registro, notas, autorizado_por,
                        id_venta_acceso, fecha_entrada
                    ) VALUES (
                        %s, %s, %s, %s::tipo_acceso_registro, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                    )
                    RETURNING id_entrada
                """, (
                    entrada_data.get('id_miembro'),
                    entrada_data.get('id_personal'),
                    entrada_data.get('nombre_visitante'),
                    entrada_data['tipo_acceso'],
                    entrada_data.get('area_accedida', 'General'),
                    entrada_data.get('dispositivo_registro'),
                    entrada_data.get('notas'),
                    entrada_data.get('autorizado_por'),
                    entrada_data.get('id_venta_acceso')
                ))
                
                id_entrada = cursor.fetchone()['id_entrada']
                self.connection.commit()
                logging.info(f"Entrada registrada con ID: {id_entrada}")
                return id_entrada
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error registrando entrada: {e}")
            return None
    
    def registrar_salida(self, id_entrada: int) -> bool:
        """Registrar la salida de una persona"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE registro_entradas
                    SET fecha_salida = CURRENT_TIMESTAMP
                    WHERE id_entrada = %s
                """, (id_entrada,))
                
                self.connection.commit()
                logging.info(f"Salida registrada para entrada {id_entrada}")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error registrando salida: {e}")
            return False
    
    def get_historial_entradas(self, id_miembro: int, limite: int = 50) -> List[Dict]:
        """Obtener historial de entradas de un miembro"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_entrada, id_miembro, fecha_entrada, fecha_salida,
                        area_accedida, notas
                    FROM registro_entradas
                    WHERE id_miembro = %s
                    ORDER BY fecha_entrada DESC
                    LIMIT %s
                """, (id_miembro, limite))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo historial de entradas: {e}")
            return []
    
    # ========== VENTAS DIGITALES (APP) ==========
    
    def crear_venta_digital(self, venta_data: Dict) -> Optional[int]:
        """
        Crear una venta digital desde la app.
        
        Args:
            venta_data: {
                'id_miembro': int,
                'id_producto_digital': int,
                'fecha_inicio': str (YYYY-MM-DD),
                'fecha_fin': str (YYYY-MM-DD),
                'monto': Decimal,
                'metodo_pago': str ('efectivo', 'tarjeta_debito', 'tarjeta_credito'),
                'referencia_pago': str (opcional),
                'id_locker': int (opcional),
                'id_usuario': int (opcional)
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ventas_digitales (
                        id_miembro, id_producto_digital, id_locker, id_usuario,
                        fecha_compra, monto, metodo_pago, referencia_pago,
                        estado, fecha_inicio, fecha_fin
                    ) VALUES (
                        %s, %s, %s, %s, CURRENT_TIMESTAMP, %s,
                        %s::tipo_metodo_pago, %s, %s::tipo_estado_venta_digital,
                        %s, %s
                    )
                    RETURNING id_venta_digital
                """, (
                    venta_data['id_miembro'],
                    venta_data['id_producto_digital'],
                    venta_data.get('id_locker'),
                    venta_data.get('id_usuario'),
                    venta_data['monto'],
                    venta_data.get('metodo_pago', 'efectivo'),
                    venta_data.get('referencia_pago'),
                    venta_data.get('estado', 'pendiente_pago'),
                    venta_data['fecha_inicio'],
                    venta_data['fecha_fin']
                ))
                
                id_venta = cursor.fetchone()['id_venta_digital']
                self.connection.commit()
                logging.info(f"Venta digital creada con ID: {id_venta}")
                return id_venta
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error creando venta digital: {e}")
            return None
    
    def get_ventas_digitales_por_miembro(self, id_miembro: int) -> List[Dict]:
        """Obtener ventas digitales de un miembro"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_venta_digital, id_miembro, id_producto_digital,
                        id_locker, fecha_compra, monto, metodo_pago,
                        estado, fecha_inicio, fecha_fin
                    FROM ventas_digitales
                    WHERE id_miembro = %s
                    ORDER BY fecha_compra DESC
                """, (id_miembro,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo ventas digitales: {e}")
            return []
    
    def actualizar_estado_venta_digital(self, id_venta_digital: int, nuevo_estado: str) -> bool:
        """Actualizar el estado de una venta digital"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ventas_digitales
                    SET estado = %s::tipo_estado_venta_digital
                    WHERE id_venta_digital = %s
                """, (nuevo_estado, id_venta_digital))
                
                self.connection.commit()
                logging.info(f"Venta digital {id_venta_digital} actualizada a estado: {nuevo_estado}")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error actualizando venta digital: {e}")
            return False
    
    # ========== NOTIFICACIONES DE PAGO ==========
    
    def crear_notificacion_pago(self, notif_data: Dict) -> Optional[int]:
        """
        Crear una notificación de pago.
        
        Args:
            notif_data: {
                'id_miembro': int,
                'id_venta_digital': int (opcional),
                'tipo_notificacion': str,
                'asunto': str,
                'descripcion': str (opcional),
                'monto_pendiente': Decimal (opcional),
                'fecha_vencimiento': str (YYYY-MM-DD, opcional),
                'para_miembro': bool,
                'para_recepcion': bool,
                'codigo_pago_generado': str (opcional)
            }
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO notificaciones_pos (
                        id_miembro, id_venta_digital, tipo_notificacion, asunto,
                        descripcion, monto_pendiente, fecha_vencimiento,
                        para_miembro, para_recepcion, codigo_pago_generado, leida, respondida
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, FALSE
                    )
                    RETURNING id_notificacion
                """, (
                    notif_data['id_miembro'],
                    notif_data.get('id_venta_digital'),
                    notif_data['tipo_notificacion'],
                    notif_data['asunto'],
                    notif_data.get('descripcion'),
                    notif_data.get('monto_pendiente'),
                    notif_data.get('fecha_vencimiento'),
                    notif_data.get('para_miembro', True),
                    notif_data.get('para_recepcion', True),
                    notif_data.get('codigo_pago_generado')
                ))
                
                id_notif = cursor.fetchone()['id_notificacion']
                self.connection.commit()
                logging.info(f"Notificación de pago creada con ID: {id_notif}")
                return id_notif
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error creando notificación de pago: {e}")
            return None
    
    def get_notificaciones_pendientes(self, para_recepcion: bool = True) -> List[Dict]:
        """Obtener notificaciones de pago pendientes"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_notificacion, id_miembro, id_venta_digital,
                        tipo_notificacion, asunto, descripcion, monto_pendiente,
                        fecha_vencimiento, codigo_pago_generado, leida, respondida,
                        creada_en
                    FROM notificaciones_pos
                    WHERE leida = FALSE AND respondida = FALSE
                        AND (%s = FALSE OR para_recepcion = TRUE)
                    ORDER BY creada_en DESC
                """, (not para_recepcion,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo notificaciones pendientes: {e}")
            return []
    
    def marcar_notificacion_como_leida(self, id_notificacion: int) -> bool:
        """Marcar una notificación como leída"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE notificaciones_pos
                    SET leida = TRUE
                    WHERE id_notificacion = %s
                """, (id_notificacion,))
                
                self.connection.commit()
                logging.info(f"Notificación {id_notificacion} marcada como leída")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error marcando notificación como leída: {e}")
            return False
    
    # ========== TURNOS DE CAJA ==========
    
    def abrir_turno_caja(self, id_usuario: int, monto_inicial: Decimal = 0) -> Optional[int]:
        """Abrir un nuevo turno de caja"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO turnos_caja (
                        id_usuario, monto_inicial, cerrado
                    ) VALUES (
                        %s, %s, FALSE
                    )
                    RETURNING id_turno
                """, (id_usuario, monto_inicial))
                
                id_turno = cursor.fetchone()['id_turno']
                self.connection.commit()
                logging.info(f"Turno de caja abierto con ID: {id_turno} para usuario {id_usuario}")
                return id_turno
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error abriendo turno de caja: {e}")
            return None
    
    def get_turno_activo(self, id_usuario: int) -> Optional[Dict]:
        """Obtener el turno activo de un usuario"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_turno, id_usuario, fecha_apertura, monto_inicial,
                        total_ventas_efectivo, monto_esperado, cerrado
                    FROM turnos_caja
                    WHERE id_usuario = %s AND cerrado = FALSE
                    ORDER BY fecha_apertura DESC
                    LIMIT 1
                """, (id_usuario,))
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error obteniendo turno activo: {e}")
            return None
    
    def cerrar_turno_caja(self, id_turno: int, monto_real_cierre: Decimal) -> bool:
        """Cerrar un turno de caja"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # Obtener datos del turno
                cursor.execute("""
                    SELECT monto_inicial, total_ventas_efectivo, monto_esperado
                    FROM turnos_caja
                    WHERE id_turno = %s AND cerrado = FALSE
                """, (id_turno,))
                
                turno = cursor.fetchone()
                if not turno:
                    logging.warning(f"Turno {id_turno} no encontrado o ya cerrado")
                    return False
                
                diferencia = monto_real_cierre - turno['monto_esperado']
                
                cursor.execute("""
                    UPDATE turnos_caja
                    SET 
                        fecha_cierre = CURRENT_TIMESTAMP,
                        monto_real_cierre = %s,
                        diferencia = %s,
                        cerrado = TRUE,
                        actualizado_en = CURRENT_TIMESTAMP
                    WHERE id_turno = %s
                """, (monto_real_cierre, diferencia, id_turno))
                
                self.connection.commit()
                logging.info(f"Turno {id_turno} cerrado. Diferencia: ${diferencia:.2f}")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error cerrando turno de caja: {e}")
            return False
    
    # ========================================================================
    # MÉTODOS PARA PAGOS EN EFECTIVO (Escaneo de Códigos QR)
    # ========================================================================
    
    def buscar_notificacion_por_codigo_pago(self, codigo_pago: str) -> Optional[Dict]:
        """Buscar una notificación de pago pendiente por código generado"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        n.id_notificacion,
                        n.id_miembro,
                        n.id_venta_digital,
                        n.tipo_notificacion,
                        n.asunto,
                        n.monto_pendiente,
                        n.codigo_pago_generado,
                        m.nombres,
                        m.apellido_paterno,
                        m.apellido_materno,
                        m.telefono
                    FROM notificaciones_pos n
                    INNER JOIN miembros m ON n.id_miembro = m.id_miembro
                    WHERE n.codigo_pago_generado = %s
                      AND n.respondida = FALSE
                """, (codigo_pago,))
                
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error buscando notificación por código: {e}")
            return None
    
    def obtener_detalle_notificacion(self, id_notificacion: int) -> Optional[Dict]:
        """Obtener detalles completos de una notificación de pago para confirmación"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        m.nombres, m.apellido_paterno, m.apellido_materno,
                        m.telefono, m.email,
                        pd.nombre as producto_nombre,
                        pd.descripcion as producto_descripcion,
                        pd.tipo as producto_tipo,
                        n.monto_pendiente,
                        n.id_miembro,
                        n.id_venta_digital
                    FROM notificaciones_pos n
                    INNER JOIN miembros m ON n.id_miembro = m.id_miembro
                    LEFT JOIN ventas_digitales vd ON n.id_venta_digital = vd.id_venta_digital
                    LEFT JOIN ca_productos_digitales pd ON vd.id_producto_digital = pd.id_producto_digital
                    WHERE n.id_notificacion = %s
                """, (id_notificacion,))
                
                return cursor.fetchone()
        except Exception as e:
            logging.error(f"Error obteniendo detalles de notificación: {e}")
            return None
    
    def obtener_notificaciones_pendientes(self) -> List[Dict]:
        """Obtener todas las notificaciones de pago pendientes para recepción"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        n.id_notificacion,
                        n.id_miembro,
                        n.id_venta_digital,
                        n.tipo_notificacion,
                        n.asunto,
                        n.monto_pendiente,
                        n.fecha_vencimiento,
                        n.creada_en,
                        n.codigo_pago_generado,
                        m.nombres,
                        m.apellido_paterno,
                        m.apellido_materno,
                        m.telefono
                    FROM notificaciones_pos n
                    INNER JOIN miembros m ON n.id_miembro = m.id_miembro
                    WHERE n.para_recepcion = TRUE
                      AND n.respondida = FALSE
                      AND n.tipo_notificacion IN ('membresia_pendiente', 'visita_pendiente', 'pago_pendiente')
                    ORDER BY n.creada_en DESC
                """)
                
                return cursor.fetchall() or []
        except Exception as e:
            logging.error(f"Error obteniendo notificaciones pendientes: {e}")
            return []
    
    def sincronizar_notificacion_supabase(self, id_notificacion: int, datos_supabase: Dict) -> bool:
        """Sincronizar una notificación que viene de Supabase a PostgreSQL local"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            logging.info(f"[sincronizar_notificacion_supabase] Sincronizando notificación {id_notificacion} desde Supabase...")
            logging.info(f"[sincronizar_notificacion_supabase] Datos recibidos de Supabase:")
            logging.info(f"  - id_miembro: {datos_supabase.get('id_miembro')}")
            logging.info(f"  - id_venta_digital: {datos_supabase.get('id_venta_digital')}")
            logging.info(f"  - codigo_pago_generado: {datos_supabase.get('codigo_pago_generado')}")
            logging.info(f"  - monto_pendiente: {datos_supabase.get('monto_pendiente')}")
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Verificar si la notificación ya existe
                cursor.execute("SELECT id_notificacion, id_venta_digital FROM notificaciones_pos WHERE id_notificacion = %s", (id_notificacion,))
                existe = cursor.fetchone()
                
                if existe:
                    logging.info(f"[sincronizar_notificacion_supabase] Notificación {id_notificacion} ya existe en PostgreSQL")
                    logging.info(f"  - id_venta_digital en BD: {existe['id_venta_digital']}")
                    return True
                
                # Insertar notificación
                logging.info(f"[sincronizar_notificacion_supabase] Insertando notificación en PostgreSQL...")
                
                # Preparar valores con defaults defensivos
                tipo_notif = datos_supabase.get('tipo_notificacion') or 'pago_efectivo_pendiente'
                asunto = datos_supabase.get('asunto') or 'Pago en Efectivo Pendiente'
                descripcion = datos_supabase.get('descripcion') or ''
                monto = datos_supabase.get('monto_pendiente') or 0
                codigo = datos_supabase.get('codigo_pago_generado')
                para_miembro = bool(datos_supabase.get('para_miembro', False))
                fecha_vencimiento = datos_supabase.get('fecha_vencimiento')
                id_miembro = datos_supabase.get('id_miembro')
                id_venta = datos_supabase.get('id_venta_digital')
                
                logging.info(f"[sincronizar_notificacion_supabase] Valores para INSERT:")
                logging.info(f"  - tipo_notificacion: {tipo_notif}")
                logging.info(f"  - asunto: {asunto}")
                logging.info(f"  - codigo_pago_generado: {codigo}")
                logging.info(f"  - id_venta_digital: {id_venta}")
                
                cursor.execute("""
                    INSERT INTO notificaciones_pos (
                        id_notificacion, id_miembro, id_venta_digital,
                        tipo_notificacion, asunto, descripcion,
                        monto_pendiente, codigo_pago_generado,
                        respondida, leida, para_miembro, para_recepcion,
                        creada_en, fecha_vencimiento
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        FALSE, FALSE, %s, TRUE, NOW(), %s
                    )
                """, (
                    id_notificacion,
                    id_miembro,
                    id_venta,
                    tipo_notif,
                    asunto,
                    descripcion,
                    monto,
                    codigo,
                    para_miembro,
                    fecha_vencimiento
                ))
                
                self.connection.commit()
                logging.info(f"[sincronizar_notificacion_supabase] ✅ Notificación {id_notificacion} insertada")
                
                # Verificar que se insertó correctamente
                cursor.execute("""
                    SELECT id_notificacion, id_miembro, id_venta_digital, codigo_pago_generado
                    FROM notificaciones_pos
                    WHERE id_notificacion = %s
                """, (id_notificacion,))
                
                verificacion = cursor.fetchone()
                if verificacion:
                    logging.info(f"[sincronizar_notificacion_supabase] ✅ Verificación exitosa:")
                    logging.info(f"  - id_notificacion: {verificacion['id_notificacion']}")
                    logging.info(f"  - id_miembro: {verificacion['id_miembro']}")
                    logging.info(f"  - id_venta_digital: {verificacion['id_venta_digital']}")
                    logging.info(f"  - codigo_pago_generado: {verificacion['codigo_pago_generado']}")
                    return True
                else:
                    logging.error(f"[sincronizar_notificacion_supabase] ❌ Verificación fallida: notificación no encontrada después de insertar")
                    return False
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"[sincronizar_notificacion_supabase] ❌ Error sincronizando: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return False
    
    def confirmar_pago_efectivo(self, id_notificacion: int, observaciones: str = None) -> bool:
        """Confirmar pago en efectivo y activar asignación correspondiente"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. Obtener datos de la venta digital
                logging.info(f"[confirmar_pago_efectivo] Iniciando búsqueda de venta digital para notificación {id_notificacion}")
                
                cursor.execute("""
                    SELECT vd.id_venta_digital, vd.id_miembro, vd.id_producto_digital,
                           vd.fecha_inicio, vd.fecha_fin, vd.id_locker,
                           pd.requiere_asignacion, pd.tipo
                    FROM notificaciones_pos n
                    INNER JOIN ventas_digitales vd ON n.id_venta_digital = vd.id_venta_digital
                    INNER JOIN ca_productos_digitales pd ON vd.id_producto_digital = pd.id_producto_digital
                    WHERE n.id_notificacion = %s AND n.id_venta_digital IS NOT NULL
                """, (id_notificacion,))
                
                venta = cursor.fetchone()
                
                # Si no encontró por id_venta_digital, buscar la venta digital más reciente del miembro
                if not venta:
                    logging.info(f"[confirmar_pago_efectivo] id_venta_digital es NULL, buscando fallback por miembro...")
                    
                    cursor.execute("""
                        SELECT 
                            n.id_miembro, n.id_venta_digital
                        FROM notificaciones_pos n
                        WHERE n.id_notificacion = %s
                    """, (id_notificacion,))
                    
                    notif = cursor.fetchone()
                    if not notif:
                        logging.error(f"[confirmar_pago_efectivo] CRÍTICO: No se encontró la notificación {id_notificacion}")
                        return False
                    
                    id_miembro = notif['id_miembro']
                    id_venta_notif = notif['id_venta_digital']
                    logging.info(f"[confirmar_pago_efectivo] Notificación encontrada: id_miembro={id_miembro}, id_venta_digital={id_venta_notif}")
                    
                    # Intenta primero con la venta_digital de la notificación (sin INNER JOIN)
                    if id_venta_notif:
                        logging.info(f"[confirmar_pago_efectivo] Intentando obtener venta_digital {id_venta_notif}...")
                        cursor.execute("""
                            SELECT vd.id_venta_digital, vd.id_miembro, vd.id_producto_digital,
                                   vd.fecha_inicio, vd.fecha_fin, vd.id_locker,
                                   pd.requiere_asignacion, pd.tipo
                            FROM ventas_digitales vd
                            LEFT JOIN ca_productos_digitales pd ON vd.id_producto_digital = pd.id_producto_digital
                            WHERE vd.id_venta_digital = %s
                        """, (id_venta_notif,))
                        
                        venta = cursor.fetchone()
                        if venta:
                            logging.info(f"[confirmar_pago_efectivo] ✅ Venta digital encontrada por ID directo: {venta['id_venta_digital']}")
                    
                    # Si aún no hay venta, buscar la más reciente del miembro
                    if not venta:
                        logging.info(f"[confirmar_pago_efectivo] Buscando venta digital más reciente para miembro {id_miembro}...")
                        cursor.execute("""
                            SELECT vd.id_venta_digital, vd.id_miembro, vd.id_producto_digital,
                                   vd.fecha_inicio, vd.fecha_fin, vd.id_locker,
                                   pd.requiere_asignacion, pd.tipo
                            FROM ventas_digitales vd
                            LEFT JOIN ca_productos_digitales pd ON vd.id_producto_digital = pd.id_producto_digital
                            WHERE vd.id_miembro = %s 
                              AND vd.estado != 'activa'
                            ORDER BY vd.id_venta_digital DESC
                            LIMIT 1
                        """, (id_miembro,))
                        
                        venta = cursor.fetchone()
                        if venta:
                            logging.info(f"[confirmar_pago_efectivo] ✅ Venta digital encontrada por fallback: {venta['id_venta_digital']}")
                
                if not venta:
                    logging.error(f"[confirmar_pago_efectivo] CRÍTICO: No se encontró venta digital para notificación {id_notificacion} (miembro {notif['id_miembro']})")
                    return False
                
                # 2. Actualizar venta_digital a 'activa'
                logging.info(f"[confirmar_pago_efectivo] Paso 2: Actualizando venta_digital {venta['id_venta_digital']} a activa...")
                timestamp_actual = datetime.now()
                referencia_pago = f"EFECTIVO_{timestamp_actual.strftime('%Y%m%d%H%M%S')}"
                
                cursor.execute("""
                    UPDATE ventas_digitales
                    SET estado = 'activa',
                        fecha_compra = %s,
                        referencia_pago = %s
                    WHERE id_venta_digital = %s
                """, (timestamp_actual, referencia_pago, venta['id_venta_digital']))
                logging.info(f"[confirmar_pago_efectivo] ✅ ventas_digitales actualizada")
                
                # 3. Actualizar notificación como resuelta
                logging.info(f"[confirmar_pago_efectivo] Paso 3: Actualizando notificación {id_notificacion} como resuelta...")
                cursor.execute("""
                    UPDATE notificaciones_pos
                    SET leida = TRUE,
                        respondida = TRUE,
                        resuelve_en = %s
                    WHERE id_notificacion = %s
                """, (timestamp_actual, id_notificacion))
                logging.info(f"[confirmar_pago_efectivo] ✅ notificaciones_pos actualizada")
                
                # 4. Crear asignación activa
                logging.info(f"[confirmar_pago_efectivo] Paso 4: Creando asignación activa para miembro {venta['id_miembro']}...")
                cursor.execute("""
                    INSERT INTO asignaciones_activas (
                        id_miembro, id_producto_digital, id_venta, id_locker,
                        activa, cancelada, fecha_inicio, fecha_fin, estado
                    ) VALUES (
                        %s, %s, NULL, %s, TRUE, FALSE, %s, %s, 'activa'
                    )
                """, (
                    venta['id_miembro'],
                    venta['id_producto_digital'],
                    venta['id_locker'],
                    venta['fecha_inicio'],
                    venta['fecha_fin']
                ))
                logging.info(f"[confirmar_pago_efectivo] ✅ asignaciones_activas creada")
                
                # 5. Registrar entrada
                logging.info(f"[confirmar_pago_efectivo] Paso 5: Registrando entrada de acceso...")
                obs_completa = f"Pago efectivo confirmado. Ref: {referencia_pago}. {observaciones or ''}"
                
                cursor.execute("""
                    INSERT INTO registro_entradas (
                        id_miembro, tipo_acceso, fecha_entrada,
                        area_accedida, dispositivo_registro, notas
                    ) VALUES (
                        %s, 'miembro', %s, 'Recepción', 'POS', %s
                    )
                """, (venta['id_miembro'], timestamp_actual, obs_completa))
                logging.info(f"[confirmar_pago_efectivo] ✅ registro_entradas creado")
                
                # 6. Crear notificación de pago completado
                logging.info(f"[confirmar_pago_efectivo] Paso 6: Creando notificación de confirmación...")
                cursor.execute("""
                    INSERT INTO notificaciones_pos (
                        id_miembro, id_venta_digital, tipo_notificacion,
                        asunto, descripcion, leida, respondida,
                        para_miembro, para_recepcion
                    ) VALUES (
                        %s, %s, 'pago_completado',
                        'Pago Confirmado',
                        'Tu pago en efectivo ha sido confirmado. Tu membresía/visita está activa.',
                        FALSE, TRUE, TRUE, FALSE
                    )
                """, (venta['id_miembro'], venta['id_venta_digital']))
                logging.info(f"[confirmar_pago_efectivo] ✅ notificaciones_pos (confirmación) creada")
                
                self.connection.commit()
                logging.info(f"[confirmar_pago_efectivo] ✅ TRANSACCIÓN COMPLETADA EXITOSAMENTE: {referencia_pago}")
                return True
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error confirmando pago: {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de conexión
    config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'HTF_DB',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        # Crear instancia del gestor
        db = PostgresManager(config)
        
        # Ejemplo: Autenticar usuario
        user = db.authenticate_user('admin', 'admin123')
        if user:
            print(f"✓ Usuario autenticado: {user['nombre_completo']}")
            print(f"  Rol: {user['rol']}")
        else:
            print("✗ Autenticación fallida")
        
        # Cerrar conexión
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")