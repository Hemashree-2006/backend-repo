def forecast(waiting_patients):

    if len(waiting_patients) == 0:
        return 0

    avg_severity = sum(p.severity for p in waiting_patients) / len(waiting_patients)

    forecast_risk = avg_severity * len(waiting_patients) * 2

    return round(forecast_risk, 2)