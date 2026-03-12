import csv
from models import Patient, Doctor


# --------------------------------------------------
# LOAD PATIENT DATA FROM CSV
# --------------------------------------------------

def load_patients(file_path):

    patients = []

    with open(file_path, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            patient = Patient(
                row["patient_id"],
                row["severity"],
                row["arrival_time"],
                row["treatment_time"],
                row["required_specialization"]
            )

            patients.append(patient)

    return patients


# --------------------------------------------------
# PRIORITY FUNCTION (SMART TRIAGE LOGIC)
# --------------------------------------------------

def priority_score(patient, current_time):

    waiting_time = max(0, current_time - patient.arrival)

    score = (
        patient.severity * 10
        + waiting_time * 2
        - patient.treatment
    )

    return score


# --------------------------------------------------
# CHECK DOCTOR COMPATIBILITY
# --------------------------------------------------

def is_compatible(patient, doctor):

    if doctor.spec == "GENERAL":
        return True

    if patient.spec == doctor.spec:
        return True

    return False


# --------------------------------------------------
# MAIN SIMULATION ENGINE
# --------------------------------------------------

def schedule(patients):

    doctors = [
        Doctor("Doctor_T", "TRAUMA"),
        Doctor("Doctor_C", "CARDIO"),
        Doctor("Doctor_G", "GENERAL")
    ]

    time = 0
    waiting_queue = []
    completed_patients = []

    events = []
    max_time = 10000  # Safety limit to prevent infinite loops

    while (patients or waiting_queue) and time < max_time:

        # -----------------------------------------
        # ADD ARRIVING PATIENTS
        # -----------------------------------------

        arriving = [p for p in patients if p.arrival <= time]

        for p in arriving:
            waiting_queue.append(p)
            patients.remove(p)

            events.append({
                "time": time,
                "event": "PATIENT_ARRIVAL",
                "patient": p.id
            })

        # -----------------------------------------
        # DOCTOR ASSIGNMENT
        # -----------------------------------------

        for doctor in doctors:

            if doctor.free_time <= time:

                compatible_patients = [
                    p for p in waiting_queue
                    if is_compatible(p, doctor)
                ]

                if not compatible_patients:
                    continue

                # choose best patient using priority
                best_patient = max(
                    compatible_patients,
                    key=lambda p: priority_score(p, time)
                )

                best_patient.start = time
                best_patient.end = time + best_patient.treatment
                best_patient.doctor = doctor.id

                doctor.free_time = best_patient.end

                waiting_queue.remove(best_patient)
                completed_patients.append(best_patient)

                events.append({
                    "time": time,
                    "event": "TREATMENT_START",
                    "doctor": doctor.id,
                    "patient": best_patient.id
                })

                events.append({
                    "time": best_patient.end,
                    "event": "TREATMENT_END",
                    "doctor": doctor.id,
                    "patient": best_patient.id
                })

        # move time forward
        time += 1

    return completed_patients, events


# --------------------------------------------------
# GENERATE JSON OUTPUT
# --------------------------------------------------

# --------------------------------------------------
# GENERATE JSON OUTPUT FOR DASHBOARD
# --------------------------------------------------

def generate_output(patients, events):

    treatments = []

    total_risk = 0

    for p in patients:

        treatments.append({
            "patient": p.id,
            "start": p.start,
            "end": p.end
        })

        waiting_time = p.start - p.arrival
        total_risk += waiting_time * p.severity

    return {
        "treatments": treatments,
        "events": events,
        "risk": total_risk
    }
# --------------------------------------------------
# RUN COMPLETE SIMULATION
# --------------------------------------------------

def run_simulation():

    patients = load_patients("data/patients.csv")

    completed, events = schedule(patients)

    output = generate_output(completed, events)

    return output