from fastapi import FastAPI, File, UploadFile
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response

import os
import shutil

from scripts.csvToPdf import gererateSinglePdfs

app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from any origin
origins = ["*"]  # Update this list with allowed origins if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Directory to store uploaded PDF files
UPLOAD_DIR = "uploaded_pdfs"


@app.get('/')
def health():
    return {'Hello': "World"}

@app.post('/get_csv_pdf')
async def convertCsvToPdf(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    csv_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(csv_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    pdf_path = gererateSinglePdfs(csv_path)
    # file_resp = FileResponse(pdf_path, media_type="application/pdf")

    # Read the file into a buffer
    with open(pdf_path, "rb") as f:
        file_data = f.read()

    # Remove files after loading into buffer
    os.remove(csv_path)
    os.remove(pdf_path)

    # Create a FastAPI response with the file data
    response = Response(content=file_data, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={pdf_path}"

    return response



if __name__ == '__main__':
    # To run the application we can use below commnads
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    # To run with multiple worker processes (for production):
    # uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4


    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)