"""
Ventana de Administración de Productos
Lista de productos con botones de acción y formulario en diálogo
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QCheckBox, QDialog, QHeaderView, QComboBox,
    QAbstractItemView, QPushButton, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
import logging
import qtawesome as qta

from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    SectionTitle,
    ContentPanel,
    StyledLabel,
    show_info_dialog,
    show_success_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog
)

# Importar ventana de nuevo producto
from ui.nuevo_producto_window import NuevoProductoWindow

# Importar diálogo de autenticación de admin
from ui.admin_auth_dialog import AdminAuthDialog


class FormularioProductoDialog(QDialog):
    """Diálogo con formulario para agregar/editar producto"""

    def __init__(self, pg_manager, producto_data=None, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.producto_data = producto_data
        self.setWindowTitle("")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.setup_ui()

        # Si hay datos, cargarlos
        if producto_data:
            self.cargar_datos(producto_data)

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = SectionTitle("DATOS DEL PRODUCTO")
        layout.addWidget(title)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)

        # Estilo para inputs
        input_style = f"""
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox {{
                padding: 8px;
                border: 2px solid #e5e7eb;
                border-radius: 4px;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """

        row = 0

        # Código
        grid.addWidget(StyledLabel("Código *:", bold=True), row, 0)
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código único del producto")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.setStyleSheet(input_style)
        grid.addWidget(self.input_codigo, row, 1)
        row += 1

        # Nombre
        grid.addWidget(StyledLabel("Nombre *:", bold=True), row, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del producto")
        self.input_nombre.setMinimumHeight(40)
        self.input_nombre.setStyleSheet(input_style)
        grid.addWidget(self.input_nombre, row, 1)
        row += 1

        # Descripción
        grid.addWidget(StyledLabel("Descripción:", bold=True), row, 0)
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción del producto (opcional)")
        self.input_descripcion.setMaximumHeight(80)
        self.input_descripcion.setStyleSheet(input_style)
        grid.addWidget(self.input_descripcion, row, 1)
        row += 1

        # Precio
        grid.addWidget(StyledLabel("Precio *:", bold=True), row, 0)
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0.01)
        self.input_precio.setMaximum(999999.99)
        self.input_precio.setDecimals(2)
        self.input_precio.setPrefix("$")
        self.input_precio.setMinimumHeight(40)
        self.input_precio.setStyleSheet(input_style)
        grid.addWidget(self.input_precio, row, 1)
        row += 1

        # Categoría
        grid.addWidget(StyledLabel("Categoría:", bold=True), row, 0)
        self.input_categoria = QComboBox()
        self.input_categoria.addItem("Seleccione una categoría", "")
        self.input_categoria.setMinimumHeight(40)
        self.input_categoria.setStyleSheet(input_style)
        self.cargar_categorias()
        grid.addWidget(self.input_categoria, row, 1)
        row += 1

        # Estado activo
        grid.addWidget(StyledLabel("Estado:", bold=True), row, 0)
        self.check_activo = QCheckBox("Producto activo")
        self.check_activo.setChecked(True)
        grid.addWidget(self.check_activo, row, 1)
        row += 1

        layout.addLayout(grid)
        layout.addStretch()

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        btn_guardar = TileButton("Guardar", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.setMaximumHeight(120)
        btn_guardar.clicked.connect(self.guardar)

        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.setMaximumHeight(120)
        btn_cancelar.clicked.connect(self.reject)

        buttons_layout.addWidget(btn_guardar)
        buttons_layout.addWidget(btn_cancelar)

        layout.addLayout(buttons_layout)

    def cargar_categorias(self):
        """Cargar categorías disponibles"""
        try:
            # Usar consulta SQL directa para obtener categorías
            sql = "SELECT id_categoria, nombre FROM ca_categorias_producto ORDER BY nombre"
            categorias_data = self.pg_manager.query(sql)
            
            for cat in categorias_data:
                self.input_categoria.addItem(cat['nombre'], cat['id_categoria'])
        except Exception as e:
            logging.error(f"Error cargando categorías: {e}")

    def cargar_datos(self, producto):
        """Cargar datos de producto existente"""
        self.input_codigo.setText(producto.get('codigo_interno', ''))
        self.input_nombre.setText(producto.get('nombre', ''))
        self.input_descripcion.setPlainText(producto.get('descripcion', '') or '')
        self.input_precio.setValue(float(producto.get('precio_venta', 0)))
        self.check_activo.setChecked(producto.get('activo', True))

        # Seleccionar categoría
        id_categoria = producto.get('id_categoria')
        if id_categoria:
            index = self.input_categoria.findData(id_categoria)
            if index >= 0:
                self.input_categoria.setCurrentIndex(index)

    def validar(self):
        """Validar datos del formulario"""
        codigo = self.input_codigo.text().strip()
        nombre = self.input_nombre.text().strip()
        precio = self.input_precio.value()

        if not codigo:
            show_warning_dialog(self, "Validación", "Debe ingresar un código para el producto")
            self.input_codigo.setFocus()
            return False

        if not nombre:
            show_warning_dialog(self, "Validación", "Debe ingresar un nombre para el producto")
            self.input_nombre.setFocus()
            return False

        if precio <= 0:
            show_warning_dialog(self, "Validación", "El precio debe ser mayor a cero")
            self.input_precio.setFocus()
            return False

        # Verificar código único si es nuevo producto
        if not self.producto_data:
            try:
                existing = self.pg_manager.client.table('ca_productos').select('id_producto').eq('codigo_interno', codigo).execute()
                if existing.data:
                    show_warning_dialog(self, "Validación", "Ya existe un producto con este código")
                    self.input_codigo.setFocus()
                    return False
            except Exception as e:
                logging.error(f"Error verificando código único: {e}")

        return True

    def guardar(self):
        """Guardar producto en la base de datos"""
        if not self.validar():
            return

        try:
            codigo = self.input_codigo.text().strip()
            nombre = self.input_nombre.text().strip()
            descripcion = self.input_descripcion.toPlainText().strip() or None
            precio = self.input_precio.value()
            id_categoria = self.input_categoria.currentData()
            activo = self.check_activo.isChecked()

            producto_data = {
                'codigo_interno': codigo,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio_venta': precio,
                'id_categoria': id_categoria if id_categoria else None,
                'activo': activo
            }

            if self.producto_data:
                # Actualizar producto existente
                success = self.pg_manager.actualizar_producto(codigo, producto_data)
                if success:
                    msg = "actualizado"
                else:
                    show_error_dialog(self, "Error", "No se pudo actualizar el producto")
                    return
            else:
                # Crear nuevo producto
                id_nuevo = self.pg_manager.insertar_producto(producto_data)
                if id_nuevo:
                    msg = "creado"
                else:
                    show_error_dialog(self, "Error", "No se pudo crear el producto")
                    return
            self.accept()

        except Exception as e:
            logging.error(f"Error guardando producto: {e}")
            show_error_dialog(self, "Error", f"No se pudo guardar el producto:\n{str(e)}")


# ============================================================
# VENTANA PRINCIPAL DE PRODUCTOS
# ============================================================

class ProductosWindow(QWidget):
    """Ventana para administrar productos"""

    cerrar_solicitado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.parent_window = parent  # Guardar referencia a la ventana padre
        self.productos = []

        self.setup_ui()
        self.cargar_productos()

    def setup_ui(self):
        """Configurar interfaz principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        # Panel de lista de productos
        lista_panel = self._setup_panel_lista()
        layout.addWidget(lista_panel)

        # Botones al pie (todos en una fila)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        btn_nuevo = TileButton("Nuevo Producto", "fa5s.plus", WindowsPhoneTheme.TILE_GREEN)
        btn_nuevo.clicked.connect(self.abrir_formulario_nuevo)
        buttons_layout.addWidget(btn_nuevo)

        btn_refrescar = TileButton("Actualizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_refrescar.clicked.connect(self.cargar_productos)
        buttons_layout.addWidget(btn_refrescar)

        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        buttons_layout.addWidget(btn_volver)

        layout.addLayout(buttons_layout)

    def _setup_panel_lista(self):
        """Panel con la tabla de productos"""
        panel = ContentPanel()
        panel_layout = QVBoxLayout(panel)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Código", "Nombre", "Precio", "Categoría", "Stock", "Estado"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # Configurar headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Código
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Precio
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Categoría
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Estado

        # Estilo de tabla
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: #e5e7eb;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }}
            QTableWidget::item:selected {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
        """)

        panel_layout.addWidget(self.table)

        return panel

    def cargar_productos(self):
        """Cargar productos desde la base de datos"""
        try:
            # Consulta personalizada que incluye id_categoria y stock
            sql = """
                SELECT 
                    p.id_producto, p.codigo_interno, p.nombre, p.descripcion,
                    p.precio_venta, p.id_categoria, c.nombre as categoria, p.activo,
                    COALESCE(SUM(i.stock_actual), 0) as stock_actual
                FROM ca_productos p
                LEFT JOIN ca_categorias_producto c ON p.id_categoria = c.id_categoria
                LEFT JOIN inventario i ON p.id_producto = i.id_producto
                WHERE p.activo = TRUE
                GROUP BY p.id_producto, p.codigo_interno, p.nombre, p.descripcion,
                         p.precio_venta, p.id_categoria, c.nombre, p.activo
                ORDER BY p.nombre
            """
            productos_data = self.pg_manager.query(sql)
            
            self.productos = []
            for item in productos_data:
                producto = {
                    'id_producto': item['id_producto'],
                    'codigo_interno': item['codigo_interno'],
                    'nombre': item['nombre'],
                    'descripcion': item['descripcion'],
                    'precio_venta': item['precio_venta'],
                    'id_categoria': item['id_categoria'],
                    'categoria': item['categoria'] or '-',
                    'activo': item['activo'],
                    'stock_actual': item['stock_actual'] or 0
                }
                self.productos.append(producto)
            
            self.actualizar_tabla()
            logging.info(f"Cargados {len(self.productos)} productos")

        except Exception as e:
            logging.error(f"Error cargando productos: {e}")
            show_error_dialog(self, "Error", "No se pudieron cargar los productos")

    def actualizar_tabla(self):
        """Actualizar tabla con los datos de productos"""
        self.table.setRowCount(0)

        for i, producto in enumerate(self.productos):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 60)  # Altura consistente

            # Código
            codigo_item = QTableWidgetItem(producto['codigo_interno'])
            codigo_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, codigo_item)

            # Nombre
            nombre_item = QTableWidgetItem(producto['nombre'])
            self.table.setItem(i, 1, nombre_item)

            # Precio
            precio_item = QTableWidgetItem(f"${producto['precio_venta']:.2f}")
            precio_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, precio_item)

            # Categoría
            categoria = producto.get('categoria') or '-'
            categoria_item = QTableWidgetItem(categoria)
            self.table.setItem(i, 3, categoria_item)

            # Stock
            stock_item = QTableWidgetItem(str(producto.get('stock_actual', 0)))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, stock_item)

            # Estado - Checkbox para activar/desactivar con iconos
            estado_checkbox = QCheckBox()
            estado_checkbox.setChecked(producto['activo'])

            # Configurar icono según estado
            if producto['activo']:
                icon = qta.icon('fa5s.toggle-on', color=WindowsPhoneTheme.TILE_GREEN)
            else:
                icon = qta.icon('fa5s.toggle-off', color=WindowsPhoneTheme.TILE_RED)

            estado_checkbox.setIcon(icon)
            estado_checkbox.setIconSize(QSize(24, 24))

            estado_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 4px;
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 0px;
                    height: 0px;
                    border: none;
                    background: transparent;
                }}
            """)

            # Conectar el cambio de estado a nuestro método
            estado_checkbox.stateChanged.connect(lambda state, p=producto, row=i: self.on_estado_changed(state, p, row))
            self.table.setCellWidget(i, 5, estado_checkbox)

    def abrir_formulario_nuevo(self):
        """Abrir ventana de nuevo producto"""
        try:
            # Crear ventana de nuevo producto
            nuevo_producto_window = NuevoProductoWindow(
                self.pg_manager,
                self.user_data,
                self.parent_window  # Pasar la ventana principal
            )
            
            # Conectar señales
            nuevo_producto_window.cerrar_solicitado.connect(self.on_nuevo_producto_cerrado)
            nuevo_producto_window.producto_guardado.connect(self.on_producto_guardado)
            
            # Agregar al stacked widget de la ventana padre y mostrar
            if self.parent_window and hasattr(self.parent_window, 'stacked_widget'):
                self.parent_window.stacked_widget.addWidget(nuevo_producto_window)
                self.parent_window.stacked_widget.setCurrentWidget(nuevo_producto_window)
                
                # Actualizar título si existe
                if hasattr(self.parent_window, 'top_bar'):
                    self.parent_window.top_bar.set_title("NUEVO PRODUCTO")
                
                logging.info("Abriendo ventana de nuevo producto")
            else:
                logging.error("No se encontró el stacked_widget en la ventana padre")
                
        except Exception as e:
            logging.error(f"Error abriendo ventana de nuevo producto: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la ventana de nuevo producto:\n{str(e)}")
    
    def on_nuevo_producto_cerrado(self):
        """Manejar cuando se cierra la ventana de nuevo producto"""
        # Regresar a la vista de productos
        if self.parent_window and hasattr(self.parent_window, 'stacked_widget'):
            self.parent_window.stacked_widget.setCurrentWidget(self)
            
            # Restaurar título
            if hasattr(self.parent_window, 'top_bar'):
                self.parent_window.top_bar.set_title("CATÁLOGO DE PRODUCTOS")
    
    def on_producto_guardado(self):
        """Manejar cuando se guarda un producto"""
        # Recargar la lista de productos
        self.cargar_productos()
        logging.info("Producto guardado, recargando lista de productos")

    def on_estado_changed(self, state, producto, row):
        """Manejar cambio de estado del producto con autenticación de admin"""
        nuevo_estado = state == Qt.Checked
        estado_anterior = producto['activo']
        
        # Si el estado no cambió realmente, no hacer nada
        if nuevo_estado == estado_anterior:
            return
            
        # Determinar la acción
        accion = "ACTIVAR" if nuevo_estado else "DESACTIVAR"
        
        # Solicitar autorización de administrador
        motivo = f"{accion} producto: {producto['nombre']} (Código: {producto['codigo_interno']})"
        auth_dialog = AdminAuthDialog(self.pg_manager, motivo, parent=self)
        
        if auth_dialog.exec() != QDialog.Accepted:
            # Revertir el cambio del checkbox
            checkbox = self.table.cellWidget(row, 5)
            if checkbox:
                checkbox.blockSignals(True)  # Evitar señal recursiva
                checkbox.setChecked(estado_anterior)
                checkbox.blockSignals(False)
            
            show_info_dialog(
                self,
                "Operación cancelada",
                "La autorización de administrador fue denegada o cancelada."
            )
            return

        # Proceder con el cambio de estado
        try:
            sql = """
                UPDATE productos 
                SET activo = %s, 
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    id_usuario_modifico = %s
                WHERE id_producto = %s
            """
            self.pg_manager.execute(sql, (nuevo_estado, auth_dialog.id_admin_autorizador, producto['id_producto']))
            
            # Actualizar el producto en la lista local
            producto['activo'] = nuevo_estado
            
            # Actualizar el icono del checkbox
            checkbox = self.table.cellWidget(row, 5)
            if checkbox:
                if nuevo_estado:
                    icon = qta.icon('fa5s.toggle-on', color=WindowsPhoneTheme.TILE_GREEN)
                else:
                    icon = qta.icon('fa5s.toggle-off', color=WindowsPhoneTheme.TILE_RED)

                checkbox.setIcon(icon)
                checkbox.setIconSize(QSize(24, 24))
            
            show_success_dialog(
                self,
                "Operación exitosa",
                f"El producto '{producto['nombre']}' ha sido {accion.lower()}do correctamente."
            )
            
            logging.info(f"Producto {producto['id_producto']} {accion.lower()}do por admin {auth_dialog.id_admin_autorizador}")
            
        except Exception as e:
            # Revertir el cambio del checkbox en caso de error
            checkbox = self.table.cellWidget(row, 5)
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(estado_anterior)
                checkbox.blockSignals(False)
            
            logging.error(f"Error al cambiar estado del producto {producto['id_producto']}: {e}")
            show_error_dialog(
                self,
                "Error",
                f"No se pudo {accion.lower()} el producto.",
                detail=str(e)
            )