"""
Gestor de Base de Datos PostgreSQL para Sistema POS
Compatible con el esquema POS_sql.txt
Usa PostgreSQL local o en servidor dedicado
"""

import logging
import bcrypt
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
import traceback

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 no está instalado. Instala con: pip install psycopg2-binary")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PostgresManager:
    """Gestor de conexión y operaciones con PostgreSQL"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Inicializar conexión a PostgreSQL
        
        Args:
            db_config: Diccionario con la configuración de conexión
                {
                    'host': 'localhost',
                    'port': '5432',
                    'database': 'nombre_db',
                    'user': 'usuario',
                    'password': 'contraseña'
                }
        """
        self.db_config = db_config
        self.connection = None
        self.is_connected = False
        self.connect()
    
    def connect(self):
        """Establecer conexión con PostgreSQL"""
        try:
            if not PSYCOPG2_AVAILABLE:
                logging.error("psycopg2 no está disponible. Instala con: pip install psycopg2-binary")
                raise ImportError("psycopg2 library not installed")
            
            # Conectar a PostgreSQL
            self.connection = psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', '5432'),
                database=self.db_config.get('database'),
                user=self.db_config.get('user'),
                password=self.db_config.get('password'),
                cursor_factory=RealDictCursor
            )
            
            self.is_connected = True
            logging.info("✅ Conexión exitosa a PostgreSQL")
            
        except Exception as e:
            logging.error(f"❌ Error conectando a PostgreSQL: {e}")
            self.is_connected = False
            raise
    
    def close(self):
        """Cerrar conexión a PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            logging.info("Conexión a PostgreSQL cerrada")
    
    def close_connection(self):
        """Alias para compatibilidad"""
        self.close()
    
    def __del__(self):
        """Destructor para cerrar conexión"""
        try:
            self.close()
        except:
            pass
    
    def initialize_database(self):
        """Verificar que la base de datos esté disponible"""
        try:
            if not self.is_connected or not self.connection or self.connection.closed:
                self.connect()
            
            # Probar acceso a tabla usuarios
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id_usuario FROM usuarios LIMIT 1")
            
            logging.info("✅ Base de datos PostgreSQL verificada correctamente")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error verificando base de datos: {e}")
            return False
    
    # ========== UTILIDADES ==========
    
    def query(self, sql: str, params: tuple = None) -> List[Dict]:
        """
        Ejecutar una consulta SELECT y devolver resultados como lista de diccionarios.
        
        Args:
            sql: Sentencia SQL SELECT
            params: Tupla de parámetros para la consulta (opcional)
            
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                results = cursor.fetchall()
                return results if results else []
        except Exception as e:
            logging.error(f"Error en query: {e}")
            return []
    
    def execute(self, sql: str, params: tuple = None) -> bool:
        """
        Ejecutar una consulta INSERT, UPDATE o DELETE.
        
        Args:
            sql: Sentencia SQL INSERT, UPDATE o DELETE
            params: Tupla de parámetros para la consulta (opcional)
            
        Returns:
            True si la operación fue exitosa, False si falló
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Confirmar la transacción
                self.connection.commit()
                return True
        except Exception as e:
            logging.error(f"Error en execute: {e}")
            # Hacer rollback en caso de error
            try:
                self.connection.rollback()
            except:
                pass
            return False
    
    def execute_with_returning(self, sql: str, params: tuple = None) -> Optional[int]:
        """
        Ejecutar una consulta INSERT con RETURNING y devolver el ID generado.
        
        Args:
            sql: Sentencia SQL INSERT con RETURNING
            params: Tupla de parámetros para la consulta (opcional)
            
        Returns:
            ID generado por la inserción, o None si falló
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Obtener el ID retornado
                result = cursor.fetchone()
                self.connection.commit()
                
                if result:
                    return result[0] if isinstance(result, (tuple, list)) else result
                return None
        except Exception as e:
            logging.error(f"Error en execute_with_returning: {e}")
            # Hacer rollback en caso de error
            try:
                self.connection.rollback()
            except:
                pass
            return None
    
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
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # Consultar usuario por nombre de usuario
                cursor.execute("""
                    SELECT id_usuario, nombre_usuario, contrasenia, nombre_completo, rol
                    FROM usuarios
                    WHERE nombre_usuario = %s AND activo = TRUE
                """, (username,))
                
                user = cursor.fetchone()
                
                if not user:
                    logging.warning(f"Usuario no encontrado o inactivo: {username}")
                    return None
                
                stored_password = user['contrasenia']
                
                # Verificar la contraseña usando bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    logging.info(f"✅ Autenticación exitosa para usuario: {username}")
                    
                    # Actualizar último acceso
                    cursor.execute("""
                        UPDATE usuarios 
                        SET ultimo_acceso = %s 
                        WHERE id_usuario = %s
                    """, (datetime.now(), user['id_usuario']))
                    self.connection.commit()
                    
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
        Crear un nuevo usuario en PostgreSQL.
        
        Args:
            username: Nombre de usuario (mínimo 3 caracteres)
            password: Contraseña en texto plano
            nombre_completo: Nombre completo del usuario
            rol: Rol del usuario (administrador, recepcionista, sistemas)
            
        Returns:
            ID del usuario creado, o None si hay error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            # Validar longitud del nombre de usuario
            if len(username) < 3:
                logging.error("El nombre de usuario debe tener al menos 3 caracteres")
                return None
            
            with self.connection.cursor() as cursor:
                # Verificar si el usuario ya existe
                cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s", (username,))
                
                if cursor.fetchone():
                    logging.warning(f"El usuario '{username}' ya existe")
                    return None
                
                # Hashear la contraseña
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                
                # Insertar nuevo usuario
                cursor.execute("""
                    INSERT INTO usuarios (nombre_usuario, contrasenia, nombre_completo, rol, activo)
                    VALUES (%s, %s, %s, %s::tipo_rol_usuario, TRUE)
                    RETURNING id_usuario
                """, (username, hashed_password, nombre_completo, rol))
                
                user_id = cursor.fetchone()['id_usuario']
                self.connection.commit()
                
                logging.info(f"✅ Usuario '{username}' creado exitosamente con ID: {user_id}")
                return user_id
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
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
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # Obtener usuario
                cursor.execute("SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s", (username,))
                user = cursor.fetchone()
                
                if not user:
                    logging.warning(f"Usuario no encontrado: {username}")
                    return False
                
                user_id = user['id_usuario']
                
                # Hashear la nueva contraseña
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
                
                # Actualizar contraseña
                cursor.execute("""
                    UPDATE usuarios 
                    SET contrasenia = %s 
                    WHERE id_usuario = %s
                """, (hashed_password, user_id))
                
                self.connection.commit()
                logging.info(f"✅ Contraseña actualizada para usuario: {username}")
                return True
                    
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error al actualizar contraseña: {e}")
            return False
    
    # ========== PRODUCTOS ==========
    
    def get_all_products(self) -> List[Dict]:
        """Obtener todos los productos activos con stock"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_producto, p.codigo_interno, p.codigo_barras, p.nombre,
                        p.descripcion, p.precio_venta, p.precio_mayoreo,
                        p.cantidad_mayoreo, p.costo_promedio, p.es_inventariable,
                        COALESCE(SUM(i.stock_actual), 0) AS stock_actual,
                        COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible
                    FROM ca_productos p
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                    WHERE p.activo = TRUE
                    GROUP BY p.id_producto
                    ORDER BY p.nombre
                """)
                
                productos = cursor.fetchall()
                logging.info(f"Obtenidos {len(productos)} productos activos")
                return productos
        
        except Exception as e:
            logging.error(f"Error obteniendo productos: {e}")
            return []
    
    def search_products(self, search_text: str) -> List[Dict]:
        """Buscar productos por código o nombre, o listar todos si vacío"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                if search_text.strip():
                    # Búsqueda con texto
                    search_pattern = f"%{search_text}%"
                    cursor.execute("""
                        SELECT 
                            p.id_producto, p.codigo_interno, p.codigo_barras, p.nombre,
                            p.descripcion, p.precio_venta, p.costo_promedio,
                            COALESCE(SUM(i.stock_actual), 0) AS stock_actual,
                            COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible
                        FROM ca_productos p
                        LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                        WHERE p.activo = TRUE
                            AND (p.nombre ILIKE %s OR p.codigo_barras ILIKE %s OR p.codigo_interno ILIKE %s)
                        GROUP BY p.id_producto
                        ORDER BY p.id_producto
                    """, (search_pattern, search_pattern, search_pattern))
                else:
                    # Listar todos ordenados por ID
                    cursor.execute("""
                        SELECT 
                            p.id_producto, p.codigo_interno, p.codigo_barras, p.nombre,
                            p.descripcion, p.precio_venta, p.costo_promedio,
                            COALESCE(SUM(i.stock_actual), 0) AS stock_actual,
                            COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible
                        FROM ca_productos p
                        LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                        WHERE p.activo = TRUE
                        GROUP BY p.id_producto
                        ORDER BY p.id_producto
                    """)
                
                productos = cursor.fetchall()
                logging.info(f"Encontrados {len(productos)} productos para '{search_text}'")
                return productos
            
        except Exception as e:
            logging.error(f"Error buscando productos: {e}")
            return []
    
    def obtener_producto_por_codigo(self, codigo_interno: str) -> Optional[Dict]:
        """Obtener producto por código interno"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_producto, p.codigo_interno, p.nombre, p.es_inventariable,
                        p.tipo_producto_fisico as tipo_producto
                    FROM ca_productos p
                    WHERE p.activo = TRUE AND p.codigo_interno = %s
                """, (codigo_interno,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logging.error(f"Error obteniendo producto por código: {e}")
            return None
    
    def obtener_movimientos_completos(self, limite: int = 1000) -> List[Dict]:
        """Obtener movimientos de inventario completos con información de productos y usuarios"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        mi.id_movimiento,
                        mi.fecha,
                        mi.tipo_movimiento,
                        p.codigo_interno,
                        'varios'::tipo_producto_detalle as tipo_producto,  -- Default value since not stored in movimientos
                        mi.cantidad,
                        mi.stock_anterior,
                        mi.stock_nuevo,
                        mi.motivo,
                        mi.id_usuario,
                        mi.id_venta,
                        p.nombre as nombre_producto,
                        u.nombre_completo as nombre_usuario
                    FROM movimientos_inventario mi
                    INNER JOIN ca_productos p ON mi.id_producto = p.id_producto
                    INNER JOIN usuarios u ON mi.id_usuario = u.id_usuario
                    ORDER BY mi.fecha DESC
                    LIMIT %s
                """, (limite,))
                
                movimientos = cursor.fetchall()
                logging.info(f"Encontrados {len(movimientos)} movimientos completos")
                return movimientos
            
        except Exception as e:
            logging.error(f"Error obteniendo movimientos completos: {e}")
            return []
    
    def obtener_inventario_completo(self) -> List[Dict]:
        """Obtener inventario completo con información de productos y ubicaciones"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_producto,
                        p.codigo_interno,
                        p.nombre,
                        p.descripcion,
                        c.nombre as categoria,
                        i.seccion,
                        p.precio_venta as precio,
                        p.precio_mayoreo,
                        p.cantidad_mayoreo,
                        i.stock_actual,
                        i.stock_minimo,
                        i.costo_promedio,
                        u.nombre as ubicacion,
                        p.requiere_refrigeracion,
                        p.es_inventariable,
                        p.activo
                    FROM ca_productos p
                    LEFT JOIN ca_categorias_producto c ON p.id_categoria = c.id_categoria
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                    LEFT JOIN ca_ubicaciones u ON i.id_ubicacion = u.id_ubicacion
                    WHERE p.activo = TRUE
                    ORDER BY p.nombre
                """)
                
                inventario = cursor.fetchall()
                logging.info(f"Encontrados {len(inventario)} productos en inventario")
                return inventario
            
        except Exception as e:
            logging.error(f"Error obteniendo inventario completo: {e}")
            return []
    
    def obtener_productos_por_categoria(self, categoria: str = None, excluir_categoria: str = None) -> List[Dict]:
        """Obtener productos por categoría o excluyendo una categoría"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                if categoria:
                    # Obtener productos de una categoría específica
                    cursor.execute("""
                        SELECT 
                            p.id_producto, p.codigo_interno, p.nombre, p.descripcion,
                            p.precio_venta, p.precio_mayoreo, p.cantidad_mayoreo, p.costo_promedio,
                            c.nombre as categoria, p.codigo_barras, p.requiere_refrigeracion,
                            p.es_inventariable, p.permite_venta_sin_stock, p.aplica_ieps,
                            p.porcentaje_ieps, p.aplica_iva, p.porcentaje_iva, p.cantidad_medida,
                            um.nombre as unidad_medida, p.activo
                        FROM ca_productos p
                        LEFT JOIN ca_categorias_producto c ON p.id_categoria = c.id_categoria
                        LEFT JOIN ca_unidades_medida um ON p.id_unidad_medida = um.id_unidad_medida
                        WHERE c.nombre = %s AND p.activo = TRUE
                        ORDER BY p.nombre
                    """, (categoria,))
                elif excluir_categoria:
                    # Obtener productos excluyendo una categoría
                    cursor.execute("""
                        SELECT 
                            p.id_producto, p.codigo_interno, p.nombre, p.descripcion,
                            p.precio_venta, p.precio_mayoreo, p.cantidad_mayoreo, p.costo_promedio,
                            c.nombre as categoria, p.codigo_barras, p.requiere_refrigeracion,
                            p.es_inventariable, p.permite_venta_sin_stock, p.aplica_ieps,
                            p.porcentaje_ieps, p.aplica_iva, p.porcentaje_iva, p.cantidad_medida,
                            um.nombre as unidad_medida, p.activo
                        FROM ca_productos p
                        LEFT JOIN ca_categorias_producto c ON p.id_categoria = c.id_categoria
                        LEFT JOIN ca_unidades_medida um ON p.id_unidad_medida = um.id_unidad_medida
                        WHERE (c.nombre IS NULL OR c.nombre != %s) AND p.activo = TRUE
                        ORDER BY p.nombre
                    """, (excluir_categoria,))
                else:
                    # Obtener todos los productos
                    cursor.execute("""
                        SELECT 
                            p.id_producto, p.codigo_interno, p.nombre, p.descripcion,
                            p.precio_venta, p.precio_mayoreo, p.cantidad_mayoreo, p.costo_promedio,
                            c.nombre as categoria, p.codigo_barras, p.requiere_refrigeracion,
                            p.es_inventariable, p.permite_venta_sin_stock, p.aplica_ieps,
                            p.porcentaje_ieps, p.aplica_iva, p.porcentaje_iva, p.cantidad_medida,
                            um.nombre as unidad_medida, p.activo
                        FROM ca_productos p
                        LEFT JOIN ca_categorias_producto c ON p.id_categoria = c.id_categoria
                        LEFT JOIN ca_unidades_medida um ON p.id_unidad_medida = um.id_unidad_medida
                        WHERE p.activo = TRUE
                        ORDER BY p.nombre
                    """)
                
                productos = cursor.fetchall()
                logging.info(f"Encontrados {len(productos)} productos {'de categoría ' + categoria if categoria else 'excluyendo ' + excluir_categoria if excluir_categoria else 'totales'}")
                return productos
            
        except Exception as e:
            logging.error(f"Error obteniendo productos por categoría: {e}")
            return []
    
    def actualizar_producto(self, codigo_interno: str, cambios: Dict) -> bool:
        """Actualizar un producto por código interno"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            # Construir la consulta de actualización dinámicamente
            set_parts = []
            values = []
            for campo, valor in cambios.items():
                set_parts.append(f"{campo} = %s")
                values.append(valor)
            
            if not set_parts:
                return True  # No hay cambios
            
            set_clause = ", ".join(set_parts)
            values.append(codigo_interno)
            
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ca_productos 
                    SET {set_clause}
                    WHERE codigo_interno = %s
                """, values)
                
                self.connection.commit()
                logging.info(f"Producto {codigo_interno} actualizado correctamente")
                return True
            
        except Exception as e:
            logging.error(f"Error actualizando producto {codigo_interno}: {e}")
            return False
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Buscar producto por código de barras"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_producto, p.codigo_interno, p.codigo_barras, p.nombre,
                        p.descripcion, p.precio_venta, p.costo_promedio,
                        COALESCE(SUM(i.stock_actual), 0) AS stock_actual,
                        COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible
                    FROM ca_productos p
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                    WHERE p.codigo_barras = %s AND p.activo = TRUE
                    GROUP BY p.id_producto
                """, (barcode,))
                
                producto = cursor.fetchone()
                
                if producto:
                    return producto
                
                logging.warning(f"Producto con código de barras {barcode} no encontrado")
                return None
        
        except Exception as e:
            logging.error(f"Error buscando producto por código de barras: {e}")
            return None
    
    def get_product_by_code(self, code: str) -> Optional[Dict]:
        """Buscar producto por código interno"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_producto, p.codigo_interno, p.codigo_barras, p.nombre,
                        p.descripcion, p.precio_venta, p.costo_promedio,
                        COALESCE(SUM(i.stock_actual), 0) AS stock_actual,
                        COALESCE(SUM(i.stock_disponible), 0) AS stock_disponible
                    FROM ca_productos p
                    LEFT JOIN inventario i ON p.id_producto = i.id_producto AND i.activo = TRUE
                    WHERE p.codigo_interno = %s AND p.activo = TRUE
                    GROUP BY p.id_producto
                """, (code,))
                
                producto = cursor.fetchone()
                
                if producto:
                    return producto
                
                logging.warning(f"Producto con código interno {code} no encontrado")
                return None
        
        except Exception as e:
            logging.error(f"Error buscando producto por código interno: {e}")
            return None
    
    def producto_existe(self, codigo_interno: str) -> bool:
        """
        Verificar si un código interno ya existe en productos.
        
        Args:
            codigo_interno: Código interno del producto a verificar
            
        Returns:
            True si el código ya existe, False si está disponible
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_producto 
                    FROM ca_productos 
                    WHERE codigo_interno = %s 
                    LIMIT 1
                """, (codigo_interno,))
                
                return cursor.fetchone() is not None
                
        except Exception as e:
            logging.error(f"Error verificando existencia de producto: {e}")
            return False
    
    def insertar_producto(self, producto_data: Dict) -> Optional[int]:
        """
        Insertar un nuevo producto en la base de datos.
        
        Args:
            producto_data: Diccionario con los datos del producto
                {
                    'codigo_interno': str,
                    'codigo_barras': str (opcional),
                    'nombre': str,
                    'descripcion': str (opcional),
                    'precio_venta': Decimal,
                    'precio_mayoreo': Decimal (opcional),
                    'cantidad_mayoreo': int (opcional),
                    'id_categoria': int (opcional),
                    'cantidad_medida': Decimal (opcional),
                    'id_unidad_medida': int (opcional),
                    'requiere_refrigeracion': bool,
                    'es_inventariable': bool,
                    'aplica_iva': bool,
                    'activo': bool
                }
                
        Returns:
            ID del producto creado, o None si hay error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ca_productos (
                        codigo_interno, codigo_barras, nombre, descripcion,
                        precio_venta, precio_mayoreo, cantidad_mayoreo,
                        id_categoria, cantidad_medida, id_unidad_medida,
                        requiere_refrigeracion, es_inventariable, aplica_iva, activo
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id_producto
                """, (
                    producto_data['codigo_interno'],
                    producto_data.get('codigo_barras'),
                    producto_data['nombre'],
                    producto_data.get('descripcion'),
                    producto_data['precio_venta'],
                    producto_data.get('precio_mayoreo'),
                    producto_data.get('cantidad_mayoreo'),
                    producto_data.get('id_categoria'),
                    producto_data.get('cantidad_medida'),
                    producto_data.get('id_unidad_medida'),
                    producto_data.get('requiere_refrigeracion', False),
                    producto_data.get('es_inventariable', True),
                    producto_data.get('aplica_iva', True),
                    producto_data.get('activo', True)
                ))
                
                id_producto = cursor.fetchone()['id_producto']
                self.connection.commit()
                
                logging.info(f"✅ Producto '{producto_data['nombre']}' insertado con ID: {id_producto}")
                return id_producto
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error insertando producto: {e}")
            logging.error(traceback.format_exc())
            return None
    
    def crear_inventario(self, inventario_data: Dict) -> Optional[int]:
        """
        Crear un registro de inventario para un producto.
        
        Args:
            inventario_data: Diccionario con los datos del inventario
                {
                    'id_producto': int,
                    'id_ubicacion': int,
                    'stock_actual': int,
                    'stock_minimo': int,
                    'stock_maximo': int (opcional),
                    'activo': bool
                }
                
        Returns:
            ID del inventario creado, o None si hay error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO inventario (
                        id_producto, id_ubicacion, stock_actual,
                        stock_minimo, stock_maximo, activo
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id_inventario
                """, (
                    inventario_data['id_producto'],
                    inventario_data.get('id_ubicacion', 1),
                    inventario_data.get('stock_actual', 0),
                    inventario_data.get('stock_minimo', 5),
                    inventario_data.get('stock_maximo'),
                    inventario_data.get('activo', True)
                ))
                
                id_inventario = cursor.fetchone()['id_inventario']
                self.connection.commit()
                
                logging.info(f"Inventario creado con ID: {id_inventario}")
                return id_inventario
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error creando inventario: {e}")
            return None
    
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
    
    # ========== VENTAS ==========
    
    def create_sale(self, venta_data: Dict) -> Optional[int]:
        """
        Crear nueva venta con transacción.
        
        Args:
            venta_data: {
                'id_vendedor': int,
                'id_cliente': int (opcional),
                'id_turno': int (opcional),
                'productos': [{'id_producto': int, 'cantidad': int, 'precio': Decimal}],
                'subtotal': Decimal,
                'descuento': Decimal,
                'impuestos': Decimal,
                'total': Decimal,
                'metodo_pago': str,
                'tipo_venta': str
            }
        
        Returns:
            ID de la venta creada, o None si hay error
        """
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                # Generar número de ticket único
                cursor.execute("""
                    SELECT 'TKT-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                           LPAD(CAST(COALESCE(MAX(CAST(SUBSTRING(numero_ticket FROM 16) AS INTEGER)), 0) + 1 AS text), 6, '0') AS numero
                    FROM ventas
                    WHERE DATE(fecha) = CURRENT_DATE
                """)
                result = cursor.fetchone()
                numero_ticket = result['numero'] if result and result['numero'] else f"TKT-{datetime.now().strftime('%Y%m%d')}-000001"
                
                # Aceptar tanto id_vendedor como id_usuario (flexibilidad)
                id_vendedor = venta_data.get('id_vendedor') or venta_data.get('id_usuario')
                if not id_vendedor:
                    raise ValueError("Se requiere id_vendedor o id_usuario en venta_data")
                
                # Aceptar id_cliente, si no viene usar cliente genérico (id=2: Cliente Mostrador)
                id_cliente = venta_data.get('id_cliente', 2)
                
                # Insertar venta
                cursor.execute("""
                    INSERT INTO ventas (
                        numero_ticket, id_vendedor, id_cliente, id_turno,
                        subtotal, descuento_general, iva, total,
                        metodo_pago, tipo_venta, estado, es_credito, pagado
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::tipo_metodo_pago, %s::tipo_venta, 'completada', FALSE, TRUE
                    )
                    RETURNING id_venta
                """, (
                    numero_ticket,
                    id_vendedor,
                    id_cliente,
                    venta_data.get('id_turno'),
                    venta_data.get('subtotal', 0),
                    venta_data.get('descuento', 0),
                    venta_data.get('iva', venta_data.get('impuestos', 0)),
                    venta_data['total'],
                    venta_data.get('metodo_pago', 'efectivo'),
                    venta_data.get('tipo_venta', 'producto')
                ))
                
                venta_id = cursor.fetchone()['id_venta']
                
                # Insertar detalles y actualizar stock
                for item in venta_data.get('productos', []):
                    # Obtener información del producto
                    cursor.execute("""
                        SELECT codigo_interno, nombre, descripcion, precio_venta, costo_promedio
                        FROM ca_productos
                        WHERE id_producto = %s
                    """, (item['id_producto'],))
                    
                    producto = cursor.fetchone()
                    if not producto:
                        logging.error(f"Producto {item['id_producto']} no encontrado")
                        raise ValueError(f"Producto {item['id_producto']} no encontrado")
                    
                    precio_unitario = Decimal(str(item.get('precio', producto['precio_venta'])))
                    costo = Decimal(str(producto['costo_promedio'] or 0))
                    subtotal_linea = precio_unitario * item['cantidad']
                    utilidad = (precio_unitario - costo) * item['cantidad']
                    
                    # Insertar detalle de venta
                    cursor.execute("""
                        INSERT INTO detalles_venta (
                            id_venta, id_producto, tipo_producto, codigo_interno,
                            cantidad, precio_unitario, subtotal_linea, total_linea,
                            nombre_producto, descripcion_producto, utilidad_linea
                        ) VALUES (
                            %s, %s, 'varios', %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        venta_id,
                        item['id_producto'],
                        producto['codigo_interno'],
                        item['cantidad'],
                        precio_unitario,
                        subtotal_linea,
                        subtotal_linea,  # total_linea = subtotal_linea (sin impuestos por ahora)
                        producto['nombre'],
                        producto.get('descripcion'),
                        utilidad
                    ))
                    
                    # Actualizar stock (primer ubicación disponible con stock)
                    cursor.execute("""
                        SELECT id_inventario, id_ubicacion, stock_actual, costo_promedio
                        FROM inventario
                        WHERE id_producto = %s AND activo = TRUE AND stock_disponible >= %s
                        ORDER BY stock_actual DESC
                        LIMIT 1
                    """, (item['id_producto'], item['cantidad']))
                    
                    inv = cursor.fetchone()
                    if not inv:
                        logging.warning(f"Stock insuficiente para producto {producto['nombre']}")
                        # Continuar pero registrar el problema
                        continue
                    
                    nuevo_stock = inv['stock_actual'] - item['cantidad']
                    
                    # Actualizar inventario
                    cursor.execute("""
                        UPDATE inventario
                        SET stock_actual = %s,
                            fecha_ultima_salida = CURRENT_TIMESTAMP
                        WHERE id_inventario = %s
                    """, (nuevo_stock, inv['id_inventario']))
                    
                    # Registrar movimiento de inventario
                    cursor.execute("""
                        INSERT INTO movimientos_inventario (
                            id_producto, id_ubicacion, tipo_movimiento,
                            cantidad, stock_anterior, stock_nuevo,
                            costo_unitario, costo_promedio_anterior, costo_promedio_nuevo,
                            id_usuario, id_venta, motivo
                        ) VALUES (
                            %s, %s, 'venta', %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        item['id_producto'],
                        inv['id_ubicacion'],
                        -item['cantidad'],
                        inv['stock_actual'],
                        nuevo_stock,
                        inv['costo_promedio'],
                        inv['costo_promedio'],
                        inv['costo_promedio'],
                        id_vendedor,
                        venta_id,
                        f"Venta {numero_ticket}"
                    ))
                
                # Actualizar totales del turno si la venta es en efectivo
                id_turno = venta_data.get('id_turno')
                metodo_pago = venta_data.get('metodo_pago', 'efectivo')
                if id_turno and metodo_pago == 'efectivo':
                    cursor.execute("""
                        UPDATE turnos_caja
                        SET total_efectivo = total_efectivo + %s
                        WHERE id_turno = %s AND cerrado = FALSE
                    """, (venta_data['total'], id_turno))
                
                self.connection.commit()
                logging.info(f"✅ Venta creada: {numero_ticket}, Total: ${venta_data['total']:.2f}")
                return venta_id
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error creando venta: {e}")
            logging.error(traceback.format_exc())
            return None
    
    # ========== CLIENTES ==========
    
    def get_cliente_by_codigo(self, codigo: str) -> Optional[Dict]:
        """Obtener cliente por código"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_cliente, codigo, nombre_completo, telefono, email, activo
                    FROM clientes
                    WHERE codigo = %s AND activo = TRUE
                """, (codigo,))
                
                return cursor.fetchone()
                
        except Exception as e:
            logging.error(f"Error obteniendo cliente: {e}")
            return None
    
    def get_total_members(self) -> int:
        """Obtener total de clientes activos"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = TRUE")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logging.error(f"Error obteniendo total de clientes: {e}")
            return 0
    
    def obtener_ultimo_codigo_cliente(self) -> Optional[str]:
        """Obtener el último código de cliente para generar uno nuevo"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT codigo FROM clientes
                    WHERE codigo LIKE 'CLI%'
                    ORDER BY CAST(SUBSTRING(codigo FROM 4) AS INTEGER) DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logging.error(f"Error obteniendo último código de cliente: {e}")
            return None
    
    def verificar_codigo_cliente_existe(self, codigo: str) -> bool:
        """Verificar si un código de cliente ya existe"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM clientes
                    WHERE codigo = %s
                """, (codigo,))
                result = cursor.fetchone()
                return result[0] > 0 if result else False
        except Exception as e:
            logging.error(f"Error verificando código de cliente: {e}")
            return False
    
    def guardar_cliente(self, cliente_data: Dict) -> Optional[int]:
        """Guardar un nuevo cliente en la base de datos"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO clientes (
                        codigo, nombres, apellido_paterno, apellido_materno,
                        telefono, email, rfc, fecha_nacimiento,
                        contacto_emergencia, telefono_emergencia,
                        limite_credito, notas, activo, fecha_registro, usuario_registro
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_cliente
                """, (
                    cliente_data['codigo'],
                    cliente_data['nombres'],
                    cliente_data['apellido_paterno'],
                    cliente_data['apellido_materno'],
                    cliente_data.get('telefono'),
                    cliente_data.get('email'),
                    cliente_data.get('rfc'),
                    cliente_data.get('fecha_nacimiento'),
                    cliente_data.get('contacto_emergencia'),
                    cliente_data.get('telefono_emergencia'),
                    cliente_data.get('limite_credito', 0.0),
                    cliente_data.get('notas'),
                    cliente_data.get('activo', True),
                    cliente_data.get('fecha_registro', datetime.now()),
                    cliente_data.get('usuario_registro')
                ))
                
                result = cursor.fetchone()
                cliente_id = result[0] if result else None
                
                self.connection.commit()
                logging.info(f"Cliente guardado: {cliente_data['codigo']} (ID: {cliente_id})")
                return cliente_id
                
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error guardando cliente: {e}")
            return None
    
    def obtener_cuentas_por_cobrar(self, filtros=None) -> List[Dict]:
        """Obtener listado de cuentas por cobrar con filtros"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            filtros = filtros or {}
            
            query = """
                SELECT 
                    cxc.id_cxc,
                    cxc.numero_cuenta,
                    cxc.total,
                    cxc.saldo,
                    cxc.pagado,
                    cxc.fecha_vencimiento,
                    cxc.estado,
                    cxc.creada_en,
                    cxc.pagada,
                    -- Información del cliente
                    c.id_cliente,
                    CONCAT(c.nombres, ' ', COALESCE(c.apellido_paterno, ''), ' ', COALESCE(c.apellido_materno, '')) as cliente,
                    c.telefono,
                    c.email,
                    -- Información de la venta
                    v.id_venta,
                    v.numero_ticket,
                    v.fecha as fecha_venta,
                    -- Cálculos
                    CASE 
                        WHEN cxc.fecha_vencimiento < CURRENT_DATE AND cxc.saldo > 0 
                        THEN CURRENT_DATE - cxc.fecha_vencimiento 
                        ELSE 0 
                    END as dias_vencidos,
                    -- Último pago
                    (SELECT MAX(fecha_pago) FROM cxc_detalle_pagos WHERE id_cxc = cxc.id_cxc) as ultimo_pago
                FROM cuentas_por_cobrar cxc
                INNER JOIN clientes c ON cxc.id_cliente = c.id_cliente
                INNER JOIN ventas v ON cxc.id_venta = v.id_venta
                WHERE cxc.activo = TRUE
            """
            
            params = []
            
            # Aplicar filtros
            if 'cliente' in filtros:
                query += " AND LOWER(CONCAT(c.nombres, ' ', COALESCE(c.apellido_paterno, ''), ' ', COALESCE(c.apellido_materno, ''))) LIKE LOWER(%s)"
                params.append(f"%{filtros['cliente']}%")
            
            if 'estado' in filtros:
                query += " AND cxc.estado = %s"
                params.append(filtros['estado'])
            
            if 'fecha_desde' in filtros:
                query += " AND cxc.fecha_vencimiento >= %s"
                params.append(filtros['fecha_desde'])
            
            if 'fecha_hasta' in filtros:
                query += " AND cxc.fecha_vencimiento <= %s"
                params.append(filtros['fecha_hasta'])
            
            if filtros.get('solo_pendientes'):
                query += " AND cxc.estado IN ('activa', 'vencida') AND cxc.saldo > 0"
            
            # Ordenar por fecha de vencimiento
            query += " ORDER BY cxc.fecha_vencimiento ASC, cxc.saldo DESC"
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                cuentas = []
                for row in rows:
                    cuenta = dict(row)
                    # Convertir fechas
                    if cuenta.get('fecha_vencimiento'):
                        cuenta['fecha_vencimiento'] = cuenta['fecha_vencimiento'].date()
                    if cuenta.get('fecha_venta'):
                        cuenta['fecha_venta'] = cuenta['fecha_venta'].date()
                    if cuenta.get('ultimo_pago'):
                        cuenta['ultimo_pago'] = cuenta['ultimo_pago'].date()
                    if cuenta.get('creada_en'):
                        cuenta['creada_en'] = cuenta['creada_en'].date()
                    
                    cuentas.append(cuenta)
                
                return cuentas
                
        except Exception as e:
            logging.error(f"Error obteniendo cuentas por cobrar: {e}")
            return []
    
    # ========== TURNOS DE CAJA ==========
    
    def abrir_turno_caja(self, id_usuario: int, monto_inicial: Decimal = 0) -> Optional[int]:
        """Abrir un nuevo turno de caja"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            from psycopg2.extras import RealDictCursor
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generar número de turno
                cursor.execute("""
                    SELECT 'TURNO-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                           LPAD(CAST(COALESCE(MAX(CAST(SUBSTRING(numero_turno FROM 18) AS INTEGER)), 0) + 1 AS TEXT), 4, '0') AS numero_turno
                    FROM turnos_caja
                    WHERE DATE(fecha_apertura) = CURRENT_DATE
                """)
                result = cursor.fetchone()
                numero_turno = result['numero_turno'] if result else f"TURNO-{datetime.now().strftime('%Y%m%d')}-0001"
                
                cursor.execute("""
                    INSERT INTO turnos_caja (
                        numero_turno, id_usuario, monto_inicial, cerrado
                    ) VALUES (
                        %s, %s, %s, FALSE
                    )
                    RETURNING id_turno
                """, (numero_turno, id_usuario, monto_inicial))
                
                result = cursor.fetchone()
                id_turno = result['id_turno'] if result else None
                
                if id_turno:
                    self.connection.commit()
                    logging.info(f"✅ Turno de caja abierto: {numero_turno} (ID: {id_turno})")
                    return id_turno
                else:
                    self.connection.rollback()
                    return None
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error abriendo turno de caja: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    
    def get_turno_activo(self, id_usuario: int) -> Optional[Dict]:
        """Obtener el turno activo de un usuario"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id_turno, numero_turno, id_usuario, fecha_apertura, 
                        monto_inicial, total_efectivo, total_ventas, cerrado
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
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Obtener datos del turno
                cursor.execute("""
                    SELECT monto_inicial, total_efectivo
                    FROM turnos_caja
                    WHERE id_turno = %s AND cerrado = FALSE
                """, (id_turno,))
                
                turno = cursor.fetchone()
                if not turno:
                    logging.warning(f"Turno {id_turno} no encontrado o ya cerrado")
                    return False
                
                # Asegurar que todos los valores sean Decimal para evitar errores de tipo
                monto_inicial = Decimal(str(turno['monto_inicial'] or 0))
                total_efectivo = Decimal(str(turno['total_efectivo'] or 0))
                monto_real_cierre = Decimal(str(monto_real_cierre or 0))
                
                monto_esperado = monto_inicial + total_efectivo
                diferencia = monto_real_cierre - monto_esperado
                
                cursor.execute("""
                    UPDATE turnos_caja
                    SET 
                        fecha_cierre = CURRENT_TIMESTAMP,
                        monto_esperado_efectivo = %s,
                        monto_real_efectivo = %s,
                        diferencia_efectivo = %s,
                        cerrado = TRUE
                    WHERE id_turno = %s
                """, (monto_esperado, monto_real_cierre, diferencia, id_turno))
                
                self.connection.commit()
                logging.info(f"✅ Turno {id_turno} cerrado. Diferencia: ${diferencia:.2f}")
                return True
        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error cerrando turno de caja: {e}")
            return False

    # ==================== MÉTODOS PARA COMPRAS Y GASTOS ====================

    def obtener_tipos_cuenta_pagar(self) -> List[Dict]:
        """Obtener lista de tipos de cuenta por pagar activos"""
        try:
            # Asegurar que no haya transacciones pendientes
            if self.connection and not self.connection.closed:
                try:
                    self.connection.rollback()
                except:
                    pass
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id_tipo_cuenta_pagar, codigo, nombre, descripcion, categoria
                    FROM ca_tipo_cuenta_pagar
                    WHERE activo = TRUE
                    ORDER BY nombre
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error obteniendo tipos de cuenta por pagar: {e}")
            return []

    def obtener_proveedores_activos(self) -> List[Dict]:
        """Obtener lista de proveedores activos"""
        try:
            # Asegurar que no haya transacciones pendientes
            if self.connection and not self.connection.closed:
                try:
                    self.connection.rollback()
                except:
                    pass
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id_proveedor, codigo, razon_social, nombre_comercial,
                           contacto_telefono, contacto_email as email, activo
                    FROM ca_proveedores
                    WHERE activo = TRUE
                    ORDER BY razon_social
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error obteniendo proveedores activos: {e}")
            return []

    def obtener_proveedor_por_id(self, id_proveedor: int) -> Optional[Dict]:
        """Obtener proveedor por ID"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM ca_proveedores
                    WHERE id_proveedor = %s AND activo = TRUE
                """, (id_proveedor,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logging.error(f"Error obteniendo proveedor por ID: {e}")
            return None

    def guardar_compra_gasto(self, datos_compra: Dict) -> bool:
        """Guardar una compra o gasto en la base de datos"""
        try:
            with self.connection.cursor() as cursor:
                # Insertar en cuentas_por_pagar
                cursor.execute("""
                    INSERT INTO cuentas_por_pagar (
                        numero_cuenta, id_tipo_cuenta_pagar, id_proveedor, id_usuario,
                        fecha_cuenta, subtotal, descuento, impuestos, total,
                        numero_factura, forma_pago, fecha_vencimiento, notas
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_cuenta_pagar
                """, (
                    datos_compra['numero_cuenta'],
                    datos_compra['id_tipo_cuenta_pagar'],
                    datos_compra.get('id_proveedor'),
                    datos_compra['id_usuario'],
                    datos_compra['fecha_cuenta'],
                    datos_compra['subtotal'],
                    datos_compra['descuento'],
                    datos_compra['impuestos'],
                    datos_compra['total'],
                    datos_compra.get('numero_factura'),
                    datos_compra.get('forma_pago', 'credito'),
                    datos_compra.get('fecha_vencimiento'),
                    datos_compra.get('notas')
                ))

                id_cuenta_pagar = cursor.fetchone()[0]

                # Si es una compra con productos, insertar detalles
                if datos_compra.get('tipo_compra') == 'compra' and datos_compra.get('detalles'):
                    for detalle in datos_compra['detalles']:
                        cursor.execute("""
                            INSERT INTO cxp_detalle_productos (
                                id_cuenta_pagar, id_producto, cantidad, precio_unitario,
                                descuento_linea, subtotal_linea
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            id_cuenta_pagar,
                            detalle['id_producto'],
                            detalle['cantidad'],
                            detalle['precio_unitario'],
                            0,  # descuento_linea
                            detalle['subtotal']
                        ))

                        # Actualizar stock si es compra de productos inventariables
                        producto = self.obtener_producto_por_codigo(detalle['codigo_interno'])
                        if producto and producto.get('es_inventariable', True):
                            # Obtener ubicación por defecto (primera activa)
                            ubicacion = self.obtener_ubicacion_por_defecto()
                            if ubicacion:
                                self.actualizar_stock(
                                    detalle['codigo_interno'],
                                    producto['tipo_producto'],
                                    detalle['cantidad'],
                                    id_ubicacion=ubicacion['id_ubicacion'],
                                    costo_unitario=detalle['precio_unitario']
                                )

                self.connection.commit()
                logging.info(f"✅ Compra/gasto guardado: {datos_compra['numero_cuenta']}")
                return True

        except Exception as e:
            try:
                self.connection.rollback()
            except:
                pass
            logging.error(f"Error guardando compra/gasto: {e}")
            return False

    def obtener_ubicacion_por_defecto(self) -> Optional[Dict]:
        """Obtener la primera ubicación activa como ubicación por defecto"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id_ubicacion, nombre
                    FROM ca_ubicaciones
                    WHERE activa = TRUE
                    ORDER BY id_ubicacion
                    LIMIT 1
                """)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logging.error(f"Error obteniendo ubicación por defecto: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de conexión
    config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'pos_db',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        # Crear instancia del gestor
        db = PostgresManager(config)
        
        # Verificar base de datos
        if db.initialize_database():
            print("✅ Base de datos inicializada correctamente")
        
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
        traceback.print_exc()
