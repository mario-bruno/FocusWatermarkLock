from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO
import os

LOGO_PATH = "logo_focus.png"
INPUT_PDF = "prova.pdf"  # Sostituisci con un tuo pdf da testare
OUTPUT_PDF = "Focus-prova.pdf"
OPACITY = 0.12

def create_watermark(page_width, page_height):
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

def apply_watermark_and_protect(pdf_path):
    from secrets import token_urlsafe
    PASSWORD = token_urlsafe(16)
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
    output_path = f"Focus-{filename}"
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Successo! File creato: {output_path}, password: {PASSWORD}")

if __name__ == "__main__":
    apply_watermark_and_protect(INPUT_PDF)