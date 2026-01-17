"""
Formulario de Nuevo Cliente para HTF POS
Formulario para agregar nuevos clientes al sistema
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDateEdit, QScrollArea, QGroupBox, QFrame, QLabel,
    QTabWidget, QSplitter, QSizePolicy, QDialog
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QIcon, QShowEvent
import logging
from datetime import date, datetime
import uuid

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


class NuevoClienteWindow(QWidget):
    """Formulario para agregar nuevos clientes al sistema"""

    cerrar_solicitado = Signal()
    cliente_guardado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data

        # Variable para evitar verificaciones duplicadas
        self.ultimo_codigo_verificado = ""

        # Bandera para cargar datos iniciales solo una vez
        self.datos_iniciales_cargados = False

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        logging.info("Iniciando setup_ui de NuevoClienteWindow")
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

        # Pestaña de Información General
        tab_general = self.crear_tab_general()
        self.tab_widget.addTab(tab_general, "Información General")

        # Pestaña de Información Adicional
        tab_adicional = self.crear_tab_adicional()
        self.tab_widget.addTab(tab_adicional, "Información Adicional")

        content_layout.addWidget(self.tab_widget)

        # Panel de botones
        buttons_panel = ContentPanel()
        buttons_layout = QHBoxLayout(buttons_panel)
        buttons_layout.setContentsMargins(20, 20, 20, 20)

        # Espacio flexible
        buttons_layout.addStretch()

        # Botón Cancelar
        self.btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        self.btn_cancelar.clicked.connect(self.cancelar)
        buttons_layout.addWidget(self.btn_cancelar)

        # Espacio entre botones
        buttons_layout.addSpacing(20)

        # Botón Guardar
        self.btn_guardar = TileButton("Guardar Cliente", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        self.btn_guardar.clicked.connect(self.guardar_cliente)
        buttons_layout.addWidget(self.btn_guardar)

        content_layout.addWidget(buttons_panel)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        logging.info("setup_ui completado exitosamente")

    def crear_tab_general(self):
        """Crear pestaña de información general"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Grupo de Código y Nombres
        grupo_codigo = QGroupBox("Código y Nombres")
        grupo_codigo.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_codigo = QFormLayout(grupo_codigo)
        layout_codigo.setContentsMargins(15, 25, 15, 15)
        layout_codigo.setSpacing(10)

        # Código
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("CLI0001")
        self.input_codigo.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        self.input_codigo.textChanged.connect(self._verificar_codigo)
        layout_codigo.addRow("Código:", self.input_codigo)

        # Nombres
        self.input_nombres = QLineEdit()
        self.input_nombres.setPlaceholderText("Nombres del cliente")
        self.input_nombres.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_codigo.addRow("Nombres:", self.input_nombres)

        # Apellido Paterno
        self.input_apellido_paterno = QLineEdit()
        self.input_apellido_paterno.setPlaceholderText("Apellido paterno")
        self.input_apellido_paterno.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_codigo.addRow("Apellido Paterno:", self.input_apellido_paterno)

        # Apellido Materno
        self.input_apellido_materno = QLineEdit()
        self.input_apellido_materno.setPlaceholderText("Apellido materno")
        self.input_apellido_materno.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_codigo.addRow("Apellido Materno:", self.input_apellido_materno)

        layout.addWidget(grupo_codigo)

        # Grupo de Contacto
        grupo_contacto = QGroupBox("Información de Contacto")
        grupo_contacto.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_contacto = QFormLayout(grupo_contacto)
        layout_contacto.setContentsMargins(15, 25, 15, 15)
        layout_contacto.setSpacing(10)

        # Teléfono
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("10 dígitos")
        self.input_telefono.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_contacto.addRow("Teléfono:", self.input_telefono)

        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("correo@ejemplo.com")
        self.input_email.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_contacto.addRow("Email:", self.input_email)

        layout.addWidget(grupo_contacto)

        return tab

    def crear_tab_adicional(self):
        """Crear pestaña de información adicional"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Grupo de Información Fiscal
        grupo_fiscal = QGroupBox("Información Fiscal")
        grupo_fiscal.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_fiscal = QFormLayout(grupo_fiscal)
        layout_fiscal.setContentsMargins(15, 25, 15, 15)
        layout_fiscal.setSpacing(10)

        # RFC
        self.input_rfc = QLineEdit()
        self.input_rfc.setPlaceholderText("RFC del cliente")
        self.input_rfc.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_fiscal.addRow("RFC:", self.input_rfc)

        layout.addWidget(grupo_fiscal)

        # Grupo de Información Personal
        grupo_personal = QGroupBox("Información Personal")
        grupo_personal.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_personal = QFormLayout(grupo_personal)
        layout_personal.setContentsMargins(15, 25, 15, 15)
        layout_personal.setSpacing(10)

        # Fecha de Nacimiento
        self.input_fecha_nacimiento = QDateEdit()
        self.input_fecha_nacimiento.setCalendarPopup(True)
        self.input_fecha_nacimiento.setDate(QDate.currentDate().addYears(-18))
        aplicar_estilo_fecha(self.input_fecha_nacimiento)
        layout_personal.addRow("Fecha de Nacimiento:", self.input_fecha_nacimiento)

        # Contacto de Emergencia
        self.input_contacto_emergencia = QLineEdit()
        self.input_contacto_emergencia.setPlaceholderText("Nombre del contacto")
        self.input_contacto_emergencia.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_personal.addRow("Contacto de Emergencia:", self.input_contacto_emergencia)

        # Teléfono de Emergencia
        self.input_telefono_emergencia = QLineEdit()
        self.input_telefono_emergencia.setPlaceholderText("Teléfono de emergencia")
        self.input_telefono_emergencia.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_personal.addRow("Teléfono de Emergencia:", self.input_telefono_emergencia)

        layout.addWidget(grupo_personal)

        # Grupo de Crédito
        grupo_credito = QGroupBox("Información de Crédito")
        grupo_credito.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_credito = QFormLayout(grupo_credito)
        layout_credito.setContentsMargins(15, 25, 15, 15)
        layout_credito.setSpacing(10)

        # Límite de Crédito
        self.input_limite_credito = TouchMoneyInput()
        self.input_limite_credito.setValue(0.00)
        layout_credito.addRow("Límite de Crédito:", self.input_limite_credito)

        layout.addWidget(grupo_credito)

        # Grupo de Notas
        grupo_notas = QGroupBox("Notas Adicionales")
        grupo_notas.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 5px;
                margin-top: 1ex;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        layout_notas = QVBoxLayout(grupo_notas)
        layout_notas.setContentsMargins(15, 25, 15, 15)

        self.input_notas = QTextEdit()
        self.input_notas.setPlaceholderText("Notas adicionales sobre el cliente...")
        self.input_notas.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QTextEdit:focus {{
                border-color: {WindowsPhoneTheme.PRIMARY_BLUE};
            }}
        """)
        layout_notas.addWidget(self.input_notas)

        layout.addWidget(grupo_notas)

        return tab

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales del formulario"""
        try:
            logging.info("Iniciando cargar_datos_iniciales")
            # Usar QTimer para retrasar la carga inicial y evitar problemas de timing
            QTimer.singleShot(100, self.generar_codigo_automatico)  # Reducido a 100ms
            logging.info("QTimer configurado para generar_codigo_automatico")
        except Exception as e:
            logging.error(f"Error cargando datos iniciales: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def generar_codigo_automatico(self):
        """Generar código automático para el cliente"""
        try:
            logging.info("Generando código automático para cliente...")

            # Verificar que el widget existe
            if not hasattr(self, 'input_codigo') or self.input_codigo is None:
                logging.warning("input_codigo no está disponible, reintentando en 200ms")
                QTimer.singleShot(200, self.generar_codigo_automatico)
                return

            logging.info("input_codigo encontrado, obteniendo último código...")

            # Obtener el último código de cliente
            ultimo_codigo = self.pg_manager.obtener_ultimo_codigo_cliente()
            logging.info(f"Último código obtenido: {ultimo_codigo}")

            if ultimo_codigo:
                # Extraer el número del código (asumiendo formato CLI0001, CLI0002, etc.)
                try:
                    numero = int(ultimo_codigo.replace('CLI', ''))
                    nuevo_numero = numero + 1
                    nuevo_codigo = f"CLI{nuevo_numero:04d}"
                    logging.info(f"Nuevo código generado: {nuevo_codigo}")
                except ValueError:
                    nuevo_codigo = f"CLI{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    logging.warning(f"Error parseando código, usando timestamp: {nuevo_codigo}")
            else:
                nuevo_codigo = "CLI0001"
                logging.info("Primer código generado: CLI0001")

            logging.info(f"Estableciendo texto en input_codigo: {nuevo_codigo}")
            if self.isVisible() and hasattr(self, 'input_codigo') and self.input_codigo is not None:
                try:
                    self.input_codigo.setText(nuevo_codigo)
                    logging.info("Código automático generado exitosamente")
                except RuntimeError as e:
                    logging.warning(f"Widget destruido antes de setText: {e}")
            else:
                logging.warning("Ventana no visible o widget no disponible, cancelando setText")

        except Exception as e:
            logging.error(f"Error generando código automático: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def _verificar_codigo(self):
        """Verificar si el código ya existe"""
        codigo = self.input_codigo.text().strip()

        if not codigo or codigo == self.ultimo_codigo_verificado:
            return

        try:
            existe = self.pg_manager.verificar_codigo_cliente_existe(codigo)
            if existe:
                self.input_codigo.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 8px;
                        border: 2px solid {WindowsPhoneTheme.ERROR_COLOR};
                        border-radius: 4px;
                        font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                        font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                        background-color: white;
                    }}
                """)
                show_warning_dialog(self, "Código Duplicado",
                                  f"El código '{codigo}' ya existe. Se generará uno automáticamente.")
                self.generar_codigo_automatico()
            else:
                self.input_codigo.setStyleSheet(f"""
                    QLineEdit {{
                        padding: 8px;
                        border: 2px solid {WindowsPhoneTheme.SUCCESS_COLOR};
                        border-radius: 4px;
                        font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                        font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                        background-color: white;
                    }}
                """)
            self.ultimo_codigo_verificado = codigo
        except Exception as e:
            logging.error(f"Error verificando código: {e}")

    def guardar_cliente(self):
        """Guardar el cliente en la base de datos"""
        try:
            # Validar datos requeridos
            codigo = self.input_codigo.text().strip()
            nombres = self.input_nombres.text().strip()
            apellido_paterno = self.input_apellido_paterno.text().strip()

            if not codigo:
                show_warning_dialog(self, "Dato Requerido", "El código del cliente es obligatorio.")
                return
            if not nombres:
                show_warning_dialog(self, "Dato Requerido", "Los nombres del cliente son obligatorios.")
                return
            if not apellido_paterno:
                show_warning_dialog(self, "Dato Requerido", "El apellido paterno es obligatorio.")
                return

            # Validar email si se proporciona
            email = self.input_email.text().strip()
            if email and not self._validar_email(email):
                show_warning_dialog(self, "Email Inválido", "El formato del email no es válido.")
                return

            # Preparar datos
            datos_cliente = {
                'codigo': codigo,
                'nombres': nombres,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': self.input_apellido_materno.text().strip() or None,
                'telefono': self.input_telefono.text().strip() or None,
                'email': email or None,
                'rfc': self.input_rfc.text().strip() or None,
                'contacto_emergencia': self.input_contacto_emergencia.text().strip() or None,
                'telefono_emergencia': self.input_telefono_emergencia.text().strip() or None,
                'fecha_nacimiento': self.input_fecha_nacimiento.date().toPython() if self.input_fecha_nacimiento.date().isValid() else None,
                'limite_credito': self.input_limite_credito.getValue(),
                'notas': self.input_notas.toPlainText().strip() or None,
                'activo': True,
                'fecha_registro': datetime.now(),
                'usuario_registro': self.user_data.get('id_usuario')
            }

            # Guardar en base de datos
            self.pg_manager.guardar_cliente(datos_cliente)

            show_success_dialog(self, "Cliente Guardado", f"El cliente {codigo} ha sido guardado exitosamente.")
            self.cliente_guardado.emit()
            self.cancelar()

        except Exception as e:
            logging.error(f"Error guardando cliente: {e}")
            show_error_dialog(self, "Error", f"Error al guardar el cliente: {str(e)}")

    def _validar_email(self, email):
        """Validar formato de email"""
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def cancelar(self):
        """Cancelar y cerrar el formulario"""
        respuesta = show_confirmation_dialog(
            self,
            "Cancelar",
            "¿Está seguro que desea cancelar? Los datos no guardados se perderán.",
            confirm_text="Sí, cancelar",
        )
        if respuesta:
            self.cerrar_solicitado.emit()

    def showEvent(self, event: QShowEvent):
        """Evento cuando la ventana se muestra por primera vez"""
        logging.info("showEvent triggered")
        super().showEvent(event)
        if not self.datos_iniciales_cargados:
            logging.info("Cargando datos iniciales por primera vez")
            self.datos_iniciales_cargados = True
            self.cargar_datos_iniciales()