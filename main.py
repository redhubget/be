from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil, os, uuid
from utils import process_docx
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload")
async def upload_report(file: UploadFile, tech_email: str = Form(...), brief_email: str = Form(...)):
    file_id = str(uuid.uuid4())
    save_path = f"static/{file_id}_{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_docx(save_path, tech_email, brief_email, output_dir="static")

    return JSONResponse({
        "message": "Processed and emailed successfully.",
        "tech_summary": result['tech_summary'],
        "brief_summary": result['brief_summary'],
        "tech_download_url": "/" + result['tech_pdf_path'],
        "brief_download_url": "/" + result['brief_pdf_path'],
        "images": result['images']
    })
