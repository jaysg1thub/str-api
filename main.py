# str-api/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json
import pypdf
import io
from database import engine, SessionLocal
import models

app = FastAPI(
    title="STR Document API",
    description="Production-ready multi-tenant lease processing gateway."
)

# 🚀 SECURE: Tables are managed via migrations or explicit startup; no drop_all here!
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "STR Document Processing Engine",
        "version": "1.0.0"
    }

@app.post("/upload", status_code=202)
def upload_lease_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid format. Only PDF files are accepted.")
    
    try:
        file_bytes = file.file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        
        extracted_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
                
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded PDF contains no extractable text.")
            
        new_job = models.AnalysisJob(
            user_id=1, 
            document_name=file.filename,
            status="pending",
            raw_text=extracted_text,
            extracted_data=None
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        return {
            "message": "File successfully uploaded and queued for processing.",
            "job_id": new_job.id,
            "filename": file.filename,
            "status": new_job.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.get("/jobs/{job_id}")
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job record not found.")
    
    if job.status != "completed":
        return {
            "job_id": job.id,
            "status": job.status,
            "document_name": job.document_name,
            "message": "Data extraction is processing or hit an operational error.",
            "raw_payload": job.extracted_data if job.status == "failed" else None
        }
    
    return {
        "job_id": job.id,
        "status": job.status,
        "document_name": job.document_name,
        "created_at": job.created_at,
        "extracted_intelligence": json.loads(job.extracted_data)
    }