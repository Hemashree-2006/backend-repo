def calculate_total_risk(patients):

    total = 0

    for p in patients:

        if p.start is None:
            continue

        waiting = p.start - p.arrival
        total += p.severity * waiting

    return total