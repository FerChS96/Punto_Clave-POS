"""
Ventana de Cuentas por Cobrar para HTF POS
Muestra el listado de cuentas por cobrar con filtros y opciones de gestión
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QSizePolicy, QFrame,
    QComboBox, QDateEdit, QLabel, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate, QThread, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, timedelta
import logging

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    CompactNavButton,
    create_page_layout,
    ContentPanel,
    StyledLabel,
    SearchBar,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog,
    aplicar_estilo_fecha
)


class CuentasCobrarLoaderThread(QThread):
    """Hilo para cargar cuentas por cobrar de forma asíncrona"""

    cuentas_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, pg_manager, filtros=None):
        super().__init__()
        self.pg_manager = pg_manager
        self.filtros = filtros or {}
        self._is_running = True
        self.setTerminationEnabled(True)

    def run(self):
        """Cargar cuentas por cobrar desde la base de datos"""
        try:
            if not self._is_running:
                logging.info("Thread cancelado antes de iniciar")
                return

            logging.info("Cargando cuentas por cobrar...")
            rows = self.pg_manager.obtener_cuentas_por_cobrar(filtros=self.filtros)

            if self._is_running:
                logging.info(f"✅ Thread obtuvo {len(rows)} registros")
                self.cuentas_loaded.emit(rows)
            else:
                logging.info("Thread cancelado antes de emitir datos")

        except Exception as e:
            if self._is_running:
                logging.error(f"Error en thread de cuentas por cobrar: {e}")
                self.error_occurred.emit(str(e))
            else:
                logging.info(f"Error en thread cancelado: {e}")

    def stop(self):
        """Detener el thread de forma segura"""
        logging.info("🛑 Señal de parada enviada al thread")
        self._is_running = False


class CuentasPorCobrarWindow(QWidget):
    """Widget para gestionar cuentas por cobrar"""

    cerrar_solicitado = Signal()
    cuenta_seleccionada = Signal(dict)  # Emitir datos de la cuenta seleccionada

    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.cuentas_data = []
        self.cuentas_filtradas = []
        self.loader_thread = None
        self.pagina_actual = 0  # Para paginación
        self.items_por_pagina = 50
        self._is_visible = True

        self.setup_ui()
        self.cargar_cuentas()

    def hideEvent(self, event):
        """Evento cuando el widget se oculta"""
        self._is_visible = False
        self.detener_carga()
        super().hideEvent(event)

    def showEvent(self, event):
        """Evento cuando el widget se muestra nuevamente"""
        self._is_visible = True
        super().showEvent(event)
    
    def detener_carga(self):
        """Detener cualquier carga en progreso - Llamado cuando se cambia de ventana"""
        try:
            if self.loader_thread and self.loader_thread.isRunning():
                logging.info("🛑 Deteniendo carga de cuentas por cobrar (ventana oculta)")
                self.loader_thread.stop()
                self.loader_thread.quit()
                if not self.loader_thread.wait(500):
                    self.loader_thread.terminate()
                    self.loader_thread.wait(500)
        except Exception as e:
            logging.error(f"Error al detener carga: {e}")

    def setup_ui(self):
        """Configurar interfaz de cuentas por cobrar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("")
        content.setLayout(content_layout)
        
        # Panel de filtros
        filters_panel = self.create_filters_panel()
        content_layout.addWidget(filters_panel)
        
        # Panel para la tabla
        table_panel = self.create_table_panel()
        content_layout.addWidget(table_panel)
        
        # Panel de información y botones (incluye paginación integrada)
        info_buttons_panel = self.create_info_buttons_panel()
        content_layout.addWidget(info_buttons_panel)
        
        layout.addWidget(content)
    
    def create_filters_panel(self):
        """Crear el panel de filtros"""
        filters_panel = ContentPanel()
        filters_layout = QVBoxLayout(filters_panel)
        
        # Primera fila de filtros
        filters_row1 = QHBoxLayout()
        filters_row1.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Buscador
        self.search_bar = SearchBar("Buscar por cliente, número de cuenta...")
        self.search_bar.connect_search(self.aplicar_filtros)
        filters_row1.addWidget(self.search_bar, stretch=3)
        
        # Filtro por estado
        estado_container = self.create_estado_filter()
        filters_row1.addWidget(estado_container, stretch=1)
        
        filters_layout.addLayout(filters_row1)
        
        # Segunda fila - Rango de fechas
        filters_row2 = self.create_fecha_filters()
        filters_layout.addLayout(filters_row2)
        
        return filters_panel
    
    def create_estado_filter(self):
        """Crear el filtro por estado"""
        estado_container = QWidget()
        estado_layout = QVBoxLayout(estado_container)
        estado_layout.setContentsMargins(0, 0, 0, 0)
        estado_layout.setSpacing(4)
        
        estado_label = StyledLabel("Estado:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        estado_layout.addWidget(estado_label)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Activa", "Pagada", "Vencida", "Cancelada"])
        self.combo_estado.setMinimumHeight(40)
        self.combo_estado.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        estado_layout.addWidget(self.combo_estado)
        
        return estado_container
    
    def create_fecha_filters(self):
        """Crear los filtros de fecha"""
        filters_row2 = QHBoxLayout()
        filters_row2.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Fecha inicio
        fecha_inicio_container = QWidget()
        fecha_inicio_layout = QVBoxLayout(fecha_inicio_container)
        fecha_inicio_layout.setContentsMargins(0, 0, 0, 0)
        fecha_inicio_layout.setSpacing(4)
        
        fecha_inicio_label = StyledLabel("Desde:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        fecha_inicio_layout.addWidget(fecha_inicio_label)
        
        self.date_desde = QDateEdit()
        self.date_desde.setDate(QDate.currentDate().addMonths(-1))
        self.date_desde.setCalendarPopup(True)
        aplicar_estilo_fecha(self.date_desde)
        self.date_desde.setMinimumHeight(40)
        self.date_desde.dateChanged.connect(self.aplicar_filtros)
        fecha_inicio_layout.addWidget(self.date_desde)
        
        filters_row2.addWidget(fecha_inicio_container, stretch=1)
        
        # Fecha fin
        fecha_fin_container = QWidget()
        fecha_fin_layout = QVBoxLayout(fecha_fin_container)
        fecha_fin_layout.setContentsMargins(0, 0, 0, 0)
        fecha_fin_layout.setSpacing(4)
        
        fecha_fin_label = StyledLabel("Hasta:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        fecha_fin_layout.addWidget(fecha_fin_label)
        
        self.date_hasta = QDateEdit()
        self.date_hasta.setDate(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        aplicar_estilo_fecha(self.date_hasta)
        self.date_hasta.setMinimumHeight(40)
        self.date_hasta.dateChanged.connect(self.aplicar_filtros)
        fecha_fin_layout.addWidget(self.date_hasta)
        
        filters_row2.addWidget(fecha_fin_container, stretch=1)
        
        # Checkbox pendientes
        self.chk_pendientes = QCheckBox("Solo pendientes")
        self.chk_pendientes.setChecked(True)
        self.chk_pendientes.stateChanged.connect(self.aplicar_filtros)
        self.chk_pendientes.setMinimumHeight(40)
        filters_row2.addWidget(self.chk_pendientes, alignment=Qt.AlignBottom)
        
        return filters_row2
    
    def create_table_panel(self):
        """Crear el panel con la tabla de cuentas"""
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla de cuentas
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Número Cuenta", "Cliente", "Total", "Saldo", "Fecha Vencimiento",
            "Estado", "Días Vencidos", "Último Pago"
        ])
        
        # Configurar header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        # Estilo de la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Conectar señales
        self.table.itemSelectionChanged.connect(self.on_seleccion_cambiada)
        
        table_layout.addWidget(self.table)
        return table_panel
    
    def create_info_buttons_panel(self):
        """Crear el panel de información y botones con paginación integrada"""
        info_buttons_panel = ContentPanel()
        info_buttons_layout = QHBoxLayout(info_buttons_panel)
        info_buttons_layout.setSpacing(8)
        
        # Etiqueta de información (con paginación integrada)
        self.info_label = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        info_buttons_layout.addWidget(self.info_label, stretch=1)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumWidth(1)
        info_buttons_layout.addWidget(separator)
        
        # Botones de paginación COMPACTOS
        self.btn_pagina_anterior = CompactNavButton(
            "Anterior", 
            "fa5s.chevron-left",
            WindowsPhoneTheme.TILE_BLUE,
            icon_position="left"
        )
        self.btn_pagina_anterior.setToolTip("Página anterior")
        self.btn_pagina_anterior.clicked.connect(self.pagina_anterior)
        info_buttons_layout.addWidget(self.btn_pagina_anterior)
        
        self.btn_proxima_pagina = CompactNavButton(
            "Siguiente",
            "fa5s.chevron-right",
            WindowsPhoneTheme.TILE_BLUE,
            icon_position="right"
        )
        self.btn_proxima_pagina.setToolTip("Página siguiente")
        self.btn_proxima_pagina.clicked.connect(self.proxima_pagina)
        info_buttons_layout.addWidget(self.btn_proxima_pagina)
        
        # Separador visual
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setMaximumWidth(1)
        info_buttons_layout.addWidget(separator2)
        
        # Botones de acción principales
        btn_ver_detalles = TileButton("Ver Detalles", "fa5s.eye", WindowsPhoneTheme.TILE_BLUE)
        btn_ver_detalles.clicked.connect(self.ver_detalles_cuenta)
        btn_ver_detalles.setMaximumWidth(150)
        info_buttons_layout.addWidget(btn_ver_detalles)
        
        btn_registrar_pago = TileButton("Registrar Pago", "fa5s.credit-card", WindowsPhoneTheme.TILE_GREEN)
        btn_registrar_pago.clicked.connect(self.registrar_pago)
        btn_registrar_pago.setMaximumWidth(180)
        info_buttons_layout.addWidget(btn_registrar_pago)
        
        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        btn_volver.setMaximumWidth(120)
        info_buttons_layout.addWidget(btn_volver)
        
        return info_buttons_panel

    def on_seleccion_cambiada(self):
        """Manejar cambios en la selección de la tabla"""
        pass  # Los botones ahora están siempre habilitados
    
    def cargar_cuentas(self):
        """Cargar cuentas por cobrar"""
        self.detener_carga()

        # Limpiar tabla y mostrar indicador de carga en info label
        self.table.setRowCount(0)
        self.info_label.setText("Cargando cuentas por cobrar...")

        # Crear y iniciar thread
        filtros = self.obtener_filtros()
        self.loader_thread = CuentasCobrarLoaderThread(self.pg_manager, filtros)
        self.loader_thread.cuentas_loaded.connect(self.on_cuentas_cargadas)
        self.loader_thread.error_occurred.connect(self.on_error_carga)
        self.loader_thread.start()

    def obtener_filtros(self):
        """Obtener filtros actuales"""
        filtros = {}

        # Texto de búsqueda
        search_text = self.search_bar.text().strip()
        if search_text:
            filtros['busqueda'] = search_text

        # Estado
        estado = self.combo_estado.currentText()
        if estado != "Todos":
            filtros['estado'] = estado.lower()

        # Fechas
        filtros['fecha_desde'] = self.date_desde.date().toPython()
        filtros['fecha_hasta'] = self.date_hasta.date().toPython()

        # Solo pendientes
        if self.chk_pendientes.isChecked():
            filtros['solo_pendientes'] = True

        return filtros

    def aplicar_filtros(self):
        """Aplicar filtros a los datos cargados"""
        if not self.cuentas_data:
            return

        filtros = self.obtener_filtros()
        self.cuentas_filtradas = self.filtrar_cuentas(self.cuentas_data, filtros)
        self.pagina_actual = 0  # Resetear paginación al filtrar
        self.actualizar_tabla()

    def filtrar_cuentas(self, cuentas, filtros):
        """Filtrar cuentas según criterios"""
        filtradas = cuentas.copy()

        # Filtrar por búsqueda general
        if 'busqueda' in filtros:
            busqueda = filtros['busqueda'].lower()
            filtradas = [
                c for c in filtradas 
                if busqueda in c.get('cliente', '').lower() or 
                   busqueda in c.get('numero_cuenta', '').lower()
            ]

        # Filtrar por estado
        if 'estado' in filtros:
            estado_filter = filtros['estado']
            filtradas = [c for c in filtradas if c.get('estado') == estado_filter]

        # Filtrar por fechas
        if 'fecha_desde' in filtros:
            fecha_desde = filtros['fecha_desde']
            filtradas = [c for c in filtradas if c.get('fecha_vencimiento') and c.get('fecha_vencimiento') >= fecha_desde]

        if 'fecha_hasta' in filtros:
            fecha_hasta = filtros['fecha_hasta']
            filtradas = [c for c in filtradas if c.get('fecha_vencimiento') and c.get('fecha_vencimiento') <= fecha_hasta]

        # Solo pendientes
        if filtros.get('solo_pendientes'):
            filtradas = [c for c in filtradas if c.get('estado') in ['activa', 'vencida'] and c.get('saldo', 0) > 0]

        return filtradas

    def on_cuentas_cargadas(self, cuentas):
        """Manejar cuentas cargadas"""
        self.cuentas_data = cuentas
        self.pagina_actual = 0
        self.aplicar_filtros()
        self.actualizar_info_label()

    def on_error_carga(self, error_msg):
        """Manejar error en carga"""
        logging.error(f"Error al cargar cuentas por cobrar: {error_msg}")
        show_error_dialog(self, "Error de Carga", f"No se pudieron cargar las cuentas por cobrar:\n{error_msg}")
        self.actualizar_info_label()

    def actualizar_tabla(self):
        """Actualizar la tabla con datos filtrados y paginados"""
        self.table.setRowCount(0)
        
        # Calcular rango de paginación
        total_items = len(self.cuentas_filtradas)
        inicio = self.pagina_actual * self.items_por_pagina
        fin = min(inicio + self.items_por_pagina, total_items)
        
        # Obtener items de la página actual
        items_pagina = self.cuentas_filtradas[inicio:fin]

        for cuenta in items_pagina:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Número de cuenta
            numero_item = QTableWidgetItem(cuenta.get('numero_cuenta', ''))
            numero_item.setData(Qt.UserRole, cuenta)  # Guardar datos completos
            self.table.setItem(row, 0, numero_item)

            # Cliente
            self.table.setItem(row, 1, QTableWidgetItem(cuenta.get('cliente', '')))

            # Total
            total_item = QTableWidgetItem(f"${cuenta.get('total', 0):,.2f}")
            total_item.setData(Qt.TextAlignmentRole, Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, total_item)

            # Saldo
            saldo = cuenta.get('saldo', 0)
            saldo_item = QTableWidgetItem(f"${saldo:,.2f}")
            saldo_item.setData(Qt.TextAlignmentRole, Qt.AlignRight | Qt.AlignVCenter)
            if saldo > 0:
                saldo_item.setForeground(Qt.red)
            self.table.setItem(row, 3, saldo_item)

            # Fecha vencimiento
            fecha_venc = cuenta.get('fecha_vencimiento')
            if fecha_venc:
                fecha_str = fecha_venc.strftime('%d/%m/%Y')
                fecha_item = QTableWidgetItem(fecha_str)
                # Colorear si está vencida
                if fecha_venc < datetime.now().date() and saldo > 0:
                    fecha_item.setForeground(Qt.red)
            else:
                fecha_item = QTableWidgetItem('')
            self.table.setItem(row, 4, fecha_item)

            # Estado
            estado = cuenta.get('estado', '').title()
            estado_item = QTableWidgetItem(estado)
            if estado.lower() == 'vencida':
                estado_item.setForeground(Qt.red)
            elif estado.lower() == 'pagada':
                estado_item.setForeground(Qt.green)
            self.table.setItem(row, 5, estado_item)

            # Días vencidos
            dias_vencidos = cuenta.get('dias_vencidos', 0)
            dias_item = QTableWidgetItem(str(dias_vencidos) if dias_vencidos > 0 else '')
            if dias_vencidos > 0:
                dias_item.setForeground(Qt.red)
            self.table.setItem(row, 6, dias_item)

            # Último pago
            ultimo_pago = cuenta.get('ultimo_pago')
            if ultimo_pago:
                pago_str = ultimo_pago.strftime('%d/%m/%Y')
            else:
                pago_str = 'Sin pagos'
            self.table.setItem(row, 7, QTableWidgetItem(pago_str))
        
        # Actualizar info label con paginación
        self.actualizar_info_label()
    
    def actualizar_info_label(self):
        """Actualizar etiqueta de información con datos de paginación"""
        total_items = len(self.cuentas_filtradas)
        total_pages = (total_items + self.items_por_pagina - 1) // self.items_por_pagina if total_items > 0 else 0
        
        inicio = self.pagina_actual * self.items_por_pagina + 1
        fin = min((self.pagina_actual + 1) * self.items_por_pagina, total_items)
        
        if total_items == 0:
            self.info_label.setText("No se encontraron cuentas por cobrar")
        else:
            self.info_label.setText(
                f"Mostrando {inicio}-{fin} de {total_items} cuentas | Página {self.pagina_actual + 1} de {total_pages}"
            )
        
        # Habilitar/deshabilitar botones de paginación
        self.btn_pagina_anterior.setEnabled(self.pagina_actual > 0)
        self.btn_proxima_pagina.setEnabled(fin < total_items)
    
    def pagina_anterior(self):
        """Ir a la página anterior"""
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.actualizar_tabla()
    
    def proxima_pagina(self):
        """Ir a la página siguiente"""
        total_items = len(self.cuentas_filtradas)
        max_pagina = (total_items - 1) // self.items_por_pagina
        if self.pagina_actual < max_pagina:
            self.pagina_actual += 1
            self.actualizar_tabla()

    def on_seleccion_cambiada(self):
        """Manejar cambio de selección"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                cuenta_data = item.data(Qt.UserRole)
                self.cuenta_seleccionada.emit(cuenta_data)

    def ver_detalles_cuenta(self):
        """Ver detalles de la cuenta seleccionada"""
        current_row = self.table.currentRow()
        if current_row < 0:
            show_warning_dialog(self, "Selección Requerida", "Por favor selecciona una cuenta para ver sus detalles.")
            return

        item = self.table.item(current_row, 0)
        cuenta_data = item.data(Qt.UserRole)

        # Mostrar detalles (por ahora un diálogo simple)
        detalles = f"""
        Número de Cuenta: {cuenta_data.get('numero_cuenta')}
        Cliente: {cuenta_data.get('cliente')}
        Total: ${cuenta_data.get('total', 0):,.2f}
        Saldo: ${cuenta_data.get('saldo', 0):,.2f}
        Estado: {cuenta_data.get('estado', '').title()}
        Fecha Vencimiento: {cuenta_data.get('fecha_vencimiento').strftime('%d/%m/%Y') if cuenta_data.get('fecha_vencimiento') else 'N/A'}
        """

        show_info_dialog(self, "Detalles de Cuenta por Cobrar", detalles)

    def registrar_pago(self):
        """Registrar un pago para la cuenta seleccionada"""
        current_row = self.table.currentRow()
        if current_row < 0:
            show_warning_dialog(self, "Selección Requerida", "Por favor selecciona una cuenta para registrar un pago.")
            return

        # Por ahora mostrar mensaje
        show_info_dialog(self, "Funcionalidad Pendiente", "La funcionalidad de registro de pagos estará disponible próximamente.")

    def ver_historial_pagos(self):
        """Ver historial de pagos de la cuenta seleccionada"""
        current_row = self.table.currentRow()
        if current_row < 0:
            show_warning_dialog(self, "Selección Requerida", "Por favor selecciona una cuenta para ver su historial de pagos.")
            return

        # Por ahora mostrar mensaje
        show_info_dialog(self, "Funcionalidad Pendiente", "La funcionalidad de historial de pagos estará disponible próximamente.")

    def volver(self):
        """Volver a la pantalla anterior"""
        self.cerrar_solicitado.emit()