"""
Gestor de impresión para impresoras instaladas como Generic/Text Only en Windows
Usa la API de Windows en lugar de puerto serial
"""

import os
import sys
import tempfile
import subprocess
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class WindowsPrinterManager:
    """
    Gestor de impresoras instaladas en Windows
    Funciona con "Generic/Text Only" y otras impresoras instaladas
    """
    
    def __init__(self, nombre_impresora: str = "Generic / Text Only"):
        """
        Inicializar gestor
        
        Args:
            nombre_impresora: Nombre exacto de la impresora instalada en Windows
        """
        self.nombre_impresora = nombre_impresora
        self.conectado = False
    
    @staticmethod
    def obtener_impresoras_instaladas() -> List[str]:
        """
        Obtener lista de impresoras instaladas en Windows
        
        Returns:
            Lista de nombres de impresoras
        """
        try:
            cmd = 'Get-Printer | Select-Object -ExpandProperty Name'
            resultado = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            impresoras = [
                linea.strip() 
                for linea in resultado.stdout.split('\n') 
                if linea.strip()
            ]
            
            logger.info(f"Impresoras encontradas: {impresoras}")
            return impresoras
        except Exception as e:
            logger.error(f"Error al obtener impresoras: {e}")
            return []
    
    @staticmethod
    def obtener_impresora_por_tipo(tipo: str = "Generic") -> str:
        """
        Buscar impresora por tipo
        
        Args:
            tipo: Palabra clave para buscar (Generic, Thermal, Text, etc)
            
        Returns:
            Nombre de la impresora o None
        """
        try:
            cmd = f'Get-Printer | Where-Object Name -Like "*{tipo}*" | Select-Object -ExpandProperty Name -First 1'
            resultado = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            nombre = resultado.stdout.strip()
            if nombre:
                logger.info(f"Impresora {tipo} encontrada: {nombre}")
                return nombre
            return None
        except Exception as e:
            logger.error(f"Error al buscar impresora {tipo}: {e}")
            return None
    
    def conectar(self) -> bool:
        """Verificar que la impresora existe"""
        try:
            impresoras = self.obtener_impresoras_instaladas()
            if self.nombre_impresora in impresoras:
                self.conectado = True
                logger.info(f"✅ Conectado a: {self.nombre_impresora}")
                return True
            else:
                logger.error(f"❌ Impresora no encontrada: {self.nombre_impresora}")
                logger.info(f"Impresoras disponibles: {impresoras}")
                return False
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False
    
    def desconectar(self):
        """Desconectar (limpieza)"""
        self.conectado = False
        logger.info("Desconectado")
    
    def enviar_texto(self, contenido: str) -> bool:
        """
        Enviar texto directamente a la impresora
        
        Args:
            contenido: Texto a imprimir
            
        Returns:
            bool: Éxito
        """
        if not self.conectado:
            logger.error("Impresora no conectada")
            return False
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                f.write(contenido)
                archivo_temp = f.name
            
            try:
                # Imprimir usando PowerShell
                cmd = f'''
                $printer = "{self.nombre_impresora}"
                $file = "{archivo_temp}"
                $null = New-Item -Path "\\\\?\\{self.nombre_impresora}" -ItemType Printer -ErrorAction SilentlyContinue
                Copy-Item -Path $file -Destination ("LPT1:" | Out-Null); 
                Get-Content $file | Out-Printer -Name $printer
                '''
                
                subprocess.run(
                    ['powershell', '-Command', cmd],
                    timeout=10,
                    capture_output=True
                )
                
                logger.info("✅ Texto enviado a impresora")
                return True
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(archivo_temp)
                except:
                    pass
        
        except Exception as e:
            logger.error(f"Error al enviar texto: {e}")
            return False
    
    def imprimir_archivo(self, ruta_archivo: str) -> bool:
        """
        Imprimir archivo de texto
        
        Args:
            ruta_archivo: Ruta del archivo a imprimir
            
        Returns:
            bool: Éxito
        """
        if not self.conectado:
            logger.error("Impresora no conectada")
            return False
        
        try:
            # Usar comando de Windows para imprimir
            cmd = f'powershell -Command "Get-Content \'{ruta_archivo}\' | Out-Printer -Name \'{self.nombre_impresora}\'"'
            
            subprocess.run(cmd, shell=True, timeout=10, capture_output=True)
            
            logger.info(f"✅ Archivo impreso: {ruta_archivo}")
            return True
        except Exception as e:
            logger.error(f"Error al imprimir archivo: {e}")
            return False


class TicketPrinterWindows(WindowsPrinterManager):
    """Impresora especializada en tickets para Windows"""
    
    def __init__(self, nombre_impresora: str = "Generic / Text Only"):
        super().__init__(nombre_impresora)
    
    def imprimir_ticket(self, datos_ticket: Dict) -> bool:
        """
        Imprimir ticket completo
        
        Args:
            datos_ticket: Diccionario con datos del ticket
            
        Returns:
            bool: Éxito
        """
        if not self.conectado:
            logger.error("Impresora no conectada")
            return False
        
        try:
            # Generar contenido del ticket
            contenido = self._generar_ticket(datos_ticket)
            
            # Enviar a impresora
            return self.enviar_texto(contenido)
        except Exception as e:
            logger.error(f"Error al imprimir ticket: {e}")
            return False
    
    def _generar_ticket(self, datos: Dict) -> str:
        """Generar contenido del ticket"""
        
        ticket = "=" * 42 + "\n"
        ticket += f"{datos.get('tienda', 'HTF GIMNASIO').center(42)}\n"
        ticket += f"{datos.get('subtitulo', 'PUNTO DE VENTA').center(42)}\n"
        ticket += "=" * 42 + "\n\n"
        
        ticket += f"Ticket: #{datos.get('numero_ticket', 0):06d}\n"
        ticket += f"Fecha: {datos.get('fecha_hora', '')}\n"
        if datos.get('cajero'):
            ticket += f"Cajero: {datos.get('cajero')}\n"
        ticket += "-" * 42 + "\n\n"
        
        # Productos
        for producto in datos.get('productos', []):
            nombre = producto['nombre'][:30]
            ticket += f"{nombre}\n"
            cantidad_precio = f"{producto['cantidad']:.0f}x ${producto['precio']:.2f}"
            subtotal = f"${producto['subtotal']:.2f}"
            espacios = 42 - len(cantidad_precio) - len(subtotal)
            ticket += f"{cantidad_precio}{' ' * espacios}{subtotal}\n"
        
        ticket += "-" * 42 + "\n"
        ticket += f"{'TOTAL:' + ' ' * 28}${datos.get('total', 0):.2f}\n"
        ticket += "=" * 42 + "\n\n"
        
        ticket += f"{datos.get('metodo_pago', 'EFECTIVO').center(42)}\n"
        ticket += "-" * 42 + "\n\n"
        
        ticket += "¡Gracias por su compra!\n"
        ticket += "Vuelva pronto\n"
        ticket += "=" * 42 + "\n"
        
        return ticket


# ===== EJEMPLO =====

if __name__ == "__main__":
    # Obtener impresoras
    print("\nImpresoras disponibles:")
    impresoras = WindowsPrinterManager.obtener_impresoras_instaladas()
    for i, imp in enumerate(impresoras, 1):
        print(f"{i}. {imp}")
    
    # Buscar impresora Generic
    print("\nBuscando impresora Generic...")
    nombre = WindowsPrinterManager.obtener_impresora_por_tipo("Generic")
    
    if nombre:
        print(f"✅ Encontrada: {nombre}")
        
        # Crear impresora de tickets
        printer = TicketPrinterWindows(nombre)
        
        if printer.conectar():
            # Datos de prueba
            datos = {
                'tienda': 'HTF GIMNASIO',
                'subtitulo': 'PUNTO DE VENTA',
                'numero_ticket': 1001,
                'fecha_hora': '19/12/2025 15:30',
                'cajero': 'TEST',
                'productos': [
                    {'nombre': 'Bebida Energética', 'cantidad': 2, 'precio': 5.00, 'subtotal': 10.00},
                    {'nombre': 'Toalla Microfibra', 'cantidad': 1, 'precio': 15.00, 'subtotal': 15.00},
                ],
                'total': 25.00,
                'metodo_pago': 'EFECTIVO'
            }
            
            if printer.imprimir_ticket(datos):
                print("✅ Ticket impreso exitosamente")
            else:
                print("❌ Error al imprimir")
            
            printer.desconectar()
    else:
        print("❌ No se encontró impresora Generic")
