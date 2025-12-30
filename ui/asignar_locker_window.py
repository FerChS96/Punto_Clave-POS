"""
Ventana de Asignación de Lockers
Grid de asignaciones con formulario para asignar/liberar lockers
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QDialog, QHeaderView, QPushButton, QLabel, QDateEdit,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
import logging
from datetime import datetime, timedelta

from ui.components import (
    WindowsPhoneTheme,
    TileButton,
    SectionTitle,
    StyledLabel,
    SearchBar,
    show_success_dialog,
    show_warning_dialog,
    show_error_dialog,
    show_confirmation_dialog
)





# ============================================================
# FORMULARIO DE ASIGNACIÓN (DIÁLOGO)
# ============================================================

class AsignarLockerDialog(QDialog):
    """Diálogo para asignar locker a miembro"""
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.setWindowTitle("Asignar Locker")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)
        
        self.miembro_seleccionado = None
        self.locker_seleccionado = None
        
        self.setup_ui()
        self.cargar_lockers_disponibles()
    
    def setup_ui(self):
        """Configurar interfaz del formulario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title = SectionTitle("ASIGNAR LOCKER")
        layout.addWidget(title)
        
        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)
        
        input_style = f"""
            QLineEdit, QComboBox, QDateEdit {{
                padding: 8px;
                border: 2px solid #e5e7eb;
                border-radius: 4px;
                font-family: {WindowsPhoneTheme.FONT_FAMILY};
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
                background-color: white;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border-color: {WindowsPhoneTheme.TILE_BLUE};
            }}
            QLineEdit:read-only {{
                background-color: #f3f4f6;
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
        
        row = 0
        
        # Buscar miembro
        grid.addWidget(StyledLabel("Miembro *:", bold=True), row, 0)
        self.input_miembro = QLineEdit()
        self.input_miembro.setPlaceholderText("Código QR o nombre del miembro")
        self.input_miembro.setMinimumHeight(40)
        self.input_miembro.setStyleSheet(input_style)
        self.input_miembro.returnPressed.connect(self.buscar_miembro)
        grid.addWidget(self.input_miembro, row, 1)
        row += 1
        
        # Info miembro
        self.label_info_miembro = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        self.label_info_miembro.setStyleSheet(f"color: {WindowsPhoneTheme.TILE_GREEN};")
        self.label_info_miembro.setWordWrap(True)
        grid.addWidget(self.label_info_miembro, row, 1)
        row += 1
        
        # Locker disponible
        grid.addWidget(StyledLabel("Locker *:", bold=True), row, 0)
        self.combo_locker = QComboBox()
        self.combo_locker.setMinimumHeight(40)
        self.combo_locker.setStyleSheet(input_style)
        grid.addWidget(self.combo_locker, row, 1)
        row += 1
        
        # Fecha inicio
        grid.addWidget(StyledLabel("Fecha Inicio *:", bold=True), row, 0)
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setMinimumHeight(40)
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_inicio.setStyleSheet(input_style)
        grid.addWidget(self.date_inicio, row, 1)
        row += 1
        
        # Fecha fin
        grid.addWidget(StyledLabel("Fecha Fin *:", bold=True), row, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        # Por defecto 30 días
        fecha_fin = QDate.currentDate().addDays(30)
        self.date_fin.setDate(fecha_fin)
        self.date_fin.setMinimumHeight(40)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setStyleSheet(input_style)
        grid.addWidget(self.date_fin, row, 1)
        row += 1
        
        layout.addLayout(grid)
        layout.addStretch()
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_asignar = TileButton("Asignar", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_asignar.setMaximumHeight(120)
        btn_asignar.clicked.connect(self.asignar_locker)
        
        btn_cancelar = TileButton("Cancelar", "fa5s.times", WindowsPhoneTheme.TILE_RED)
        btn_cancelar.setMaximumHeight(120)
        btn_cancelar.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_asignar)
        buttons_layout.addWidget(btn_cancelar)
        
        layout.addLayout(buttons_layout)
    
    def cargar_lockers_disponibles(self):
        """Cargar lockers disponibles (no asignados)"""
        try:
            # Obtener todos los lockers activos
            response = self.pg_manager.client.table('lockers').select('id_locker, numero, ubicacion, tipo').eq('activo', True).execute()
            all_lockers = response.data if response.data else []
            
            # Obtener lockers ya asignados
            response_asignados = self.pg_manager.client.table('asignaciones_activas').select('id_locker').eq('activa', True).execute()
            locker_ids_asignados = {item['id_locker'] for item in (response_asignados.data or [])}
            
            # Filtrar lockers disponibles
            lockers = [l for l in all_lockers if l['id_locker'] not in locker_ids_asignados]
            
            self.combo_locker.clear()
            for locker in lockers:
                texto = f"{locker['numero']} - {locker['ubicacion'] or 'Sin ubicación'}"
                self.combo_locker.addItem(texto, locker['id_locker'])
            
            if len(lockers) == 0:
                self.combo_locker.addItem("No hay lockers disponibles", None)
                    
        except Exception as e:
            logging.error(f"Error cargando lockers disponibles: {e}")
            show_error_dialog(self, "Error", f"No se pudieron cargar los lockers:\n{str(e)}")
    
    def buscar_miembro(self):
        """Buscar miembro por código o nombre"""
        texto = self.input_miembro.text().strip()
        
        if not texto:
            show_warning_dialog(self, "Validación", "Ingrese un código QR o nombre para buscar")
            return
        
        try:
            # Buscar por código QR
            response = self.pg_manager.client.table('miembros').select('id_miembro, nombres, apellido_paterno, apellido_materno, codigo_qr, telefono, activo').eq('codigo_qr', texto).execute()
            miembro = response.data[0] if response.data else None
            
            # Si no encuentra por código QR, buscar por nombre
            if not miembro:
                response_nombres = self.pg_manager.client.table('miembros').select('id_miembro, nombres, apellido_paterno, apellido_materno, codigo_qr, telefono, activo').execute()
                for m in (response_nombres.data or []):
                    nombre_completo = f"{m.get('nombres', '')} {m.get('apellido_paterno', '')} {m.get('apellido_materno', '')}".lower()
                    if texto.lower() in nombre_completo:
                        miembro = m
                        break
                
                if not miembro:
                    show_warning_dialog(self, "No encontrado", f"No se encontró ningún miembro con: {texto}")
                    self.label_info_miembro.setText("")
                    self.miembro_seleccionado = None
                    return
                
                if not miembro['activo']:
                    show_warning_dialog(
                        self,
                        "Miembro inactivo",
                        f"El miembro '{miembro['nombre_completo']}' no está activo"
                    )
                    self.label_info_miembro.setText("")
                    self.miembro_seleccionado = None
                    return
                
                # Verificar si ya tiene locker
                response_locker = self.pg_manager.client.table('asignaciones_activas').select('id_locker').eq('id_miembro', miembro['id_miembro']).eq('activa', True).execute()
                locker_actual = None
                if response_locker.data:
                    # Obtener número del locker
                    locker_id = response_locker.data[0]['id_locker']
                    response_locker_num = self.pg_manager.client.table('lockers').select('numero').eq('id_locker', locker_id).single().execute()
                    locker_actual = response_locker_num.data if response_locker_num.data else None
                if locker_actual:
                    show_warning_dialog(
                        self,
                        "Ya tiene locker",
                        f"El miembro ya tiene asignado el locker: {locker_actual['numero']}"
                    )
                    self.label_info_miembro.setText("")
                    self.miembro_seleccionado = None
                    return
                
                self.miembro_seleccionado = miembro
                self.label_info_miembro.setText(
                    f"✓ Miembro: {miembro['nombre_completo']} | Tel: {miembro['telefono'] or 'N/A'}"
                )
                
        except Exception as e:
            logging.error(f"Error buscando miembro: {e}")
            show_error_dialog(self, "Error", f"Error al buscar miembro:\n{str(e)}")
    
    def validar(self):
        """Validar datos del formulario"""
        if not self.miembro_seleccionado:
            show_warning_dialog(self, "Validación", "Debe buscar y seleccionar un miembro")
            return False
        
        if self.combo_locker.currentData() is None:
            show_warning_dialog(self, "Validación", "No hay lockers disponibles para asignar")
            return False
        
        fecha_inicio = self.date_inicio.date().toPython()
        fecha_fin = self.date_fin.date().toPython()
        
        if fecha_fin <= fecha_inicio:
            show_warning_dialog(self, "Validación", "La fecha de fin debe ser posterior a la fecha de inicio")
            return False
        
        return True
    
    def asignar_locker(self):
        """Asignar locker al miembro"""
        if not self.validar():
            return
        
        try:
            id_miembro = self.miembro_seleccionado['id_miembro']
            id_locker = self.combo_locker.currentData()
            fecha_inicio = self.date_inicio.date().toPython()
            fecha_fin = self.date_fin.date().toPython()
            id_usuario = self.user_data['id_usuario']
            
            # Buscar producto digital de tipo locker
            response = self.pg_manager.client.table('ca_productos_digitales').select('id_producto_digital').eq('tipo', 'locker').eq('activo', True).limit(1).execute()
            producto = response.data[0] if response.data else None
            
            if not producto:
                show_warning_dialog(
                    self,
                    "Error de configuración",
                    "No hay productos digitales de tipo 'locker' configurados en el sistema"
                )
                return
            
            id_producto_digital = producto['id_producto_digital']
            
            # Crear asignación
            asignacion_data = {
                'id_miembro': id_miembro,
                'id_producto_digital': id_producto_digital,
                'fecha_inicio': str(fecha_inicio),
                'fecha_fin': str(fecha_fin),
                'id_locker': id_locker,
                'activa': True
            }
            response = self.pg_manager.client.table('asignaciones_activas').insert(asignacion_data).execute()
            id_asignacion = response.data[0]['id_asignacion'] if response.data else None
            
            # Registrar entrada
            entrada_data = {
                'id_miembro': id_miembro,
                'tipo_entrada': 'normal',
                'id_usuario': id_usuario
            }
            self.pg_manager.client.table('registro_entradas').insert(entrada_data).execute()
            
            locker_numero = self.combo_locker.currentText().split(' - ')[0]
            show_success_dialog(
                self,
                "Éxito",
                f"Locker {locker_numero} asignado correctamente"
            )
            
            logging.info(f"Locker asignado: {id_asignacion} - Miembro: {id_miembro}, Locker: {id_locker}")
            self.accept()
                
        except Exception as e:
            logging.error(f"Error asignando locker: {e}")
            show_error_dialog(self, "Error", f"No se pudo asignar el locker:\n{str(e)}")


# ============================================================
# VENTANA PRINCIPAL DE ASIGNACIONES
# ============================================================

class AsignacionesLockersWindow(QWidget):
    """Ventana para ver y administrar asignaciones de lockers"""
    
    cerrar_solicitado = Signal()
    
    def __init__(self, pg_manager, user_data, parent=None):
        super().__init__(parent)
        self.pg_manager = pg_manager
        self.user_data = user_data
        self.asignaciones_data = []
        
        self.setup_ui()
        self.cargar_asignaciones()
    
    def setup_ui(self):
        """Configurar interfaz de la ventana"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM,
                                 WindowsPhoneTheme.MARGIN_MEDIUM)
        layout.setSpacing(WindowsPhoneTheme.MARGIN_SMALL)
        
        # Título
        title = SectionTitle("ASIGNACIONES DE LOCKERS")
        layout.addWidget(title)
        
        # Buscador
        self.search_bar = SearchBar("Buscar por miembro, locker o código QR...")
        self.search_bar.connect_search(self.filtrar_asignaciones)
        layout.addWidget(self.search_bar)
        
        # Panel de acciones
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_nuevo = TileButton("Asignar", "fa5s.plus", WindowsPhoneTheme.TILE_GREEN)
        btn_nuevo.clicked.connect(self.abrir_formulario_asignar)
        
        btn_refrescar = TileButton("Refrescar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_refrescar.clicked.connect(self.cargar_asignaciones)
        
        panel_layout.addWidget(btn_nuevo)
        panel_layout.addWidget(btn_refrescar)
        panel_layout.addStretch()
        
        self.info_total = StyledLabel("Total: 0 asignaciones", bold=True, size=WindowsPhoneTheme.FONT_SIZE_SUBTITLE)
        self.info_total.setStyleSheet(f"color: {WindowsPhoneTheme.PRIMARY_BLUE};")
        panel_layout.addWidget(self.info_total, alignment=Qt.AlignVCenter)
        
        layout.addLayout(panel_layout)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Locker", "Miembro", "Código QR", "Fecha Inicio", "Fecha Vencimiento", 
            "Días Restantes", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 100)
        
        # Aplicar estilos a la tabla
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
        
        layout.addWidget(self.table)
        
        # Botón Volver
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        buttons_layout.addStretch()
        
        btn_volver = TileButton("Volver", "fa5s.arrow-left", WindowsPhoneTheme.TILE_RED)
        btn_volver.clicked.connect(self.cerrar_solicitado.emit)
        
        buttons_layout.addWidget(btn_volver)
        
        layout.addLayout(buttons_layout)
    
    def cargar_asignaciones(self):
        """Cargar asignaciones activas de lockers"""
        try:
            # Obtener asignaciones de lockers
            response = self.pg_manager.client.table('asignaciones_activas').select('id_asignacion, id_miembro, id_locker, fecha_inicio, fecha_fin, activa').order('activa', desc=True).order('fecha_inicio', desc=True).execute()
            
            # Filtrar solo aquellas con locker asignado (id_locker no nulo)
            asignaciones_raw = [a for a in (response.data if response.data else []) if a.get('id_locker') is not None]
            self.asignaciones_data = []
            
            for asig in asignaciones_raw:
                # Obtener datos del miembro
                response_miembro = self.pg_manager.client.table('miembros').select('nombres, apellido_paterno, apellido_materno, codigo_qr').eq('id_miembro', asig['id_miembro']).single().execute()
                miembro = response_miembro.data if response_miembro.data else {}
                
                # Obtener datos del locker
                response_locker = self.pg_manager.client.table('lockers').select('numero, ubicacion').eq('id_locker', asig['id_locker']).single().execute()
                locker = response_locker.data if response_locker.data else {}
                
                # Construir registro completo
                asig_completa = {
                    'id_asignacion': asig['id_asignacion'],
                    'id_miembro': asig['id_miembro'],
                    'id_locker': asig['id_locker'],
                    'fecha_inicio': asig['fecha_inicio'],
                    'fecha_fin': asig['fecha_fin'],
                    'activa': asig['activa'],
                    'nombre_completo': f"{miembro.get('nombres', '')} {miembro.get('apellido_paterno', '')} {miembro.get('apellido_materno', '')}".strip(),
                    'codigo_qr': miembro.get('codigo_qr'),
                    'locker_numero': locker.get('numero'),
                    'locker_ubicacion': locker.get('ubicacion')
                }
                self.asignaciones_data.append(asig_completa)
                self.mostrar_asignaciones(self.asignaciones_data)
                
        except Exception as e:
            logging.error(f"Error cargando asignaciones: {e}")
            show_error_dialog(self, "Error", f"No se pudieron cargar las asignaciones:\n{str(e)}")
    
    def mostrar_asignaciones(self, asignaciones):
        """Mostrar asignaciones en la tabla"""
        self.table.setRowCount(0)
        
        hoy = datetime.now().date()
        
        for i, asig in enumerate(asignaciones):
            self.table.insertRow(i)
            
            # Locker
            locker_texto = f"{asig['locker_numero']} ({asig['locker_ubicacion'] or 'N/A'})"
            self.table.setItem(i, 0, QTableWidgetItem(locker_texto))
            
            # Miembro
            self.table.setItem(i, 1, QTableWidgetItem(asig['nombre_completo']))
            
            # Código QR
            self.table.setItem(i, 2, QTableWidgetItem(asig['codigo_qr'] or "N/A"))
            
            # Fecha inicio
            fecha_inicio_str = asig['fecha_inicio'].strftime('%d/%m/%Y')
            self.table.setItem(i, 3, QTableWidgetItem(fecha_inicio_str))
            
            # Fecha vencimiento
            fecha_fin_str = asig['fecha_fin'].strftime('%d/%m/%Y')
            self.table.setItem(i, 4, QTableWidgetItem(fecha_fin_str))
            
            # Días restantes
            if asig['activa']:
                dias_restantes = (asig['fecha_fin'] - hoy).days
                item_dias = QTableWidgetItem(str(dias_restantes))
                
                if dias_restantes < 0:
                    item_dias.setForeground(Qt.red)
                elif dias_restantes <= 7:
                    item_dias.setForeground(Qt.darkYellow)
                else:
                    item_dias.setForeground(Qt.darkGreen)
                    
                self.table.setItem(i, 5, item_dias)
            else:
                self.table.setItem(i, 5, QTableWidgetItem("N/A"))
            
            # Estado
            estado = "Activa" if asig['activa'] else "Liberada"
            item_estado = QTableWidgetItem(estado)
            if asig['activa']:
                item_estado.setForeground(Qt.darkGreen)
            else:
                item_estado.setForeground(Qt.gray)
            self.table.setItem(i, 6, item_estado)
            
            # Botones de acción
            if asig['activa']:
                btn_liberar = QPushButton("Liberar")
                btn_liberar.setToolTip("Liberar locker")
                btn_liberar.setMinimumHeight(35)
                btn_liberar.setMaximumHeight(35)
                btn_liberar.setFont(QFont(WindowsPhoneTheme.FONT_FAMILY, 9, QFont.Bold))
                btn_liberar.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {WindowsPhoneTheme.TILE_RED};
                        color: white;
                        border: none;
                        padding: 5px 12px;
                        border-radius: 3px;
                    }}
                    QPushButton:hover {{
                        background-color: {WindowsPhoneTheme.TILE_ORANGE};
                    }}
                """)
                btn_liberar.clicked.connect(lambda checked, a=asig: self.liberar_locker(a))
                self.table.setCellWidget(i, 7, btn_liberar)
            else:
                self.table.setItem(i, 7, QTableWidgetItem(""))
        
        # Actualizar info
        total = len(asignaciones)
        activas = sum(1 for a in asignaciones if a['activa'])
        self.info_total.setText(f"Total: {total} asignaciones ({activas} activas)")
    
    def filtrar_asignaciones(self):
        """Filtrar asignaciones por búsqueda"""
        texto = self.search_bar.get_text().lower()
        
        if not texto:
            self.mostrar_asignaciones(self.asignaciones_data)
            return
        
        filtradas = [
            a for a in self.asignaciones_data
            if texto in a['nombre_completo'].lower()
            or texto in a['locker_numero'].lower()
            or texto in (a['codigo_qr'] or "").lower()
        ]
        
        self.mostrar_asignaciones(filtradas)
    
    def abrir_formulario_asignar(self):
        """Abrir formulario para asignar locker"""
        dialog = AsignarLockerDialog(self.pg_manager, self.user_data, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_asignaciones()
    
    def liberar_locker(self, asignacion):
        """Liberar un locker asignado"""
        if not show_confirmation_dialog(
            self,
            "Confirmar liberación",
            f"¿Desea liberar el locker '{asignacion['locker_numero']}' de {asignacion['nombre_completo']}?",
            "El locker quedará disponible para asignar a otro miembro."
        ):
            return
        
        try:
            # Actualizar estado de asignación
            self.pg_manager.client.table('asignaciones_activas').update({'activa': False}).eq('id_asignacion', asignacion['id_asignacion']).execute()
            
            show_success_dialog(
                self,
                "Éxito",
                f"Locker '{asignacion['locker_numero']}' liberado correctamente"
            )
            
            self.cargar_asignaciones()
            logging.info(f"Locker liberado: {asignacion['id_asignacion']}")
                
        except Exception as e:
            logging.error(f"Error liberando locker: {e}")
            show_error_dialog(self, "Error", f"No se pudo liberar el locker:\n{str(e)}")
