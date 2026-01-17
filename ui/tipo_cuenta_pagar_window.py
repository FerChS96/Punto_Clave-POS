"""
Ventana de Administración de Tipos de Cuenta por Pagar
Lista de tipos de cuenta por pagar con botones de acción y formulario en diálogo
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QCheckBox, QDialog, QHeaderView, QComboBox,
    QAbstractItemView, QPushButton
)
from PySide6.QtCore import Qt, Signal
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


class FormularioTipoCuentaPagarDialog(QDialog):
    """Diálogo con formulario para agregar/editar tipo de cuenta por pagar"""

    def __init__(self, pg_manager, tipo_cuenta_data=None, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.tipo_cuenta_data = tipo_cuenta_data
        self.setWindowTitle("")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.setup_ui()

        # Si hay datos, cargarlos
        if tipo_cuenta_data:
            self.cargar_datos(tipo_cuenta_data)

    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = SectionTitle("DATOS DEL TIPO DE CUENTA POR PAGAR")
        layout.addWidget(title)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)

        row = 0

        # Estilo para inputs
        input_style = f"""
            QLineEdit, QComboBox, QTextEdit {{
                padding: 8px;
                border: 2px solid #e5e7eb;
                border-radius:4px;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
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
        self.input_codigo.setPlaceholderText("Código único del tipo de cuenta")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.setStyleSheet(input_style)
        grid.addWidget(self.input_codigo, row, 1)
        row += 1

        # Nombre
        grid.addWidget(StyledLabel("Nombre:", bold=True), row, 0)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del tipo de cuenta")
        self.input_nombre.setMinimumHeight(40)
        self.input_nombre.setStyleSheet(input_style)
        grid.addWidget(self.input_nombre, row, 1)
        row += 1

        # Descripción
        grid.addWidget(StyledLabel("Descripción:", bold=True), row, 0)
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Descripción detallada")
        self.input_descripcion.setMaximumHeight(80)
        self.input_descripcion.setStyleSheet(input_style)
        grid.addWidget(self.input_descripcion, row, 1)
        row += 1

        # Categoría
        grid.addWidget(StyledLabel("Categoría:", bold=True), row, 0)
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems([
            "compras", "servicios", "gastos", "nomina", "impuestos", "otros"
        ])
        self.combo_categoria.setMinimumHeight(40)
        self.combo_categoria.setStyleSheet(input_style)
        grid.addWidget(self.combo_categoria, row, 1)
        row += 1

        # Requiere Proveedor
        grid.addWidget(StyledLabel("Requiere Proveedor:", bold=True), row, 0)
        self.check_requiere_proveedor = QCheckBox("Sí, requiere proveedor")
        self.check_requiere_proveedor.setChecked(True)
        grid.addWidget(self.check_requiere_proveedor, row, 1)
        row += 1

        # Cuenta Contable
        grid.addWidget(StyledLabel("Cuenta Contable:", bold=True), row, 0)
        self.input_cuenta_contable = QLineEdit()
        self.input_cuenta_contable.setPlaceholderText("Código de cuenta contable (opcional)")
        self.input_cuenta_contable.setMinimumHeight(40)
        self.input_cuenta_contable.setStyleSheet(input_style)
        grid.addWidget(self.input_cuenta_contable, row, 1)
        row += 1

        layout.addLayout(grid)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.clicked.connect(self.reject)

        btn_guardar = TileButton("Guardar", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_tipo_cuenta)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_guardar)

        layout.addLayout(buttons_layout)

    def cargar_datos(self, tipo_cuenta_data):
        """Cargar datos del tipo de cuenta en el formulario"""
        self.input_codigo.setText(tipo_cuenta_data.get('codigo', ''))
        self.input_nombre.setText(tipo_cuenta_data.get('nombre', ''))
        self.input_descripcion.setPlainText(tipo_cuenta_data.get('descripcion', ''))
        self.combo_categoria.setCurrentText(tipo_cuenta_data.get('categoria', 'otros'))
        self.check_requiere_proveedor.setChecked(tipo_cuenta_data.get('requiere_proveedor', True))
        self.input_cuenta_contable.setText(tipo_cuenta_data.get('cuenta_contable', ''))

    def validar_datos(self):
        """Validar datos del formulario"""
        errores = []

        if not self.input_codigo.text().strip():
            errores.append("El código es obligatorio")

        if not self.input_nombre.text().strip():
            errores.append("El nombre es obligatorio")

        return errores

    def guardar_tipo_cuenta(self):
        """Guardar datos del tipo de cuenta"""
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
                'nombre': self.input_nombre.text().strip(),
                'descripcion': self.input_descripcion.toPlainText().strip() or None,
                'categoria': self.combo_categoria.currentText(),
                'requiere_proveedor': self.check_requiere_proveedor.isChecked(),
                'cuenta_contable': self.input_cuenta_contable.text().strip() or None
            }

            if self.tipo_cuenta_data:
                # Actualizar tipo de cuenta existente
                sql = """
                    UPDATE ca_tipo_cuenta_pagar SET
                        codigo = %s, nombre = %s, descripcion = %s, categoria = %s,
                        requiere_proveedor = %s, cuenta_contable = %s
                    WHERE id_tipo_cuenta_pagar = %s
                """
                params = list(datos.values()) + [self.tipo_cuenta_data['id_tipo_cuenta_pagar']]
                success = self.pg_manager.execute(sql, params)
                if not success:
                    raise Exception("Error al actualizar tipo de cuenta")
                show_success_dialog(self, "Éxito", "Tipo de cuenta actualizado correctamente")
            else:
                # Insertar nuevo tipo de cuenta
                sql = """
                    INSERT INTO ca_tipo_cuenta_pagar (
                        codigo, nombre, descripcion, categoria, requiere_proveedor, cuenta_contable
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                success = self.pg_manager.execute(sql, list(datos.values()))
                if not success:
                    raise Exception("Error al crear tipo de cuenta")
                show_success_dialog(self, "Éxito", "Tipo de cuenta creado correctamente")

            self.accept()

        except Exception as e:
            logging.error(f"Error guardando tipo de cuenta: {e}")
            show_error_dialog(self, "Error", f"No se pudo guardar el tipo de cuenta: {e}")


class TipoCuentaPagarWindow(QWidget):
    """Ventana para administrar tipos de cuenta por pagar"""

    cerrar_solicitado = Signal()

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.tipos_cuenta = []

        self.setup_ui()
        self.cargar_tipos_cuenta()

    def setup_ui(self):
        """Configurar interfaz principal"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)

        # Panel de lista de tipos de cuenta
        lista_panel = self._setup_panel_lista()
        layout.addWidget(lista_panel)

        # Botones al pie (todos en una fila)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)

        btn_nuevo = TileButton("Nuevo Tipo", "fa5s.plus", WindowsPhoneTheme.TILE_GREEN)
        btn_nuevo.clicked.connect(self.abrir_formulario_nuevo)
        buttons_layout.addWidget(btn_nuevo)

        btn_refrescar = TileButton("Actualizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_refrescar.clicked.connect(self.cargar_tipos_cuenta)
        buttons_layout.addWidget(btn_refrescar)

        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        buttons_layout.addWidget(btn_volver)

        layout.addLayout(buttons_layout)

    def _setup_panel_lista(self):
        """Panel con la tabla de tipos de cuenta"""
        panel = ContentPanel()
        panel_layout = QVBoxLayout(panel)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Categoría", "Requiere Prov.", "Estado", "Acciones"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        # Configurar headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Categoría
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Requiere Prov.
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Estado
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Acciones

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

    def cargar_tipos_cuenta(self):
        """Cargar tipos de cuenta desde la base de datos"""
        try:
            sql = """
                SELECT id_tipo_cuenta_pagar, codigo, nombre, descripcion,
                       categoria, requiere_proveedor, cuenta_contable, activo
                FROM ca_tipo_cuenta_pagar
                ORDER BY nombre
            """
            self.tipos_cuenta = self.pg_manager.query(sql)
            self.actualizar_tabla()

            logging.info(f"Cargados {len(self.tipos_cuenta)} tipos de cuenta por pagar")

        except Exception as e:
            logging.error(f"Error cargando tipos de cuenta: {e}")
            show_error_dialog(self, "Error", "No se pudieron cargar los tipos de cuenta por pagar")

    def actualizar_tabla(self):
        """Actualizar tabla con los datos de tipos de cuenta"""
        self.table.setRowCount(0)

        for i, tipo_cuenta in enumerate(self.tipos_cuenta):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 60)  # Altura consistente

            # ID
            id_item = QTableWidgetItem(str(tipo_cuenta['id_tipo_cuenta_pagar']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, id_item)

            # Código
            codigo_item = QTableWidgetItem(tipo_cuenta['codigo'])
            self.table.setItem(i, 1, codigo_item)

            # Nombre
            nombre_item = QTableWidgetItem(tipo_cuenta['nombre'])
            self.table.setItem(i, 2, nombre_item)

            # Categoría
            categoria_item = QTableWidgetItem(tipo_cuenta['categoria'].title())
            categoria_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, categoria_item)

            # Requiere Proveedor
            requiere = "Sí" if tipo_cuenta['requiere_proveedor'] else "No"
            requiere_item = QTableWidgetItem(requiere)
            requiere_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, requiere_item)

            # Estado
            estado = "✓ Activo" if tipo_cuenta['activo'] else "✗ Inactivo"
            estado_item = QTableWidgetItem(estado)
            estado_item.setTextAlignment(Qt.AlignCenter)
            if tipo_cuenta['activo']:
                estado_item.setForeground(Qt.darkGreen)
            else:
                estado_item.setForeground(Qt.darkRed)
            self.table.setItem(i, 5, estado_item)

            # Botones de acción con iconos
            acciones_widget = QWidget()
            acciones_widget.setStyleSheet("background: transparent;")
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 5, 5, 5)
            acciones_layout.setSpacing(5)

            # Botón Editar con icono
            btn_editar = QPushButton()
            btn_editar.setIcon(qta.icon('fa5s.edit', color='white'))
            btn_editar.setToolTip("Editar tipo de cuenta")
            btn_editar.setMinimumHeight(30)
            btn_editar.setFixedWidth(40)
            btn_editar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WindowsPhoneTheme.TILE_BLUE};
                    color: white;
                    border: none;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: #1976d2;
                }}
            """)
            btn_editar.clicked.connect(lambda checked, tc=tipo_cuenta: self.editar_tipo_cuenta(tc))
            acciones_layout.addWidget(btn_editar)

            # Botón Eliminar con icono
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(qta.icon('fa5s.trash', color='white'))
            btn_eliminar.setToolTip("Eliminar tipo de cuenta")
            btn_eliminar.setMinimumHeight(30)
            btn_eliminar.setFixedWidth(40)
            btn_eliminar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WindowsPhoneTheme.TILE_RED};
                    color: white;
                    border: none;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: #c62828;
                }}
            """)
            btn_eliminar.clicked.connect(lambda checked, tc=tipo_cuenta: self.eliminar_tipo_cuenta(tc))
            acciones_layout.addWidget(btn_eliminar)

            self.table.setCellWidget(i, 6, acciones_widget)

    def abrir_formulario_nuevo(self):
        """Abrir formulario para crear nuevo tipo de cuenta"""
        dialog = FormularioTipoCuentaPagarDialog(self.pg_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_tipos_cuenta()

    def abrir_formulario_editar(self, row):
        """Abrir formulario para editar tipo de cuenta existente"""
        if row < 0 or row >= len(self.tipos_cuenta):
            return

        tipo_cuenta = self.tipos_cuenta[row]
        dialog = FormularioTipoCuentaPagarDialog(
            self.pg_manager,
            tipo_cuenta_data=dict(tipo_cuenta),
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.cargar_tipos_cuenta()

    def toggle_estado(self, row):
        """Alternar estado activo/inactivo del tipo de cuenta"""
        if row < 0 or row >= len(self.tipos_cuenta):
            return

        tipo_cuenta = self.tipos_cuenta[row]
        nuevo_estado = not tipo_cuenta['activo']

        try:
            sql = "UPDATE ca_tipo_cuenta_pagar SET activo = %s WHERE id_tipo_cuenta_pagar = %s"
            success = self.pg_manager.execute(sql, (nuevo_estado, tipo_cuenta['id_tipo_cuenta_pagar']))

            if success:
                show_success_dialog(
                    self, "Éxito",
                    f"Tipo de cuenta {'activado' if nuevo_estado else 'desactivado'} correctamente"
                )
                self.cargar_tipos_cuenta()
            else:
                raise Exception("Error al actualizar estado")

        except Exception as e:
            logging.error(f"Error cambiando estado: {e}")
            show_error_dialog(self, "Error", f"No se pudo cambiar el estado: {e}")

    def editar_tipo_cuenta(self, tipo_cuenta):
        """Abrir formulario para editar tipo de cuenta"""
        dialog = FormularioTipoCuentaPagarDialog(
            self.pg_manager,
            tipo_cuenta_data=dict(tipo_cuenta),
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.cargar_tipos_cuenta()

    def eliminar_tipo_cuenta(self, tipo_cuenta):
        """Eliminar tipo de cuenta después de confirmación"""
        # Confirmar eliminación
        if not show_confirmation_dialog(
            self,
            "Confirmar eliminación",
            f"¿Desea eliminar el tipo de cuenta '{tipo_cuenta['nombre']}'?",
            "Esta acción no se puede deshacer."
        ):
            return

        try:
            id_tipo_cuenta = tipo_cuenta['id_tipo_cuenta_pagar']

            # Verificar si tiene cuentas por pagar asociadas
            cuentas_response = self.pg_manager.query(
                "SELECT COUNT(*) as count FROM cuentas_por_pagar WHERE id_tipo_cuenta_pagar = %s",
                (id_tipo_cuenta,)
            )

            if cuentas_response and cuentas_response[0]['count'] > 0:
                show_warning_dialog(
                    self,
                    "No se puede eliminar",
                    f"El tipo de cuenta '{tipo_cuenta['nombre']}' tiene {cuentas_response[0]['count']} cuentas por pagar asociadas.",
                    "Primero debe eliminar o reasignar las cuentas por pagar."
                )
                return

            # Eliminar tipo de cuenta
            sql = "DELETE FROM ca_tipo_cuenta_pagar WHERE id_tipo_cuenta_pagar = %s"
            success = self.pg_manager.execute(sql, (id_tipo_cuenta,))

            if success:
                show_success_dialog(
                    self,
                    "Éxito",
                    f"Tipo de cuenta '{tipo_cuenta['nombre']}' eliminado correctamente"
                )
                self.cargar_tipos_cuenta()
                logging.info(f"Tipo de cuenta eliminado: {tipo_cuenta['nombre']}")
            else:
                raise Exception("Error al eliminar")

        except Exception as e:
            logging.error(f"Error eliminando tipo de cuenta: {e}")
            show_error_dialog(self, "Error", f"No se pudo eliminar el tipo de cuenta:\n{str(e)}")