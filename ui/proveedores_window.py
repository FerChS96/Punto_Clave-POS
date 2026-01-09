"""
Ventana de Gestión de Proveedores para HTF POS
Grid con lista de proveedores y formulario separado en diálogo
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


class FormularioProveedorDialog(QDialog):
    """Diálogo con formulario para agregar/editar proveedores"""

    def __init__(self, pg_manager, proveedor_data=None, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.proveedor_data = proveedor_data
        self.setWindowTitle("")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(800)

        self.setup_ui()

        # Si hay datos, cargarlos
        if proveedor_data:
            self.cargar_datos(proveedor_data)

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = SectionTitle("DATOS DEL PROVEEDOR")
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
        self.input_codigo.setPlaceholderText("Código único del proveedor")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.setStyleSheet(input_style)
        grid.addWidget(self.input_codigo, row, 1)
        row += 1

        # Razón Social
        grid.addWidget(StyledLabel("Razón Social:", bold=True), row, 0)
        self.input_razon_social = QLineEdit()
        self.input_razon_social.setPlaceholderText("Razón social del proveedor")
        self.input_razon_social.setMinimumHeight(40)
        self.input_razon_social.setStyleSheet(input_style)
        grid.addWidget(self.input_razon_social, row, 1)
        row += 1

        # Nombre Comercial
        grid.addWidget(StyledLabel("Nombre Comercial:", bold=True), row, 0)
        self.input_nombre_comercial = QLineEdit()
        self.input_nombre_comercial.setPlaceholderText("Nombre comercial (opcional)")
        self.input_nombre_comercial.setMinimumHeight(40)
        self.input_nombre_comercial.setStyleSheet(input_style)
        grid.addWidget(self.input_nombre_comercial, row, 1)
        row += 1

        # RFC
        grid.addWidget(StyledLabel("RFC:", bold=True), row, 0)
        self.input_rfc = QLineEdit()
        self.input_rfc.setPlaceholderText("RFC (12-13 caracteres)")
        self.input_rfc.setMaxLength(13)
        self.input_rfc.setMinimumHeight(40)
        self.input_rfc.setStyleSheet(input_style)
        grid.addWidget(self.input_rfc, row, 1)
        row += 1

        # Contacto Nombre
        grid.addWidget(StyledLabel("Contacto:", bold=True), row, 0)
        self.input_contacto_nombre = QLineEdit()
        self.input_contacto_nombre.setPlaceholderText("Nombre del contacto")
        self.input_contacto_nombre.setMinimumHeight(40)
        self.input_contacto_nombre.setStyleSheet(input_style)
        grid.addWidget(self.input_contacto_nombre, row, 1)
        row += 1

        # Contacto Teléfono
        grid.addWidget(StyledLabel("Teléfono:", bold=True), row, 0)
        self.input_contacto_telefono = QLineEdit()
        self.input_contacto_telefono.setPlaceholderText("Teléfono del contacto")
        self.input_contacto_telefono.setMaxLength(20)
        self.input_contacto_telefono.setMinimumHeight(40)
        self.input_contacto_telefono.setStyleSheet(input_style)
        grid.addWidget(self.input_contacto_telefono, row, 1)
        row += 1

        # Contacto Email
        grid.addWidget(StyledLabel("Email:", bold=True), row, 0)
        self.input_contacto_email = QLineEdit()
        self.input_contacto_email.setPlaceholderText("correo@ejemplo.com")
        self.input_contacto_email.setMinimumHeight(40)
        self.input_contacto_email.setStyleSheet(input_style)
        grid.addWidget(self.input_contacto_email, row, 1)
        row += 1

        # Dirección
        grid.addWidget(StyledLabel("Dirección:", bold=True), row, 0)
        self.input_direccion = QTextEdit()
        self.input_direccion.setPlaceholderText("Dirección completa del proveedor")
        self.input_direccion.setMinimumHeight(60)
        self.input_direccion.setStyleSheet(input_style)
        grid.addWidget(self.input_direccion, row, 1)
        row += 1

        # Días de Crédito
        grid.addWidget(StyledLabel("Días Crédito:", bold=True), row, 0)
        self.input_dias_credito = QLineEdit()
        self.input_dias_credito.setPlaceholderText("0")
        self.input_dias_credito.setMaxLength(3)
        self.input_dias_credito.setMinimumHeight(40)
        self.input_dias_credito.setStyleSheet(input_style)
        # Validador para números enteros 0-365
        validator = QIntValidator(0, 365, self.input_dias_credito)
        self.input_dias_credito.setValidator(validator)
        grid.addWidget(self.input_dias_credito, row, 1)
        row += 1

        # Límite de Crédito
        grid.addWidget(StyledLabel("Límite Crédito:", bold=True), row, 0)
        self.input_limite_credito = TouchMoneyInput(
            minimum=0.0,
            maximum=999999.99,
            decimals=2,
            default_value=0.0
        )
        grid.addWidget(self.input_limite_credito, row, 1)
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

    def cargar_datos(self, proveedor):
        """Cargar datos en el formulario"""
        self.input_codigo.setText(proveedor['codigo'])
        self.input_razon_social.setText(proveedor['razon_social'])
        self.input_nombre_comercial.setText(proveedor['nombre_comercial'] or "")
        self.input_rfc.setText(proveedor['rfc'] or "")
        self.input_contacto_nombre.setText(proveedor['contacto_nombre'] or "")
        self.input_contacto_telefono.setText(proveedor['contacto_telefono'] or "")
        self.input_contacto_email.setText(proveedor['contacto_email'] or "")
        self.input_direccion.setText(proveedor['direccion'] or "")
        self.input_dias_credito.setText(str(proveedor['dias_credito'] or 0))
        self.input_limite_credito.setValue(proveedor['limite_credito'] or 0.0)

    def validar_formulario(self):
        """Validar datos del formulario"""
        if not self.input_codigo.text().strip():
            show_warning_dialog(self, "Validación", "El código es obligatorio")
            return False

        if not self.input_razon_social.text().strip():
            show_warning_dialog(self, "Validación", "La razón social es obligatoria")
            return False

        # Validar RFC si se proporciona
        rfc = self.input_rfc.text().strip()
        if rfc and len(rfc) not in [12, 13]:
            show_warning_dialog(self, "Validación", "El RFC debe tener 12 o 13 caracteres")
            return False

        return True

    def guardar(self):
        """Guardar datos del proveedor"""
        if not self.validar_formulario():
            return

        try:
            # Preparar datos
            datos = {
                'codigo': self.input_codigo.text().strip(),
                'razon_social': self.input_razon_social.text().strip(),
                'nombre_comercial': self.input_nombre_comercial.text().strip() or None,
                'rfc': self.input_rfc.text().strip() or None,
                'contacto_nombre': self.input_contacto_nombre.text().strip() or None,
                'contacto_telefono': self.input_contacto_telefono.text().strip() or None,
                'contacto_email': self.input_contacto_email.text().strip() or None,
                'direccion': self.input_direccion.toPlainText().strip() or None,
                'dias_credito': int(self.input_dias_credito.text() or 0),
                'limite_credito': float(self.input_limite_credito.value()),
            }

            if self.proveedor_data:
                # Actualizar
                sql = """
                    UPDATE ca_proveedores 
                    SET codigo = %s, razon_social = %s, nombre_comercial = %s, rfc = %s,
                        contacto_nombre = %s, contacto_telefono = %s, contacto_email = %s,
                        direccion = %s, dias_credito = %s, limite_credito = %s
                    WHERE id_proveedor = %s
                """
                params = (
                    datos['codigo'], datos['razon_social'], datos['nombre_comercial'], datos['rfc'],
                    datos['contacto_nombre'], datos['contacto_telefono'], datos['contacto_email'],
                    datos['direccion'], datos['dias_credito'], datos['limite_credito'],
                    self.proveedor_data['id_proveedor']
                )
                success = self.pg_manager.execute(sql, params)
                if not success:
                    raise Exception("Error al actualizar proveedor")
                mensaje = "Proveedor actualizado correctamente"
            else:
                # Insertar - agregar campos requeridos para nueva inserción
                datos['saldo_actual'] = 0.0
                datos['activo'] = True
                sql = """
                    INSERT INTO ca_proveedores 
                    (codigo, razon_social, nombre_comercial, rfc, contacto_nombre, contacto_telefono, 
                     contacto_email, direccion, dias_credito, limite_credito, saldo_actual, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_proveedor
                """
                params = (
                    datos['codigo'], datos['razon_social'], datos['nombre_comercial'], datos['rfc'],
                    datos['contacto_nombre'], datos['contacto_telefono'], datos['contacto_email'],
                    datos['direccion'], datos['dias_credito'], datos['limite_credito'],
                    datos['saldo_actual'], datos['activo']
                )
                result = self.pg_manager.execute_with_returning(sql, params)
                if result is None:
                    raise Exception("Error al insertar proveedor")
                mensaje = "Proveedor registrado correctamente"

            show_success_dialog(self, "Éxito", mensaje)

            # Aceptar el diálogo
            self.accept()

        except Exception as e:
            logging.error(f"Error guardando proveedor: {e}")
            show_error_dialog(self, "Error", f"No se pudo guardar: {e}")


class ProveedoresWindow(QWidget):
    """Widget con grid de proveedores"""

    cerrar_solicitado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data

        self.setup_ui()
        self.cargar_proveedores()

    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        # Tabla de proveedores
        self.tabla_proveedores = QTableWidget()
        self.tabla_proveedores.setColumnCount(7)
        self.tabla_proveedores.setHorizontalHeaderLabels([
            "ID", "Código", "Razón Social", "Contacto", "Teléfono", "Email", "Estado"
        ])

        # Configurar tabla
        self.tabla_proveedores.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_proveedores.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_proveedores.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_proveedores.horizontalHeader().setStretchLastSection(True)
        self.tabla_proveedores.verticalHeader().setVisible(False)

        # Ajustar columnas
        header = self.tabla_proveedores.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Razón Social
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Contacto
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Estado

        # Aplicar estilos a la tabla
        self.tabla_proveedores.setStyleSheet(f"""
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

        layout.addWidget(self.tabla_proveedores)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        btn_agregar = TileButton("Agregar Proveedor", "fa5s.user-plus", WindowsPhoneTheme.TILE_GREEN)
        btn_agregar.clicked.connect(self.agregar_proveedor)

        btn_editar = TileButton("Editar", "fa5s.edit", WindowsPhoneTheme.TILE_BLUE)
        btn_editar.clicked.connect(self.editar_proveedor)

        btn_desactivar = TileButton("Dar de Baja", "fa5s.user-times", WindowsPhoneTheme.TILE_ORANGE)
        btn_desactivar.clicked.connect(self.desactivar_proveedor)

        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)

        buttons_layout.addWidget(btn_agregar)
        buttons_layout.addWidget(btn_editar)
        buttons_layout.addWidget(btn_desactivar)
        buttons_layout.addWidget(btn_volver)

        layout.addLayout(buttons_layout)

    def cargar_proveedores(self):
        """Cargar lista de proveedores"""
        try:
            sql = """
                SELECT id_proveedor, codigo, razon_social, nombre_comercial, 
                       contacto_nombre, contacto_telefono, contacto_email, activo
                FROM ca_proveedores
                ORDER BY razon_social
            """
            proveedores = self.pg_manager.query(sql)
            self.tabla_proveedores.setRowCount(0)

            for proveedor in proveedores:
                row = self.tabla_proveedores.rowCount()
                self.tabla_proveedores.insertRow(row)

                # ID
                id_item = QTableWidgetItem(str(proveedor['id_proveedor']))
                self.tabla_proveedores.setItem(row, 0, id_item)

                # Código
                self.tabla_proveedores.setItem(row, 1, QTableWidgetItem(proveedor['codigo']))

                # Razón Social (usar nombre comercial si existe, sino razón social)
                nombre_mostrar = proveedor['nombre_comercial'] or proveedor['razon_social']
                self.tabla_proveedores.setItem(row, 2, QTableWidgetItem(nombre_mostrar))

                # Contacto
                contacto = proveedor['contacto_nombre'] if proveedor['contacto_nombre'] else "N/A"
                self.tabla_proveedores.setItem(row, 3, QTableWidgetItem(contacto))

                # Teléfono
                telefono = proveedor['contacto_telefono'] if proveedor['contacto_telefono'] else "N/A"
                self.tabla_proveedores.setItem(row, 4, QTableWidgetItem(telefono))

                # Email
                email = proveedor['contacto_email'] if proveedor['contacto_email'] else "N/A"
                self.tabla_proveedores.setItem(row, 5, QTableWidgetItem(email))

                # Estado
                estado = "Activo" if proveedor['activo'] else "Inactivo"
                estado_item = QTableWidgetItem(estado)
                if not proveedor['activo']:
                    estado_item.setForeground(Qt.red)
                self.tabla_proveedores.setItem(row, 6, estado_item)

        except Exception as e:
            logging.error(f"Error cargando proveedores: {e}")
            show_error_dialog(self, "Error", f"No se pudo cargar los proveedores: {e}")

    def agregar_proveedor(self):
        """Abrir formulario para agregar proveedor"""
        dialog = FormularioProveedorDialog(self.pg_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_proveedores()

    def editar_proveedor(self):
        """Abrir formulario para editar proveedor seleccionado"""
        selected = self.tabla_proveedores.selectedItems()
        if not selected:
            show_warning_dialog(self, "Selección", "Debe seleccionar un proveedor para editar")
            return

        row = selected[0].row()
        id_proveedor = int(self.tabla_proveedores.item(row, 0).text())

        try:
            sql = "SELECT * FROM ca_proveedores WHERE id_proveedor = %s"
            result = self.pg_manager.query(sql, (id_proveedor,))
            proveedor = result[0] if result else None
            if proveedor:
                dialog = FormularioProveedorDialog(
                    self.pg_manager,
                    proveedor_data=dict(proveedor),
                    parent=self
                )
                if dialog.exec() == QDialog.Accepted:
                    self.cargar_proveedores()

        except Exception as e:
            logging.error(f"Error cargando datos de proveedor: {e}")
            show_error_dialog(self, "Error", f"No se pudo cargar los datos: {e}")

    def desactivar_proveedor(self):
        """Dar de baja al proveedor seleccionado"""
        selected = self.tabla_proveedores.selectedItems()
        if not selected:
            show_warning_dialog(self, "Selección", "Debe seleccionar un proveedor para dar de baja")
            return

        row = selected[0].row()
        id_proveedor = int(self.tabla_proveedores.item(row, 0).text())
        nombre_proveedor = self.tabla_proveedores.item(row, 2).text()

        if show_confirmation_dialog(
            self,
            "Confirmar Baja",
            f"¿Desea dar de baja a {nombre_proveedor}?",
            detail="Esta acción marcará al proveedor como inactivo.",
            confirm_text="Sí, dar de baja",
            cancel_text="Cancelar"
        ):
            try:
                sql = "UPDATE ca_proveedores SET activo = %s WHERE id_proveedor = %s"
                success = self.pg_manager.execute(sql, (False, id_proveedor))
                if not success:
                    raise Exception("Error al desactivar proveedor")

                show_success_dialog(self, "Éxito", "Proveedor dado de baja correctamente")

                self.cargar_proveedores()

            except Exception as e:
                logging.error(f"Error dando de baja proveedor: {e}")
                show_error_dialog(self, "Error", f"No se pudo dar de baja: {e}")