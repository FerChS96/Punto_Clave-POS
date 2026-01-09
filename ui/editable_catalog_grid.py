"""
Componente de Grid Editable para Catálogo de Productos
Permite editar información de productos en una tabla unificada
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QTabWidget, QSizePolicy, QMessageBox, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
import logging

from ui.components import WindowsPhoneTheme, TileButton, StyledLabel, show_info_dialog, show_warning_dialog, show_error_dialog, create_page_layout, ContentPanel, SearchBar


class EditableCatalogGrid(QWidget):
    """Widget con grid editable para catálogo de productos"""
    
    # Enum de unidades de medida
    UNIDADES_MEDIDA = [
        "",  # Opción vacía
        "gramos",
        "kilogramos",
        "mililitros",
        "litros",
        "piezas",
        "onzas",
        "libras",
        "galones",
        "caja",
        "paquete"
    ]
    
    catalogo_actualizado = Signal()
    
    def __init__(self, postgres_manager, parent=None):
        super().__init__(parent)
        self.pg_manager = postgres_manager
        self.productos_varios = []
        self.cambios_pendientes = {}  # {codigo_interno: {campo: valor_nuevo, ...}}
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configurar interfaz del grid editable"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        content = QWidget()
        content_layout = create_page_layout("CATÁLOGO DE PRODUCTOS - EDICIÓN")
        content.setLayout(content_layout)
        
        # Panel de búsqueda
        search_panel = ContentPanel()
        search_layout = QHBoxLayout(search_panel)
        search_layout.setSpacing(10)
        
        search_layout.addWidget(StyledLabel("Buscar:", bold=True))
        self.search_varios = SearchBar("Buscar por código, nombre o descripción...")
        self.search_varios.connect_search(self.filtrar_productos_varios)
        search_layout.addWidget(self.search_varios, stretch=1)
        
        search_layout.addWidget(StyledLabel("Categoría:", bold=True))
        self.combo_categoria_varios = QComboBox()
        self.combo_categoria_varios.setMinimumWidth(150)
        self.combo_categoria_varios.addItem("Todas")
        self.combo_categoria_varios.currentTextChanged.connect(self.filtrar_productos_varios)
        self.combo_categoria_varios.setStyleSheet(f"""
            QComboBox {{
                padding: 6px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
            }}
        """)
        search_layout.addWidget(self.combo_categoria_varios)
        
        search_layout.addWidget(StyledLabel("Estado:", bold=True))
        self.combo_activo_varios = QComboBox()
        self.combo_activo_varios.addItems(["Todos", "Activos", "Inactivos"])
        self.combo_activo_varios.currentTextChanged.connect(self.filtrar_productos_varios)
        self.combo_activo_varios.setStyleSheet(f"""
            QComboBox {{
                padding: 6px;
                border: 2px solid {WindowsPhoneTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: white;
            }}
        """)
        search_layout.addWidget(self.combo_activo_varios)
        
        content_layout.addWidget(search_panel)
        
        # Panel con tabla
        table_panel = ContentPanel()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabla_varios = self.crear_tabla_productos_varios()
        table_layout.addWidget(self.tabla_varios)
        content_layout.addWidget(table_panel)
        
        # Panel de información de cambios
        info_cambios_panel = ContentPanel()
        info_cambios_layout = QHBoxLayout(info_cambios_panel)
        
        self.label_cambios = StyledLabel("", size=WindowsPhoneTheme.FONT_SIZE_SMALL)
        self.label_cambios.setStyleSheet(f"color: {WindowsPhoneTheme.TILE_ORANGE}; font-weight: bold;")
        info_cambios_layout.addWidget(self.label_cambios, stretch=1)
        
        content_layout.addWidget(info_cambios_panel)
        
        # Panel de botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(WindowsPhoneTheme.TILE_SPACING)
        
        btn_guardar = TileButton("Guardar Cambios", "fa5s.save", WindowsPhoneTheme.TILE_GREEN)
        btn_guardar.clicked.connect(self.guardar_cambios)
        botones_layout.addWidget(btn_guardar)
        
        btn_descartar = TileButton("Descartar", "fa5s.undo", WindowsPhoneTheme.TILE_ORANGE)
        btn_descartar.clicked.connect(self.descartar_cambios)
        botones_layout.addWidget(btn_descartar)
        
        btn_recargar = TileButton("Recargar", "fa5s.sync", WindowsPhoneTheme.TILE_BLUE)
        btn_recargar.clicked.connect(self.cargar_datos)
        botones_layout.addWidget(btn_recargar)
        
        content_layout.addLayout(botones_layout)
        
        layout.addWidget(content)
    
    def crear_tabla_productos_varios(self):
        """Crear tabla editable para productos varios"""
        tabla = QTableWidget()
        tabla.setColumnCount(18)
        tabla.setHorizontalHeaderLabels([
            "Código", "Nombre", "Descripción", "Precio Venta", "Precio Mayoreo", "Cant Mayoreo", 
            "Costo Promedio", "Categoría", "Código Barras", "Requiere Refrig", "Es Inventariable", 
            "Permite Sin Stock", "Aplica IEPS", "% IEPS", "Aplica IVA", "% IVA", "Cantidad Medida", 
            "Unidad Medida", "Activo"
        ])
        
        # Configurar header
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)   # Código
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)            # Descripción
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # Precio Venta
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Precio Mayoreo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # Cant Mayoreo
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)   # Costo Promedio
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)   # Categoría
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)   # Código Barras
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)   # Requiere Refrig
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # Es Inventariable
        header.setSectionResizeMode(11, QHeaderView.ResizeToContents)  # Permite Sin Stock
        header.setSectionResizeMode(12, QHeaderView.ResizeToContents)  # Aplica IEPS
        header.setSectionResizeMode(13, QHeaderView.ResizeToContents)  # % IEPS
        header.setSectionResizeMode(14, QHeaderView.ResizeToContents)  # Aplica IVA
        header.setSectionResizeMode(15, QHeaderView.ResizeToContents)  # % IVA
        header.setSectionResizeMode(16, QHeaderView.ResizeToContents)  # Cantidad Medida
        header.setSectionResizeMode(17, QHeaderView.ResizeToContents)  # Unidad Medida
        header.setSectionResizeMode(18, QHeaderView.ResizeToContents)  # Activo
        
        tabla.verticalHeader().setVisible(False)
        tabla.verticalHeader().setDefaultSectionSize(60)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        tabla.setAlternatingRowColors(True)
        tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aplicar estilos
        tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: #e5e7eb;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
            }}
            QTableWidget::item:selected {{
                background-color: {WindowsPhoneTheme.TILE_BLUE};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {WindowsPhoneTheme.BG_LIGHT};
                color: {WindowsPhoneTheme.PRIMARY_BLUE};
                padding: 10px 6px;
                border: none;
                border-bottom: 2px solid {WindowsPhoneTheme.TILE_BLUE};
                font-weight: bold;
                font-family: '{WindowsPhoneTheme.FONT_FAMILY}';
                font-size: {WindowsPhoneTheme.FONT_SIZE_NORMAL}px;
            }}
        """)
        
        tabla.itemChanged.connect(self.on_item_changed)
        
        return tabla
    

    
    def cargar_datos(self):
        """Cargar datos de productos desde la base de datos"""
        try:
            logging.info("Cargando catálogo de productos...")
            
            # Obtener todos los productos
            self.productos_varios = self.pg_manager.obtener_productos_por_categoria()
            self.suplementos = []  # Ya no se usa separadamente
            
            # Actualizar combos de filtros
            self.actualizar_combos_filtros()
            
            # Poblar tabla
            self.poblar_tabla_productos_varios()
            
            self.cambios_pendientes = {}
            self.actualizar_label_cambios()
            
            logging.info(f"Catálogo cargado: {len(self.productos_varios)} productos")
            
        except Exception as e:
            logging.error(f"Error cargando catálogo: {e}")
            show_error_dialog(self, "Error al cargar", "No se pudo cargar el catálogo de productos", detail=str(e))
    
    def actualizar_combos_filtros(self):
        """Actualizar los combos de filtros con valores únicos"""
        # Categorías únicas de productos varios
        categorias = set()
        for producto in self.productos_varios:
            cat = producto.get('categoria')
            if cat:
                categorias.add(cat)
        
        self.combo_categoria_varios.clear()
        self.combo_categoria_varios.addItem("Todas")
        for cat in sorted(categorias):
            self.combo_categoria_varios.addItem(cat)
    
    def poblar_tabla_productos_varios(self):
        """Poblar tabla de productos varios"""
        tabla = self.tabla_varios
        tabla.setRowCount(0)
        
        for row, producto in enumerate(self.productos_varios):
            tabla.insertRow(row)
            
            # Código (no editable)
            item_codigo = QTableWidgetItem(str(producto.get('codigo_interno', '')))
            item_codigo.setFlags(item_codigo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            tabla.setItem(row, 0, item_codigo)
            
            # Nombre (editable)
            tabla.setItem(row, 1, QTableWidgetItem(str(producto.get('nombre', ''))))
            
            # Descripción (editable)
            tabla.setItem(row, 2, QTableWidgetItem(str(producto.get('descripcion', ''))))
            
            # Precio Venta (editable)
            item_precio_venta = QTableWidgetItem(f"{float(producto.get('precio_venta', 0)):.2f}")
            tabla.setItem(row, 3, item_precio_venta)
            
            # Precio Mayoreo (editable)
            precio_mayoreo = producto.get('precio_mayoreo')
            item_precio_mayoreo = QTableWidgetItem(f"{float(precio_mayoreo):.2f}" if precio_mayoreo else "")
            tabla.setItem(row, 4, item_precio_mayoreo)
            
            # Cantidad Mayoreo (editable)
            cantidad_mayoreo = producto.get('cantidad_mayoreo')
            item_cantidad_mayoreo = QTableWidgetItem(str(cantidad_mayoreo) if cantidad_mayoreo else "")
            tabla.setItem(row, 5, item_cantidad_mayoreo)
            
            # Costo Promedio (editable)
            costo_promedio = producto.get('costo_promedio')
            item_costo = QTableWidgetItem(f"{float(costo_promedio):.2f}" if costo_promedio else "")
            tabla.setItem(row, 6, item_costo)
            
            # Categoría (editable)
            tabla.setItem(row, 7, QTableWidgetItem(str(producto.get('categoria', ''))))
            
            # Código Barras (editable)
            tabla.setItem(row, 8, QTableWidgetItem(str(producto.get('codigo_barras', '') or '')))
            
            # Requiere Refrigeración (editable)
            item_refrig = QTableWidgetItem("Sí" if producto.get('requiere_refrigeracion', False) else "No")
            tabla.setItem(row, 9, item_refrig)
            
            # Es Inventariable (editable)
            item_invent = QTableWidgetItem("Sí" if producto.get('es_inventariable', True) else "No")
            tabla.setItem(row, 10, item_invent)
            
            # Permite Venta Sin Stock (editable)
            item_sin_stock = QTableWidgetItem("Sí" if producto.get('permite_venta_sin_stock', False) else "No")
            tabla.setItem(row, 11, item_sin_stock)
            
            # Aplica IEPS (editable)
            item_ieps = QTableWidgetItem("Sí" if producto.get('aplica_ieps', False) else "No")
            tabla.setItem(row, 12, item_ieps)
            
            # % IEPS (editable)
            porcentaje_ieps = producto.get('porcentaje_ieps', 0)
            item_porcentaje_ieps = QTableWidgetItem(f"{float(porcentaje_ieps):.2f}" if porcentaje_ieps else "0.00")
            tabla.setItem(row, 13, item_porcentaje_ieps)
            
            # Aplica IVA (editable)
            item_iva = QTableWidgetItem("Sí" if producto.get('aplica_iva', True) else "No")
            tabla.setItem(row, 14, item_iva)
            
            # % IVA (editable)
            porcentaje_iva = producto.get('porcentaje_iva', 16)
            item_porcentaje_iva = QTableWidgetItem(f"{float(porcentaje_iva):.2f}" if porcentaje_iva else "16.00")
            tabla.setItem(row, 15, item_porcentaje_iva)
            
            # Cantidad Medida (editable)
            cantidad_medida = producto.get('cantidad_medida')
            item_cantidad_medida = QTableWidgetItem(f"{float(cantidad_medida):.2f}" if cantidad_medida else "")
            tabla.setItem(row, 16, item_cantidad_medida)
            
            # Unidad Medida (editable - Combo)
            combo_unidad = QComboBox()
            combo_unidad.addItems(self.UNIDADES_MEDIDA)
            valor_actual = str(producto.get('unidad_medida', '') or '')
            if valor_actual in self.UNIDADES_MEDIDA:
                combo_unidad.setCurrentText(valor_actual)
            combo_unidad.currentTextChanged.connect(lambda text, r=row: self._on_combo_changed(r, 17, text))
            combo_unidad.setStyleSheet("""
                QComboBox {
                    padding: 4px;
                    border: none;
                    background-color: white;
                }
            """)
            tabla.setCellWidget(row, 17, combo_unidad)
            
            # Activo (editable)
            item_activo = QTableWidgetItem("Sí" if producto.get('activo', True) else "No")
            tabla.setItem(row, 18, item_activo)
    

    
    def _on_combo_changed(self, row, col, text):
        """Manejar cambio en un QComboBox de unidad"""
        tabla = self.tabla_varios
        codigo_item = tabla.item(row, 0)
        
        if codigo_item:
            codigo = codigo_item.text()
            
            # Inicializar entrada si no existe
            if codigo not in self.cambios_pendientes:
                self.cambios_pendientes[codigo] = {}
            
            # Determinar el nombre del campo basado en las columnas de productos varios
            campos = ['codigo_interno', 'nombre', 'descripcion', 'marca', 'tipo', 'precio_venta', 'categoria', 'cantidad_medida', 'unidad_medida', 'codigo_barras', 'stock_actual', 'stock_minimo', 'ubicacion', 'fecha_vencimiento', 'notas', 'activo', 'fecha_creacion', 'fecha_actualizacion']
            
            if col < len(campos):
                campo = campos[col]
                
                # Resaltar celda modificada
                widget = tabla.cellWidget(row, col)
                if widget:
                    widget.setStyleSheet(f"""
                        QComboBox {{
                            padding: 4px;
                            border: 2px solid #ff8c00;
                            background-color: #fff3cd;
                        }}
                    """)
                
                self.cambios_pendientes[codigo][campo] = text
                self.actualizar_label_cambios()
    
    def on_item_changed(self, item):
        """Manejar cambio en un item de la tabla"""
        # Obtener código del producto
        tabla = self.tabla_varios
        row = item.row()
        codigo_item = tabla.item(row, 0)
        
        if codigo_item:
            codigo = codigo_item.text()
            col = item.column()
            
            # Lista completa de campos para productos varios (18 columnas)
            campos = [
                'codigo_interno', 'nombre', 'descripcion', 'marca', 'tipo', 'precio_venta', 
                'categoria', 'cantidad_medida', 'unidad_medida', 'codigo_barras', 'stock_actual', 
                'stock_minimo', 'ubicacion', 'fecha_vencimiento', 'notas', 'activo', 
                'fecha_creacion', 'fecha_actualizacion'
            ]
            
            if col < len(campos):
                campo = campos[col]
                
                # No registrar cambios en código
                if campo == 'codigo_interno':
                    return
                
                # Inicializar entrada si no existe
                if codigo not in self.cambios_pendientes:
                    self.cambios_pendientes[codigo] = {}
                
                valor = item.text()
                
                # Resaltar celda modificada
                item.setBackground(QBrush(QColor("#fff3cd")))
                
                self.cambios_pendientes[codigo][campo] = valor
                self.actualizar_label_cambios()
    
    def actualizar_label_cambios(self):
        """Actualizar etiqueta de cambios pendientes"""
        total_cambios = sum(len(v) for v in self.cambios_pendientes.values())
        if total_cambios > 0:
            self.label_cambios.setText(f"[!] {total_cambios} cambios pendientes de guardar")
            self.label_cambios.setStyleSheet("color: #ff8c00; font-weight: bold;")
        else:
            self.label_cambios.setText("")
            self.label_cambios.setStyleSheet("")
    
    def guardar_cambios(self):
        """Guardar cambios en la base de datos"""
        if not self.cambios_pendientes:
            show_info_dialog(self, "Sin cambios", "No hay cambios pendientes para guardar")
            return
        
        try:
            total_guardados = 0
            errores = []
            
            for codigo, cambios in self.cambios_pendientes.items():
                try:
                    # Convertir valores booleanos
                    for campo in ['activo', 'requiere_refrigeracion', 'es_inventariable', 'permite_venta_sin_stock', 'aplica_ieps', 'aplica_iva']:
                        if campo in cambios:
                            cambios[campo] = cambios[campo].lower() in ['sí', 'si', 'true', '1']
                    
                    # Convertir precios y costos a float
                    for campo in ['precio_venta', 'precio_mayoreo', 'costo_promedio', 'porcentaje_ieps', 'porcentaje_iva']:
                        if campo in cambios and cambios[campo]:
                            try:
                                cambios[campo] = float(cambios[campo])
                            except ValueError:
                                cambios[campo] = 0.0
                    
                    # Convertir cantidades a int/float según corresponda
                    if 'cantidad_mayoreo' in cambios and cambios['cantidad_mayoreo']:
                        try:
                            cambios['cantidad_mayoreo'] = int(float(cambios['cantidad_mayoreo']))
                        except ValueError:
                            cambios['cantidad_mayoreo'] = None
                    
                    # Convertir cantidad_medida a float (puede ser None/vacío)
                    if 'cantidad_medida' in cambios:
                        cambios['cantidad_medida'] = float(cambios['cantidad_medida']) if cambios['cantidad_medida'].strip() else None
                    
                    # Actualizar en base de datos
                    self.pg_manager.actualizar_producto(codigo, cambios)
                    total_guardados += 1
                    
                except Exception as e:
                    errores.append(f"{codigo}: {str(e)}")
                    logging.error(f"Error actualizando {codigo}: {e}")
            
            # Limpiar cambios y recargar
            self.cambios_pendientes = {}
            self.actualizar_label_cambios()
            self.cargar_datos()
            
            mensaje = f"Se guardaron {total_guardados} productos"
            if errores:
                mensaje += f"\n\nErrores:\n" + "\n".join(errores)
                show_warning_dialog(self, "Guardado parcial", mensaje)
            else:
                show_info_dialog(self, "Éxito", mensaje)
            
            self.catalogo_actualizado.emit()
            logging.info(f"Cambios guardados: {total_guardados} productos actualizados")
            
        except Exception as e:
            logging.error(f"Error guardando cambios: {e}")
            show_error_dialog(self, "Error al guardar", "No se pudieron guardar los cambios", detail=str(e))
    
    def descartar_cambios(self):
        """Descartar cambios pendientes"""
        if not self.cambios_pendientes:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Descartar todos los cambios pendientes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cambios_pendientes = {}
            self.cargar_datos()
    
    def filtrar_productos_varios(self):
        """Filtrar productos varios por búsqueda, categoría y estado"""
        texto_busqueda = self.search_varios.text().lower()
        categoria_filtro = self.combo_categoria_varios.currentText()
        estado_filtro = self.combo_activo_varios.currentText()
        
        for row in range(self.tabla_varios.rowCount()):
            mostrar_fila = True
            
            # Filtro de búsqueda
            if texto_busqueda:
                codigo = self.tabla_varios.item(row, 0).text().lower()
                nombre = self.tabla_varios.item(row, 1).text().lower()
                descripcion = self.tabla_varios.item(row, 2).text().lower() if self.tabla_varios.item(row, 2) else ""
                
                if not (texto_busqueda in codigo or texto_busqueda in nombre or texto_busqueda in descripcion):
                    mostrar_fila = False
            
            # Filtro de categoría
            if mostrar_fila and categoria_filtro != "Todas":
                categoria = self.tabla_varios.item(row, 4).text()
                if categoria != categoria_filtro:
                    mostrar_fila = False
            
            # Filtro de estado
            if mostrar_fila and estado_filtro != "Todos":
                activo = self.tabla_varios.item(row, 6).text()
                if estado_filtro == "Activos" and activo != "Sí":
                    mostrar_fila = False
                elif estado_filtro == "Inactivos" and activo != "No":
                    mostrar_fila = False
            
            self.tabla_varios.setRowHidden(row, not mostrar_fila)
    

