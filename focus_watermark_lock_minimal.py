import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO
import secrets

APP_NAME = "Focus Watermark Lock"

def create_watermark(page_width, page_height):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    logo = Image.open("logo_focus.png").convert("RGBA")
    logo_width = int((2 / 3) * page_width)
    logo = logo.resize((logo_width, logo_width), Image.LANCZOS)
    alpha = logo.split()[3]
    alpha = alpha.point(lambda p: int(p * 0.12))
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

def apply_watermark_and_protect(pdf_path):
    PASSWORD = secrets.token_urlsafe(16)
    filename = os.path.basename(pdf_path)
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
    writer.encrypt("", PASSWORD)
    output_folder = os.path.join(os.path.dirname(pdf_path), "Watermark")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"Focus-{filename}")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path, PASSWORD

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(200, 200, 420, 180)
        layout = QVBoxLayout()
        self.info = QLabel("Scegli un PDF da convertire.")
        layout.addWidget(self.info)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.choose_btn = QPushButton("Scegli PDF")
        self.choose_btn.clicked.connect(self.choose_pdf)
        layout.addWidget(self.choose_btn)
        self.result = QLabel("")
        layout.addWidget(self.result)
        self.setLayout(layout)
    def choose_pdf(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Scegli PDF", "", "PDF Files (*.pdf)")
            if file_path:
                self.info.setText("Conversione in corso...")
                self.progress.setValue(0)
                output_path, pwd = apply_watermark_and_protect(file_path)
                self.progress.setValue(100)
                self.result.setText(f"Fatto!\n{output_path}\nPassword: {pwd}")
        except Exception as e:
            import traceback
            self.result.setText("Errore: " + str(e) + "\n" + traceback.format_exc())
            self.progress.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())