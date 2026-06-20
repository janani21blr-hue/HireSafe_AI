from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from detector import analyze_job_description

# Initialize the API
app = FastAPI(
    title="HireSafe AI Core API",
    description="Automated B2B endpoint for placement cells to verify job postings at scale.",
    version="1.0"
)

# Define the expected input from a user/institution
class JobRequest(BaseModel):
    job_text: str

# Define the POST endpoint
@app.post("/api/v1/scan")
async def scan_job_posting(request: JobRequest):
    if not request.job_text or len(request.job_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Job description text is too short or empty.")

    try:
        # Call your existing brain
        result = analyze_job_description(request.job_text)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)