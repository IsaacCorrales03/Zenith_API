import requests
import time
import threading

class Bot:
    def __init__(self, url, sleep_time):
        self.url = url
        self.sleep_time = sleep_time
        self.active = False
        self.thread = None

    def peticion_periodica(self):
        while self.active:
            try:
                print("Realizando la petición")
                r = requests.get(self.url, timeout=5)
                if r.status_code == 200:
                    print("[El servidor sigue funcional]")
            except Exception as e:
                print(f"Error en petición periódica: {e}")
            time.sleep(self.sleep_time)

    def iniciar(self):
        if not self.active:
            print("Bot iniciado")
            self.active = True
            self.thread = threading.Thread(target=self.peticion_periodica)
            self.thread.daemon = True
            self.thread.start()

    def detener(self):
        print("Deteniendo bot...")
        self.active = False
        if self.thread:
            self.thread.join()  # Esperar a que el hilo termine
