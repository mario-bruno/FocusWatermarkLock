from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(".pdf"):
            print("Nuovo PDF rilevato:", event.src_path)

folder = input("Inserisci percorso assoluto della cartella da monitorare: ").strip()
if not os.path.isdir(folder):
    print("Cartella non valida!")
    exit(1)

observer = Observer()
observer.schedule(Handler(), folder, recursive=False)
observer.start()
print("In ascolto sulla cartella:", folder)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()