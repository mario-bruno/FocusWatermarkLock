import sys
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QScrollArea, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO

APP_NAME = "Focus Watermark Lock"
LOGO_PATH = "logo_focus.png"
ICNS_PATH = "icon.icns"
OPACITY = 0.12
WATERMARK_FOLDER = "Watermark"
DB_PATH = "focus_settings.db"
# Palette monocroma dal logo
COLOR_MAIN = "#1561AE"  # Blu logo Focus
COLOR_DARK = "#1E2D42"  # Grigio scuro logo Focus

# --- DATABASE FUNCTIONS ---
def get_settings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS counters (key TEXT PRIMARY KEY, value INTEGER)")
    c.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", ("last_folder", ""))
    c.execute("INSERT OR IGNORE INTO counters VALUES (?,?)", ("files_processed", 0))
    conn.commit()
    c.execute("SELECT value FROM settings WHERE key='last_folder'")
    folder = c.fetchone()[0]
    c.execute("SELECT value FROM counters WHERE key='files_processed'")
    files_processed = int(c.fetchone()[0])
    conn.close()
    return folder, files_processed

def save_last_folder(folder):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='last_folder'", (folder,))
    conn.commit()
    conn.close()

def increment_files_processed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE counters SET value = value + 1 WHERE key='files_processed'")
    conn.commit()
    c.execute("SELECT value FROM counters WHERE key='files_processed'")
    count = int(c.fetchone()[0])
    conn.close()
    return count

def reset_files_processed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE counters SET value=0 WHERE key='files_processed'")
    conn.commit()
    conn.close()

def set_files_processed(n):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE counters SET value=? WHERE key='files_processed'", (n,))
    conn.commit()
    conn.close()

# --- PDF FUNCTIONS ---
def create_watermark(page_width, page_height):
    try:
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_width = int((2 / 3) * page_width)
        logo = logo.resize((logo_width, logo_width), Image.LANCZOS)
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * OPACITY))
        logo.putalpha(alpha)
        temp_logo = BytesIO()
        logo.save(temp_logo, format="PNG")
        temp_logo.seek(0)
        x = (page_width - logo_width) / 2
        y = (page_height - logo_width) / 2
        can.drawImage(ImageReader(temp_logo), x, y, width=logo_width, height=logo_width, mask='auto')
        can.save()
        packet.seek(0)
        return PdfReader(packet)
    except Exception as e:
        print(f"Errore nella creazione del watermark: {e}")
        raise

def apply_watermark_and_protect(pdf_path):
    try:
        filename = os.path.basename(pdf_path)
        dirname = os.path.dirname(pdf_path)
        output_folder = os.path.join(dirname, WATERMARK_FOLDER)
        os.makedirs(output_folder, exist_ok=True)
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        n_pages = len(reader.pages)
        first_page = reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        watermark = create_watermark(page_width, page_height).pages[0]
        for i, page in enumerate(reader.pages):
            page.merge_page(watermark)
            writer.add_page(page)
        writer.add_metadata({"/Author": "Focus"})
        # Solo visualizzazione, blocco copia/incolla/modifica base (default)
        writer.encrypt("", None)  # NO permissions arg!
        output_path = os.path.join(output_folder, f"Focus-{filename}")
        with open(output_path, "wb") as f:
            writer.write(f)
        return True, output_path
    except Exception as e:
        print("Eccezione:", e)
        return False, str(e)

# --- GUI CLASSES ---
class FileInfoWidget(QFrame):
    def __init__(self, filename):
        super().__init__()
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.label = QLabel(filename)
        hbox.addWidget(self.label, 2)
        self.status_icon = QLabel()
        self.status_icon.setFixedWidth(32)
        hbox.addWidget(self.status_icon)
        self.delete_icon = QLabel()
        self.delete_icon.setFixedWidth(24)
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        self.delete_icon.setPixmap(pixmap)
        hbox.addWidget(self.delete_icon)
        self.delete_icon.setCursor(Qt.PointingHandCursor)
        self.delete_icon.setToolTip("Rimuovi questa riga")
        hbox.addStretch()
        self.delete_icon.mousePressEvent = self._on_delete
        self._delete_callback = None
    def set_status(self, ok):
        if ok:
            self.status_icon.setPixmap(self._draw_icon(Qt.green, check=True))
        else:
            self.status_icon.setPixmap(self._draw_icon(Qt.red, check=False))
    def set_delete_callback(self, func):
        self._delete_callback = func
    def _on_delete(self, event):
        if self._delete_callback:
            self._delete_callback(self)
    def _draw_icon(self, color, check=True):
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        pen = QPen(color)
        pen.setWidth(3)
        painter.setPen(pen)
        if check:
            painter.drawLine(5, 13, 10, 17)
            painter.drawLine(10, 17, 17, 4)
        else:
            painter.drawLine(5, 5, 15, 15)
            painter.drawLine(15, 5, 5, 15)
        painter.end()
        return pixmap

class MainWindow(QWidget):
    pdf_detected = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        try:
            self.setWindowIcon(QIcon(ICNS_PATH))
        except Exception:
            pass
        self.resize(600, 500)
        self.folder_path, self.files_processed = get_settings()
        self.observer = None
        self.processed_files = set()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        # LOGO
        self.logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH).scaledToWidth(110, Qt.SmoothTransformation)
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        # INFO
        self.info = QLabel()
        self.info.setAlignment(Qt.AlignCenter)
        self.update_folder_info()
        layout.addWidget(self.info)
        # BUTTON SCEGLI CARTELLA
        self.choose_btn = QPushButton("Scegli cartella")
        self.choose_btn.clicked.connect(self.choose_folder)
        self.choose_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_MAIN};
                color: #fff;
                border-radius: 8px;
                padding: 8px 25px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLOR_DARK};
            }}
        """)
        layout.addWidget(self.choose_btn, alignment=Qt.AlignCenter)
        # COUNTER
        self.counter_label = QLabel()
        self.counter_label.setText(self.get_counter_text())
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("font-size:18px; margin:16px 0 6px 0; color: #222;")
        layout.addWidget(self.counter_label)
        # SCROLL FILES
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.files_widget = QWidget()
        self.files_layout = QVBoxLayout()
        self.files_layout.addStretch()
        self.files_widget.setLayout(self.files_layout)
        self.scroll.setWidget(self.files_widget)
        layout.addWidget(self.scroll, stretch=1)
        # CLEAR BUTTON
        self.clear_btn = QPushButton("Ripulisci")
        self.clear_btn.clicked.connect(self.clear_all_files)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_DARK};
                color: #fff;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 40px 8px 40px;
                margin-left: 40px; margin-right: 40px;
            }}
            QPushButton:hover {{
                background: {COLOR_MAIN};
            }}
        """)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.setStyleSheet("QWidget { font-size: 15px; }")
        self.pdf_detected.connect(self.process_pdf)

        # AUTO-START MONITORING IF FOLDER WAS PREVIOUSLY CHOSEN
        if self.folder_path and os.path.isdir(self.folder_path):
            self.start_monitor()

    def get_counter_text(self):
        return f"File processati correttamente: <b>{self.files_processed}</b>"

    def update_folder_info(self):
        if self.folder_path:
            self.info.setText(f"In ascolto sulla cartella:<br><b>{self.folder_path}</b>")
        else:
            self.info.setText(f"<b>Scegli una cartella da monitorare</b>")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Scegli la cartella da monitorare")
        if folder:
            self.folder_path = folder
            save_last_folder(folder)
            self.update_folder_info()
            self.start_monitor()

    def start_monitor(self):
        if self.observer:
            self.observer.stop()
        self.observer = Observer()
        event_handler = PDFHandler(self.pdf_detected, self.processed_files)
        self.observer.schedule(event_handler, self.folder_path, recursive=False)
        self.observer.start()

    def process_pdf(self, pdf_path):
        print("DEBUG: process_pdf chiamato con", pdf_path)
        filename = os.path.basename(pdf_path)
        file_widget = FileInfoWidget(filename)
        self.files_layout.insertWidget(self.files_layout.count() - 1, file_widget)
        file_widget.set_delete_callback(self.remove_file_widget)
        ok, msg = apply_watermark_and_protect(pdf_path)
        print("DEBUG: risultato apply_watermark_and_protect:", ok, msg)
        file_widget.set_status(ok)
        if ok:
            file_widget.label.setToolTip(f"Salvato in:\n{msg}\n")
            self.files_processed = increment_files_processed()
            self.counter_label.setText(self.get_counter_text())
        else:
            file_widget.label.setToolTip(msg)
            print(f"Errore su {filename}: {msg}")

    def remove_file_widget(self, widget):
        self.files_layout.removeWidget(widget)
        widget.deleteLater()

    def clear_all_files(self):
        for i in reversed(range(self.files_layout.count() - 1)):
            item = self.files_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.files_layout.removeWidget(widget)
                    widget.deleteLater()
        # NON resetto il contatore, quindi NON chiamo reset_files_processed()
        self.counter_label.setText(self.get_counter_text())

    def closeEvent(self, event):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        event.accept()

class PDFHandler(FileSystemEventHandler):
    def __init__(self, signal, processed_files):
        self.signal = signal
        self.processed_files = processed_files

    def on_created(self, event):
        if event.src_path.lower().endswith(".pdf"):
            if event.src_path not in self.processed_files:
                self.processed_files.add(event.src_path)
                self.signal.emit(event.src_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.setApplicationName(APP_NAME)
    sys.exit(app.exec_())