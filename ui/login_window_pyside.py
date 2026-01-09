"""
Ventana de Login Moderna con PySide6 para POS HTF
Integrado con PostgreSQL
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import logging
import os

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    show_error_dialog,
    show_info_dialog,
    show_success_dialog
)

class LoginWindow(QMainWindow):
    # Signal que se emite cuando el login es exitoso
    login_success = Signal(dict)
    
    def __init__(self, pg_manager=None):
        super().__init__()
        self.pg_manager = pg_manager
        
        # Usar colores del tema
        self.PRIMARY_BLUE = WindowsPhoneTheme.PRIMARY_BLUE
        self.SECONDARY_BLUE = "#2563eb"
        self.ACCENT_RED = WindowsPhoneTheme.TILE_RED
        self.HOVER_BLUE = WindowsPhoneTheme.TILE_BLUE
        
        # Usar fuente del tema
        self.font_text = WindowsPhoneTheme.FONT_FAMILY
        self.font_title = WindowsPhoneTheme.FONT_FAMILY
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        self.setWindowTitle("HTF Gimnasio - Sistema POS")
        self.setFixedSize(1000, 600)
        
        # Establecer icono de la ventana
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'pos_icono.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel izquierdo - Branding
        self.create_branding_panel(main_layout)
        
        # Panel derecho - Login
        self.create_login_panel(main_layout)
        
        # Aplicar estilos
        self.apply_styles()
        
        # Centrar ventana
        self.center_window()
        
    def create_branding_panel(self, parent_layout):
        """Crear panel izquierdo con branding"""
        branding_frame = QFrame()
        branding_frame.setObjectName("brandingPanel")
        branding_frame.setMinimumWidth(400)
        
        layout = QVBoxLayout(branding_frame)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Logo/Título
        title = QLabel("HTF")
        title.setObjectName("brandingTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 72, QFont.Bold))
        
        subtitle = QLabel("GIMNASIO")
        subtitle.setObjectName("brandingSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 24, QFont.Light))
        
        description = QLabel("Sistema de Punto de Venta")
        description.setObjectName("brandingDescription")
        description.setAlignment(Qt.AlignCenter)
        description.setFont(QFont("Segoe UI", 12))
        
        version = QLabel("v1.0.0")
        version.setObjectName("brandingVersion")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Segoe UI", 10))
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(version)
        layout.addStretch()
        
        parent_layout.addWidget(branding_frame)
        
    def create_login_panel(self, parent_layout):
        """Crear panel derecho con formulario de login"""
        login_frame = QFrame()
        login_frame.setObjectName("loginPanel")
        login_frame.setMinimumWidth(600)
        
        layout = QVBoxLayout(login_frame)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(80, 0, 80, 0)
        layout.setSpacing(25)
        
        # Título del login
        login_title = QLabel("Iniciar Sesión")
        login_title.setObjectName("loginTitle")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        
        # Campo de usuario
        user_label = QLabel("Usuario")
        user_label.setObjectName("fieldLabel")
        user_label.setFont(QFont("Segoe UI", 11))
        
        self.username_input = QLineEdit()
        self.username_input.setObjectName("inputField")
        self.username_input.setPlaceholderText("Ingresa tu usuario")
        self.username_input.setMinimumHeight(50)
        self.username_input.setFont(QFont("Segoe UI", 12))
        self.username_input.returnPressed.connect(self.handle_login)
        
        # Campo de contraseña
        password_label = QLabel("Contraseña")
        password_label.setObjectName("fieldLabel")
        password_label.setFont(QFont("Segoe UI", 11))
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("inputField")
        self.password_input.setPlaceholderText("Ingresa tu contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setFont(QFont("Segoe UI", 12))
        self.password_input.returnPressed.connect(self.handle_login)

        # Icono para mostrar/ocultar contraseña (sin overlays para evitar recortes)
        self._toggle_password_action = None
        try:
            import qtawesome as qta

            self.password_input.setTextMargins(0, 0, 36, 0)
            self._toggle_password_action = self.password_input.addAction(
                qta.icon('fa5s.eye', color=self.PRIMARY_BLUE),
                QLineEdit.TrailingPosition
            )
            self._toggle_password_action.setToolTip("Mostrar contraseña")
            self._toggle_password_action.triggered.connect(self.toggle_password_visibility)
        except Exception:
            self._toggle_password_action = None
        
        # Botón de login
        self.login_button = QPushButton("INICIAR SESIÓN")
        self.login_button.setObjectName("loginButton")
        self.login_button.setMinimumHeight(55)
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        
        # Info de usuario por defecto
        info_label = QLabel("")
        info_label.setObjectName("infoLabel")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 9))
        
        # Agregar widgets al layout
        layout.addWidget(login_title)
        layout.addSpacing(30)
        layout.addWidget(user_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_button)
        layout.addSpacing(10)
        layout.addWidget(info_label)
        
        parent_layout.addWidget(login_frame)
        
    def apply_styles(self):
        """Aplicar estilos QSS con colores del logo HTF"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
            }}
            
            #brandingPanel {{
                background: {self.PRIMARY_BLUE};
                border: none;
            }}
            
            #brandingTitle {{
                color: white;
                font-weight: bold;
                font-family: '{self.font_title}';
            }}
            
            #brandingSubtitle {{
                color: rgba(255, 255, 255, 0.95);
                letter-spacing: 8px;
                font-family: '{self.font_title}';
            }}
            
            #brandingDescription {{
                color: rgba(255, 255, 255, 0.8);
                font-family: '{self.font_text}';
            }}
            
            #brandingVersion {{
                color: rgba(255, 255, 255, 0.6);
                font-family: '{self.font_text}';
            }}
            
            #loginPanel {{
                background-color: white;
                border: none;
            }}
            
            #loginTitle {{
                color: {self.PRIMARY_BLUE};
                margin-bottom: 10px;
                font-family: '{self.font_title}';
                font-weight: bold;
            }}
            
            #fieldLabel {{
                color: #374151;
                margin-bottom: 5px;
                font-family: '{self.font_text}';
                font-weight: 600;
            }}
            
            #inputField {{
                padding: 12px 16px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                color: #1f2937;
                font-family: '{self.font_text}';
                font-size: 14px;
            }}
            
            #inputField:focus {{
                border: 2px solid {self.PRIMARY_BLUE};
                background-color: white;
            }}
            
            #loginButton {{
                background: {self.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 15px;
                margin-top: 10px;
                font-family: '{self.font_text}';
                font-weight: bold;
                font-size: 14px;
            }}
            
            #loginButton:hover {{
                background: {self.HOVER_BLUE};
            }}
            
            #loginButton:pressed {{
                background: {self.SECONDARY_BLUE};
            }}
            
            #infoLabel {{
                color: #9ca3af;
                font-style: italic;
                font-family: '{self.font_text}';
            }}
        """)
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        screen = self.screen().geometry()
        window = self.frameGeometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
    def update_connection_status(self):
        """Actualizar el indicador de conexión"""
        # Verificar conexión a PostgreSQL local
        pg_connected = False
    def update_connection_status(self):
        """Actualizar estado de conexión - Eliminado para simplificar UI"""
        pass
            
    def handle_login(self):
        """Manejar el evento de login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validar campos vacíos
        if not username:
            self.show_error("Por favor ingresa tu usuario")
            self.username_input.setFocus()
            return
            
        if not password:
            self.show_error("Por favor ingresa tu contraseña")
            self.password_input.setFocus()
            return
        
        # Verificar que existe conexión a la base de datos
        if not self.pg_manager:
            self.show_error("No hay conexión a la base de datos")
            return
        
        # Deshabilitar botón mientras se procesa
        self.login_button.setEnabled(False)
        self.login_button.setText("VERIFICANDO...")
        
        try:
            # Autenticar usuario en PostgreSQL local
            user = self.pg_manager.authenticate_user(username, password)
            
            if user:
                logging.info(f"Login exitoso: {username} (Rol: {user['rol']})")
                
                # Mostrar mensaje de éxito visual
                self.login_button.setText("✓ ACCESO CONCEDIDO")
                self.login_button.setStyleSheet("""
                    QPushButton {
                        background: #38a169;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 15px;
                        font-weight: bold;
                    }
                """)
                
                # Emitir señal de login exitoso con datos del usuario
                self.login_success.emit(user)
                
                # Cerrar ventana de login
                self.close()
            else:
                logging.warning(f"Login fallido para usuario: {username}")
                self.show_error("Usuario o contraseña incorrectos")
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            logging.error(f"Error en login: {e}")
            self.show_error(f"Error inesperado durante la autenticación")
        
        finally:
            # Rehabilitar botón y restaurar texto
            self.login_button.setEnabled(True)
            self.login_button.setText("INICIAR SESIÓN")
            self.login_button.setStyleSheet("")  # Restaurar estilo original

    def toggle_password_visibility(self):
        """Mostrar/ocultar texto en el campo de contraseña."""
        if not self._toggle_password_action:
            return

        try:
            import qtawesome as qta
        except Exception:
            return

        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self._toggle_password_action.setIcon(qta.icon('fa5s.eye-slash', color=self.PRIMARY_BLUE))
            self._toggle_password_action.setToolTip("Ocultar contraseña")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self._toggle_password_action.setIcon(qta.icon('fa5s.eye', color=self.PRIMARY_BLUE))
            self._toggle_password_action.setToolTip("Mostrar contraseña")
            
    def show_error(self, message):
        """Mostrar mensaje de error"""
        show_error_dialog(self, "Error", message)
        
    def show_success(self, message):
        """Mostrar mensaje de éxito"""
        show_success_dialog(self, "Éxito", message)