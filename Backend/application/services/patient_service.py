from application.models import PatientHistory, Doctor, Referrals, ReferralStatusEnum, ReferralTypeEnum
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
                "id": h.id,
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


#Say patient has a pending OPD referral
#Now the patient sees the referral card in the dash
#Patient chooses to follow the card's flow and books the appointment (hence we complete the referral here)
#Patient decides to follow the general flow of the patient side and book that way. (in that case if the dept, doctor referred to and the patient they match) we complete the referral.
#So both the flows once referral doctor is booked, will mark the referral as completed!
def complete_matching_opd_referral(patient_id, doctor_id, department_id):
    referral = Referrals.query.filter(
        Referrals.patient_id == patient_id,
        Referrals.referred_to_doctor_id == doctor_id,
        Referrals.referred_to_dept_id == department_id,
        Referrals.referral_status == ReferralStatusEnum.pending,
        Referrals.referral_type == ReferralTypeEnum.OPD
    ).first()

    if referral:
        referral.referral_status = ReferralStatusEnum.completed