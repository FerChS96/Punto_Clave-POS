"""
Ventana de Historial de Turnos de Caja para HTF POS
Usando componentes reutilizables del sistema de diseño
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QSizePolicy, QFrame,
    QComboBox, QDateEdit, QLabel
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Importar componentes del sistema de diseño
from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    SectionTitle,
    ContentPanel,
    StyledLabel,
    SearchBar,
    show_info_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_success_dialog,
    aplicar_estilo_fecha,
    create_page_layout
)


class HistorialTurnosWindow(QWidget):
    """Widget para ver el historial completo de turnos de caja"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.turnos_data = []
        self.turnos_filtrados = []
        
        # Timer para detectar entrada del escáner
        self.scanner_timer = QTimer()
        self.scanner_timer.setSingleShot(True)
        self.scanner_timer.setInterval(300)  # 300ms después de que deje de escribir
        self.scanner_timer.timeout.connect(self.aplicar_filtros)
        
        self.setup_ui()
        self.cargar_turnos()
    
    def setup_ui(self):
        """Configurar interfaz del historial"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Contenido
        content = QWidget()
        content_layout = create_page_layout("")
        content.setLayout(content_layout)
        
        # Buscador
        self.search_bar = SearchBar("Buscar por usuario...")
        self.search_bar.connect_search(self.on_search_changed)
        content_layout.addWidget(self.search_bar)
        
        # Panel de filtros
        filters_panel = self.create_filters_panel()
        content_layout.addWidget(filters_panel)
        
        # Panel para la tabla
        table_panel = self.create_table_panel()
        content_layout.addWidget(table_panel)
        
        # Panel de información y botones
        info_buttons_panel = self.create_info_buttons_panel()
        content_layout.addLayout(info_buttons_panel)
        
        layout.addWidget(content)
    
    def create_filters_panel(self):
        """Crear el panel de filtros"""
        filters_panel = ContentPanel()
        filters_layout = QHBoxLayout(filters_panel)
        filters_layout.setSpacing(WindowsPhoneTheme.MARGIN_MEDIUM)
        
        # Fecha desde
        desde_container = QWidget()
        desde_layout = QVBoxLayout(desde_container)
        desde_layout.setContentsMargins(0, 0, 0, 0)
        desde_layout.setSpacing(4)
        desde_label = StyledLabel("Desde:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        desde_layout.addWidget(desde_label)
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setMinimumHeight(40)
        self.fecha_inicio.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.fecha_inicio.dateChanged.connect(self.aplicar_filtros)
        aplicar_estilo_fecha(self.fecha_inicio)
        desde_layout.addWidget(self.fecha_inicio)
        filters_layout.addWidget(desde_container, stretch=1)
        
        # Fecha hasta
        hasta_container = QWidget()
        hasta_layout = QVBoxLayout(hasta_container)
        hasta_layout.setContentsMargins(0, 0, 0, 0)
        hasta_layout.setSpacing(4)
        hasta_label = StyledLabel("Hasta:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        hasta_layout.addWidget(hasta_label)
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setMinimumHeight(40)
        self.fecha_fin.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.fecha_fin.dateChanged.connect(self.aplicar_filtros)
        aplicar_estilo_fecha(self.fecha_fin)
        hasta_layout.addWidget(self.fecha_fin)
        filters_layout.addWidget(hasta_container, stretch=1)
        
        # Filtro por estado
        estado_container = QWidget()
        estado_layout = QVBoxLayout(estado_container)
        estado_layout.setContentsMargins(0, 0, 0, 0)
        estado_layout.setSpacing(4)
        estado_label = StyledLabel("Estado:", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        estado_layout.addWidget(estado_label)
        self.estado_combo = QComboBox()
        self.estado_combo.setMinimumHeight(40)
        self.estado_combo.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL))
        self.estado_combo.addItems(["Todos", "Abiertos", "Cerrados"])
        self.estado_combo.setCurrentIndex(0)
        self.estado_combo.currentTextChanged.connect(self.aplicar_filtros)
        estado_layout.addWidget(self.estado_combo)
        filters_layout.addWidget(estado_container, stretch=1)
        
        # Botón limpiar filtros
        btn_limpiar_container = QWidget()
        btn_limpiar_layout = QVBoxLayout(btn_limpiar_container)
        btn_limpiar_layout.setContentsMargins(0, 0, 0, 0)
        btn_limpiar_layout.setSpacing(4)
        limpiar_spacer = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        btn_limpiar_layout.addWidget(limpiar_spacer)
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setMinimumHeight(40)
        btn_limpiar.setMinimumWidth(100)
        btn_limpiar.setObjectName("tileButton")
        btn_limpiar.setProperty("tileColor", WindowsPhoneTheme.TILE_ORANGE)
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        btn_limpiar_layout.addWidget(btn_limpiar)
        filters_layout.addWidget(btn_limpiar_container)
        
        return filters_panel
    
    def create_table_panel(self):
        """Crear panel con la tabla de turnos"""
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        
        # Tabla
        self.tabla_turnos = QTableWidget()
        self.tabla_turnos.setColumnCount(10)
        self.tabla_turnos.setHorizontalHeaderLabels([
            "ID", "Usuario", "Apertura", "Cierre", "Monto Inicial",
            "Ventas Efectivo", "Monto Esperado", "Monto Real", "Diferencia", "Estado"
        ])
        
        # Configurar tabla
        self.tabla_turnos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_turnos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_turnos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_turnos.verticalHeader().setVisible(False)
        
        # Ajustar columnas
        header = self.tabla_turnos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Usuario
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Apertura
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cierre
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Monto Inicial
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Ventas
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Esperado
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Real
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Diferencia
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Estado
        
        # Aplicar estilos a la tabla (consistente con personal_window)
        self.tabla_turnos.setStyleSheet(f"""
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
        
        # Conectar doble clic para ver detalles
        self.tabla_turnos.itemDoubleClicked.connect(self.mostrar_detalles_turno)
        
        table_layout.addWidget(self.tabla_turnos)
        
        return table_panel
    
    def create_info_buttons_panel(self):
        """Crear panel de información y botones"""
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        # Label de total de registros
        self.label_total = StyledLabel("Total de turnos: 0", bold=True)
        panel_layout.addWidget(self.label_total)
        
        panel_layout.addStretch()
        
        # Botón refrescar
        btn_refrescar = TileButton("Actualizar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_refrescar.setMaximumHeight(120)
        btn_refrescar.clicked.connect(self.cargar_turnos)
        panel_layout.addWidget(btn_refrescar)
        
        # Botón volver
        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.setMaximumHeight(120)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        panel_layout.addWidget(btn_volver)
        
        return panel_layout
    
    def cargar_turnos(self):
        """Cargar turnos desde la base de datos"""
        try:
            # Obtener turnos usando PostgreSQL
            turnos = self.pg_manager.query("""
                SELECT 
                    tc.id_turno,
                    tc.numero_turno,
                    tc.fecha_apertura,
                    tc.fecha_cierre,
                    tc.monto_inicial,
                    tc.total_efectivo,
                    tc.monto_esperado_efectivo,
                    tc.monto_real_efectivo as monto_real_cierre,
                    tc.diferencia_efectivo as diferencia,
                    tc.cerrado,
                    u.nombre_completo as nombre_usuario,
                    u.nombre_usuario as username
                FROM turnos_caja tc
                LEFT JOIN usuarios u ON tc.id_usuario = u.id_usuario
                ORDER BY tc.fecha_apertura DESC
            """) or []
            
            # Procesar datos
            self.turnos_data = []
            for turno in turnos:
                # Convertir tuple/dict to dict
                if isinstance(turno, tuple):
                    turno_dict = {
                        'id_turno': turno[0],
                        'numero_turno': turno[1],
                        'fecha_apertura': turno[2],
                        'fecha_cierre': turno[3],
                        'monto_inicial': turno[4],
                        'total_efectivo': turno[5],
                        'monto_esperado_efectivo': turno[6],
                        'monto_real_cierre': turno[7],
                        'diferencia': turno[8],
                        'cerrado': turno[9],
                        'nombre_usuario': turno[10] or 'N/A',
                        'username': turno[11]
                    }
                else:
                    turno_dict = turno
                    turno_dict['nombre_usuario'] = turno.get('nombre_usuario') or 'N/A'
                
                self.turnos_data.append(turno_dict)
            
            self.aplicar_filtros()
                
        except Exception as e:
            logging.error(f"Error cargando turnos: {e}")
            show_error_dialog(self, "Error", f"No se pudieron cargar los turnos: {e}")
    
    def on_search_changed(self, text):
        """Reiniciar timer cuando cambia el texto de búsqueda"""
        self.scanner_timer.start()
    
    def aplicar_filtros(self):
        """Aplicar filtros a los datos de turnos"""
        # Obtener valores de filtros
        texto_busqueda = self.search_bar.text().strip().lower()
        estado_filtro = self.estado_combo.currentText()
        fecha_inicio = self.fecha_inicio.date().toPython()
        fecha_fin = self.fecha_fin.date().toPython()
        
        # Filtrar datos
        self.turnos_filtrados = []
        for turno in self.turnos_data:
            # Filtro de búsqueda por usuario
            if texto_busqueda and texto_busqueda not in turno['nombre_usuario'].lower():
                continue
            
            # Filtro de estado
            if estado_filtro == "Abiertos" and turno['cerrado']:
                continue
            elif estado_filtro == "Cerrados" and not turno['cerrado']:
                continue
            
            # Filtro de fechas
            if turno['fecha_apertura']:
                try:
                    # Convertir string a datetime si es necesario
                    if isinstance(turno['fecha_apertura'], str):
                        fecha_apertura = datetime.fromisoformat(turno['fecha_apertura'].replace('Z', '+00:00')).date()
                    else:
                        fecha_apertura = turno['fecha_apertura'].date()
                    
                    if fecha_apertura < fecha_inicio or fecha_apertura > fecha_fin:
                        continue
                except Exception as e:
                    logging.error(f"Error procesando fecha de turno: {e}")
                    continue
            
            self.turnos_filtrados.append(turno)
        
        # Actualizar tabla
        self.actualizar_tabla()
    
    def actualizar_tabla(self):
        """Actualizar contenido de la tabla"""
        self.tabla_turnos.setRowCount(len(self.turnos_filtrados))
        
        for row_idx, turno in enumerate(self.turnos_filtrados):
            # ID
            self.tabla_turnos.setItem(row_idx, 0, QTableWidgetItem(str(turno['id_turno'])))
            
            # Usuario
            self.tabla_turnos.setItem(row_idx, 1, QTableWidgetItem(turno['nombre_usuario']))
            
            # Fecha apertura
            if turno['fecha_apertura']:
                try:
                    if isinstance(turno['fecha_apertura'], str):
                        fecha_obj = datetime.fromisoformat(turno['fecha_apertura'].replace('Z', '+00:00'))
                        fecha_apertura = fecha_obj.strftime("%d/%m/%Y %H:%M")
                    else:
                        fecha_apertura = turno['fecha_apertura'].strftime("%d/%m/%Y %H:%M")
                except:
                    fecha_apertura = str(turno['fecha_apertura'])
            else:
                fecha_apertura = ""
            self.tabla_turnos.setItem(row_idx, 2, QTableWidgetItem(fecha_apertura))
            
            # Fecha cierre
            if turno['fecha_cierre']:
                try:
                    if isinstance(turno['fecha_cierre'], str):
                        fecha_obj = datetime.fromisoformat(turno['fecha_cierre'].replace('Z', '+00:00'))
                        fecha_cierre = fecha_obj.strftime("%d/%m/%Y %H:%M")
                    else:
                        fecha_cierre = turno['fecha_cierre'].strftime("%d/%m/%Y %H:%M")
                except:
                    fecha_cierre = str(turno['fecha_cierre'])
            else:
                fecha_cierre = "ABIERTO"
            item_cierre = QTableWidgetItem(fecha_cierre)
            if not turno['cerrado']:
                item_cierre.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
            self.tabla_turnos.setItem(row_idx, 3, item_cierre)
            
            # Monto inicial
            monto_inicial = f"${float(turno['monto_inicial']):.2f}" if turno['monto_inicial'] is not None else "$0.00"
            self.tabla_turnos.setItem(row_idx, 4, QTableWidgetItem(monto_inicial))
            
            # Ventas efectivo
            ventas = f"${float(turno['total_efectivo']):.2f}" if turno['total_efectivo'] is not None else "$0.00"
            self.tabla_turnos.setItem(row_idx, 5, QTableWidgetItem(ventas))
            
            # Monto esperado
            esperado = f"${float(turno['monto_esperado_efectivo']):.2f}" if turno['monto_esperado_efectivo'] is not None else "$0.00"
            self.tabla_turnos.setItem(row_idx, 6, QTableWidgetItem(esperado))
            
            # Monto real
            if turno['monto_real_cierre'] is not None:
                real = f"${float(turno['monto_real_cierre']):.2f}"
            else:
                real = "-"
            self.tabla_turnos.setItem(row_idx, 7, QTableWidgetItem(real))
            
            # Diferencia
            if turno['diferencia'] is not None:
                diferencia_valor = float(turno['diferencia'])
                diferencia = f"${diferencia_valor:.2f}"
                item_diferencia = QTableWidgetItem(diferencia)
                
                # Colorear según si hay faltante o sobrante
                if diferencia_valor < 0:
                    item_diferencia.setForeground(Qt.red)
                    item_diferencia.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
                elif diferencia_valor > 0:
                    item_diferencia.setForeground(Qt.darkGreen)
                
                self.tabla_turnos.setItem(row_idx, 8, item_diferencia)
            else:
                self.tabla_turnos.setItem(row_idx, 8, QTableWidgetItem("-"))
            
            # Estado
            estado = "CERRADO" if turno['cerrado'] else "ABIERTO"
            item_estado = QTableWidgetItem(estado)
            if not turno['cerrado']:
                item_estado.setForeground(Qt.darkGreen)
                item_estado.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, WindowsPhoneTheme.FONT_SIZE_NORMAL, QFont.Bold))
            self.tabla_turnos.setItem(row_idx, 9, item_estado)
        
        # Actualizar label de total
        self.label_total.setText(f"Total de turnos: {len(self.turnos_filtrados)}")
    
    def mostrar_detalles_turno(self, item):
        """Mostrar detalles completos del turno seleccionado"""
        row = item.row()
        if row < 0 or row >= len(self.turnos_filtrados):
            return
        
        turno = self.turnos_filtrados[row]
        
        # Construir mensaje de detalles
        detalles = f"TURNO #{turno['id_turno']}\n"
        detalles += f"Usuario: {turno['nombre_usuario']}\n\n"
        
        detalles += "--- APERTURA ---\n"
        # Convertir fecha_apertura si es string
        if turno['fecha_apertura']:
            try:
                if isinstance(turno['fecha_apertura'], str):
                    fecha_obj = datetime.fromisoformat(turno['fecha_apertura'].replace('Z', '+00:00'))
                    fecha_apertura_str = fecha_obj.strftime('%d/%m/%Y %H:%M')
                else:
                    fecha_apertura_str = turno['fecha_apertura'].strftime('%d/%m/%Y %H:%M')
            except:
                fecha_apertura_str = str(turno['fecha_apertura'])
        else:
            fecha_apertura_str = "N/A"
        detalles += f"Fecha: {fecha_apertura_str}\n"
        detalles += f"Monto inicial: ${float(turno['monto_inicial']):.2f}\n\n"
        
        if turno['cerrado']:
            detalles += "--- CIERRE ---\n"
            # Convertir fecha_cierre si es string
            if turno['fecha_cierre']:
                try:
                    if isinstance(turno['fecha_cierre'], str):
                        fecha_obj = datetime.fromisoformat(turno['fecha_cierre'].replace('Z', '+00:00'))
                        fecha_cierre_str = fecha_obj.strftime('%d/%m/%Y %H:%M')
                    else:
                        fecha_cierre_str = turno['fecha_cierre'].strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_cierre_str = str(turno['fecha_cierre'])
            else:
                fecha_cierre_str = "N/A"
            detalles += f"Fecha: {fecha_cierre_str}\n"
            detalles += f"Ventas en efectivo: ${float(turno['total_efectivo']):.2f}\n"
            detalles += f"Monto esperado: ${float(turno['monto_esperado_efectivo']):.2f}\n"
            detalles += f"Monto real: ${float(turno['monto_real_cierre']):.2f}\n"
            
            diferencia = float(turno['diferencia'])
            estado_dif = "SOBRANTE" if diferencia > 0 else "FALTANTE" if diferencia < 0 else "EXACTO"
            detalles += f"Diferencia: ${abs(diferencia):.2f} ({estado_dif})\n\n"
        else:
            detalles += "--- ESTADO ---\n"
            detalles += "TURNO ABIERTO\n\n"
        
        # Mostrar notas si existen
        if turno.get('notas_apertura'):
            detalles += "--- NOTAS ---\n"
            detalles += turno['notas_apertura']
        
        show_info_dialog(self, f"Detalles del Turno #{turno['id_turno']}", detalles)
    
    def limpiar_filtros(self):
        """Limpiar todos los filtros"""
        self.search_bar.clear()
        self.estado_combo.setCurrentIndex(0)
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_fin.setDate(QDate.currentDate())
        self.aplicar_filtros()
