"""
Diálogo de Acceso de Miembro para HTF POS
Muestra información del miembro con foto al registrar entrada
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QGraphicsOpacityEffect, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PySide6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QCursor
import logging
from datetime import datetime
import os

from ui.components import (
    WindowsPhoneTheme,
    TileButton
)


class FotoLoaderThread(QThread):
    """Hilo para cargar la foto del miembro de forma asíncrona"""
    foto_loaded = pyqtSignal(QPixmap)
    
    def __init__(self, foto_path):
        super().__init__()
        self.foto_path = foto_path
    
    def run(self):
        """Cargar la foto en un hilo separado"""
        if self.foto_path and os.path.exists(self.foto_path):
            pixmap = QPixmap(self.foto_path)
            if not pixmap.isNull():
                self.foto_loaded.emit(pixmap)
                return
        
        # Si no hay foto o hay error, emitir None
        self.foto_loaded.emit(None)


class AccesoMiembroDialog(QDialog):
    """Diálogo para mostrar información del miembro al registrar acceso"""
    
    acceso_confirmado = Signal(dict)  # Emite los datos del miembro cuando se confirma
    
    def __init__(self, miembro_data, parent=None):
        super().__init__(parent)
        self.miembro_data = miembro_data
        self.foto_thread = None
        
        # Configuración de ventana
        self.setWindowTitle("Acceso al Gimnasio")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Configurar flags para ventana sin bordes
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Variables para arrastre
        self.dragging = False
        self.drag_position = None
        
        # Efecto de opacidad para animaciones
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Configurar UI
        self.setup_ui()
        self.aplicar_estilos()
        
        # Cargar foto de forma asíncrona
        self.cargar_foto_async()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        # Layout principal con margen para sombra
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Contenedor principal
        container = QFrame()
        container.setObjectName("dialogContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # ===== ENCABEZADO =====
        header = self.create_header()
        container_layout.addWidget(header)
        
        # ===== CONTENIDO PRINCIPAL =====
        content = self.create_content()
        container_layout.addWidget(content)
        
        # ===== BOTONES DE ACCIÓN =====
        buttons_layout = self.create_buttons_layout()
        container_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(container)
    
    def create_header(self):
        """Crear el encabezado del diálogo"""
        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setMinimumHeight(80)
        header.setCursor(QCursor(Qt.OpenHandCursor))  # Cursor para indicar que se puede arrastrar
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("¡BIENVENIDO!")
        title.setObjectName("dialogTitle")
        title.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        self.hora_label = QLabel(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
        self.hora_label.setStyleSheet(f"color: white; font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;")
        self.hora_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.hora_label)
        
        return header
    
    def create_content(self):
        """Crear el contenido principal del diálogo"""
        content = QWidget()
        content.setObjectName("dialogContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(25)
        
        # ===== FOTO DEL MIEMBRO =====
        foto_container = QHBoxLayout()
        foto_container.setAlignment(Qt.AlignCenter)
        
        self.foto_label = QLabel()
        self.foto_label.setFixedSize(200, 200)
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setObjectName("fotoMiembro")
        
        # Mostrar placeholder inicialmente
        self.mostrar_placeholder()
        
        foto_container.addWidget(self.foto_label)
        content_layout.addLayout(foto_container)
        
        # ===== DATOS DEL MIEMBRO =====
        datos_container = self.create_datos_container()
        content_layout.addWidget(datos_container)
        
        # Espaciador
        content_layout.addStretch()
        
        return content
    
    def create_datos_container(self):
        """Crear el contenedor con los datos del miembro"""
        datos_container = QFrame()
        datos_container.setObjectName("datosContainer")
        datos_layout = QVBoxLayout(datos_container)
        datos_layout.setContentsMargins(20, 20, 20, 20)
        datos_layout.setSpacing(15)
        
        # Nombre completo
        nombre_completo = f"{self.miembro_data.get('nombres', '')} {self.miembro_data.get('apellido_paterno', '')} {self.miembro_data.get('apellido_materno', '')}".strip()
        nombre_label = QLabel(nombre_completo.upper())
        nombre_label.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 20, QFont.Bold))
        nombre_label.setAlignment(Qt.AlignCenter)
        nombre_label.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE};")
        datos_layout.addWidget(nombre_label)
        
        # Línea divisoria
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e5e7eb; max-height: 1px;")
        datos_layout.addWidget(line)
        
        # Información adicional en grid
        info_layout = QGridLayout()
        info_layout.setSpacing(12)
        
        # ID Miembro
        self.agregar_info_row(info_layout, 0, "ID Miembro:", f"#{self.miembro_data.get('id_miembro', 'N/A')}")
        
        # Fecha de registro
        fecha_registro = self.miembro_data.get('fecha_registro', 'N/A')
        self.agregar_info_row(info_layout, 1, "Miembro desde:", fecha_registro)
        
        # Teléfono
        telefono = self.miembro_data.get('telefono', 'No registrado')
        self.agregar_info_row(info_layout, 2, "Teléfono:", telefono)
        
        # Email
        email = self.miembro_data.get('email', 'No registrado')
        self.agregar_info_row(info_layout, 3, "Email:", email)
        
        # Estado
        estado = "ACTIVO" if self.miembro_data.get('activo', False) else "INACTIVO"
        estado_color = WindowsPhoneTheme.TILE_GREEN if self.miembro_data.get('activo', False) else WindowsPhoneTheme.TILE_RED
        self.agregar_info_row(info_layout, 4, "Estado:", estado, estado_color)
        
        datos_layout.addLayout(info_layout)
        return datos_container
    
    def create_buttons_layout(self):
        """Crear el layout con los botones de acción"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(40, 20, 40, 30)
        buttons_layout.setSpacing(20)
        
        # Verificar si el miembro está activo
        if self.miembro_data.get('activo', False):
            btn_confirmar = TileButton(
                "REGISTRAR ENTRADA",
                "fa5s.check-circle",
                WindowsPhoneTheme.TILE_GREEN
            )
            btn_confirmar.setMinimumHeight(100)
            btn_confirmar.clicked.connect(self.confirmar_acceso)
            buttons_layout.addWidget(btn_confirmar, 2)
        else:
            # Mostrar mensaje de miembro inactivo
            mensaje_inactivo = QLabel("⚠️ MIEMBRO INACTIVO - Contactar recepción")
            mensaje_inactivo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 14, QFont.Bold))
            mensaje_inactivo.setStyleSheet(f"color: {WindowsPhoneTheme.TILE_RED}; padding: 15px;")
            mensaje_inactivo.setAlignment(Qt.AlignCenter)
            buttons_layout.addWidget(mensaje_inactivo, 2)
        
        btn_cancelar = TileButton(
            "CANCELAR",
            "fa5s.times-circle",
            WindowsPhoneTheme.TILE_RED
        )
        btn_cancelar.setMinimumHeight(100)
        btn_cancelar.clicked.connect(self.close_with_animation)
        buttons_layout.addWidget(btn_cancelar, 1)
        
        return buttons_layout
    
    def agregar_info_row(self, layout, row, etiqueta, valor, color_valor=None):
        """Agregar una fila de información al grid"""
        # Etiqueta
        label_etiqueta = QLabel(etiqueta)
        label_etiqueta.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
        label_etiqueta.setStyleSheet("color: #6b7280;")
        label_etiqueta.setMinimumWidth(150)
        layout.addWidget(label_etiqueta, row, 0)
        
        # Valor
        label_valor = QLabel(valor)
        label_valor.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        if color_valor:
            label_valor.setStyleSheet(f"color: {color_valor}; font-weight: bold;")
        else:
            label_valor.setStyleSheet("color: #1f2937;")
        layout.addWidget(label_valor, row, 1)
    
    def cargar_foto_async(self):
        """Cargar foto del miembro de forma asíncrona"""
        # Primero mostrar placeholder
        self.mostrar_placeholder()
        
        # Crear un hilo para cargar la foto
        foto_path = self.miembro_data.get('foto')
        self.foto_thread = FotoLoaderThread(foto_path)
        self.foto_thread.foto_loaded.connect(self.on_foto_loaded)
        self.foto_thread.start()
    
    def on_foto_loaded(self, pixmap):
        """Manejar la carga de la foto cuando el hilo termina"""
        if pixmap and not pixmap.isNull():
            # Escalar manteniendo proporción
            pixmap = pixmap.scaled(
                200, 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            # Crear imagen circular
            pixmap = self.crear_imagen_circular(pixmap)
            self.foto_label.setPixmap(pixmap)
    
    def crear_imagen_circular(self, pixmap):
        """Crear una imagen circular a partir de un pixmap"""
        # Crear un pixmap cuadrado del tamaño de la imagen
        size = min(pixmap.width(), pixmap.height())
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Crear path circular
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Dibujar imagen centrada
        x = (size - pixmap.width()) // 2
        y = (size - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()
        
        return rounded
    
    def mostrar_placeholder(self):
        """Mostrar placeholder cuando no hay foto"""
        # Crear placeholder con iniciales
        iniciales = self.obtener_iniciales()
        
        placeholder = QPixmap(200, 200)
        placeholder.fill(Qt.transparent)
        
        painter = QPainter(placeholder)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Círculo de fondo
        painter.setBrush(QColor(WindowsPhoneTheme.TILE_BLUE))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 200, 200)
        
        # Iniciales
        painter.setPen(Qt.white)
        painter.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 60, QFont.Bold))
        painter.drawText(0, 0, 200, 200, Qt.AlignCenter, iniciales)
        
        painter.end()
        
        self.foto_label.setPixmap(placeholder)
    
    def obtener_iniciales(self):
        """Obtener iniciales del nombre del miembro"""
        nombres = self.miembro_data.get('nombres', 'X').strip()
        apellido = self.miembro_data.get('apellido_paterno', 'X').strip()
        
        inicial_nombre = nombres[0].upper() if nombres else 'X'
        inicial_apellido = apellido[0].upper() if apellido else 'X'
        
        return f"{inicial_nombre}{inicial_apellido}"
    
    def confirmar_acceso(self):
        """Confirmar y registrar el acceso"""
        logging.info(f"Acceso confirmado para miembro ID: {self.miembro_data.get('id_miembro')}")
        self.acceso_confirmado.emit(self.miembro_data)
        self.close_with_animation()
    
    def close_with_animation(self):
        """Cerrar el diálogo con animación"""
        # Animación de salida
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.InCubic)
        self.opacity_animation.finished.connect(self.close)
        self.opacity_animation.start()
    
    def showEvent(self, event):
        """Evento cuando se muestra el diálogo"""
        super().showEvent(event)
        
        # Iniciar animación de entrada
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_animation.start()
        
        # Actualizar hora cada segundo
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.actualizar_hora)
        self.update_timer.start(1000)
    
    def actualizar_hora(self):
        """Actualizar la etiqueta de hora"""
        self.hora_label.setText(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
    
    def mousePressEvent(self, event):
        """Iniciar arrastre cuando se presiona el mouse"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Mover la ventana mientras se arrastra"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Terminar arrastre cuando se suelta el mouse"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def closeEvent(self, event):
        """Evento al cerrar el diálogo"""
        # Detener hilo de carga de foto si está activo
        if self.foto_thread and self.foto_thread.isRunning():
            self.foto_thread.terminate()
            self.foto_thread.wait()
            
        # Detener timer de actualización de hora
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
            
        super().closeEvent(event)
    
    def aplicar_estilos(self):
        """Aplicar estilos personalizados al diálogo"""
        self.setStyleSheet(f"""
            #dialogContainer {{
                background-color: white;
                border: 3px solid {WindowsPhoneTheme.PRIMARY_BLUE};
                border-radius: 0px;
            }}
            
            #dialogHeader {{
                background-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
            
            #dialogTitle {{
                color: white;
            }}
            
            #dialogContent {{
                background-color: white;
            }}
            
            #datosContainer {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                border: 2px solid {WindowsPhoneTheme.PRIMARY_BLUE};
                border-radius: 0px;
            }}
            
            #fotoMiembro {{
                border: 4px solid {WindowsPhoneTheme.PRIMARY_BLUE};
                border-radius: 100px;
                background-color: white;
            }}
        """)