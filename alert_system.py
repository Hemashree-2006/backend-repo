def generate_alerts(waiting_patients, current_time):

    alerts = []

    for p in waiting_patients:

        waiting = current_time - p.arrival

        if p.severity >= 4 and waiting > 5:

            alerts.append({
                "patient": p.id,
                "severity": p.severity,
                "waiting_time": waiting,
                "alert": "CRITICAL PATIENT WAITING"
            })

    return alerts