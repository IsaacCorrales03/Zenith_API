import threading
import time
import sys
import signal
import logging
from datetime import datetime
from waitress import serve
from main import app
from logger_config import get_logger
logger = get_logger()
from bot import Bot
from server_strings import service_url

class AdvancedInteractiveTerminal:
    def __init__(self, bot, app, host='127.0.0.1', port=1900):
        self.bot = bot
        self.app = app
        self.host = host
        self.port = port
        self.server_thread = None
        self.bot_thread = None
        self.running = False
        self.start_time = datetime.now()
        self.commands = {
            'reload': self.reload_bot,
            'restart': self.restart_bot,
            'status': self.show_status,
            'help': self.show_help,
            'uptime': self.show_uptime,
            'logs': self.show_recent_logs,
            'clear': self.clear_screen,
            'config': self.show_config,
            'stop': self.stop_system,
            'exit': self.stop_system,
            'quit': self.stop_system
        }
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Maneja señales del sistema"""
        print(f"\n🛑 Señal {signum} recibida. Deteniendo sistema...")
        self.running = False
        
    def start_server(self):
        """Inicia el servidor en un hilo separado"""
        try:
            logger.warning(f"Servidor iniciado en: http://{self.host}:{self.port}")
            serve(self.app, host=self.host, port=self.port, threads=4)
        except Exception as e:
            logger.error(f"Error en servidor: {e}")
            
    def start_bot(self):
        """Inicia el bot en un hilo separado"""
        try:
            self.bot.iniciar()
        except Exception as e:
            logger.error(f"Error en bot: {e}")
            
    def reload_bot(self):
        """Reinicia solo el bot"""
        print("🔄 Reiniciando bot...")
        try:
            if hasattr(self.bot, 'detener'):
                self.bot.detener()
            time.sleep(1)
            
            # Recrear bot
            self.bot = Bot(service_url, 40)
            self.bot_thread = threading.Thread(target=self.start_bot, daemon=True)
            self.bot_thread.start()
            
            print("✅ Bot reiniciado exitosamente")
        except Exception as e:
            print(f"❌ Error al reiniciar bot: {e}")
            
    def restart_bot(self):
        """Reinicia completamente el sistema"""
        print("🔄 Reiniciando sistema completo...")
        self.stop_system(restart=True)
        time.sleep(2)
        self.start_system()
        
    def show_status(self):
        """Muestra el estado detallado del sistema"""
        print("\n" + "="*50)
        print("📊 ESTADO DEL SISTEMA")
        print("="*50)
        print(f"🟢 Servidor: {'Activo' if self.running else 'Inactivo'}")
        print(f"🌐 URL: http://{self.host}:{self.port}")
        print(f"🤖 Bot: {'Activo' if self.bot.get_status else 'Inactivo'}")
        print(f"⏰ Tiempo activo: {datetime.now() - self.start_time}")
        print(f"🧵 Hilos activos: {threading.active_count()}")
        print("="*50)
        
    def show_uptime(self):
        """Muestra tiempo de actividad en formato dd:hh:mm:ss"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"⏱️ Sistema activo por: {days:02}:{hours:02}:{minutes:02}:{seconds:02}")
        
    def show_recent_logs(self):
        """Muestra logs recientes (simulado)"""
        print("\n📋 Últimos logs:")
        print("-" * 30)
        # Aquí podrías implementar lectura de archivo de logs
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sistema funcionando normalmente")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Bot activo")
        
    def show_config(self):
        """Muestra configuración actual"""
        print("\n⚙️ CONFIGURACIÓN:")
        print(f"Host: {self.host}")
        print(f"Puerto: {self.port}")
        print(f"Hilos del servidor: 4")
        print(f"Intervalo del bot: 40s")
        
    def clear_screen(self):
        """Limpia la pantalla"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🚀 Terminal de Control - Sistema de Monitoreo")
        print("=" * 50)
        
    def show_help(self):
        """Muestra ayuda completa"""
        print("\n" + "="*50)
        print("📋 COMANDOS DISPONIBLES")
        print("="*50)
        print("  reload     - Reiniciar solo el bot")
        print("  restart    - Reiniciar sistema completo")
        print("  status     - Estado detallado del sistema")
        print("  uptime     - Tiempo de actividad")
        print("  logs       - Mostrar logs recientes")
        print("  config     - Mostrar configuración")
        print("  clear      - Limpiar terminal")
        print("  help       - Mostrar esta ayuda")
        print("  stop/exit  - Detener y salir")
        print("="*50)
        print("💡 Tip: Usa Ctrl+C para forzar salida")
        
    def start_system(self):
        """Inicia todo el sistema"""
        print("🚀 Iniciando sistema...")
        
        # Iniciar bot
        self.bot_thread = threading.Thread(target=self.start_bot, daemon=True)
        self.bot_thread.start()
        
        # Iniciar servidor
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()
        
        self.running = True
        self.start_time = datetime.now()
        print("✅ Sistema iniciado correctamente")
        
    def stop_system(self, restart=False):
        """Detiene el sistema"""
        if not restart:
            print("🛑 Deteniendo sistema...")
        self.running = False
        
        if hasattr(self.bot, 'detener'):
            self.bot.detener()
            
        if not restart:
            logger.critical("Servidor detenido")
            
    def process_command(self, command):
        """Procesa un comando ingresado"""
        command = command.strip().lower()
        
        if command in self.commands:
            self.commands[command]()
        elif command == '':
            pass
        else:
            print(f"❌ Comando desconocido: '{command}'")
            print("💡 Usa 'help' para ver comandos disponibles")
            
    def run(self):
        """Ejecuta la terminal interactiva principal"""
        self.clear_screen()
        self.start_system()
        
        print("💡 Escribe 'help' para ver comandos disponibles")
        print("🔧 Terminal lista para comandos...")
        
        try:
            while self.running:
                try:
                    command = input("\n🔧 > ")
                    self.process_command(command)
                    
                    if command.lower() in ['stop', 'exit', 'quit']:
                        break
                        
                except KeyboardInterrupt:
                    print("\n🛑 Ctrl+C detectado.")
                    confirm = input("¿Realmente quieres salir? (s/N): ")
                    if confirm.lower() in ['s', 'si', 'yes', 'y']:
                        self.running = False
                        break
                    else:
                        print("Continuando...")
                        
                except EOFError:
                    print("\n🛑 EOF detectado. Saliendo...")
                    self.running = False
                    break
                    
        except Exception as e:
            logger.error(f"Error en terminal: {e}")
            
        finally:
            self.stop_system()
            print("👋 ¡Hasta luego!")
            sys.exit(0)

# Uso en tu código principal
if __name__ == '__main__':
    uptime_bot = Bot(service_url, 40)
    
    terminal = AdvancedInteractiveTerminal(
        bot=uptime_bot,
        app=app,
        host='127.0.0.1',
        port=1900
    )
    
    terminal.run()