from application.models import Doctor, AssignedPatient, Patient, SpecializationDept, Referrals, Appointment
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from application.cache import cache_get, cache_delete, cache_set, cache_delete_pattern

def get_doctors_paginated(page, per_page):
    doctor_page = (
        Doctor.query.options(
            joinedload(Doctor.user),
            joinedload(Doctor.departments)
            #, joinedload(Doctor.assigned_patients) Forgot the use, add this if needed
            #     .joinedload(AssignedPatient.patient)
            #     .joinedload(Patient.user)
        ).paginate(page=page, per_page=per_page, error_out=False)
    )
    
    return {
        "doctors": [
            {
                "doctor_id": doc.id,
                "doctor_name": doc.user.username,
                "department_names": [dept.department_name for dept in doc.departments],
                "department_ids": [dept.id for dept in doc.departments],
                "email": doc.user.email,
                # "assigned_patients": [ap.patient.user.username for ap in doc.assigned_patients],  I forgot why I added this. Add it later if needed
                "blacklisted": doc.user.blacklisted
            } for doc in doctor_page.items
        ],
        "pagination": {
            "page": doctor_page.page,
            "per_page": doctor_page.per_page,
            "total": doctor_page.total
        }
    }
    
def get_departments_belonging_to_a_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if not doctor:
        return {"error": "Doctor doesn't exist"}, 404
    departments = doctor.departments
    return {
        "departments": [
            {
                "id": dept.id,
                "name": dept.department_name
            } for dept in departments
        ]
    }
    
def create_opd_referral(doctor, patient_id, dept_id, referred_to_doc_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"error": "Patient doesn't exist"}, 404
    if patient.is_admitted:
        return {"error": "Patient is currently admitted"}, 400
    
    department = SpecializationDept.query.get(dept_id)
    if not department:
        return {"error": "Department doesn't exist"}, 404
    
    referred_to_doc = None
    if referred_to_doc_id:
        referred_to_doc = Doctor.query.get(referred_to_doc_id)
        if not referred_to_doc:
            return {"error": "Doctor being referred to doesn't exist"}, 404
    
    if referred_to_doc:
        if department not in referred_to_doc.departments:
            return {"error": "Doctor doesn't belong to the selected department"}, 400
        
    existing = Referrals.query.filter(
        Referrals.patient_id == patient.id,
        Referrals.referral_type == ReferralTypeEnum.OPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).first()
    
    if existing:
        return {"error": "A referral already pending for this patient"}, 400
    
    referral = Referrals(
        patient_id=patient.id,
        referred_by_doctor_id=doctor.id,
        referred_to_dept_id=department.id,
        referred_to_doctor_id=referred_to_doc.id if referred_to_doc else None,
        referral_date=datetime.now(),
        referral_type=ReferralTypeEnum.OPD,
        referral_status=ReferralStatusEnum.pending
    )
    try:
        db.session.add(referral)
        db.session.commit()
        cache_delete_pattern("admin_opd_referrals_page_*")
        return {"message": "Patient referred successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": "Error when referring patient"}, 500
    
    
def create_ipd_referral(doctor, patient_id, dept_id, referred_to_doc_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"error": "Patient doesn't exist"}, 404
    if not patient.is_admitted:
        return {"error": "Patient is currently not admitted"}, 400
    if not patient.assigned_to or patient.assigned_to.doctor_id != doctor.id:
        return {"error": "Patient is not assigned to you"}, 403
    
    dept = SpecializationDept.query.get(dept_id)
    if not dept:
        return {"error": "Department doesn't exist"}, 404
    
    referred_to_doc = None
    if referred_to_doc_id:
        referred_to_doc = Doctor.query.get(referred_to_doc_id)
        if not referred_to_doc:
            return {"error": "The doctor this patient is being referred to doesn't exist"}, 404
        if dept not in referred_to_doc.departments:
            return {"error": "Doctor doesn't belong to the selected department"}, 400
        
    existing = Referrals.query.filter(
        Referrals.patient_id == patient_id, 
        Referrals.referral_type == ReferralTypeEnum.IPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).first()
    
    if existing:
        return {"error": "Referral approval pending!"}, 400
    
    referral = Referrals(
        patient_id=patient.id,
        referred_by_doctor_id=doctor.id,
        referred_to_dept_id=dept.id,
        referred_to_doctor_id=referred_to_doc.id if referred_to_doc else None,
        referral_date=datetime.now(),
        referral_type=ReferralTypeEnum.IPD,
        referral_status=ReferralStatusEnum.pending
    )
    
    try:
        db.session.add(referral)
        db.session.commit()
        return {"message": "Patient refer request sent, waiting for approval"}, 201
    except Exception:
        db.session.rollback()
        return {"error": "Error Referring patient"}, 500