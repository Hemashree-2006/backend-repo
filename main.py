from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import json
import csv

from scheduler import load_patients, schedule
from risk_engine import calculate_total_risk

app = FastAPI()

# ----------------------------
# CORS (for frontend connection)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# file where uploaded csv will be stored
CSV_PATH = "uploaded_patients.csv"
SUBMISSION_PATH = "data/submission.json"


@app.get("/")
def home():
    return {"message": "Smart Triage API is running"}


# ----------------------------
# Helper: Generate submission.json from CSV
# ----------------------------
def generate_submission_json():
    if not os.path.exists(CSV_PATH):
        return
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            try:
                start = int(row.get("arrival_time", 0))
                duration = int(row.get("treatment_time", 0))
                end = start + duration
            except:
                start, end = 0, 0
            data.append({
                "patient": row.get("patient_id", ""),
                "severity": row.get("severity", ""),
                "start": start,
                "end": end
            })
    os.makedirs("data", exist_ok=True)
    with open(SUBMISSION_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ----------------------------
# Upload CSV from Dashboard
# ----------------------------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    with open(CSV_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    generate_submission_json()  # <-- Automatically create submission.json
    return {"message": "CSV uploaded successfully"}


# ----------------------------
# Run simulation
# ----------------------------
@app.get("/run")
def run_simulation():
    # check if CSV exists
    if not os.path.exists(CSV_PATH):
        return {
            "treatments": [],
            "events": [],
            "risk": 0,
            "message": "Upload CSV file first"
        }

    patients = load_patients(CSV_PATH)
    scheduled, events = schedule(patients)
    risk = calculate_total_risk(scheduled)

    treatments = []
    for p in scheduled:
        treatments.append({
            "patient": p.id,
            "doctor": p.doctor,
            "severity": p.severity,
            "start": p.start,
            "end": p.end
        })

    return {
        "treatments": treatments,
        "events": events,
        "risk": risk
    }


# ----------------------------
# Serve submission.json
# ----------------------------
@app.get("/submission")
def get_submission():
    if not os.path.exists(SUBMISSION_PATH):
        return JSONResponse(content={"error": "submission.json not found"}, status_code=404)
    with open(SUBMISSION_PATH) as f:
        data = json.load(f)
    return JSONResponse(content=data)