"""
Diálogo para Abrir Turno Automáticamente al Iniciar Sesión
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
import logging
from datetime import datetime
from decimal import Decimal
import qtawesome as qta

from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    StyledLabel,
    TouchMoneyInput,
    show_error_dialog,
    show_success_dialog
)


class AbrirTurnoDialog(QDialog):
    """Diálogo para abrir turno con monto inicial"""
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.turno_id = None
        
        self.setWindowTitle("Abrir Turno de Caja")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Aplicar estilo del tema
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
            }}
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        title = QLabel("INICIAR TURNO DE CAJA")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 20, QFont.Bold))
        title.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE};")
        layout.addWidget(title)
        
        # Información del usuario
        info_usuario = StyledLabel(
            f"Usuario: {self.user_data['nombre_completo']}\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            bold=True,
            size=14
        )
        info_usuario.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_usuario)
        
        # Instrucción
        instruccion = StyledLabel(
            "Ingrese el monto inicial en caja para comenzar el turno:",
            size=12
        )
        instruccion.setAlignment(Qt.AlignCenter)
        instruccion.setWordWrap(True)
        layout.addWidget(instruccion)
        
        # Input de monto
        self.monto_input = TouchMoneyInput()
        self.monto_input.setMinimumHeight(80)
        layout.addWidget(self.monto_input)
        
        # Nota
        nota = QLabel("Este monto será el punto de partida para el cierre de caja")
        nota.setAlignment(Qt.AlignCenter)
        nota.setStyleSheet(f"""
            color: #666;
            font-family: {WindowsPhoneTheme.FONT_FAMILY};
            font-size: {WindowsPhoneTheme.FONT_SIZE_SMALL}px;
            font-style: italic;
        """)
        layout.addWidget(nota)
        
        layout.addStretch()
        
        # Botones personalizados con iconos más pequeños
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        # Botón Iniciar
        btn_confirmar = QPushButton()
        btn_layout = QVBoxLayout(btn_confirmar)
        btn_layout.setContentsMargins(15, 15, 15, 15)
        btn_layout.setSpacing(8)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        icon_confirmar = QLabel()
        icon_confirmar.setAlignment(Qt.AlignCenter)
        icon_confirmar.setPixmap(qta.icon('fa5s.check', color='white').pixmap(QSize(40, 40)))
        icon_confirmar.setStyleSheet("background: transparent;")
        btn_layout.addWidget(icon_confirmar)
        
        text_confirmar = QLabel("Iniciar\nTurno")
        text_confirmar.setAlignment(Qt.AlignCenter)
        text_confirmar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 14, QFont.Bold))
        text_confirmar.setStyleSheet("color: white; background: transparent;")
        btn_layout.addWidget(text_confirmar)
        
        btn_confirmar.setMinimumHeight(120)
        btn_confirmar.setMinimumWidth(200)
        btn_confirmar.setCursor(Qt.PointingHandCursor)
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_GREEN};
                border: none;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: #00b300;
            }}
            QPushButton:pressed {{
                background-color: #008500;
            }}
        """)
        btn_confirmar.clicked.connect(self.abrir_turno)
        buttons_layout.addWidget(btn_confirmar)
        
        # Botón Cancelar
        btn_cancelar = QPushButton()
        btn_cancelar_layout = QVBoxLayout(btn_cancelar)
        btn_cancelar_layout.setContentsMargins(15, 15, 15, 15)
        btn_cancelar_layout.setSpacing(8)
        btn_cancelar_layout.setAlignment(Qt.AlignCenter)
        
        icon_cancelar = QLabel()
        icon_cancelar.setAlignment(Qt.AlignCenter)
        icon_cancelar.setPixmap(qta.icon('fa5s.times', color='white').pixmap(QSize(40, 40)))
        icon_cancelar.setStyleSheet("background: transparent;")
        btn_cancelar_layout.addWidget(icon_cancelar)
        
        text_cancelar = QLabel("Cancelar")
        text_cancelar.setAlignment(Qt.AlignCenter)
        text_cancelar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 14, QFont.Bold))
        text_cancelar.setStyleSheet("color: white; background: transparent;")
        btn_cancelar_layout.addWidget(text_cancelar)
        
        btn_cancelar.setMinimumHeight(120)
        btn_cancelar.setMinimumWidth(200)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WindowsPhoneTheme.TILE_RED};
                border: none;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: #ff1a00;
            }}
            QPushButton:pressed {{
                background-color: #b30f00;
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        layout.addLayout(buttons_layout)
    
    def abrir_turno(self):
        """Crear el turno en la base de datos"""
        try:
            # Obtener monto inicial
            monto_inicial = self.monto_input.value()  # Usar value() en lugar de get_value()
            
            if monto_inicial < 0:
                show_error_dialog(self, "Error", "El monto inicial no puede ser negativo")
                return
            
            # Usar el método abrir_turno_caja de PostgresManager
            turno_id = self.pg_manager.abrir_turno_caja(
                id_usuario=self.user_data['id_usuario'],
                monto_inicial=Decimal(str(monto_inicial))
            )
            
            if turno_id:
                self.turno_id = turno_id
                logging.info(f"Turno {self.turno_id} abierto para usuario {self.user_data['nombre_completo']} con monto inicial ${monto_inicial:.2f}")
                
                show_success_dialog(
                    self, 
                    "Turno Iniciado", 
                    f"Turno abierto correctamente\nMonto inicial: ${monto_inicial:.2f}"
                )
                
                self.accept()
            else:
                show_error_dialog(self, "Error", "No se pudo crear el turno")
                
        except Exception as e:
            logging.error(f"Error abriendo turno: {e}")
            show_error_dialog(self, "Error", f"Error al abrir turno:\n{str(e)}")
    
    def get_turno_id(self):
        """Obtener el ID del turno creado"""
        return self.turno_id
