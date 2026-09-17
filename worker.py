# str-api/worker.py
import os
import time
import json
from sqlalchemy.orm import Session
from anthropic import Anthropic
from database import engine, SessionLocal
import models
import schemas

# Initialize the Anthropic client using the environment key
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def process_pending_job(db: Session, job: models.AnalysisJob):
    print(f"\n--- [START] Processing Job ID {job.id} for document: {job.document_name} ---")
    
    # 1. Flip status to processing instantly
    job.status = "processing"
    db.commit()

    try:
        print("Sending contract text to Anthropic Claude (Claude 3.5 Sonnet)...")
        
        # 2. Call Claude with the dynamic text pulled straight from the database column
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  
            max_tokens=4000,
            system="You are an expert commercial real estate attorney. Extract lease attributes and identify severe liability anomalies.",
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this contract text. Fill out the schema completely: \n\n{job.raw_text}" # 🚀 DYNAMIC ROW TEXT PASSED HERE
                }
            ],
            tools=[
                {
                    "name": "lease_extractor",
                    "description": "Formats extracted contract data and legal anomalies cleanly.",
                    "input_schema": schemas.LeaseExtractionSchema.model_json_schema()
                }
            ],
            tool_choice={"type": "tool", "name": "lease_extractor"}
        )

        # 3. Pull out the structured tool use block
        tool_use_block = [block for block in response.content if block.type == "tool_use"]
        extracted_json_dict = tool_use_block.input

        # 4. Save the stringified JSON payload down to our database column
        job.extracted_data = json.dumps(extracted_json_dict)
        job.status = "completed"
        db.commit()
        print(f"--- [SUCCESS] Job ID {job.id} finalized inside str_db! ---")

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.extracted_data = json.dumps({"error": str(e)})
        db.commit()
        print(f"--- [ERROR] Job ID {job.id} failed: {str(e)} ---")

def start_polling_loop():
    print("🚀 STR Background Worker initialized. Scanning str_db for pending actions...")
    
    while True:
        db = SessionLocal()
        try:
            pending_job = (
                db.query(models.AnalysisJob)
                .filter(models.AnalysisJob.status == "pending")
                .order_by(models.AnalysisJob.id.asc())
                .first()
            )

            if pending_job:
                process_pending_job(db, pending_job)
            else:
                print("Checking for pending jobs... (Database empty, sleeping 5s)", end="\r")
                time.sleep(5)
                
        except Exception as loop_error:
            print(f"\n[LOOP EXCEPTION]: {str(loop_error)}")
            time.sleep(5)
        finally:
            db.close()

if __name__ == "__main__":
    start_polling_loop()
