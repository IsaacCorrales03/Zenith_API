import requests
import time
import threading
from logger_config import get_logger

logger = get_logger("ZenithServer")

class Bot:
    def __init__(self, url, sleep_time):
        self.url = url
        self.sleep_time = sleep_time
        self.active = False
        self.thread = None

    def peticion_periodica(self):
        while self.active:
            try:
                logger.info("Realizando petición")
                r = requests.get(self.url, timeout=5)
                if r.status_code == 200:
                    logger.debug("[El servidor sigue funcional]")
            except Exception as e:
                logger.error(f"Error en petición periódica: {e}")
            time.sleep(self.sleep_time)
    def get_status(self):
        return self.active
    def iniciar(self):
        if not self.active:
            logger.info("Bot iniciado")
            self.active = True
            self.thread = threading.Thread(target=self.peticion_periodica)
            self.thread.daemon = True
            self.thread.start()

    def detener(self):
        logger.info("Deteniendo bot...")
        self.active = False
        if self.thread:
            self.thread.join()
