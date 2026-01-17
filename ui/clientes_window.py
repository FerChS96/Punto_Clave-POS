"""
Ventana de Gestión de Clientes para HTF POS
Grid con lista de clientes y formulario separado en diálogo
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox,
    QDateEdit, QHeaderView, QAbstractItemView, QGridLayout, QFrame, QDialog,
    QTextEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIntValidator
import logging
from datetime import date, datetime
import uuid

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    SectionTitle,
    ContentPanel,
    StyledLabel,
    show_success_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog,
    aplicar_estilo_fecha,
    TouchMoneyInput
)


class FormularioClienteDialog(QDialog):
    """Diálogo con formulario para agregar/editar clientes"""

    def __init__(self, pg_manager, cliente_data=None, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.cliente_data = cliente_data
        self.setWindowTitle("")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(900)

        self.setup_ui()

        # Si hay datos, cargarlos
        if cliente_data:
            self.cargar_datos(cliente_data)

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = SectionTitle("DATOS DEL CLIENTE")
        layout.addWidget(title)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)

        row = 0

        # Estilo para inputs
        input_style = f"""
            QLineEdit, QComboBox, QDateEdit, QTextEdit {{
                padding: 8px;
                border: 2px solid #e5e7eb;
                border-radius:4px;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 10px;
            }}
        """

        # Código
        grid.addWidget(StyledLabel("Código:", bold=True), row, 0)
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código único del cliente")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.setStyleSheet(input_style)
        grid.addWidget(self.input_codigo, row, 1)
        row += 1

        # Nombres
        grid.addWidget(StyledLabel("Nombres:", bold=True), row, 0)
        self.input_nombres = QLineEdit()
        self.input_nombres.setPlaceholderText("Nombres del cliente")
        self.input_nombres.setMinimumHeight(40)
        self.input_nombres.setStyleSheet(input_style)
        grid.addWidget(self.input_nombres, row, 1)
        row += 1

        # Apellido Paterno
        grid.addWidget(StyledLabel("Apellido Paterno:", bold=True), row, 0)
        self.input_apellido_paterno = QLineEdit()
        self.input_apellido_paterno.setPlaceholderText("Apellido paterno")
        self.input_apellido_paterno.setMinimumHeight(40)
        self.input_apellido_paterno.setStyleSheet(input_style)
        grid.addWidget(self.input_apellido_paterno, row, 1)
        row += 1

        # Apellido Materno
        grid.addWidget(StyledLabel("Apellido Materno:", bold=True), row, 0)
        self.input_apellido_materno = QLineEdit()
        self.input_apellido_materno.setPlaceholderText("Apellido materno (opcional)")
        self.input_apellido_materno.setMinimumHeight(40)
        self.input_apellido_materno.setStyleSheet(input_style)
        grid.addWidget(self.input_apellido_materno, row, 1)
        row += 1

        # Teléfono
        grid.addWidget(StyledLabel("Teléfono:", bold=True), row, 0)
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono del cliente")
        self.input_telefono.setMaxLength(20)
        self.input_telefono.setMinimumHeight(40)
        self.input_telefono.setStyleSheet(input_style)
        grid.addWidget(self.input_telefono, row, 1)
        row += 1

        # Email
        grid.addWidget(StyledLabel("Email:", bold=True), row, 0)
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Correo electrónico")
        self.input_email.setMinimumHeight(40)
        self.input_email.setStyleSheet(input_style)
        grid.addWidget(self.input_email, row, 1)
        row += 1

        # RFC
        grid.addWidget(StyledLabel("RFC:", bold=True), row, 0)
        self.input_rfc = QLineEdit()
        self.input_rfc.setPlaceholderText("RFC (opcional)")
        self.input_rfc.setMaxLength(13)
        self.input_rfc.setMinimumHeight(40)
        self.input_rfc.setStyleSheet(input_style)
        grid.addWidget(self.input_rfc, row, 1)
        row += 1

        # Fecha de Nacimiento
        grid.addWidget(StyledLabel("Fecha Nacimiento:", bold=True), row, 0)
        self.input_fecha_nacimiento = QDateEdit()
        self.input_fecha_nacimiento.setCalendarPopup(True)
        self.input_fecha_nacimiento.setDisplayFormat("dd/MM/yyyy")
        self.input_fecha_nacimiento.setDate(QDate.currentDate().addYears(-18))  # Default 18 años
        aplicar_estilo_fecha(self.input_fecha_nacimiento)
        grid.addWidget(self.input_fecha_nacimiento, row, 1)
        row += 1

        # Contacto de Emergencia
        grid.addWidget(StyledLabel("Contacto Emergencia:", bold=True), row, 0)
        self.input_contacto_emergencia = QLineEdit()
        self.input_contacto_emergencia.setPlaceholderText("Nombre del contacto de emergencia")
        self.input_contacto_emergencia.setMinimumHeight(40)
        self.input_contacto_emergencia.setStyleSheet(input_style)
        grid.addWidget(self.input_contacto_emergencia, row, 1)
        row += 1

        # Teléfono de Emergencia
        grid.addWidget(StyledLabel("Tel. Emergencia:", bold=True), row, 0)
        self.input_telefono_emergencia = QLineEdit()
        self.input_telefono_emergencia.setPlaceholderText("Teléfono de emergencia")
        self.input_telefono_emergencia.setMaxLength(20)
        self.input_telefono_emergencia.setMinimumHeight(40)
        self.input_telefono_emergencia.setStyleSheet(input_style)
        grid.addWidget(self.input_telefono_emergencia, row, 1)
        row += 1

        # Límite de Crédito
        grid.addWidget(StyledLabel("Límite Crédito:", bold=True), row, 0)
        self.input_limite_credito = TouchMoneyInput()
        self.input_limite_credito.setPlaceholderText("0.00")
        grid.addWidget(self.input_limite_credito, row, 1)
        row += 1

        # Notas
        grid.addWidget(StyledLabel("Notas:", bold=True), row, 0)
        self.input_notas = QTextEdit()
        self.input_notas.setPlaceholderText("Notas adicionales del cliente")
        self.input_notas.setMaximumHeight(80)
        self.input_notas.setStyleSheet(input_style)
        grid.addWidget(self.input_notas, row, 1)
        row += 1

        layout.addLayout(grid)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.reject)

        btn_guardar = TileButton("Guardar", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_cliente)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_guardar)

        layout.addLayout(buttons_layout)

    def cargar_datos(self, cliente_data):
        """Cargar datos del cliente en el formulario"""
        self.input_codigo.setText(cliente_data.get('codigo', ''))
        self.input_nombres.setText(cliente_data.get('nombres', ''))
        self.input_apellido_paterno.setText(cliente_data.get('apellido_paterno', ''))
        self.input_apellido_materno.setText(cliente_data.get('apellido_materno', ''))
        self.input_telefono.setText(cliente_data.get('telefono', ''))
        self.input_email.setText(cliente_data.get('email', ''))
        self.input_rfc.setText(cliente_data.get('rfc', ''))
        self.input_contacto_emergencia.setText(cliente_data.get('contacto_emergencia', ''))
        self.input_telefono_emergencia.setText(cliente_data.get('telefono_emergencia', ''))
        self.input_limite_credito.setText(str(cliente_data.get('limite_credito', 0)))
        self.input_notas.setPlainText(cliente_data.get('notas', ''))

        # Fecha de nacimiento
        fecha_nac = cliente_data.get('fecha_nacimiento')
        if fecha_nac:
            if isinstance(fecha_nac, str):
                fecha_nac = datetime.fromisoformat(fecha_nac.split('T')[0]).date()
            elif isinstance(fecha_nac, datetime):
                fecha_nac = fecha_nac.date()
            self.input_fecha_nacimiento.setDate(QDate(fecha_nac))
        else:
            self.input_fecha_nacimiento.setDate(QDate())  # Fecha vacía

    def validar_datos(self):
        """Validar datos del formulario"""
        errores = []

        if not self.input_codigo.text().strip():
            errores.append("El código es obligatorio")

        if not self.input_nombres.text().strip():
            errores.append("Los nombres son obligatorios")

        if not self.input_apellido_paterno.text().strip():
            errores.append("El apellido paterno es obligatorio")

        # Validar email si se proporciona
        email = self.input_email.text().strip()
        if email and not self.validar_email(email):
            errores.append("El formato del email no es válido")

        # Validar teléfono si se proporciona
        telefono = self.input_telefono.text().strip()
        if telefono and len(telefono) < 10:
            errores.append("El teléfono debe tener al menos 10 dígitos")

        return errores

    def validar_email(self, email):
        """Validar formato de email"""
        import re
        patron = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return re.match(patron, email) is not None

    def guardar_cliente(self):
        """Guardar datos del cliente"""
        # Validar datos
        errores = self.validar_datos()
        if errores:
            show_warning_dialog(self, "Datos Incompletos",
                              "Por favor corrija los siguientes errores:\n\n" + "\n".join(errores))
            return

        try:
            # Preparar datos
            datos = {
                'codigo': self.input_codigo.text().strip(),
                'nombres': self.input_nombres.text().strip(),
                'apellido_paterno': self.input_apellido_paterno.text().strip(),
                'apellido_materno': self.input_apellido_materno.text().strip() or None,
                'telefono': self.input_telefono.text().strip() or None,
                'email': self.input_email.text().strip() or None,
                'rfc': self.input_rfc.text().strip() or None,
                'fecha_nacimiento': self.input_fecha_nacimiento.date().toPython() if self.input_fecha_nacimiento.date().isValid() else None,
                'contacto_emergencia': self.input_contacto_emergencia.text().strip() or None,
                'telefono_emergencia': self.input_telefono_emergencia.text().strip() or None,
                'limite_credito': float(self.input_limite_credito.get_value()),
                'notas': self.input_notas.toPlainText().strip() or None
            }

            if self.cliente_data:
                # Actualizar cliente existente
                sql = """
                    UPDATE clientes SET
                        codigo = %s, nombres = %s, apellido_paterno = %s, apellido_materno = %s,
                        telefono = %s, email = %s, rfc = %s, fecha_nacimiento = %s,
                        contacto_emergencia = %s, telefono_emergencia = %s,
                        limite_credito = %s, notas = %s
                    WHERE id_cliente = %s
                """
                params = list(datos.values()) + [self.cliente_data['id_cliente']]
                success = self.pg_manager.execute(sql, params)
                if not success:
                    raise Exception("Error al actualizar cliente")
                show_success_dialog(self, "Éxito", "Cliente actualizado correctamente")
            else:
                # Insertar nuevo cliente
                sql = """
                    INSERT INTO clientes (
                        codigo, nombres, apellido_paterno, apellido_materno,
                        telefono, email, rfc, fecha_nacimiento,
                        contacto_emergencia, telefono_emergencia,
                        limite_credito, notas
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                success = self.pg_manager.execute(sql, list(datos.values()))
                if not success:
                    raise Exception("Error al crear cliente")
                show_success_dialog(self, "Éxito", "Cliente creado correctamente")

            self.accept()

        except Exception as e:
            logging.error(f"Error guardando cliente: {e}")
            show_error_dialog(self, "Error", f"No se pudo guardar el cliente: {e}")


class ClientesWindow(QWidget):
    """Widget con grid de clientes"""

    cerrar_solicitado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data

        self.setup_ui()
        self.cargar_clientes()

    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(8)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre Completo", "Teléfono", "Email", "Límite Crédito", "Total Compras", "Estado"
        ])

        # Configurar tabla
        self.tabla_clientes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_clientes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_clientes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_clientes.horizontalHeader().setStretchLastSection(True)
        self.tabla_clientes.verticalHeader().setVisible(False)

        # Ajustar columnas
        header = self.tabla_clientes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nombre Completo
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Límite Crédito
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Total Compras
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Estado

        # Aplicar estilos a la tabla
        self.tabla_clientes.setStyleSheet(f"""
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

        layout.addWidget(self.tabla_clientes)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        btn_agregar = TileButton("Agregar Cliente", "fa5s.user-plus", WindowsPhoneTheme.TILE_GREEN)
        btn_agregar.clicked.connect(self.agregar_cliente)

        btn_editar = TileButton("Editar", "fa5s.edit", WindowsPhoneTheme.TILE_BLUE)
        btn_editar.clicked.connect(self.editar_cliente)

        btn_desactivar = TileButton("Dar de Baja", "fa5s.user-times", WindowsPhoneTheme.TILE_ORANGE)
        btn_desactivar.clicked.connect(self.desactivar_cliente)

        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)

        buttons_layout.addWidget(btn_agregar)
        buttons_layout.addWidget(btn_editar)
        buttons_layout.addWidget(btn_desactivar)
        buttons_layout.addWidget(btn_volver)

        layout.addLayout(buttons_layout)

    def cargar_clientes(self):
        """Cargar lista de clientes"""
        try:
            sql = """
                SELECT id_cliente, codigo, nombres, apellido_paterno, apellido_materno,
                       telefono, email, limite_credito, total_compras, activo
                FROM clientes
                ORDER BY apellido_paterno, apellido_materno, nombres
            """
            clientes = self.pg_manager.query(sql)
            self.tabla_clientes.setRowCount(0)

            for cliente in clientes:
                row = self.tabla_clientes.rowCount()
                self.tabla_clientes.insertRow(row)

                # ID
                id_item = QTableWidgetItem(str(cliente['id_cliente']))
                self.tabla_clientes.setItem(row, 0, id_item)

                # Código
                self.tabla_clientes.setItem(row, 1, QTableWidgetItem(cliente['codigo']))

                # Nombre Completo
                nombre_completo = f"{cliente['nombres']} {cliente['apellido_paterno']}"
                if cliente['apellido_materno']:
                    nombre_completo += f" {cliente['apellido_materno']}"
                self.tabla_clientes.setItem(row, 2, QTableWidgetItem(nombre_completo))

                # Teléfono
                telefono = cliente['telefono'] if cliente['telefono'] else "N/A"
                self.tabla_clientes.setItem(row, 3, QTableWidgetItem(telefono))

                # Email
                email = cliente['email'] if cliente['email'] else "N/A"
                self.tabla_clientes.setItem(row, 4, QTableWidgetItem(email))

                # Límite Crédito
                limite = f"${cliente['limite_credito']:.2f}" if cliente['limite_credito'] else "$0.00"
                self.tabla_clientes.setItem(row, 5, QTableWidgetItem(limite))

                # Total Compras
                total = f"${cliente['total_compras']:.2f}" if cliente['total_compras'] else "$0.00"
                self.tabla_clientes.setItem(row, 6, QTableWidgetItem(total))

                # Estado
                estado = "Activo" if cliente['activo'] else "Inactivo"
                estado_item = QTableWidgetItem(estado)
                if not cliente['activo']:
                    estado_item.setForeground(Qt.red)
                self.tabla_clientes.setItem(row, 7, estado_item)

        except Exception as e:
            logging.error(f"Error cargando clientes: {e}")
            show_error_dialog(self, "Error", f"No se pudo cargar los clientes: {e}")

    def agregar_cliente(self):
        """Abrir formulario para agregar cliente"""
        dialog = FormularioClienteDialog(self.pg_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_clientes()

    def editar_cliente(self):
        """Abrir formulario para editar cliente seleccionado"""
        selected = self.tabla_clientes.selectedItems()
        if not selected:
            show_warning_dialog(self, "Selección", "Debe seleccionar un cliente para editar")
            return

        row = selected[0].row()
        id_cliente = int(self.tabla_clientes.item(row, 0).text())

        try:
            sql = "SELECT * FROM clientes WHERE id_cliente = %s"
            result = self.pg_manager.query(sql, (id_cliente,))
            cliente = result[0] if result else None
            if cliente:
                dialog = FormularioClienteDialog(
                    self.pg_manager,
                    cliente_data=dict(cliente),
                    parent=self
                )
                if dialog.exec() == QDialog.Accepted:
                    self.cargar_clientes()

        except Exception as e:
            logging.error(f"Error cargando datos de cliente: {e}")
            show_error_dialog(self, "Error", f"No se pudo cargar los datos: {e}")

    def desactivar_cliente(self):
        """Dar de baja al cliente seleccionado"""
        selected = self.tabla_clientes.selectedItems()
        if not selected:
            show_warning_dialog(self, "Selección", "Debe seleccionar un cliente para dar de baja")
            return

        row = selected[0].row()
        id_cliente = int(self.tabla_clientes.item(row, 0).text())
        nombre_cliente = self.tabla_clientes.item(row, 2).text()

        if show_confirmation_dialog(
            self,
            "Confirmar Baja",
            f"¿Desea dar de baja a {nombre_cliente}?",
            detail="Esta acción marcará al cliente como inactivo.",
            confirm_text="Sí, dar de baja",
            cancel_text="Cancelar"
        ):
            try:
                sql = "UPDATE clientes SET activo = %s WHERE id_cliente = %s"
                success = self.pg_manager.execute(sql, (False, id_cliente))
                if not success:
                    raise Exception("Error al desactivar cliente")

                show_success_dialog(self, "Éxito", "Cliente dado de baja correctamente")

                self.cargar_clientes()

            except Exception as e:
                logging.error(f"Error dando de baja cliente: {e}")
                show_error_dialog(self, "Error", f"No se pudo dar de baja: {e}")