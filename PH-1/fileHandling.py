from fastapi import FastAPI, File, UploadFile
from typing import List
import pandas as pd
from PyPDF2 import PdfReader
import io

app = FastAPI()

#single file data upload, the below code accepts .text and .log files.
@app.post("/file-upload")
async def file_upload(file: UploadFile = File(...)):
    content = await file.read()

    try:
        text_p = content.decode("utf-8")[:200]
    except:
        text_p = "file cannot be previewed"

    return {
        "fileName": file.filename,
        "fileType": file.content_type,
        "fileSize": len(content),
        "FileContent": text_p
    }

#multiple file data upload, the below code accepts excel sheet and pdf files.
@app.post("/multiple-file-upload")
async def read_multi_file(files: List[UploadFile] = File(..., media_type="multipart/form-data")):
    results = []
    for file in files:
        content = await file.read()
        fileName = file.filename

        if fileName.endswith((".xls",".xlsx")):
            data_frame = pd.read_excel(io.BytesIO(content))
            results.append({
                "filename": fileName,
                "fileType": 'Excel',
                "fileSize": len(content),
                "preview": data_frame.head(3).to_dict()
            })
        elif fileName.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(content))
            text="".join([p.extract_text() or "" for p in pdf_reader.pages[:2]])
            results.append({
                "filename": fileName,
                "fileType": 'pdf',
                "fileSize": len(content),
                "preview": text
            })
        elif fileName.endswith((".txt",".log")):
            try:
                text_p = content.decode("utf-8")[:200]
            except:
                text_p = "file cannot be previewed"
            results.append({
                "fileName": file.filename,
                "fileType": file.content_type,
                "fileSize": len(content),
                "FileContent": text_p
            })
        else:
            results.append({
                "Error": "unsupported file type uploaded"
            })
    return results