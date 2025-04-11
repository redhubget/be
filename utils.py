from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import os
import re

def extract_text(docx_path):
    doc = Document(docx_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return full_text

def extract_images(docx_path, output_dir):
    from zipfile import ZipFile
    import uuid

    images = []
    with ZipFile(docx_path, 'r') as docx:
        for file in docx.namelist():
            if file.startswith("word/media/") and (file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")):
                img_data = docx.read(file)
                img_name = f"{uuid.uuid4()}.jpg"
                img_path = os.path.join(output_dir, img_name)
                with open(img_path, "wb") as f:
                    f.write(img_data)
                images.append(img_path)
    return images

def generate_pdf(text, images, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 40
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:110])
        y -= 14
    for img_path in images:
        c.showPage()
        try:
            c.drawImage(img_path, 50, 250, width=500, preserveAspectRatio=True, mask='auto')
        except:
            pass
    c.save()

def process_docx(file_path, tech_email, brief_email, output_dir="static"):
    raw_text = extract_text(file_path)
    tech_summary = "\n".join([line for line in raw_text.splitlines() if len(line.strip()) > 60])
    brief_summary = "\n".join([line for line in raw_text.splitlines() if len(line.strip()) > 20 and len(line.strip()) < 60])

    images = extract_images(file_path, output_dir)
    img_rel = [img.replace(output_dir, "static").replace("\\", "/").replace("\\", "/") for img in images]

    tech_pdf = os.path.join(output_dir, f"tech_summary_{uuid.uuid4().hex}.pdf")
    brief_pdf = os.path.join(output_dir, f"brief_summary_{uuid.uuid4().hex}.pdf")

    generate_pdf(tech_summary, images, tech_pdf)
    generate_pdf(brief_summary, images, brief_pdf)

    return {
        "tech_summary": tech_summary,
        "brief_summary": brief_summary,
        "images": [img.replace("static", "static") for img in images],
        "tech_pdf_path": tech_pdf,
        "brief_pdf_path": brief_pdf
    }
