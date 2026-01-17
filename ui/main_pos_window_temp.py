"""Ventana principal del sistema Punto Clave.
Interfaz sencilla con pestañas en la parte inferior
Para rol: Recepcionista
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QGridLayout, QScrollArea, QSizePolicy, QDialog,
    QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QCursor
import logging
import subprocess
import sys
import os

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    InfoTile,
    SectionTitle,
    StyledLabel,
    TabButton,
    TopBar,
    apply_windows_phone_stylesheet,
    create_page_layout,
    create_tile_grid_layout,
    show_success_dialog,
    show_error_dialog,
    show_warning_dialog,
    show_info_dialog
)

# Importar ventanas de ventas
from ui.ventas import (
    NuevaVentaWindow,
    VentasDiaWindow,
    HistorialVentasWindow,
    CierreCajaWindow
)

# Importar ventanas disponibles
from ui.inventario_window import InventarioWindow
from ui.cuentas_por_pagar_window import CuentasPorPagarWindow
from ui.nueva_compra_window import NuevaCompraWindow
from ui.nuevo_producto_window import NuevoProductoWindow
from ui.productos_window import ProductosWindow
from ui.proveedores_window import ProveedoresWindow
from ui.clientes_window import ClientesWindow
from ui.tipo_cuenta_pagar_window import TipoCuentaPagarWindow
from ui.historial_movimientos_window import HistorialMovimientosWindow
from ui.historial_turnos_window import HistorialTurnosWindow
from ui.asignacion_turnos_window import AsignacionTurnosWindow
from ui.ubicaciones_window import UbicacionesWindow
from ui.movimiento_inventario_window import MovimientoInventarioWindow
from database.postgres_manager import PostgresManager


class MainPOSWindow(QMainWindow):
    """Ventana principal del sistema POS"""
    
    logout_requested = Signal()
    
    def __init__(self, user_data, pg_manager, turno_id=None):
        super().__init__()
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.turno_id = turno_id  # ID del turno activo
        
        self.setWindowTitle("PUNTO CLAVE")
        self.setGeometry(100, 50, 1400, 900)
        
        # Establecer icono de la ventana
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'pos_icono.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Establecer tamaño mínimo para evitar problemas de layout
        self.setMinimumSize(1000, 700)
        
        # Iniciar en pantalla completa
        self.showMaximized()
        
        # Variables de estado
        self.current_tab = 0
        
        # Monitor de entradas (desactivado por ahora)
        self.monitor_entradas = None
        self.notificaciones_activas = []  # Lista de notificaciones abiertas
        
        # Aplicar estilos Windows Phone
        apply_windows_phone_stylesheet(self)
        
        self.setup_ui()
        
        # Iniciar monitor de entradas (desactivado)
        # self.iniciar_monitor_entradas()
        
    def setup_ui(self):
        """Configurar interfaz principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra superior con información de usuario (usando componente)
        self.top_bar = TopBar(
            title="PUNTO CLAVE",
            user_name=self.user_data['nombre_completo'],
            user_role=self.user_data['rol']
        )
        main_layout.addWidget(self.top_bar)
        
        # Área de contenido (cambia según la pestaña)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Crear las páginas de cada pestaña
        self.create_sales_page()
        self.create_inventory_page()
        self.create_admin_page()
        self.create_tab6_page()
        self.create_tab5_page()
        self.create_config_page()
        
        # Barra de navegación inferior con pestañas
        self.create_bottom_nav(main_layout)
        
        # Mostrar la primera pestaña (Ventas)
        self.stacked_widget.setCurrentIndex(0)
        
    def create_bottom_nav(self, parent_layout):
        """Crear barra de navegación inferior usando TabButton"""
        self.nav_bar = QFrame()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedHeight(WindowsPhoneTheme.NAV_BAR_HEIGHT)
        
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        # Definir pestañas con iconos y colores
        tabs = [
            {"name": "Punto de Venta", "icon": "fa5s.shopping-cart", "color": WindowsPhoneTheme.TILE_RED, "index": 0},
            {"name": "Ventas", "icon": "fa5s.list-alt", "color": WindowsPhoneTheme.TILE_ORANGE, "index": 1},
            {"name": "Inventario", "icon": "fa5s.boxes", "color": WindowsPhoneTheme.TILE_GREEN, "index": 2},
            {"name": "Compras y Gastos", "icon": "fa5s.shopping-bag", "color": WindowsPhoneTheme.TILE_TEAL, "index": 3},
            {"name": "Clientes", "icon": "fa5s.users", "color": WindowsPhoneTheme.TILE_BLUE, "index": 4},
            {"name": "Admin/Config", "icon": "fa5s.cogs", "color": WindowsPhoneTheme.TILE_PURPLE, "index": 5},
        ]
        
        # Crear botones usando componente TabButton
        self.tab_buttons = []
        for tab in tabs:
            btn = TabButton(tab['name'], tab['icon'], tab['color'])
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked, idx=tab['index']: self.switch_tab(idx))
            nav_layout.addWidget(btn)
            self.tab_buttons.append(btn)
        
        # Activar primera pestaña
        self.tab_buttons[0].setChecked(True)
        
        parent_layout.addWidget(self.nav_bar)
        
    def switch_tab(self, index):
        """Cambiar de pestaña"""
        self.current_tab = index
        self.stacked_widget.setCurrentIndex(index)
        
        # Actualizar estado visual de botones
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
            
        logging.info(f"Cambio a pestaña: {index}")
        
    # ========== PÁGINAS DE CONTENIDO ==========
    
    def create_sales_page(self):
        """Página de punto de venta usando TileButton"""
        page = QWidget()
        layout = create_page_layout("PUNTO DE VENTA")
        page.setLayout(layout)
        
        # Grid de tiles - 2 filas x 2 columnas
        grid = create_tile_grid_layout()
        
        # Botones de acciones usando componente TileButton
        btn_nueva_venta = TileButton("Nueva Venta", "fa5s.cash-register", WindowsPhoneTheme.TILE_RED)
        btn_nueva_venta.clicked.connect(self.abrir_nueva_venta)
        grid.addWidget(btn_nueva_venta, 0, 0)
        
        btn_ventas_dia = TileButton("Ventas del Día", "fa5s.list-alt", WindowsPhoneTheme.TILE_ORANGE)
        btn_ventas_dia.clicked.connect(self.abrir_ventas_dia)
        grid.addWidget(btn_ventas_dia, 0, 1)
        
        btn_cierre = TileButton("Cierre de Caja", "fa5s.lock", WindowsPhoneTheme.TILE_MAGENTA)
        btn_cierre.clicked.connect(self.abrir_cierre_caja)
        grid.addWidget(btn_cierre, 1, 0)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_inventory_page(self):
        """Página de ventas usando TileButton"""
        page = QWidget()
        layout = create_page_layout("VENTAS")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Historial\nVentas", "icon": "fa5s.history", "color": WindowsPhoneTheme.TILE_PURPLE, "callback": self.abrir_historial},
            {"text": "Cancelaciones", "icon": "fa5s.times-circle", "color": WindowsPhoneTheme.TILE_RED, "callback": self.show_mock_dialog},
            {"text": "Ventas a\nCrédito", "icon": "fa5s.credit-card", "color": WindowsPhoneTheme.TILE_BLUE, "callback": self.show_mock_dialog},
            {"text": "Reporte\nVendedores", "icon": "fa5s.chart-bar", "color": WindowsPhoneTheme.TILE_GREEN, "callback": self.show_mock_dialog},
            {"text": "Estadísticas", "icon": "fa5s.chart-line", "color": WindowsPhoneTheme.TILE_ORANGE, "callback": self.show_mock_dialog},
        ]
        
        # Agregar los botones al grid
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            if action["callback"]:
                btn.clicked.connect(action["callback"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        

        
    def create_admin_page(self):
        """Página de inventario usando TileButton"""
        page = QWidget()
        layout = create_page_layout("INVENTARIO")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Productos", "icon": "fa5s.box", "color": WindowsPhoneTheme.TILE_BLUE, "callback": self.abrir_productos},
            {"text": "Inventario", "icon": "fa5s.warehouse", "color": WindowsPhoneTheme.TILE_GREEN, "callback": self.abrir_inventario},
            {"text": "Movimientos", "icon": "fa5s.exchange-alt", "color": WindowsPhoneTheme.TILE_PURPLE, "callback": self.abrir_historial_movimientos},
            {"text": "Ajustes del\nInventario", "icon": "fa5s.tools", "color": WindowsPhoneTheme.TILE_ORANGE, "callback": self.abrir_movimiento_inventario},
            {"text": "Conteo\nFísico", "icon": "fa5s.clipboard-check", "color": WindowsPhoneTheme.TILE_TEAL, "callback": self.show_mock_dialog},
        ]
        
        # Agregar los botones al grid
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            if action["callback"]:
                btn.clicked.connect(action["callback"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
    
    def create_tab5_page(self):
        """Página de clientes usando TileButton"""
        page = QWidget()
        layout = create_page_layout("CLIENTES")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Directorio", "icon": "fa5s.address-book", "color": WindowsPhoneTheme.TILE_BLUE, "callback": self.abrir_clientes},
            {"text": "Nuevo\nCliente", "icon": "fa5s.user-plus", "color": WindowsPhoneTheme.TILE_GREEN, "callback": self.show_mock_dialog},
            {"text": "Cuentas por\nCobrar", "icon": "fa5s.money-bill-wave", "color": WindowsPhoneTheme.TILE_ORANGE, "callback": self.show_mock_dialog},
            {"text": "Cobros", "icon": "fa5s.hand-holding-usd", "color": WindowsPhoneTheme.TILE_PURPLE, "callback": self.show_mock_dialog},
            {"text": "Historial", "icon": "fa5s.history", "color": WindowsPhoneTheme.TILE_TEAL, "callback": self.show_mock_dialog},
        ]
        
        # Agregar los botones al grid
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            if action["callback"]:
                btn.clicked.connect(action["callback"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_config_page(self):
        """Página de administración y configuración usando TileButton"""
        page = QWidget()
        layout = create_page_layout("ADMINISTRACIÓN / CONFIGURACIÓN")
        page.setLayout(layout)
        
        # Grid de administración/configuración
        grid = create_tile_grid_layout()
        
        # Solo mostrar si es administrador
        if self.user_data['rol'] in ['administrador', 'sistemas']:
            # Fila 1 - Funcionalidades administrativas
            btn_personal = TileButton("Gestionar\nProveedores", "fa5s.truck", WindowsPhoneTheme.TILE_GREEN)
            btn_personal.clicked.connect(self.abrir_gestion_proveedores)
            grid.addWidget(btn_personal, 0, 0)
            
            btn_dias_festivos = TileButton("Cuentas por\nPagar", "fa5s.file-invoice-dollar", WindowsPhoneTheme.TILE_BLUE)
            btn_dias_festivos.clicked.connect(self.abrir_dias_festivos)
            grid.addWidget(btn_dias_festivos, 0, 1)
            
            btn_historial_turnos = TileButton("Historial\nTurnos", "fa5s.cash-register", WindowsPhoneTheme.TILE_TEAL)
            btn_historial_turnos.clicked.connect(self.abrir_historial_turnos)
            grid.addWidget(btn_historial_turnos, 0, 2)
            
            btn_asignar_turnos = TileButton("Asignar\nTurnos", "fa5s.calendar-check", WindowsPhoneTheme.TILE_ORANGE)
            btn_asignar_turnos.clicked.connect(self.abrir_asignacion_turnos)
            grid.addWidget(btn_asignar_turnos, 0, 3)
            
            # Fila 2 - Más admin
            btn_ubicaciones = TileButton("Gestionar\nUbicaciones", "fa5s.warehouse", WindowsPhoneTheme.TILE_BLUE)
            btn_ubicaciones.clicked.connect(self.abrir_gestion_ubicaciones)
            grid.addWidget(btn_ubicaciones, 1, 0)
            
            btn_catalogo_lockers = TileButton("Catálogo\nde Clientes", "fa5s.users", WindowsPhoneTheme.TILE_TEAL)
            btn_catalogo_lockers.clicked.connect(self.abrir_catalogo_lockers)
            grid.addWidget(btn_catalogo_lockers, 1, 1)
            
            btn_historial_ventas = TileButton("Historial\nVentas", "fa5s.history", WindowsPhoneTheme.TILE_PURPLE)
            btn_historial_ventas.clicked.connect(self.abrir_historial)
            grid.addWidget(btn_historial_ventas, 1, 2)
            
            btn_historial_lockers = TileButton("Historial\nLockers", "fa5s.key", WindowsPhoneTheme.TILE_MAGENTA)
            btn_historial_lockers.clicked.connect(self.abrir_historial_lockers)
            grid.addWidget(btn_historial_lockers, 1, 3)
            
            # Fila 3 - Configuración
            btn_change_password = TileButton("Cambiar\nContraseña", "fa5s.lock", WindowsPhoneTheme.TILE_ORANGE)
            btn_change_password.clicked.connect(self.cambiar_contrasena)
            grid.addWidget(btn_change_password, 2, 0)
            
            btn_sync = TileButton("Sincronizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
            grid.addWidget(btn_sync, 2, 1)
            
            btn_tipos_cxp = TileButton("Catálogo\nTipos CxP", "fa5s.file-invoice-dollar", WindowsPhoneTheme.TILE_TEAL)
            btn_tipos_cxp.clicked.connect(self.abrir_catalogo_tipos_cxp)
            grid.addWidget(btn_tipos_cxp, 2, 2)
            
            btn_logout = TileButton("Cerrar\nSesión", "fa5s.sign-out-alt", WindowsPhoneTheme.TILE_RED)
            btn_logout.clicked.connect(self.handle_logout)
            grid.addWidget(btn_logout, 2, 3)
        else:
            # Si no es administrador, mostrar mensaje
            no_access_label = StyledLabel(
                "Acceso restringido a administradores",
                bold=True,
                size=WindowsPhoneTheme.FONT_SIZE_TITLE
            )
            no_access_label.setAlignment(Qt.AlignCenter)
            no_access_label.setStyleSheet(f"color: {WindowsPhoneTheme.TEXT_SECONDARY}; padding: 50px;")
            layout.addWidget(no_access_label)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_tab5_page(self):
        """Página de clientes usando TileButton"""
        page = QWidget()
        layout = create_page_layout("CLIENTES")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Directorio", "icon": "fa5s.address-book", "color": WindowsPhoneTheme.TILE_BLUE, "callback": self.abrir_clientes},
            {"text": "Nuevo\nCliente", "icon": "fa5s.user-plus", "color": WindowsPhoneTheme.TILE_GREEN, "callback": self.show_mock_dialog},
            {"text": "Cuentas por\nCobrar", "icon": "fa5s.money-bill-wave", "color": WindowsPhoneTheme.TILE_ORANGE, "callback": self.show_mock_dialog},
            {"text": "Cobros", "icon": "fa5s.hand-holding-usd", "color": WindowsPhoneTheme.TILE_PURPLE, "callback": self.show_mock_dialog},
            {"text": "Historial", "icon": "fa5s.history", "color": WindowsPhoneTheme.TILE_TEAL, "callback": self.show_mock_dialog},
        ]
        
        # Agregar los botones al grid
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            if action["callback"]:
                btn.clicked.connect(action["callback"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def create_tab6_page(self):
        """Página de compras y gastos usando TileButton"""
        page = QWidget()
        layout = create_page_layout("COMPRAS Y GASTOS")
        page.setLayout(layout)
        
        # Grid de tiles
        grid = create_tile_grid_layout()
        
        actions = [
            {"text": "Nueva\nCompra", "icon": "fa5s.cart-plus", "color": WindowsPhoneTheme.TILE_BLUE, "callback": self.abrir_nueva_compra},
            {"text": "Gastos y\nServicios", "icon": "fa5s.file-invoice-dollar", "color": WindowsPhoneTheme.TILE_GREEN, "callback": self.abrir_nuevo_gasto},
            {"text": "Cuentas por\nPagar", "icon": "fa5s.money-bill-wave", "color": WindowsPhoneTheme.TILE_ORANGE, "callback": self.abrir_cuentas_por_pagar},
            {"text": "Pagos", "icon": "fa5s.credit-card", "color": WindowsPhoneTheme.TILE_PURPLE, "callback": self.show_mock_dialog},
            {"text": "Proveedores", "icon": "fa5s.truck", "color": WindowsPhoneTheme.TILE_TEAL, "callback": self.abrir_proveedores},
        ]
        
        # Agregar los botones al grid
        for i, action in enumerate(actions):
            btn = TileButton(action["text"], action["icon"], action["color"])
            if action["callback"]:
                btn.clicked.connect(action["callback"])
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.stacked_widget.addWidget(page)
        
    def handle_logout(self):
        """Manejar cierre de sesión"""
        logging.info(f"Usuario {self.user_data['username']} cerró sesión")
        self.logout_requested.emit()
        self.close()
    
    def cambiar_contrasena(self):
        """Abrir diálogo para cambiar contraseña"""
        from PySide6.QtWidgets import QDialog, QLineEdit
        import bcrypt
        
        class CambiarContrasenaDialog(QDialog):
            def __init__(self, parent, pg_manager, user_data):
                super().__init__(parent)
                self.pg_manager = pg_manager
                self.user_data = user_data
                
                self.setModal(True)
                self.setWindowTitle("Cambiar Contraseña")
                self.setMinimumWidth(500)
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                
                # Layout principal
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                
                # Header
                header = QFrame()
                header.setStyleSheet(f"background-color: {WindowsPhoneTheme.PRIMARY_BLUE};")
                header_layout = QHBoxLayout(header)
                header_layout.setContentsMargins(28, 24, 28, 24)
                
                title_label = QLabel("CAMBIAR CONTRASEÑA")
                title_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_LARGE, QFont.Bold))
                title_label.setStyleSheet("color: white;")
                title_label.setAlignment(Qt.AlignCenter)
                header_layout.addWidget(title_label)
                
                layout.addWidget(header)
                
                # Content
                content = QFrame()
                content.setStyleSheet("background-color: white;")
                content_layout = QVBoxLayout(content)
                content_layout.setContentsMargins(40, 30, 40, 30)
                content_layout.setSpacing(20)
                
                # Contraseña actual
                lbl_actual = StyledLabel("Contraseña Actual:", bold=True)
                content_layout.addWidget(lbl_actual)
                
                self.input_actual = QLineEdit()
                self.input_actual.setEchoMode(QLineEdit.Password)
                self.input_actual.setPlaceholderText("Ingrese su contraseña actual")
                self.input_actual.setMinimumHeight(45)
                self.input_actual.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 10px 15px;
                        border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                        font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                    }}
                    QLineEdit:focus {{
                        border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                    }}
                """)
                self._toggle_actual_action = self._add_password_toggle(self.input_actual)
                content_layout.addWidget(self.input_actual)
                
                content_layout.addSpacing(10)
                
                # Nueva contraseña
                lbl_nueva = StyledLabel("Nueva Contraseña:", bold=True)
                content_layout.addWidget(lbl_nueva)
                
                self.input_nueva = QLineEdit()
                self.input_nueva.setEchoMode(QLineEdit.Password)
                self.input_nueva.setPlaceholderText("Ingrese nueva contraseña")
                self.input_nueva.setMinimumHeight(45)
                self.input_nueva.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 10px 15px;
                        border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                        font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                    }}
                    QLineEdit:focus {{
                        border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                    }}
                """)
                self._toggle_nueva_action = self._add_password_toggle(self.input_nueva)
                content_layout.addWidget(self.input_nueva)
                
                content_layout.addSpacing(10)
                
                # Confirmar contraseña
                lbl_confirmar = StyledLabel("Confirmar Nueva Contraseña:", bold=True)
                content_layout.addWidget(lbl_confirmar)
                
                self.input_confirmar = QLineEdit()
                self.input_confirmar.setEchoMode(QLineEdit.Password)
                self.input_confirmar.setPlaceholderText("Confirme nueva contraseña")
                self.input_confirmar.setMinimumHeight(45)
                self.input_confirmar.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 10px 15px;
                        border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                        font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                    }}
                    QLineEdit:focus {{
                        border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
                    }}
                """)
                self._toggle_confirmar_action = self._add_password_toggle(self.input_confirmar)
                content_layout.addWidget(self.input_confirmar)
                
                content_layout.addSpacing(20)
                
                # Botones
                buttons_layout = QHBoxLayout()
                buttons_layout.setSpacing(14)
                buttons_layout.addStretch()
                
                btn_cancelar = QPushButton("Cancelar")
                btn_cancelar.setMinimumSize(120, 45)
                btn_cancelar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
                btn_cancelar.setCursor(QCursor(Qt.PointingHandCursor))
                btn_cancelar.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {WindowsPhoneTheme.TILE_GRAY};
                        color: white;
                        border: none;
                        padding: 10px 20px;
                    }}
                    QPushButton:hover {{
                        background-color: #8a8a8a;
                    }}
                """)
                btn_cancelar.clicked.connect(self.reject)
                buttons_layout.addWidget(btn_cancelar)
                
                btn_cambiar = QPushButton("Cambiar")
                btn_cambiar.setMinimumSize(120, 45)
                btn_cambiar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
                btn_cambiar.setCursor(QCursor(Qt.PointingHandCursor))
                btn_cambiar.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {WindowsPhoneTheme.TILE_GREEN};
                        color: white;
                        border: none;
                        padding: 10px 20px;
                    }}
                    QPushButton:hover {{
                        background-color: #00b300;
                    }}
                """)
                btn_cambiar.clicked.connect(self.cambiar)
                btn_cambiar.setDefault(True)
                buttons_layout.addWidget(btn_cambiar)
                
                content_layout.addLayout(buttons_layout)
                layout.addWidget(content)

            def _add_password_toggle(self, line_edit: QLineEdit):
                """Agrega acción de mostrar/ocultar contraseña al QLineEdit."""
                try:
                    import qtawesome as qta
                except Exception:
                    return None

                # Reservar espacio para el icono dentro del input
                line_edit.setTextMargins(0, 0, 36, 0)
                action = line_edit.addAction(
                    qta.icon('fa5s.eye', color=WindowsPhoneTheme.PRIMARY_BLUE),
                    QLineEdit.TrailingPosition
                )
                action.setToolTip("Mostrar contraseña")
                action.triggered.connect(
                    lambda checked=False, le=line_edit, act=action: self._toggle_password_visibility(le, act)
                )
                return action

            def _toggle_password_visibility(self, line_edit: QLineEdit, action):
                """Alterna visibilidad de contraseña para un campo."""
                try:
                    import qtawesome as qta
                except Exception:
                    return

                if line_edit.echoMode() == QLineEdit.Password:
                    line_edit.setEchoMode(QLineEdit.Normal)
                    action.setIcon(qta.icon('fa5s.eye-slash', color=WindowsPhoneTheme.PRIMARY_BLUE))
                    action.setToolTip("Ocultar contraseña")
                else:
                    line_edit.setEchoMode(QLineEdit.Password)
                    action.setIcon(qta.icon('fa5s.eye', color=WindowsPhoneTheme.PRIMARY_BLUE))
                    action.setToolTip("Mostrar contraseña")
            
            def cambiar(self):
                """Validar y cambiar contraseña"""
                actual = self.input_actual.text().strip()
                nueva = self.input_nueva.text().strip()
                confirmar = self.input_confirmar.text().strip()
                
                # Validaciones
                if not actual or not nueva or not confirmar:
                    show_warning_dialog(self, "Campos Vacíos", "Todos los campos son obligatorios.")
                    return
                
                if len(nueva) < 6:
                    show_warning_dialog(self, "Contraseña Débil", "La nueva contraseña debe tener al menos 6 caracteres.")
                    return
                
                if nueva != confirmar:
                    show_warning_dialog(self, "No Coinciden", "La nueva contraseña y la confirmación no coinciden.")
                    return
                
                try:
                    # Verificar contraseña actual
                    result = self.pg_manager.client.table('usuarios').select('contrasenia').eq('nombre_usuario', self.user_data['username']).execute()
                    
                    if not result.data:
                        show_error_dialog(self, "Error", "No se encontró el usuario.")
                        return
                    
                    stored_password = result.data[0]['contrasenia']
                    
                    # Verificar contraseña actual con bcrypt
                    if not bcrypt.checkpw(actual.encode('utf-8'), stored_password.encode('utf-8')):
                        show_error_dialog(self, "Contraseña Incorrecta", "La contraseña actual no es correcta.")
                        return
                    
                    # Cambiar contraseña usando el método del manager
                    if self.pg_manager.update_user_password(self.user_data['username'], nueva):
                        show_success_dialog(self, "Contraseña Actualizada", "Su contraseña ha sido cambiada exitosamente.")
                        self.accept()
                    else:
                        show_error_dialog(self, "Error", "No se pudo actualizar la contraseña.")
                
                except Exception as e:
                    logging.error(f"Error cambiando contraseña: {e}")
                    show_error_dialog(self, "Error", f"Error al cambiar contraseña:\n{str(e)}")
        
        # Mostrar diálogo
        dialog = CambiarContrasenaDialog(self, self.pg_manager, self.user_data)
        dialog.exec()
        
    # ========== MÉTODOS DE VENTAS ==========
    
    def abrir_nueva_venta(self):
        """Abrir widget de nueva venta"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("NUEVA VENTA")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de nueva venta
            nueva_venta_widget = NuevaVentaWindow(
                self.pg_manager, 
                self.user_data,
                self.turno_id,  # Pasar ID del turno actual
                self
            )
            nueva_venta_widget.venta_completada.connect(self.on_venta_completada)
            nueva_venta_widget.cerrar_solicitado.connect(self.volver_a_ventas)
            
            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(nueva_venta_widget)
            self.stacked_widget.setCurrentWidget(nueva_venta_widget)
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo widget de nueva venta")
        except Exception as e:
            logging.error(f"Error abriendo nueva venta: {e}")
            
    def abrir_ventas_dia(self):
        """Abrir widget de ventas del turno"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("VENTAS DEL TURNO")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de ventas del turno
            ventas_dia_widget = VentasDiaWindow(
                self.pg_manager,
                None,  # supabase_service (deshabilitado)
                self.user_data,
                self.turno_id,  # Pasar ID del turno actual
                self
            )
            ventas_dia_widget.cerrar_solicitado.connect(self.volver_a_ventas)
            
            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(ventas_dia_widget)
            self.stacked_widget.setCurrentWidget(ventas_dia_widget)
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo widget de ventas del turno")
        except Exception as e:
            logging.error(f"Error abriendo ventas del día: {e}")
            
    def abrir_historial(self):
        """Abrir widget de historial de ventas"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("HISTORIAL DE VENTAS")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Verificar desde qué pestaña se está abriendo
            current_index = self.stacked_widget.currentIndex()
            
            # Crear widget de historial
            historial_widget = HistorialVentasWindow(
                self.pg_manager, 
                self.user_data, 
                self
            )
            
            # Conectar señal según la vista actual
            # Índice 0 = Punto de Venta, Índice 1 = Ventas, Índice 2 = Inventario, Índice 5 = Admin/Config
            if current_index == 1:
                historial_widget.cerrar_solicitado.connect(self.volver_a_inventario)
            elif current_index == 2:
                historial_widget.cerrar_solicitado.connect(self.volver_a_administracion)
            elif current_index == 5:
                historial_widget.cerrar_solicitado.connect(self.volver_a_config)
            else:
                historial_widget.cerrar_solicitado.connect(self.volver_a_ventas)
            
            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(historial_widget)
            self.stacked_widget.setCurrentWidget(historial_widget)
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo widget de historial")
        except Exception as e:
            logging.error(f"Error abriendo historial: {e}")
            
    def abrir_historial_lockers(self):
        """Abrir widget de historial de lockers - DESHABILITADO (módulo removido)"""
        logging.warning("Módulo de historial de lockers ya no está disponible")
        # TODO: Restaurar cuando se reimplemente el módulo HistorialLockersWindow
            
    def abrir_cierre_caja(self):
        """Abrir widget de cierre de caja"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("CIERRE DE CAJA")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de cierre de caja
            cierre_widget = CierreCajaWindow(
                self.pg_manager, 
                self.user_data, 
                self
            )
            cierre_widget.cerrar_solicitado.connect(self.volver_a_ventas)
            
            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(cierre_widget)
            self.stacked_widget.setCurrentWidget(cierre_widget)
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo widget de cierre de caja")
        except Exception as e:
            logging.error(f"Error abriendo cierre de caja: {e}")

    
    
    def debug_procesar_pago(self, dialog):
        """Procesar pago desde el diálogo de debug - DESHABILITADO"""
        logging.warning("Funcionalidad de procesamiento de pago deshabilitada (Supabase removido)")
        show_warning_dialog(self, "Módulo Deshabilitado", "Esta funcionalidad no está disponible en la versión actual")
    
    def _on_notificacion_procesada_debug(self, datos_notificacion):
        """Callback cuando se procesa una notificación desde el debug modal"""
        logging.info(f"[DEBUG] Notificación procesada: {datos_notificacion}")
        # Aquí se pueden actualizar contadores, actualizar UI, etc.
            
    def volver_a_ventas(self):
        """Volver a la página principal de ventas"""
        # Restaurar título
        self.top_bar.set_title("PUNTO CLAVE")
        
        # Mostrar barra de navegación
        self.nav_bar.show()
        
        # Obtener el widget actual
        current_widget = self.stacked_widget.currentWidget()
        
        # Cambiar a la página de ventas (índice 0)
        self.stacked_widget.setCurrentIndex(0)
        self.switch_tab(0)
        
        # Remover el widget de ventas del stack después de un momento
        # para evitar problemas de referencia
        QTimer.singleShot(100, lambda: self.remover_widget_temporal(current_widget))
        
        # Forzar actualización del layout
        QTimer.singleShot(0, self.update_layout)
        
        logging.info("Volviendo a página de ventas")
        
    def update_layout(self):
        """Forzar actualización del layout después de cambiar de widget"""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            current_widget.updateGeometry()
        self.stacked_widget.updateGeometry()
        self.updateGeometry()
        
    def remover_widget_temporal(self, widget):
        """Remover un widget temporal del stack"""
        try:
            index = self.stacked_widget.indexOf(widget)
            if index > 4:  # Solo remover widgets temporales (después de las 5 páginas principales)
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
        except Exception as e:
            logging.error(f"Error removiendo widget temporal: {e}")
            
    def on_venta_completada(self, venta_info):
        """Manejar cuando se completa una venta"""
        logging.info(f"Venta completada: ID {venta_info['id_venta']}, Total: ${venta_info['total']:.2f}")
        # Aquí se pueden agregar actualizaciones adicionales como refrescar estadísticas
    
    def abrir_gestion_proveedores(self):
        """Abrir widget de gestión de proveedores"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de proveedores
            proveedores_window = ProveedoresWindow(self.pg_manager, self.user_data, self)

            # Conectar señal de cerrar
            proveedores_window.cerrar_solicitado.connect(self.volver_a_config)

            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(proveedores_window)
            self.stacked_widget.setCurrentWidget(proveedores_window)

            # Actualizar título
            self.top_bar.set_title("PROVEEDORES")

            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)

            logging.info("Abriendo gestión de proveedores")

        except Exception as e:
            logging.error(f"Error abriendo gestión de proveedores: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la gestión de proveedores: {e}")
    
    def abrir_proveedores(self):
        """Abrir widget de proveedores desde Compras y Gastos"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de proveedores
            proveedores_window = ProveedoresWindow(self.pg_manager, self.user_data, self)

            # Conectar señal de cerrar para volver a Compras y Gastos (pestaña 3)
            proveedores_window.cerrar_solicitado.connect(self.volver_a_compras_gastos)

            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(proveedores_window)
            self.stacked_widget.setCurrentWidget(proveedores_window)

            # Actualizar título
            self.top_bar.set_title("PROVEEDORES")

            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)

            logging.info("Abriendo proveedores desde Compras y Gastos")

        except Exception as e:
            logging.error(f"Error abriendo proveedores: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la gestión de proveedores: {e}")
    
    def abrir_dias_festivos(self):
        """Abrir widget de cuentas por pagar"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("CUENTAS POR PAGAR")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de cuentas por pagar
            cuentas_widget = CuentasPorPagarWindow(self.pg_manager, self.user_data)
            
            # Conectar señal de cierre
            cuentas_widget.cerrar_solicitado.connect(self.volver_a_config)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(cuentas_widget)
            self.stacked_widget.setCurrentWidget(cuentas_widget)
            
        except Exception as e:
            logging.error(f"Error abriendo cuentas por pagar: {e}")
            show_error_dialog(self, "Error", f"Error al abrir cuentas por pagar: {e}")
    
    def abrir_historial_turnos(self):
        """Abrir widget de historial de turnos de caja"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("HISTORIAL DE TURNOS")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de historial de turnos
            turnos_widget = HistorialTurnosWindow(self.pg_manager, self.user_data)
            
            # Conectar señal de cierre
            turnos_widget.cerrar_solicitado.connect(self.volver_a_config)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(turnos_widget)
            self.stacked_widget.setCurrentWidget(turnos_widget)
            
            logging.info("Abriendo historial de turnos")
            
        except Exception as e:
            logging.error(f"Error abriendo historial de turnos: {e}")
    
    def abrir_asignacion_turnos(self):
        """Abrir widget de asignación de turnos"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("ASIGNACIÓN DE TURNOS")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de asignación de turnos
            asignacion_widget = AsignacionTurnosWindow(self.pg_manager, self.user_data)
            
            # Conectar señal de cierre
            asignacion_widget.cerrar_solicitado.connect(self.volver_a_config)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(asignacion_widget)
            self.stacked_widget.setCurrentWidget(asignacion_widget)
            
            logging.info("Abriendo asignación de turnos")
            
        except Exception as e:
            logging.error(f"Error abriendo asignación de turnos: {e}")
    
    def abrir_gestion_ubicaciones(self):
        """Abrir widget de gestión de ubicaciones"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("GESTIÓN DE UBICACIONES")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear widget de ubicaciones
            ubicaciones_widget = UbicacionesWindow(self.pg_manager, self.user_data)
            
            # Conectar señal de cierre
            ubicaciones_widget.cerrar_solicitado.connect(self.volver_a_config)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(ubicaciones_widget)
            self.stacked_widget.setCurrentWidget(ubicaciones_widget)
            
            logging.info("Abriendo gestión de ubicaciones")
            
        except Exception as e:
            logging.error(f"Error abriendo gestión de ubicaciones: {e}")
    
    def abrir_catalogo_lockers(self):
        """Abrir ventana de catálogo de clientes"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("CLIENTES")

            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de clientes
            clientes_window = ClientesWindow(self.pg_manager, self.user_data, self)
            clientes_window.cerrar_solicitado.connect(self.volver_a_config)

            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(clientes_window)
            self.stacked_widget.setCurrentWidget(clientes_window)

            # Forzar actualización del layout
            self.stacked_widget.update()

            logging.info("Abriendo catálogo de clientes")

        except Exception as e:
            logging.error(f"Error abriendo catálogo de clientes: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el catálogo de clientes: {e}")
    
    def abrir_catalogo_tipos_cxp(self):
        """Abrir ventana de catálogo de tipos de cuenta por pagar"""
        try:
            # Actualizar título de la barra superior
            self.top_bar.set_title("TIPOS CUENTA POR PAGAR")

            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de tipos de cuenta por pagar
            tipos_cxp_window = TipoCuentaPagarWindow(self.pg_manager, self.user_data, self)
            tipos_cxp_window.cerrar_solicitado.connect(self.volver_a_config)

            # Agregar al stack y cambiar a esa vista
            self.stacked_widget.addWidget(tipos_cxp_window)
            self.stacked_widget.setCurrentWidget(tipos_cxp_window)

            # Forzar actualización del layout
            self.stacked_widget.update()

            logging.info("Abriendo catálogo de tipos de cuenta por pagar")

        except Exception as e:
            logging.error(f"Error abriendo catálogo de tipos de cuenta por pagar: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el catálogo de tipos de cuenta por pagar: {e}")
    
    def abrir_asignaciones_lockers(self):
        """Abrir ventana de asignación de lockers mensuales - DESHABILITADO (módulo removido)"""
        logging.warning("Módulo de asignaciones de lockers mensuales ya no está disponible")
        show_warning_dialog(self, "Módulo Deshabilitado", "Esta funcionalidad no está disponible en la versión actual")
        # TODO: Restaurar cuando se reimplemente el módulo AsignacionesLockersWindow
    
    def abrir_asignaciones_lockers_diarios(self):
        """Abrir ventana de asignación de lockers diarios - DESHABILITADO (módulo removido)"""
        logging.warning("Módulo de asignaciones de lockers diarios ya no está disponible")
        show_warning_dialog(self, "Módulo Deshabilitado", "Esta funcionalidad no está disponible en la versión actual")
        # TODO: Restaurar cuando se reimplemente el módulo AsignarLockerDiarioWindow
    
    def volver_a_administracion(self):
        """Volver a la página de administración"""
        # Restaurar título
        self.top_bar.set_title("PUNTO CLAVE")
        
        # Mostrar barra de navegación
        self.nav_bar.show()
        
        # Obtener el widget actual
        current_widget = self.stacked_widget.currentWidget()
        
        # Cambiar a la página de administración (índice 2)
        self.stacked_widget.setCurrentIndex(2)
        self.switch_tab(2)
        
        # Remover el widget temporal
        QTimer.singleShot(100, lambda: self.remover_widget_temporal(current_widget))
    
    def volver_a_config(self):
        """Volver a la página de configuración/administración"""
        # Restaurar título
        self.top_bar.set_title("PUNTO CLAVE")
        
        # Mostrar barra de navegación
        self.nav_bar.show()
        
        # Obtener el widget actual
        current_widget = self.stacked_widget.currentWidget()
        
        # Cambiar a la página de configuración (índice 5)
        self.stacked_widget.setCurrentIndex(5)
        self.switch_tab(5)
        
        # Remover el widget temporal
        QTimer.singleShot(100, lambda: self.remover_widget_temporal(current_widget))
    
    def abrir_inventario(self):
        """Abrir widget de inventario"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de inventario
            inventario_window = InventarioWindow(
                self.pg_manager,
                self.user_data,
                self
            )
            
            # Conectar señal de cerrar
            inventario_window.cerrar_solicitado.connect(self.volver_a_administracion)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(inventario_window)
            self.stacked_widget.setCurrentWidget(inventario_window)
            
            # Actualizar título
            self.top_bar.set_title("INVENTARIO")
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo grid de inventario")
            
        except Exception as e:
            logging.error(f"Error abriendo inventario: {e}")
    
    def abrir_productos(self):
        """Abrir widget de productos"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de productos
            productos_window = ProductosWindow(
                self.pg_manager,
                self.user_data,
                self
            )
            
            # Conectar señal de cerrar
            productos_window.cerrar_solicitado.connect(self.volver_a_inventario)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(productos_window)
            self.stacked_widget.setCurrentWidget(productos_window)
            
            # Actualizar título
            self.top_bar.set_title("CATÁLOGO DE PRODUCTOS")
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo grid de productos")
            
        except Exception as e:
            logging.error(f"Error abriendo productos: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el catálogo de productos:\n{str(e)}")
    
    def abrir_nuevo_producto(self):
        """Abrir ventana de nuevo producto"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de nuevo producto
            nuevo_producto_window = NuevoProductoWindow(
                self.pg_manager,
                self.user_data,
                self
            )
            
            # Conectar señal de cerrar
            nuevo_producto_window.cerrar_solicitado.connect(self.volver_a_administracion)
            nuevo_producto_window.producto_guardado.connect(self.on_producto_guardado)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(nuevo_producto_window)
            self.stacked_widget.setCurrentWidget(nuevo_producto_window)
            
            # Actualizar título
            self.top_bar.set_title("NUEVO PRODUCTO")
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo formulario de nuevo producto")
            
        except Exception as e:
            logging.error(f"Error abriendo nuevo producto: {e}")
    
    def abrir_registro_entrada(self):
        """Abrir formulario de registro de entrada"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de registro de entrada
            entrada_window = MovimientoInventarioWindow(
                "entrada",
                self.pg_manager,
                self.user_data,
                self
            )
            
            # Conectar señales
            entrada_window.cerrar_solicitado.connect(self.volver_a_administracion)
            entrada_window.movimiento_registrado.connect(self.on_movimiento_registrado)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(entrada_window)
            self.stacked_widget.setCurrentWidget(entrada_window)
            
            # Actualizar título
            self.top_bar.set_title("REGISTRAR ENTRADA")
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo formulario de registro de entrada")
            
        except Exception as e:
            logging.error(f"Error abriendo registro de entrada: {e}")
    
    def abrir_registro_salida(self):
        """Abrir formulario de registro de salida"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de registro de salida
            salida_window = MovimientoInventarioWindow(
                "salida",
                self.pg_manager,
                self.user_data,
                self
            )
            
            # Conectar señales
            salida_window.cerrar_solicitado.connect(self.volver_a_administracion)
            salida_window.movimiento_registrado.connect(self.on_movimiento_registrado)
            
            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(salida_window)
            self.stacked_widget.setCurrentWidget(salida_window)
            
            # Actualizar título
            self.top_bar.set_title("REGISTRAR SALIDA")
            
            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)
            
            logging.info("Abriendo formulario de registro de salida")
            
        except Exception as e:
            logging.error(f"Error abriendo registro de salida: {e}")
    
    def volver_a_inventario(self):
        """Volver a la página de inventario"""
        # Restaurar título
        self.top_bar.set_title("PUNTO CLAVE")
        
        # Mostrar barra de navegación
        self.nav_bar.show()
        
        # Obtener el widget actual
        current_widget = self.stacked_widget.currentWidget()
        
        # Cambiar a la página de inventario (índice 2)
        self.stacked_widget.setCurrentIndex(2)
        self.switch_tab(2)
        
        # Remover el widget temporal
        QTimer.singleShot(100, lambda: self.remover_widget_temporal(current_widget))
        
        # Forzar actualización del layout
        QTimer.singleShot(0, self.update_layout)
        
        logging.info("Volviendo a página de inventario")
    
    def on_producto_guardado(self):
        """Manejar cuando se guarda un producto"""
        logging.info(f"Producto guardado")
        self.volver_a_inventario()
        # Aquí se pueden agregar actualizaciones adicionales
    
    def on_movimiento_registrado(self, movimiento_info):
        """Manejar cuando se registra un movimiento de inventario"""
        logging.info(
            f"Movimiento registrado: {movimiento_info['tipo']} - "
            f"{movimiento_info['producto']} - Cantidad: {movimiento_info['cantidad']}"
        )
    
    def abrir_historial_movimientos(self):
        """Abrir ventana de historial de movimientos"""
        try:
            # Crear ventana de historial
            historial_window = HistorialMovimientosWindow(
                self.pg_manager,
                self.user_data,
                parent=self
            )
            
            # Conectar señal de cerrar
            historial_window.cerrar_solicitado.connect(self.volver_a_administracion)
            
            # Agregar al stacked widget
            index = self.stacked_widget.addWidget(historial_window)
            self.stacked_widget.setCurrentIndex(index)
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Actualizar título
            self.top_bar.set_title("Historial de Movimientos")
            
            logging.info("Ventana de historial de movimientos abierta")
            
        except Exception as e:
            logging.error(f"Error abriendo historial de movimientos: {e}")
    
    def abrir_movimiento_inventario(self):
        """Abrir ventana de movimientos de inventario (ajustes)"""
        try:
            logging.info("Abriendo ventana de movimientos de inventario...")
            
            # Crear ventana de movimientos de inventario
            movimiento_window = MovimientoInventarioWindow("ajuste", self.pg_manager, self.user_data, parent=self)
            movimiento_window.cerrar_solicitado.connect(self.volver_a_inventario)
            
            # Agregar al stacked widget y mostrar
            self.stacked_widget.addWidget(movimiento_window)
            self.stacked_widget.setCurrentWidget(movimiento_window)
            
            # Cambiar título
            self.top_bar.set_title("MOVIMIENTOS DE INVENTARIO")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            logging.info("Ventana de movimientos de inventario abierta")
            
        except Exception as e:
            logging.error(f"Error abriendo movimientos de inventario: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la ventana de movimientos de inventario:\n{str(e)}")
    
    def abrir_nueva_compra(self):
        """Abrir formulario de nueva compra"""
        try:
            logging.info("Abriendo formulario de nueva compra...")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear formulario de nueva compra
            compra_window = NuevaCompraWindow(self.pg_manager, self.user_data, tipo_compra="compra", parent=self)
            compra_window.cerrar_solicitado.connect(self.volver_a_compras_gastos)
            compra_window.compra_guardada.connect(self.on_compra_gasto_guardado)
            
            # Agregar al stacked widget y mostrar
            self.stacked_widget.addWidget(compra_window)
            self.stacked_widget.setCurrentWidget(compra_window)
            
            # Cambiar título
            self.top_bar.set_title("NUEVA COMPRA")
            
            logging.info("Formulario de nueva compra abierto")
            
        except Exception as e:
            logging.error(f"Error abriendo nueva compra: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el formulario de nueva compra:\n{str(e)}")
    
    def abrir_nuevo_gasto(self):
        """Abrir formulario de nuevo gasto/servicio"""
        try:
            logging.info("Abriendo formulario de nuevo gasto...")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear formulario de nuevo gasto
            gasto_window = NuevaCompraWindow(self.pg_manager, self.user_data, tipo_compra="gasto", parent=self)
            gasto_window.cerrar_solicitado.connect(self.volver_a_compras_gastos)
            gasto_window.compra_guardada.connect(self.on_compra_gasto_guardado)
            
            # Agregar al stacked widget y mostrar
            self.stacked_widget.addWidget(gasto_window)
            self.stacked_widget.setCurrentWidget(gasto_window)
            
            # Cambiar título
            self.top_bar.set_title("NUEVO GASTO/SERVICIO")
            
            logging.info("Formulario de nuevo gasto abierto")
            
        except Exception as e:
            logging.error(f"Error abriendo nuevo gasto: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el formulario de nuevo gasto:\n{str(e)}")
    
    def abrir_cuentas_por_pagar(self):
        """Abrir ventana de cuentas por pagar"""
        try:
            logging.info("Abriendo ventana de cuentas por pagar...")
            
            # Ocultar barra de navegación
            self.nav_bar.hide()
            
            # Crear ventana de cuentas por pagar
            cuentas_window = CuentasPorPagarWindow(self.pg_manager, self.user_data, parent=self)
            cuentas_window.cerrar_solicitado.connect(self.volver_a_compras_gastos)
            
            # Agregar al stacked widget y mostrar
            self.stacked_widget.addWidget(cuentas_window)
            self.stacked_widget.setCurrentWidget(cuentas_window)
            
            # Cambiar título
            self.top_bar.set_title("CUENTAS POR PAGAR")
            
            logging.info("Ventana de cuentas por pagar abierta")
            
        except Exception as e:
            logging.error(f"Error abriendo cuentas por pagar: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la ventana de cuentas por pagar:\n{str(e)}")
    
    def abrir_proveedores(self):
        """Abrir widget de proveedores desde Compras y Gastos"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de proveedores
            proveedores_window = ProveedoresWindow(self.pg_manager, self.user_data, self)

            # Conectar señal de cerrar para volver a Compras y Gastos (pestaña 3)
            proveedores_window.cerrar_solicitado.connect(self.volver_a_compras_gastos)

            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(proveedores_window)
            self.stacked_widget.setCurrentWidget(proveedores_window)

            # Actualizar título
            self.top_bar.set_title("PROVEEDORES")

            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)

            logging.info("Abriendo proveedores desde Compras y Gastos")

        except Exception as e:
            logging.error(f"Error abriendo proveedores: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir la gestión de proveedores: {e}")
    
    def volver_a_compras_gastos(self):
        """Volver a la página de compras y gastos"""
        try:
            # Mostrar barra de navegación
            self.nav_bar.show()
            
            # Cambiar al índice de compras y gastos (3)
            self.stacked_widget.setCurrentIndex(3)
            self.top_bar.set_title("COMPRAS Y GASTOS")
            
            logging.info("Volviendo a página de compras y gastos")
            
        except Exception as e:
            logging.error(f"Error volviendo a compras y gastos: {e}")
    
    def volver_a_clientes(self):
        """Volver a la página de clientes"""
        try:
            # Mostrar barra de navegación
            self.nav_bar.show()
            
            # Cambiar al índice de clientes (4)
            self.stacked_widget.setCurrentIndex(4)
            self.top_bar.set_title("CLIENTES")
            
            logging.info("Volviendo a página de clientes")
            
        except Exception as e:
            logging.error(f"Error volviendo a clientes: {e}")
    
    def abrir_clientes(self):
        """Abrir ventana de directorio de clientes"""
        try:
            # Ocultar barra de navegación
            self.nav_bar.hide()

            # Crear ventana de clientes
            clientes_window = ClientesWindow(self.pg_manager, self.user_data, self)

            # Conectar señal de cerrar para volver a Clientes (pestaña 4)
            clientes_window.cerrar_solicitado.connect(self.volver_a_clientes)

            # Agregar al stack y mostrar
            self.stacked_widget.addWidget(clientes_window)
            self.stacked_widget.setCurrentWidget(clientes_window)

            # Actualizar título
            self.top_bar.set_title("DIRECTORIO DE CLIENTES")

            # Forzar actualización del layout
            QTimer.singleShot(0, self.update_layout)

            logging.info("Abriendo directorio de clientes")

        except Exception as e:
            logging.error(f"Error abriendo clientes: {e}")
            show_error_dialog(self, "Error", f"No se pudo abrir el directorio de clientes: {e}")
    
    def on_compra_gasto_guardado(self, datos):
        """Manejar cuando se guarda una compra o gasto"""
        logging.info(f"Compra/gasto guardado: {datos.get('numero_cuenta', 'N/A')}")
        # Aquí se podría actualizar alguna lista o estadística si fuera necesario
    
    def abrir_historial_acceso(self):
        """Abrir ventana de historial de acceso - DESHABILITADO (módulo removido)"""
        logging.warning("Módulo de historial de acceso ya no está disponible")
        show_warning_dialog(self, "Módulo Deshabilitado", "Esta funcionalidad no está disponible en la versión actual")
        # TODO: Restaurar cuando se reimplemente el módulo HistorialAccesoWindow
    

    
    # ========== POSICIONAMIENTO Y NOTIFICACIONES ==========
    
    def posicionar_notificacion(self, notificacion):
        """Posicionar notificación en la pantalla"""
        # Obtener geometría de la ventana principal
        main_geometry = self.geometry()
        
        # Calcular posición (esquina superior derecha con margen)
        margen = 20
        x = main_geometry.right() - notificacion.width() - margen
        y = main_geometry.top() + margen
        
        # Ajustar posición si hay otras notificaciones
        offset_vertical = 0
        for notif in self.notificaciones_activas:
            if notif.isVisible():
                offset_vertical += notif.height() + 10
        
        y += offset_vertical
        
        # Establecer posición
        notificacion.move(x, y)
    
    def remover_notificacion(self, notificacion):
        """Remover notificación de la lista activa"""
        if notificacion in self.notificaciones_activas:
            self.notificaciones_activas.remove(notificacion)
            logging.debug(f"Notificación removida. Activas: {len(self.notificaciones_activas)}")
    
    def closeEvent(self, event):
        """Evento al cerrar la ventana principal"""
        try:
            # Verificar si hay turno abierto
            if self.turno_id and self.pg_manager:
                try:
                    # Usar el método get_turno_activo de PostgresManager
                    turno = self.pg_manager.get_turno_activo(self.user_data['id_usuario'])
                    
                    if turno and not turno.get('cerrado'):
                        # Mostrar advertencia de turno abierto
                        from ui.components import show_confirmation_dialog
                        from datetime import datetime
                        
                        fecha_apertura = turno.get('fecha_apertura', '')
                        if isinstance(fecha_apertura, str):
                            try:
                                fecha_obj = datetime.fromisoformat(fecha_apertura.replace('Z', '+00:00'))
                                fecha_apertura = fecha_obj.strftime('%d/%m/%Y %H:%M')
                            except:
                                pass
                        
                        # Preguntar si desea cerrar de todas formas
                        respuesta = show_confirmation_dialog(
                            self,
                            "Turno Abierto",
                            f"⚠️ ADVERTENCIA: Tienes un turno abierto\n\n"
                            f"Fecha apertura: {fecha_apertura}\n"
                            f"Monto inicial: ${float(turno.get('monto_inicial', 0)):.2f}\n\n"
                            f"Recuerda cerrar el turno antes de finalizar el día.",
                            detail="¿Deseas cerrar el POS de todas formas?",
                            confirm_text="Cerrar de todas formas",
                            cancel_text="Cancelar"
                        )
                        
                        # Si el usuario cancela, ignorar el evento de cierre
                        if not respuesta:
                            event.ignore()
                            return
                            
                except Exception as e:
                    logging.error(f"Error verificando turno al cerrar: {e}")
            
            # Detener monitor de entradas
            if self.monitor_entradas:
                try:
                    self.monitor_entradas.detener()
                    logging.info("Monitor de entradas detenido")
                except Exception as e:
                    logging.error(f"Error deteniendo monitor de entradas: {e}")
            
            # Cerrar todas las notificaciones activas
            for notificacion in list(self.notificaciones_activas):
                try:
                    notificacion.close()
                except:
                    pass
            
            self.notificaciones_activas.clear()
            
            # Aceptar el evento de cierre
            event.accept()
            logging.info("Aplicación cerrada correctamente")
                
        except Exception as e:
            logging.error(f"Error en closeEvent: {e}")
            event.accept()
    
    def show_mock_dialog(self):
        """Mostrar diálogo para funcionalidades en desarrollo"""
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Próximamente")
        msg.setText("Esta funcionalidad está en desarrollo")
        msg.setInformativeText("Estamos trabajando en implementar esta característica.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

