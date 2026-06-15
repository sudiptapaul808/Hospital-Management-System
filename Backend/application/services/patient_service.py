from application.models import PatientHistory, Doctor
from sqlalchemy.orm import joinedload

def get_patient_history(patient_id, page, per_page):
    histories = (
        PatientHistory.query.options(
            joinedload(PatientHistory.doctor)
                .joinedload(Doctor.user)
            ).filter(PatientHistory.patient_id == patient_id)
            .order_by(PatientHistory.diagnosis_date.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    return {
        "data": [
            {
                "doctor_name": h.doctor.user.username,
                "department": h.department,
                "visit_type": h.visit_type,
                "test_done": h.test_done,
                "diagnosis_date": h.diagnosis_date.isoformat(),
                "diagnosis": h.diagnosis,
                "medicine": h.medicine
            } for h in histories.items
        ],
        "pagination": {
            "page": histories.page,
            "per_page": histories.per_page,
            "total": histories.total
        }
    }