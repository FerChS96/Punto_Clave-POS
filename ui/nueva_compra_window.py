"""
Formulario de Nueva Compra/Gasto para HTF POS
Formulario unificado para registrar compras y gastos
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDateEdit, QScrollArea, QGroupBox, QFrame, QLabel,
    QTabWidget, QSplitter, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer, QEvent
from PySide6.QtGui import QFont, QIcon
import logging
from datetime import datetime
import qtawesome as qta

from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    create_page_layout,
    ContentPanel,
    TouchNumericInput,
    TouchMoneyInput,
    SectionTitle,
    StyledLabel,
    aplicar_estilo_fecha,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_success_dialog,
    show_confirmation_dialog
)
from database.postgres_manager import PostgresManager


class NuevaCompraWindow(QWidget):
    """Formulario unificado para registrar compras y gastos"""

    cerrar_solicitado = Signal()
    compra_guardada = Signal(dict)

    def __init__(self, pg_manager, user_data, tipo_compra="compra", parent=None):
        """
        tipo_compra: "compra" para compras de productos, "gasto" para gastos/servicios
        """
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.tipo_compra = tipo_compra  # "compra" o "gasto"

        # Datos del formulario
        self.proveedor_seleccionado = None
        self.detalles_compra = []  # Para compras de productos
        self.tipo_cuenta_seleccionado = None

        self.setup_ui()
        self.cargar_datos_iniciales()

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Contenido principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
            }}
        """)

        content = QWidget()
        content_layout = create_page_layout("")
        content.setLayout(content_layout)

        # Crear pestañas para organizar la información
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {WindowsPhoneTheme.BORDER_COLOR};
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.TEXT_PRIMARY};
                padding: 12px 20px;
                border: 1px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-bottom: none;
                font-weight: bold;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 3px solid {WindowsPhoneTheme.TILE_BLUE};
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
            QTabBar::tab:hover {{
                background-color: #f0f0f0;
            }}
        """)

        # ===== PESTAÑA 1: INFORMACIÓN GENERAL =====
        self.crear_pestana_general()

        # ===== PESTAÑA 2: DETALLES DE LA COMPRA =====
        if self.tipo_compra == "compra":
            self.crear_pestana_productos()
        else:
            self.crear_pestana_gasto()

        content_layout.addWidget(self.tab_widget)

        # ===== BOTONES DE ACCIÓN =====
        self.crear_panel_botones(content_layout)

        # Configurar scroll
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Enfocar primer campo
        if hasattr(self, 'numero_factura_input'):
            self.numero_factura_input.setFocus()

    def crear_pestana_general(self):
        """Crear la pestaña de información general"""
        tab_general = QWidget()
        layout = QVBoxLayout(tab_general)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título de la sección
        titulo_texto = "Información General de la Compra" if self.tipo_compra == "compra" else "Información General del Gasto"
        titulo = QLabel(titulo_texto)
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Formulario en grid para mejor organización
        form_grid = QGridLayout()
        form_grid.setSpacing(15)

        # Fila 1: Número de Factura y Fecha
        factura_label = QLabel("Número de Factura")
        factura_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(factura_label, 0, 0)

        fecha_label = QLabel("Fecha *")
        fecha_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(fecha_label, 0, 2)

        # Campos
        self.numero_factura_input = QLineEdit()
        self.numero_factura_input.setPlaceholderText("Ingrese número de factura...")
        self.numero_factura_input.setMinimumHeight(46)
        self.numero_factura_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        form_grid.addWidget(self.numero_factura_input, 1, 0)

        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setMinimumHeight(46)
        self.fecha_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        aplicar_estilo_fecha(self.fecha_input)
        form_grid.addWidget(self.fecha_input, 1, 2)

        # Fila 2: Tipo de Cuenta y Proveedor
        tipo_label = QLabel("Tipo de Cuenta *")
        tipo_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(tipo_label, 2, 0)

        proveedor_label = QLabel("Proveedor")
        proveedor_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(proveedor_label, 2, 2)

        # Combo Tipo de Cuenta
        self.tipo_cuenta_combo = QComboBox()
        self.tipo_cuenta_combo.setMinimumHeight(46)
        self.tipo_cuenta_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.tipo_cuenta_combo.currentTextChanged.connect(self.on_tipo_cuenta_changed)
        form_grid.addWidget(self.tipo_cuenta_combo, 3, 0)

        # Combo Proveedor
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setMinimumHeight(46)
        self.proveedor_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.proveedor_combo.setEditable(True)
        self.proveedor_combo.currentTextChanged.connect(self.on_proveedor_changed)
        form_grid.addWidget(self.proveedor_combo, 3, 2)

        # Fila 3: Subtotal y Descuento
        subtotal_label = QLabel("Subtotal *")
        subtotal_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(subtotal_label, 4, 0)

        descuento_label = QLabel("Descuento")
        descuento_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(descuento_label, 4, 2)

        # Campos monetarios
        self.subtotal_input = TouchMoneyInput()
        form_grid.addWidget(self.subtotal_input, 5, 0)

        self.descuento_input = TouchMoneyInput()
        form_grid.addWidget(self.descuento_input, 5, 2)

        # Fila 4: Impuestos y Total
        impuestos_label = QLabel("Impuestos")
        impuestos_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(impuestos_label, 6, 0)

        total_label = QLabel("Total *")
        total_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(total_label, 6, 2)

        self.impuestos_input = TouchMoneyInput()
        form_grid.addWidget(self.impuestos_input, 7, 0)

        self.total_input = TouchMoneyInput()
        self.total_input.setReadOnly(True)  # Calculado automáticamente
        form_grid.addWidget(self.total_input, 7, 2)

        # Conectar cambios para calcular total
        self.subtotal_input.valueChanged.connect(self.calcular_total)
        self.descuento_input.valueChanged.connect(self.calcular_total)
        self.impuestos_input.valueChanged.connect(self.calcular_total)

        # Observaciones
        obs_label = QLabel("Observaciones")
        obs_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(obs_label)

        self.observaciones_input = QTextEdit()
        self.observaciones_input.setPlaceholderText("Observaciones adicionales...")
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        layout.addWidget(self.observaciones_input)

        layout.addLayout(form_grid)
        layout.addStretch()

        self.tab_widget.addTab(tab_general, "General")

    def crear_pestana_productos(self):
        """Crear la pestaña de detalles de productos (solo para compras)"""
        tab_productos = QWidget()
        layout = QVBoxLayout(tab_productos)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("Productos de la Compra")
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Panel de búsqueda de productos
        search_panel = ContentPanel()
        search_layout = QVBoxLayout(search_panel)

        search_title = QLabel("Buscar Producto")
        search_title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        search_layout.addWidget(search_title)

        # Búsqueda por código o nombre
        self.producto_search_input = QLineEdit()
        self.producto_search_input.setPlaceholderText("Código interno, código de barras o nombre del producto...")
        self.producto_search_input.setMinimumHeight(46)
        self.producto_search_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.producto_search_input.returnPressed.connect(self.buscar_producto)
        search_layout.addWidget(self.producto_search_input)

        # Información del producto seleccionado
        self.producto_info_label = QLabel("")
        self.producto_info_label.setWordWrap(True)
        self.producto_info_label.setStyleSheet(f"""
            color: {WindowsPhoneTheme.PRIMARY_BLUE};
            padding: 10px;
            background-color: {WindowsPhoneTheme.BG_LIGHT};
            border-radius: 4px;
            margin: 10px 0;
        """)
        self.producto_info_label.hide()
        search_layout.addWidget(self.producto_info_label)

        # Formulario para agregar producto
        producto_form = QGridLayout()
        producto_form.setSpacing(10)

        # Cantidad y Precio Unitario
        cant_label = QLabel("Cantidad *")
        cant_label.setStyleSheet("font-weight: bold;")
        producto_form.addWidget(cant_label, 0, 0)

        precio_label = QLabel("Precio Unitario *")
        precio_label.setStyleSheet("font-weight: bold;")
        producto_form.addWidget(precio_label, 0, 1)

        self.cantidad_input = TouchNumericInput(minimum=1, maximum=9999, default_value=1)
        producto_form.addWidget(self.cantidad_input, 1, 0)

        self.precio_unitario_input = TouchMoneyInput()
        producto_form.addWidget(self.precio_unitario_input, 1, 1)

        # Botón agregar
        btn_agregar = TileButton("Agregar Producto", "fa5s.plus", WindowsPhoneTheme.TILE_GREEN)
        btn_agregar.clicked.connect(self.agregar_producto_a_compra)
        producto_form.addWidget(btn_agregar, 2, 0, 1, 2)

        search_layout.addLayout(producto_form)
        layout.addWidget(search_panel)

        # Tabla de productos agregados
        self.crear_tabla_productos(layout)

        self.tab_widget.addTab(tab_productos, "Productos")

    def crear_pestana_gasto(self):
        """Crear la pestaña de detalles del gasto (solo para gastos)"""
        tab_gasto = QWidget()
        layout = QVBoxLayout(tab_gasto)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("Detalles del Gasto/Servicio")
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Descripción del gasto
        desc_label = QLabel("Descripción del Gasto/Servicio *")
        desc_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(desc_label)

        self.descripcion_gasto_input = QTextEdit()
        self.descripcion_gasto_input.setPlaceholderText("Describa el gasto o servicio...")
        self.descripcion_gasto_input.setMinimumHeight(100)
        self.descripcion_gasto_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        layout.addWidget(self.descripcion_gasto_input)

        # Información adicional
        info_panel = ContentPanel()
        info_layout = QGridLayout(info_panel)
        info_layout.setSpacing(15)

        # Referencia y Fecha de vencimiento
        ref_label = QLabel("Referencia/Recibo")
        ref_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(ref_label, 0, 0)

        venc_label = QLabel("Fecha de Vencimiento")
        venc_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(venc_label, 0, 1)

        self.referencia_input = QLineEdit()
        self.referencia_input.setPlaceholderText("Número de recibo, contrato, etc.")
        self.referencia_input.setMinimumHeight(46)
        self.referencia_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        info_layout.addWidget(self.referencia_input, 1, 0)

        self.fecha_vencimiento_input = QDateEdit()
        self.fecha_vencimiento_input.setDate(QDate.currentDate().addDays(30))  # 30 días por defecto
        self.fecha_vencimiento_input.setMinimumHeight(46)
        self.fecha_vencimiento_input.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        aplicar_estilo_fecha(self.fecha_vencimiento_input)
        info_layout.addWidget(self.fecha_vencimiento_input, 1, 1)

        layout.addWidget(info_panel)
        layout.addStretch()

        self.tab_widget.addTab(tab_gasto, "Detalles del Gasto")

    def crear_tabla_productos(self, parent_layout):
        """Crear tabla para mostrar productos agregados a la compra"""
        # Panel de la tabla
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)

        table_title = QLabel("Productos Agregados")
        table_title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        table_layout.addWidget(table_title)

        # Tabla
        self.productos_table = QTableWidget()
        self.productos_table.setColumnCount(5)
        self.productos_table.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio Unit.", "Subtotal", "Acciones"
        ])

        # Configurar tabla
        header = self.productos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Producto
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Cantidad
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Precio Unit.
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Subtotal
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Acciones

        self.productos_table.setColumnWidth(1, 100)
        self.productos_table.setColumnWidth(2, 120)
        self.productos_table.setColumnWidth(3, 120)
        self.productos_table.setColumnWidth(4, 100)

        self.productos_table.setAlternatingRowColors(True)
        self.productos_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.productos_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        table_layout.addWidget(self.productos_table)
        parent_layout.addWidget(table_panel)

    def crear_panel_botones(self, parent_layout):
        """Crear panel de botones de acción"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        # Botón Cancelar
        btn_cancelar = TileButton(
            "Cancelar",
            "fa5s.times",
            WindowsPhoneTheme.TILE_RED
        )
        btn_cancelar.clicked.connect(self.cerrar_solicitado.emit)
        buttons_layout.addWidget(btn_cancelar)

        # Espaciador
        buttons_layout.addStretch()

        # Botón Guardar
        texto_boton = "Guardar Compra" if self.tipo_compra == "compra" else "Guardar Gasto"
        btn_guardar = TileButton(
            texto_boton,
            "fa5s.save",
            WindowsPhoneTheme.TILE_GREEN
        )
        btn_guardar.clicked.connect(self.guardar_compra)
        buttons_layout.addWidget(btn_guardar)

        parent_layout.addLayout(buttons_layout)

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales para los combos"""
        try:
            # Cargar tipos de cuenta por pagar
            tipos_cuenta = self.pg_manager.obtener_tipos_cuenta_pagar()
            self.tipo_cuenta_combo.clear()
            self.tipo_cuenta_combo.addItem("-- Seleccionar Tipo --", None)
            for tipo in tipos_cuenta:
                self.tipo_cuenta_combo.addItem(tipo['nombre'], tipo['id_tipo_cuenta_pagar'])

            # Cargar proveedores
            proveedores = self.pg_manager.obtener_proveedores_activos()
            self.proveedor_combo.clear()
            self.proveedor_combo.addItem("-- Seleccionar Proveedor --", None)
            for prov in proveedores:
                display_text = f"{prov['codigo']} - {prov['razon_social']}"
                self.proveedor_combo.addItem(display_text, prov['id_proveedor'])

        except Exception as e:
            logging.error(f"Error cargando datos iniciales: {e}")
            show_error_dialog(self, "Error", "No se pudieron cargar los datos iniciales")

    def on_tipo_cuenta_changed(self, text):
        """Manejar cambio de tipo de cuenta"""
        current_data = self.tipo_cuenta_combo.currentData()
        self.tipo_cuenta_seleccionado = current_data

    def on_proveedor_changed(self, text):
        """Manejar cambio de proveedor"""
        current_data = self.proveedor_combo.currentData()
        if current_data:
            try:
                proveedor = self.pg_manager.obtener_proveedor_por_id(current_data)
                self.proveedor_seleccionado = proveedor
            except Exception as e:
                logging.error(f"Error obteniendo proveedor: {e}")
                self.proveedor_seleccionado = None
        else:
            self.proveedor_seleccionado = None

    def calcular_total(self):
        """Calcular el total automáticamente"""
        try:
            subtotal = self.subtotal_input.value()
            descuento = self.descuento_input.value()
            impuestos = self.impuestos_input.value()

            total = subtotal - descuento + impuestos
            self.total_input.setValue(total)
        except:
            self.total_input.setValue(0)

    def buscar_producto(self):
        """Buscar producto por código o nombre"""
        busqueda = self.producto_search_input.text().strip()
        if not busqueda:
            return

        try:
            productos = self.pg_manager.buscar_productos(busqueda, limite=10)
            if productos:
                producto = productos[0]  # Tomar el primero
                self.mostrar_info_producto(producto)
            else:
                show_warning_dialog(self, "Producto no encontrado",
                                  f"No se encontró ningún producto con: {busqueda}")
        except Exception as e:
            logging.error(f"Error buscando producto: {e}")
            show_error_dialog(self, "Error", "Error al buscar el producto")

    def mostrar_info_producto(self, producto):
        """Mostrar información del producto seleccionado"""
        info = f"""
        <b>{producto['nombre']}</b><br>
        Código: {producto['codigo_interno']}<br>
        Precio Venta: ${producto['precio_venta']:.2f}<br>
        Stock Actual: {producto.get('stock_actual', 0)}
        """
        self.producto_info_label.setText(info)
        self.producto_info_label.show()
        self.producto_seleccionado = producto

    def agregar_producto_a_compra(self):
        """Agregar producto a la lista de compra"""
        if not self.producto_seleccionado:
            show_warning_dialog(self, "Producto requerido",
                              "Primero debe buscar y seleccionar un producto")
            return

        cantidad = self.cantidad_input.value()
        precio_unitario = self.precio_unitario_input.value()

        if cantidad <= 0:
            show_warning_dialog(self, "Cantidad inválida", "La cantidad debe ser mayor a 0")
            return

        if precio_unitario <= 0:
            show_warning_dialog(self, "Precio inválido", "El precio unitario debe ser mayor a 0")
            return

        # Calcular subtotal
        subtotal = cantidad * precio_unitario

        # Agregar a la lista
        detalle = {
            'id_producto': self.producto_seleccionado['id_producto'],
            'codigo_interno': self.producto_seleccionado['codigo_interno'],
            'nombre': self.producto_seleccionado['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio_unitario,
            'subtotal': subtotal
        }

        self.detalles_compra.append(detalle)
        self.actualizar_tabla_productos()

        # Limpiar campos
        self.producto_search_input.clear()
        self.producto_info_label.hide()
        self.producto_seleccionado = None
        self.cantidad_input.setValue(1)
        self.precio_unitario_input.setValue(0)

        # Recalcular totales
        self.calcular_totales_compra()

    def actualizar_tabla_productos(self):
        """Actualizar la tabla de productos"""
        self.productos_table.setRowCount(len(self.detalles_compra))

        for row, detalle in enumerate(self.detalles_compra):
            # Producto
            self.productos_table.setItem(row, 0, QTableWidgetItem(detalle['nombre']))

            # Cantidad
            self.productos_table.setItem(row, 1, QTableWidgetItem(str(detalle['cantidad'])))

            # Precio Unitario
            self.productos_table.setItem(row, 2, QTableWidgetItem(f"${detalle['precio_unitario']:.2f}"))

            # Subtotal
            self.productos_table.setItem(row, 3, QTableWidgetItem(f"${detalle['subtotal']:.2f}"))

            # Botón eliminar
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(qta.icon('fa5s.trash', color='red'))
            btn_eliminar.setToolTip("Eliminar producto")
            btn_eliminar.clicked.connect(lambda checked, r=row: self.eliminar_producto(r))
            self.productos_table.setCellWidget(row, 4, btn_eliminar)

    def eliminar_producto(self, row):
        """Eliminar producto de la lista"""
        if row < len(self.detalles_compra):
            del self.detalles_compra[row]
            self.actualizar_tabla_productos()
            self.calcular_totales_compra()

    def calcular_totales_compra(self):
        """Calcular totales de la compra"""
        subtotal = sum(detalle['subtotal'] for detalle in self.detalles_compra)
        self.subtotal_input.setValue(subtotal)
        # El descuento e impuestos se mantienen como están

    def validar_datos(self):
        """Validar que todos los datos requeridos estén completos"""
        errores = []

        # Validaciones generales
        if not self.tipo_cuenta_seleccionado:
            errores.append("Debe seleccionar un tipo de cuenta")

        fecha = self.fecha_input.date().toPython()
        if fecha > datetime.now().date():
            errores.append("La fecha no puede ser futura")

        subtotal = self.subtotal_input.value()
        if subtotal <= 0:
            errores.append("El subtotal debe ser mayor a 0")

        total = self.total_input.value()
        if total <= 0:
            errores.append("El total debe ser mayor a 0")

        # Validaciones específicas por tipo
        if self.tipo_compra == "compra":
            if not self.detalles_compra:
                errores.append("Debe agregar al menos un producto a la compra")
        else:  # gasto
            if not self.descripcion_gasto_input.toPlainText().strip():
                errores.append("Debe ingresar una descripción del gasto")

        return errores

    def guardar_compra(self):
        """Guardar la compra o gasto"""
        # Validar datos
        errores = self.validar_datos()
        if errores:
            mensaje_error = "Por favor corrija los siguientes errores:\n\n" + "\n".join(f"• {error}" for error in errores)
            show_warning_dialog(self, "Datos incompletos", mensaje_error)
            return

        try:
            # Preparar datos para guardar
            datos_compra = {
                'numero_cuenta': self.generar_numero_cuenta(),
                'id_tipo_cuenta_pagar': self.tipo_cuenta_seleccionado,
                'id_proveedor': self.proveedor_seleccionado['id_proveedor'] if self.proveedor_seleccionado else None,
                'id_usuario': self.user_data.get('id_usuario'),
                'fecha_cuenta': self.fecha_input.date().toPython().strftime('%Y-%m-%d'),
                'subtotal': self.subtotal_input.value(),
                'descuento': self.descuento_input.value(),
                'impuestos': self.impuestos_input.value(),
                'total': self.total_input.value(),
                'numero_factura': self.numero_factura_input.text().strip() or None,
                'numero_pedido': None,  # Podría agregarse después
                'forma_pago': 'credito',  # Por defecto crédito
                'fecha_vencimiento': self.fecha_vencimiento_input.date().toPython().strftime('%Y-%m-%d') if hasattr(self, 'fecha_vencimiento_input') else None,
                'notas': self.observaciones_input.toPlainText().strip() or None,
                'tipo_compra': self.tipo_compra,
                'detalles': self.detalles_compra if self.tipo_compra == "compra" else None,
                'descripcion_gasto': self.descripcion_gasto_input.toPlainText().strip() if self.tipo_compra == "gasto" else None,
                'referencia': self.referencia_input.text().strip() if hasattr(self, 'referencia_input') else None
            }

            # Guardar en base de datos
            resultado = self.pg_manager.guardar_compra_gasto(datos_compra)

            if resultado:
                show_success_dialog(
                    self,
                    "Compra/Gasto guardado",
                    f"La {'compra' if self.tipo_compra == 'compra' else 'gasto'} ha sido guardada exitosamente"
                )
                self.compra_guardada.emit(datos_compra)
                self.cerrar_solicitado.emit()
            else:
                show_error_dialog(self, "Error", "No se pudo guardar la compra/gasto")

        except Exception as e:
            logging.error(f"Error guardando compra/gasto: {e}")
            show_error_dialog(self, "Error", f"Error al guardar: {str(e)}")

    def generar_numero_cuenta(self):
        """Generar número único para la cuenta"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        tipo_prefix = 'COMP' if self.tipo_compra == 'compra' else 'GASTO'
        return f"{tipo_prefix}-{timestamp}"