from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict
import base64
from cleaner import SpreadsheetCleaner
from submission_manager import submission_manager

app = FastAPI(title="Form Pipeline API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class StudentData(BaseModel):
    row_number: int
    data: Dict[str, str]

class SubmitRequest(BaseModel):
    url: str
    students: List[StudentData]

@app.get("/")
async def root():
    return {"message": "Form Pipeline API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/clean")
async def clean_spreadsheet(file: UploadFile = File(...)):
    """
    Clean and validate uploaded spreadsheet.
    
    Validates headers, cleans data, detects duplicates.
    Returns processed results and cleaned file.
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel file (.xlsx or .xls)"
        )
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Process spreadsheet
    cleaner = SpreadsheetCleaner()
    result = cleaner.process_spreadsheet(content, file.filename)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )
    
    # Encode cleaned file as base64 for JSON response
    cleaned_file_b64 = base64.b64encode(result["cleaned_file"]).decode('utf-8')
    
    return {
        "success": True,
        "results": result["results"],
        "summary": result["summary"],
        "cleaned_file": cleaned_file_b64,
        "filename": f"cleaned_{file.filename}"
    }

@app.post("/submit")
async def submit_forms(request: SubmitRequest):
    """
    Start batch form submission.
    
    Processes students one by one, filling and submitting forms.
    Returns job status with total count.
    """
    try:
        # Convert Pydantic models to dicts for processing
        students_data = [
            {
                'row_number': student.row_number,
                'data': student.data
            }
            for student in request.students
        ]
        
        result = await submission_manager.start_submission(
            url=request.url,
            students=students_data
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/status")
async def get_status():
    """
    Get current submission status.
    
    Returns progress, logs, errors, and elapsed time.
    Polls this endpoint for real-time updates.
    """
    return submission_manager.get_status()

@app.post("/pause")
async def pause_submission():
    """
    Pause submission at current position.
    
    Can be resumed later from the same position.
    """
    try:
        result = await submission_manager.pause()
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.post("/resume")
async def resume_submission():
    """
    Resume paused submission.
    
    Continues from the position where it was paused.
    """
    try:
        result = await submission_manager.resume()
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.post("/kill")
async def kill_submission():
    """
    Stop submission completely.
    
    Cannot be resumed - requires starting over.
    """
    try:
        result = await submission_manager.kill()
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
