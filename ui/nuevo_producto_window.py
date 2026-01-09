"""
Formulario de Nuevo Producto para HTF POS
Formulario unificado para agregar productos al catálogo unificado
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDateEdit, QScrollArea, QGroupBox, QFrame, QLabel,
    QTabWidget, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer, QEvent
from PySide6.QtGui import QFont, QIcon
import logging

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


class NuevoProductoWindow(QWidget):
    """Formulario unificado para agregar productos al catálogo"""

    cerrar_solicitado = Signal()
    producto_guardado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data

        # Variable para evitar verificaciones duplicadas
        self.ultimo_codigo_verificado = ""

        # Timer para detectar entrada del escáner
        self.barcode_timer = QTimer()
        self.barcode_timer.setSingleShot(True)
        self.barcode_timer.setInterval(300)  # 300ms después de que deje de escribir
        self.barcode_timer.timeout.connect(self._verificar_codigo_barras)

        self.setup_ui()
        self.cargar_datos_iniciales()
    
    def setup_ui(self):
        """Configurar interfaz del formulario con mejor UX"""
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

        # ===== PESTAÑA 1: INFORMACIÓN BÁSICA =====
        self.crear_pestana_basica()

        # ===== PESTAÑA 2: DETALLES Y ESPECIFICACIONES =====
        self.crear_pestana_detalles()

        # ===== PESTAÑA 3: INVENTARIO Y UBICACIÓN =====
        self.crear_pestana_inventario()

        content_layout.addWidget(self.tab_widget)

        # ===== BOTONES DE ACCIÓN =====
        self.crear_panel_botones(content_layout)

        # Configurar scroll
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Enfocar primer campo
        self.codigo_interno_input.setFocus()

    def crear_pestana_basica(self):
        """Crear la pestaña de información básica"""
        tab_basica = QWidget()
        layout = QVBoxLayout(tab_basica)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título de la sección
        titulo = QLabel("Información Básica del Producto")
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Formulario en grid para mejor organización
        form_grid = QGridLayout()
        form_grid.setSpacing(15)

        # Fila 1: Código Interno y Nombre
        codigo_label = QLabel("Código Interno *")
        codigo_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(codigo_label, 0, 0)

        nombre_label = QLabel("Nombre del Producto *")
        nombre_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(nombre_label, 0, 2)

        self.codigo_interno_input = QLineEdit()
        self.codigo_interno_input.setPlaceholderText("Ej: PROD001, SUP001")
        self.codigo_interno_input.setMinimumHeight(40)
        self.codigo_interno_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        self.codigo_interno_input.textChanged.connect(lambda text: self.codigo_interno_input.setText(text.upper()))
        form_grid.addWidget(self.codigo_interno_input, 1, 0)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo y descriptivo")
        self.nombre_input.setMinimumHeight(40)
        self.nombre_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        form_grid.addWidget(self.nombre_input, 1, 2)

        # Fila 2: Precio y Estado
        precio_label = QLabel("Precio de Venta *")
        precio_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(precio_label, 2, 0)

        estado_label = QLabel("Estado del Producto")
        estado_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(estado_label, 2, 2)

        self.precio_input = TouchMoneyInput(
            minimum=0.01,
            maximum=999999.99,
            decimals=2,
            default_value=0.0
        )
        form_grid.addWidget(self.precio_input, 3, 0)

        self.activo_check = QCheckBox("Producto activo y disponible para venta")
        self.activo_check.setChecked(True)
        self.activo_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_GREEN};
                border-color: {WindowsPhoneTheme.TILE_GREEN};
            }}
        """)
        form_grid.addWidget(self.activo_check, 3, 2)

        # Fila 3: Precios Mayoreo
        mayoreo_label = QLabel("Precio Mayoreo")
        mayoreo_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(mayoreo_label, 4, 0)

        cantidad_mayoreo_label = QLabel("Cantidad Mayoreo")
        cantidad_mayoreo_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(cantidad_mayoreo_label, 4, 2)

        self.precio_mayoreo_input = TouchMoneyInput(
            minimum=0.0,
            maximum=999999.99,
            decimals=2,
            default_value=0.0
        )
        form_grid.addWidget(self.precio_mayoreo_input, 5, 0)

        self.cantidad_mayoreo_input = TouchNumericInput(
            minimum=0,
            maximum=999999,
            default_value=0
        )
        form_grid.addWidget(self.cantidad_mayoreo_input, 5, 2)

        # Fila 4: Costo Promedio e Imagen
        costo_label = QLabel("Costo Promedio")
        costo_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(costo_label, 6, 0)

        imagen_label = QLabel("URL de Imagen")
        imagen_label.setStyleSheet("font-weight: bold;")
        form_grid.addWidget(imagen_label, 6, 2)

        self.costo_promedio_input = TouchMoneyInput(
            minimum=0.0,
            maximum=999999.99,
            decimals=2,
            default_value=0.0
        )
        form_grid.addWidget(self.costo_promedio_input, 7, 0)

        self.imagen_url_input = QLineEdit()
        self.imagen_url_input.setPlaceholderText("https://ejemplo.com/imagen.jpg")
        self.imagen_url_input.setMinimumHeight(40)
        self.imagen_url_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        form_grid.addWidget(self.imagen_url_input, 7, 2)

        # Configurar columnas stretch
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 0)  # Espacio entre columnas
        form_grid.setColumnStretch(2, 2)

        layout.addLayout(form_grid)

        # Descripción
        desc_label = QLabel("Descripción del Producto")
        desc_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(desc_label)

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Describe las características, beneficios, uso recomendado...")
        self.descripcion_input.setMaximumHeight(80)
        self.descripcion_input.setStyleSheet(f"""
            QTextEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QTextEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        layout.addWidget(self.descripcion_input)

        self.tab_widget.addTab(tab_basica, "General")

    def crear_pestana_detalles(self):
        """Crear la pestaña de detalles y especificaciones"""
        tab_detalles = QWidget()
        layout = QVBoxLayout(tab_detalles)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título de la sección
        titulo = QLabel("Detalles y Especificaciones")
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Formulario en dos columnas
        form_grid = QGridLayout()
        form_grid.setSpacing(15)

        # Columna 1: Identificación y Categorización
        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(15)

        # Grupo: Identificación
        grupo_id = QGroupBox("Identificación")
        grupo_id.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_id.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        id_layout = QFormLayout(grupo_id)
        id_layout.setSpacing(10)

        # Código de Barras
        self.codigo_barras_input = QLineEdit()
        self.codigo_barras_input.setPlaceholderText("Escanee o ingrese el código de barras")
        self.codigo_barras_input.setMinimumHeight(40)
        self.codigo_barras_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        self.codigo_barras_input.installEventFilter(self)
        self.codigo_barras_input.textChanged.connect(self._on_barcode_text_changed)
        id_layout.addRow("Código de Barras:", self.codigo_barras_input)

        col1_layout.addWidget(grupo_id)

        # Grupo: Clasificación
        grupo_clasif = QGroupBox("Clasificación")
        grupo_clasif.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_clasif.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        clasif_layout = QFormLayout(grupo_clasif)
        clasif_layout.setSpacing(10)

        # Categoría
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems([
            "-- Seleccionar categoría --",
            "Suplementos Alimenticios",
            "Proteínas",
            "Vitaminas y Minerales",
            "Bebidas Energéticas",
            "Snacks Saludables",
            "Accesorios Deportivos",
            "Ropa Deportiva",
            "Equipamiento",
            "Otros"
        ])
        self.categoria_combo.setMinimumHeight(40)
        self.categoria_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QComboBox:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        clasif_layout.addRow("Categoría:", self.categoria_combo)

        # Marca
        self.marca_input = QLineEdit()
        self.marca_input.setPlaceholderText("Ej: Optimum Nutrition, Adidas")
        self.marca_input.setMinimumHeight(40)
        self.marca_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        clasif_layout.addRow("Marca:", self.marca_input)

        # Tipo
        self.tipo_input = QLineEdit()
        self.tipo_input.setPlaceholderText("Ej: Whey Protein, Zapatillas Running")
        self.tipo_input.setMinimumHeight(40)
        self.tipo_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        clasif_layout.addRow("Tipo/Subtipo:", self.tipo_input)

        col1_layout.addWidget(grupo_clasif)
        col1_layout.addStretch(1)

        # Columna 2: Medidas y Características
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(15)

        # Grupo: Medidas y Empaque
        grupo_medidas = QGroupBox("Medidas y Empaque")
        grupo_medidas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_medidas.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        medidas_layout = QFormLayout(grupo_medidas)
        medidas_layout.setSpacing(10)

        # Cantidad de Medida
        self.cantidad_medida_input = TouchMoneyInput(
            minimum=0.0,
            maximum=999999.99,
            decimals=2,
            default_value=0.0,
            prefix=""
        )
        medidas_layout.addRow("Cantidad de Medida:", self.cantidad_medida_input)

        # Unidad de Medida
        self.unidad_medida_combo = QComboBox()
        self.unidad_medida_combo.addItems([
            "-- Seleccionar unidad --",
            "gramos", "kilogramos", "mililitros", "litros",
            "piezas", "onzas", "libras", "galones",
            "caja", "paquete", "bolsa", "botella"
        ])
        self.unidad_medida_combo.setMinimumHeight(40)
        self.unidad_medida_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QComboBox:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        medidas_layout.addRow("Unidad de Medida:", self.unidad_medida_combo)

        col2_layout.addWidget(grupo_medidas)

        # Grupo: Características Especiales
        grupo_caract = QGroupBox("Características Especiales")
        grupo_caract.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_caract.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        caract_layout = QVBoxLayout(grupo_caract)
        caract_layout.setSpacing(10)

        self.refrigeracion_check = QCheckBox("❄️ Requiere refrigeración")
        self.refrigeracion_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        caract_layout.addWidget(self.refrigeracion_check)

        # Categoría Contable
        contable_layout = QHBoxLayout()
        contable_layout.addWidget(QLabel("Categoría Contable:"))
        self.categoria_contable_input = QLineEdit()
        self.categoria_contable_input.setPlaceholderText("Ej: SUPLEMENTOS, BEBIDAS")
        self.categoria_contable_input.setMinimumHeight(40)
        self.categoria_contable_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        contable_layout.addWidget(self.categoria_contable_input)
        caract_layout.addLayout(contable_layout)

        # Impuestos
        impuestos_layout = QGridLayout()
        impuestos_layout.setSpacing(10)

        # IEPS
        ieps_check = QCheckBox("Aplica IEPS")
        ieps_check.setChecked(False)
        ieps_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        impuestos_layout.addWidget(ieps_check, 0, 0)

        self.porcentaje_ieps_input = TouchMoneyInput(
            minimum=0.0,
            maximum=100.0,
            decimals=2,
            default_value=0.0,
            prefix=""
        )
        self.porcentaje_ieps_input.setEnabled(False)
        ieps_check.toggled.connect(self.porcentaje_ieps_input.setEnabled)
        impuestos_layout.addWidget(QLabel("% IEPS:"), 0, 1)
        impuestos_layout.addWidget(self.porcentaje_ieps_input, 0, 2)

        # IVA
        iva_check = QCheckBox("Aplica IVA")
        iva_check.setChecked(True)
        iva_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        impuestos_layout.addWidget(iva_check, 1, 0)

        self.porcentaje_iva_input = TouchMoneyInput(
            minimum=0.0,
            maximum=100.0,
            decimals=2,
            default_value=16.0,
            prefix=""
        )
        self.porcentaje_iva_input.setEnabled(True)
        iva_check.toggled.connect(self.porcentaje_iva_input.setEnabled)
        impuestos_layout.addWidget(QLabel("% IVA:"), 1, 1)
        impuestos_layout.addWidget(self.porcentaje_iva_input, 1, 2)

        caract_layout.addLayout(impuestos_layout)

        # Fecha de Vencimiento
        venc_layout = QHBoxLayout()
        venc_layout.addWidget(StyledLabel("Fecha de Vencimiento", bold=True))

        self.fecha_vencimiento_input = QDateEdit()
        self.fecha_vencimiento_input.setCalendarPopup(True)
        self.fecha_vencimiento_input.setDate(QDate.currentDate().addYears(1))
        self.fecha_vencimiento_input.setMinimumHeight(46)
        aplicar_estilo_fecha(self.fecha_vencimiento_input)
        venc_layout.addWidget(self.fecha_vencimiento_input)
        caract_layout.addLayout(venc_layout)

        col2_layout.addWidget(grupo_caract)
        col2_layout.addStretch(1)

        # Agregar columnas al grid
        form_grid.addLayout(col1_layout, 0, 0)
        form_grid.addLayout(col2_layout, 0, 1)
        form_grid.setColumnStretch(0, 1)
        form_grid.setColumnStretch(1, 1)

        layout.addLayout(form_grid)
        # Evitar que el contenido se "estire" y genere espacios vacíos dentro de los grupos
        layout.addStretch(1)

        self.tab_widget.addTab(tab_detalles, "Detalles")

    def crear_pestana_inventario(self):
        """Crear la pestaña de inventario y ubicación"""
        tab_inventario = QWidget()
        layout = QVBoxLayout(tab_inventario)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título de la sección
        titulo = QLabel("Inventario y Ubicación")
        titulo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_SUBTITLE, QFont.Bold))
        titulo.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Grupo: Configuración de Inventario
        grupo_inventario = QGroupBox("Configuración Inicial de Inventario")
        grupo_inventario.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_inventario.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        inventario_layout = QGridLayout(grupo_inventario)
        inventario_layout.setSpacing(15)

        # Stock Inicial
        stock_label = QLabel("Stock Inicial:")
        stock_label.setStyleSheet("font-weight: bold;")
        inventario_layout.addWidget(stock_label, 0, 0)

        self.stock_inicial_input = TouchNumericInput(
            minimum=0,
            maximum=999999,
            default_value=0
        )
        inventario_layout.addWidget(self.stock_inicial_input, 0, 1)

        # Stock Mínimo
        stock_min_label = QLabel("Stock Mínimo:")
        stock_min_label.setStyleSheet("font-weight: bold;")
        inventario_layout.addWidget(stock_min_label, 1, 0)

        self.stock_minimo_input = TouchNumericInput(
            minimum=0,
            maximum=999999,
            default_value=5
        )
        inventario_layout.addWidget(self.stock_minimo_input, 1, 1)

        # Información adicional
        info_label = QLabel("El stock inicial se puede ajustar después de guardar el producto.")
        info_label.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_SECONDARY}; font-style: italic; margin-top: 10px;")
        inventario_layout.addWidget(info_label, 2, 0, 1, 2)

        # Configuración adicional de inventario
        config_layout = QVBoxLayout()
        config_layout.setSpacing(8)

        self.es_inventariable_check = QCheckBox("Producto inventariable (controla stock)")
        self.es_inventariable_check.setChecked(True)
        self.es_inventariable_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        config_layout.addWidget(self.es_inventariable_check)

        self.permite_venta_sin_stock_check = QCheckBox("Permitir venta sin stock disponible")
        self.permite_venta_sin_stock_check.setChecked(False)
        self.permite_venta_sin_stock_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        config_layout.addWidget(self.permite_venta_sin_stock_check)

        inventario_layout.addLayout(config_layout, 3, 0, 1, 2)

        layout.addWidget(grupo_inventario)

        # Grupo: Ubicación en Almacén
        grupo_ubicacion = QGroupBox("Ubicación en Almacén")
        grupo_ubicacion.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_ubicacion.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        ubicacion_layout = QVBoxLayout(grupo_ubicacion)
        ubicacion_layout.setSpacing(10)

        self.ubicacion_combo = QComboBox()
        self.ubicacion_combo.setMinimumHeight(45)
        self.ubicacion_combo.addItem("-- Seleccionar ubicación --", None)
        self.ubicacion_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QComboBox:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        ubicacion_layout.addWidget(self.ubicacion_combo)

        # Campo adicional para ubicación específica
        ubicacion_layout.addWidget(QLabel("Ubicación Específica (opcional):"))
        self.ubicacion_especifica_input = QLineEdit()
        self.ubicacion_especifica_input.setPlaceholderText("Ej: Estante A-3, Refrigerador 2")
        self.ubicacion_especifica_input.setMinimumHeight(40)
        self.ubicacion_especifica_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        ubicacion_layout.addWidget(self.ubicacion_especifica_input)

        layout.addWidget(grupo_ubicacion)

        # Grupo: Notas Adicionales
        grupo_notas = QGroupBox("Notas Adicionales")
        grupo_notas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        grupo_notas.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)

        notas_layout = QVBoxLayout(grupo_notas)
        self.notas_input = QTextEdit()
        self.notas_input.setPlaceholderText("Información adicional sobre el producto, cuidados especiales, instrucciones...")
        self.notas_input.setMaximumHeight(100)
        self.notas_input.setStyleSheet(f"""
            QTextEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QTextEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
        """)
        notas_layout.addWidget(self.notas_input)

        layout.addWidget(grupo_notas)

        # Espacio sobrante al final para mantener alturas homogéneas entre pestañas
        layout.addStretch(1)

        self.tab_widget.addTab(tab_inventario, "Inventario")

    def crear_panel_botones(self, parent_layout):
        """Crear el panel de botones de acción"""
        buttons_panel = ContentPanel()
        buttons_layout = QHBoxLayout(buttons_panel)
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        buttons_layout.setContentsMargins(20, 15, 20, 15)

        btn_guardar = TileButton("Guardar Producto", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_producto)
        buttons_layout.addWidget(btn_guardar)

        btn_limpiar = TileButton("Limpiar Formulario", "fa5s.eraser", WindowsPhoneTheme.TILE_ORANGE)
        btn_limpiar.clicked.connect(self.limpiar_formulario)
        buttons_layout.addWidget(btn_limpiar)

        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.confirmar_cancelar)
        buttons_layout.addWidget(btn_cancelar)

        parent_layout.addWidget(buttons_panel)

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales como ubicaciones"""
        self.cargar_ubicaciones()
    
    def eventFilter(self, obj, event):
        """Filtrar eventos para detectar Enter del scanner en código de barras"""
        if obj == self.codigo_barras_input and event.type() == QEvent.KeyPress:
            key_event = event
            logging.info(f"[EVENT FILTER] Tecla presionada: {key_event.key()} (Enter={Qt.Key_Return})")
            
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                logging.info("[EVENT FILTER] Enter detectado - verificando código de barras")
                self._verificar_codigo_barras()
                return True  # Evento manejado
        
        return super().eventFilter(obj, event)
    
    def _on_barcode_text_changed(self):
        """Detectar cuando se ingresa texto (para capturar escáner)"""
        texto = self.codigo_barras_input.text().strip()
        
        # Reiniciar el timer cada vez que cambia el texto
        self.barcode_timer.stop()
        
        # Resetear el último código verificado si el usuario está editando
        if len(texto) < 8:
            self.ultimo_codigo_verificado = ""
        
        # Si el texto tiene longitud suficiente para ser un código de barras
        if len(texto) >= 8:  # Códigos de barras típicamente tienen 8+ dígitos
            logging.info(f"[SCANNER TIMER] Detectado código de longitud {len(texto)}, iniciando timer...")
            # Iniciar timer para verificar después de 300ms de inactividad
            self.barcode_timer.start()
    
    def _verificar_codigo_barras(self):
        """Verificar si el código de barras ya existe cuando se presiona Enter"""
        codigo_barras = self.codigo_barras_input.text().strip()
        
        # Evitar verificar el mismo código múltiples veces
        if not codigo_barras or codigo_barras == self.ultimo_codigo_verificado:
            return
        
        logging.info(f"[SCANNER] Verificando código de barras: '{codigo_barras}' (longitud: {len(codigo_barras)})")
        self.ultimo_codigo_verificado = codigo_barras
        
        try:
            # Buscar si ya existe el código de barras en la tabla unificada
            producto_existente = self.pg_manager.query(f"""
                SELECT codigo_interno, nombre, categoria
                FROM ca_productos
                WHERE codigo_barras = '{codigo_barras}' AND activo = true
                LIMIT 1
            """)

            if producto_existente and len(producto_existente) > 0:
                p = producto_existente[0]
                logging.warning(f"Código de barras duplicado: {codigo_barras}")
                show_warning_dialog(
                    self,
                    "Código de barras duplicado",
                    f"El código de barras ya existe en el sistema:\n\n"
                    f"Código Interno: {p['codigo_interno']}\n"
                    f"Nombre: {p['nombre']}\n"
                    f"Categoría: {p.get('categoria', 'N/A')}"
                )
                self.tab_widget.setCurrentIndex(1)  # Ir a pestaña de detalles
                self.codigo_barras_input.setFocus()
                self.codigo_barras_input.selectAll()
                return

            # Si no existe, mover al siguiente campo sin diálogo
            logging.info(f"[SCANNER] Código de barras {codigo_barras} disponible - moviendo al siguiente campo")
            self.categoria_combo.setFocus()
            
        except Exception as e:
            logging.error(f"Error verificando código de barras: {e}")
            show_error_dialog(
                self,
                "Error de verificación",
                "No se pudo verificar el código de barras"
            )
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        # Pestaña Básico
        self.codigo_interno_input.clear()
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.precio_input.setValue(0.0)
        self.precio_mayoreo_input.setValue(0.0)
        self.cantidad_mayoreo_input.setValue(0)
        self.costo_promedio_input.setValue(0.0)
        self.imagen_url_input.clear()
        self.activo_check.setChecked(True)

        # Pestaña Detalles
        self.codigo_barras_input.clear()
        self.categoria_combo.setCurrentIndex(0)
        self.marca_input.clear()
        self.tipo_input.clear()
        self.cantidad_medida_input.setValue(0.0)
        self.unidad_medida_combo.setCurrentIndex(0)
        self.refrigeracion_check.setChecked(False)
        self.categoria_contable_input.clear()
        # Resetear checkboxes de impuestos
        self.porcentaje_ieps_input.setValue(0.0)
        self.porcentaje_iva_input.setValue(16.0)
        self.fecha_vencimiento_input.setDate(QDate.currentDate().addYears(1))

        # Pestaña Inventario
        self.stock_inicial_input.setValue(0)
        self.stock_minimo_input.setValue(5)
        self.es_inventariable_check.setChecked(True)
        self.permite_venta_sin_stock_check.setChecked(False)
        self.ubicacion_combo.setCurrentIndex(0)
        self.ubicacion_especifica_input.clear()
        self.notas_input.clear()

        # Resetear pestaña a la primera
        self.tab_widget.setCurrentIndex(0)

        # Enfocar primer campo
        self.codigo_interno_input.setFocus()

        logging.info("Formulario limpiado")
    
    def cargar_ubicaciones(self):
        """Cargar ubicaciones desde el catálogo ca_ubicaciones"""
        try:
            # Usar el método get_ubicaciones de PostgreSQL
            ubicaciones = self.pg_manager.get_ubicaciones()
            
            # Agregar ubicaciones al combo
            for ubicacion in ubicaciones:
                self.ubicacion_combo.addItem(
                    ubicacion['nombre'],
                    ubicacion['id_ubicacion']
                )
            
            if ubicaciones:
                # Seleccionar la segunda opción (primera ubicación real) por defecto
                self.ubicacion_combo.setCurrentIndex(1)
                logging.info(f"Cargadas {len(ubicaciones)} ubicaciones")
            else:
                logging.warning("No hay ubicaciones disponibles en el catálogo")
                    
        except Exception as e:
            logging.error(f"Error cargando ubicaciones: {e}")
            show_error_dialog(
                self,
                "Error",
                "No se pudieron cargar las ubicaciones del catálogo"
            )
    
    def confirmar_cancelar(self):
        """Confirmar antes de cancelar"""
        if show_confirmation_dialog(
            self,
            "Cancelar",
            "¿Desea cancelar y volver sin guardar?",
            "Se perderán todos los cambios no guardados."
        ):
            self.cerrar_solicitado.emit()
    
    def validar_campos(self):
        """Validar campos del formulario"""
        # Validar campos básicos (requeridos)
        if not self.codigo_interno_input.text().strip():
            show_warning_dialog(self, "Campo requerido", "Debe ingresar un código interno.")
            self.tab_widget.setCurrentIndex(0)
            self.codigo_interno_input.setFocus()
            return False

        if not self.nombre_input.text().strip():
            show_warning_dialog(self, "Campo requerido", "Debe ingresar un nombre para el producto.")
            self.tab_widget.setCurrentIndex(0)
            self.nombre_input.setFocus()
            return False

        if self.precio_input.value() <= 0:
            show_warning_dialog(self, "Precio inválido", "El precio de venta debe ser mayor a cero.")
            self.tab_widget.setCurrentIndex(0)
            self.precio_input.setFocus()
            return False

        # Validar ubicación
        if self.ubicacion_combo.currentIndex() == 0:
            show_warning_dialog(self, "Campo requerido", "Debe seleccionar una ubicación de almacén.")
            self.tab_widget.setCurrentIndex(2)
            self.ubicacion_combo.setFocus()
            return False

        # Validar stock inicial y mínimo
        if self.stock_inicial_input.value() < 0:
            show_warning_dialog(self, "Valor inválido", "El stock inicial no puede ser negativo.")
            self.tab_widget.setCurrentIndex(2)
            self.stock_inicial_input.setFocus()
            return False

        if self.stock_minimo_input.value() < 0:
            show_warning_dialog(self, "Valor inválido", "El stock mínimo no puede ser negativo.")
            self.tab_widget.setCurrentIndex(2)
            self.stock_minimo_input.setFocus()
            return False

        # Verificar código interno único
        codigo = self.codigo_interno_input.text().strip().upper()
        if self.pg_manager.producto_existe(codigo):
            show_error_dialog(
                self,
                "Código duplicado",
                f"El código '{codigo}' ya existe en el sistema.",
                "Por favor, use un código diferente."
            )
            self.tab_widget.setCurrentIndex(0)
            self.codigo_interno_input.setFocus()
            return False

        # Verificar código de barras único (si se proporcionó)
        codigo_barras = self.codigo_barras_input.text().strip()
        if codigo_barras:
            existente = self.pg_manager.query(f"""
                SELECT codigo_interno, nombre
                FROM ca_productos
                WHERE codigo_barras = '{codigo_barras}' AND activo = true
                LIMIT 1
            """)
            if existente and len(existente) > 0:
                p = existente[0]
                show_warning_dialog(
                    self,
                    "Código de barras duplicado",
                    f"El código de barras '{codigo_barras}' ya existe en el sistema.",
                    f"Producto: {p['codigo_interno']} - {p['nombre']}"
                )
                self.tab_widget.setCurrentIndex(1)
                self.codigo_barras_input.setFocus()
                return False

        return True
    
    def guardar_producto(self):
        """Guardar el producto en la base de datos"""
        try:
            # Validar campos
            if not self.validar_campos():
                return

            # Preparar datos del producto para la tabla unificada ca_productos
            producto_data = {
                'codigo_interno': self.codigo_interno_input.text().strip().upper(),
                'nombre': self.nombre_input.text().strip(),
                'descripcion': self.descripcion_input.toPlainText().strip() or None,
                'imagen_url': self.imagen_url_input.text().strip() or None,
                'precio_venta': self.precio_input.value(),
                'precio_mayoreo': self.precio_mayoreo_input.value() if self.precio_mayoreo_input.value() > 0 else None,
                'cantidad_mayoreo': int(self.cantidad_mayoreo_input.value()) if self.cantidad_mayoreo_input.value() > 0 else None,
                'costo_promedio': self.costo_promedio_input.value() if self.costo_promedio_input.value() > 0 else None,
                'categoria': self.categoria_combo.currentText() if self.categoria_combo.currentIndex() > 0 else None,
                'categoria_contable': self.categoria_contable_input.text().strip() or None,
                'marca': self.marca_input.text().strip() or None,
                'tipo': self.tipo_input.text().strip() or None,
                'cantidad_medida': self.cantidad_medida_input.value() if self.cantidad_medida_input.value() > 0 else None,
                'unidad_medida': self.unidad_medida_combo.currentText() if self.unidad_medida_combo.currentIndex() > 0 else None,
                'codigo_barras': self.codigo_barras_input.text().strip() or None,
                'requiere_refrigeracion': self.refrigeracion_check.isChecked(),
                'es_inventariable': self.es_inventariable_check.isChecked(),
                'permite_venta_sin_stock': self.permite_venta_sin_stock_check.isChecked(),
                'aplica_ieps': self.porcentaje_ieps_input.value() > 0,
                'porcentaje_ieps': self.porcentaje_ieps_input.value() if self.porcentaje_ieps_input.value() > 0 else 0,
                'aplica_iva': self.porcentaje_iva_input.value() > 0,
                'porcentaje_iva': self.porcentaje_iva_input.value() if self.porcentaje_iva_input.value() > 0 else 0,
                'stock_actual': int(self.stock_inicial_input.value()),
                'stock_minimo': int(self.stock_minimo_input.value()),
                'ubicacion': self.ubicacion_especifica_input.text().strip() or None,
                'fecha_vencimiento': self.fecha_vencimiento_input.date().toString("yyyy-MM-dd") if self.fecha_vencimiento_input.date() > QDate.currentDate() else None,
                'notas': self.notas_input.toPlainText().strip() or None,
                'activo': self.activo_check.isChecked()
            }

            # Guardar producto en la tabla unificada
            success = self.pg_manager.insertar_producto(producto_data)

            if success:
                # Obtener ID de ubicación seleccionada para el inventario
                id_ubicacion = self.ubicacion_combo.currentData()

                # Crear registro en inventario con la ubicación
                inventario_data = {
                    'codigo_interno': producto_data['codigo_interno'],
                    'tipo_producto': 'producto',  # Ahora todos son productos unificados
                    'stock_actual': producto_data['stock_actual'],
                    'stock_minimo': producto_data['stock_minimo'],
                    'id_ubicacion': id_ubicacion,
                    'activo': producto_data['activo']
                }

                self.pg_manager.crear_inventario(inventario_data)

                # Mostrar mensaje de éxito
                show_success_dialog(
                    self,
                    "Producto guardado",
                    f"El producto '{producto_data['nombre']}' se guardó correctamente.",
                    f"Código: {producto_data['codigo_interno']}\n"
                    f"Inventario inicial: {producto_data['stock_actual']} unidades\n"
                    f"Stock mínimo: {producto_data['stock_minimo']} unidades"
                )

                # Limpiar formulario y emitir señal
                self.limpiar_formulario()
                self.producto_guardado.emit()

                logging.info(f"Producto guardado: {producto_data['codigo_interno']} - {producto_data['nombre']}")
            else:
                show_error_dialog(
                    self,
                    "Error al guardar",
                    "No se pudo guardar el producto.",
                    "Verifique los datos e intente nuevamente."
                )

        except Exception as e:
            logging.error(f"Error guardando producto: {e}")
            show_error_dialog(
                self,
                "Error",
                "Ocurrió un error al guardar el producto",
                detail=str(e)
            )
