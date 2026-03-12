class Patient:

    def __init__(self, pid, severity, arrival, treatment, spec):

        self.id = pid
        self.severity = int(severity)
        self.arrival = int(arrival)
        self.treatment = int(treatment)
        self.spec = spec

        self.start = None
        self.end = None
        self.doctor = None


class Doctor:

    def __init__(self, did, spec):

        self.id = did
        self.spec = spec
        self.free_time = 0