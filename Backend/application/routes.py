from typing_extensions import Doc
from flask import current_app as app, jsonify, request, abort
from .models import *
from flask_jwt_extended import create_access_token, current_user, jwt_required, get_jwt_identity
from functools import wraps
from datetime import date, datetime, time, timedelta
from application.cache import cache_get, cache_delete, cache_set, cache_delete_pattern
from sqlalchemy.orm import joinedload
#services
from application.services.department_service import *
from application.services.doctor_service import *
from application.services.patient_service import *
#concurrency control while creating a new row. (check models.py)
from sqlalchemy.exc import IntegrityError

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200

@app.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    user = current_user
    return jsonify({
        "email": user.email,
        "role": user.role.value 
    })

#RBAC decorator
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            # if current_user.role.value != required_role:
            if not current_user or current_user.role.value != required_role:
                return jsonify(message = "unauthorized"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

#Blacklist check decorator.
def blacklist_check(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).one_or_none()
        
        if user.blacklisted:
            return jsonify({"error": "Your account has been blacklisted"}), 403
        return fn(*args, **kwargs)
    return wrapper

#LOGIN FOR ALL
@app.route("/api/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    
    user = User.query.filter_by(email=email).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Wrong Email or Password"), 401
    
    if user.blacklisted:
        return jsonify({"error": "Your Account has been Blacklisted"}), 403
    access_token = create_access_token(identity=user)
    return jsonify({
        "access_token": access_token,
        "role": user.role.value
    })


####################################### ADMIN ROUTES ###############################################
@app.route("/api/admin_dashboard/summary", methods=["GET"])
@role_required("admin")
def admin_summary():
    cache_key = "admin_summary"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    summary = [
        {"label": "Doctors", "value": User.query.filter(User.role == RoleEnum.doctor).count()},
        {"label": "Patients", "value": User.query.filter(User.role == RoleEnum.patient).count()},
        {"label": "Appointments", "value": Appointment.query.count()},
        {"label": "Departments", "value": SpecializationDept.query.count()}
    ]
    cache_set(cache_key, summary)
    return jsonify(summary)

@app.route("/api/admin/doctors/currently_available", methods=["GET"])
@role_required("admin")
def currently_available_doctors():
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    
    currently_available = DoctorAvailability.query.options(
        joinedload(DoctorAvailability.doctor).joinedload(Doctor.user),
        joinedload(DoctorAvailability.department)
    ).filter(
        DoctorAvailability.date == today,
        DoctorAvailability.start_time <= current_time,
        DoctorAvailability.end_time > current_time
    ).all()
    
    data = [
        {
            "doctor_id": c.doctor_id,
            "doctor_name": c.doctor.user.username,
            "department": c.department.department_name,
            "start_time": c.start_time.strftime("%H:%M"),
            "end_time": c.end_time.strftime("%H:%M")
        } for c in currently_available
    ]
    
    return jsonify(data)

# @app.route("/api/admin_dashboard/patients", methods=["GET"])
# @role_required("admin") #jwt_required embedded in this
# def admin_patients(): #late make sure to add another result, i.e, the departments data as well. 
#     patients_page = int(request.args.get("patients_page", 1))
#     per_page = int(request.args.get("per_page", 10))
    
#     cache_key = f"admin_patients_page_{patients_page}_per_{per_page}"
#     cached = cache_get(cache_key)
#     if cached:
#         return jsonify(cached)

#     patients_query = User.query.filter(User.role == RoleEnum.patient).paginate(page=patients_page, per_page=per_page, error_out=False)
#     patients_data = []
#     for u in patients_query.items:
#         histories = [
#             {
#                 "id": h.id,
#                 "doctor_id": h.doctor_id,
#                 "doctor_name": h.doctor.user.username,
#                 "diagnosis_date": h.diagnosis_date.isoformat(),
#                 "department": h.department,
#                 "visit_type": h.visit_type,
#                 "test_done": h.test_done,
#                 "diagnosis": h.diagnosis,
#                 "medicine": h.medicine
#             } for h in u.patient.patient_histories
#         ]
#         patients_data.append({
#                 "id": u.id,
#                 "username": u.username,
#                 "email": u.email,
#                 "role": u.role.value,
#                 "age": u.patient.age,
#                 "gender": u.patient.gender,
#                 "admission": u.patient.is_admitted,
#                 "medical_history": histories
#             })
#     response = {
#         "patients": {
#             "data": patients_data,
#             "pagination": {
#                 "page": patients_query.page,
#                 "per_page": patients_query.per_page,
#                 "total": patients_query.total
#             }
#         }
#     }
    
#     cache_set(cache_key, response)
    
#     return jsonify(response)

@app.route("/api/admin_dashboard/patients", methods=["GET"])
@role_required("admin")
def admin_patients_list():
    patients_page = int(request.args.get("patients_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"admin_patients_page_{patients_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    patients_query = User.query.filter(
        User.role == RoleEnum.patient
    ).paginate(page=patients_page, per_page=per_page, error_out=False)
    
    patients_data = []
    for u in patients_query.items:
        patients_data.append({
                "patient_id": u.id,
                "patient_name": u.username,
                "age": u.patient.age,
                "gender": u.patient.gender,
                "admission": u.patient.is_admitted,
            })
    response = {
        "patients": patients_data,
        "pagination": {
            "page": patients_query.page,
            "per_page": patients_query.per_page,
            "total": patients_query.total
        }
    }
    
    cache_set(cache_key, response)
    
    return jsonify(response)

#add approval for referrals for IPD patients.
@app.route("/api/admin_dashboard/admitted_patients", methods=["GET"])
@role_required("admin")
def admitted_patients():
    patients_page = int(request.args.get("patients_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"admin_admitted_patients_page_{patients_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    admitted_patients = Patient.query.options(
        joinedload(Patient.user),
        joinedload(Patient.assigned_to)
            .joinedload(AssignedPatient.doctor)
            .joinedload(Doctor.user)
    ).filter(
        Patient.is_admitted == True
    ).paginate(page=patients_page, per_page=per_page, error_out=False)
    
    pending_referral_patient_ids = {  #here we're making a set to check which patient id's have pending ipd referral. 
        referral.patient_id
        for referral in
        Referrals.query.filter(
            Referrals.referral_type == ReferralTypeEnum.IPD,
            Referrals.referral_status == ReferralStatusEnum.pending
        ).all()
    }

    data = []
    for p in admitted_patients.items:
        data.append({
            "patient_id": p.id,
            "patient_name": p.user.username,
            "age": p.age,
            "gender": p.gender,
            "is_referral_pending": p.id in pending_referral_patient_ids
        })

    response = {
        "patients": data,
        "pagination": {
            "page": admitted_patients.page,
            "per_page": admitted_patients.per_page,
            "total": admitted_patients.total
        }
    }
    
    cache_set(cache_key, response)
    
    return jsonify(response), 200
    
@app.route("/api/admin_dashboard/doctors", methods=["GET"])
@role_required("admin") 
def admin_doctors():   
    doctors_page = int(request.args.get("doctors_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"admin_doctors_page_{doctors_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    doctors = get_doctors_paginated(doctors_page, per_page)
    
    response = doctors
    
    cache_set(cache_key, response)
    
    return jsonify(response)
    
# @app.route("/api/admin_dashboard/upcoming_appointments", methods=["GET"])
# @role_required("admin") 
# def admin_upcoming_appointments():
#     upcoming_appointments_page = int(request.args.get("upcoming_appointments_page", 1))
#     per_page = int(request.args.get("per_page", 10))
    
#     cache_key = f"admin_upcoming_appointments_page_{upcoming_appointments_page}_per_{per_page}"
#     cached = cache_get(cache_key)
#     if cached:
#         return jsonify(cached)
    
#     upcoming_appointments_query = Appointment.query.filter(Appointment.appointment_datetime >= datetime.now()).order_by(Appointment.appointment_datetime.asc()).paginate(page=upcoming_appointments_page, per_page=per_page, error_out=False)
#     upcoming_appointments_data = [
#         {
#             "id": a.id,
#             "patient_id": a.patient_id,
#             "doctor_id": a.doctor_id,
#             "doctor_name": a.doctor.user.username,
#             "patient_name": a.patient.user.username,
#             "appointment_time": a.appointment_datetime.isoformat(),
#             "status": a.status.value
#         } for a in upcoming_appointments_query.items
#     ]
    
#     response = {
#         "upcoming_appointments": {
#             "data": upcoming_appointments_data,
#             "pagination": {
#                 "page": upcoming_appointments_query.page,
#                 "per_page": upcoming_appointments_query.per_page,
#                 "total": upcoming_appointments_query.total
#             }
#         },
#     }
    
#     cache_set(cache_key, response)
    
#     return jsonify(response)
    
# @app.route("/api/admin_dashboard/passed_appointments", methods=["GET"])
# @role_required("admin") 
# def admin_passed_appointments():
#     passed_appointments_page = int(request.args.get("passed_appointments_page", 1))
#     per_page = int(request.args.get("per_page", 10))
    
#     cache_key = f"admin_passed_appointments_page_{passed_appointments_page}_per_{per_page}"
#     cached = cache_get(cache_key)
#     if cached:
#         return jsonify(cached)
    
#     passed_appointments_query = Appointment.query.filter(Appointment.appointment_datetime <= datetime.now()).order_by(Appointment.appointment_datetime.asc()).paginate(page=passed_appointments_page, per_page=per_page, error_out=False)
#     passed_appointments_data = [
#         {
#             "id": a.id,
#             "patient_id": a.patient_id,
#             "doctor_id": a.doctor_id,
#             "doctor_name": a.doctor.user.username,
#             "patient_name": a.patient.user.username,
#             "appointment_time": a.appointment_datetime.isoformat(),
#             "status": a.status.value
#         } for a in passed_appointments_query.items
#     ]
    
#     response = {
#         "passed_appointments": {
#             "data": passed_appointments_data,
#             "pagination": {
#                 "page": passed_appointments_query.page,
#                 "per_page": passed_appointments_query.per_page,
#                 "total": passed_appointments_query.total
#             }
#         },
#     }
    
#     cache_set(cache_key, response)
    
#     return jsonify(response)
    
@app.route("/api/admin_dashboard/departments", methods=["GET"])
@role_required("admin") 
def admin_departments():
    departments_page = int(request.args.get("departments_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"admin_departments_page_{departments_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    departments = get_departments_paginated(departments_page, per_page)
    
    response = departments
    
    cache_set(cache_key, response)
    
    return jsonify(response)

# @app.route("/api/admin_dashboard/opd_referrals", methods=["GET"])
# @role_required("admin")
# def admin_opd_referrals_page():
#     referrals_page = int(request.args.get("referrals_page", 1))
#     per_page = int(request.args.get("per_page", 10))
    
#     cache_key = f"admin_opd_referrals_page_{referrals_page}_per_{per_page}"
#     cached = cache_get(cache_key)
    
#     if cached:
#         return jsonify(cached)
    
#     referred_patients_query = (
#         Referrals.query.options(
#             joinedload(Referrals.patient).joinedload(Patient.user),
#             joinedload(Referrals.referred_by).joinedload(Doctor.user),
#             joinedload(Referrals.department),
#             joinedload(Referrals.referred_to).joinedload(Doctor.user)
#         ).filter(Referrals.referral_type == ReferralTypeEnum.OPD)
#         .order_by(Referrals.referral_date.desc())
#         .paginate(page=referrals_page, per_page=per_page, error_out=False)
#     )
#     referral_data = [
#         {
#             "referral_id": r.id,
            
#             "patient_id": r.patient_id,
#             "patient_name": r.patient.user.username,
            
#             "referred_by_doctor_id": r.referred_by_doctor_id,
#             "referred_by_doctor_name": r.referred_by.user.username,
            
#             "referred_to_department_id": r.referred_to_dept_id,
#             "referred_to_department_name": r.department.department_name, 
            
#             "referred_to_doctor_id": r.referred_to_doctor_id, #we don't need if else even though nullable = True here cause we're not working with objects
#             "referred_to_doctor_name": r.referred_to.user.username if r.referred_to else None, #This if else cause it will cause error for nullable = True stuff AND we're storing objects here
            
#             "referral_date": r.referral_date.isoformat() if r.referral_date else None
#         } for r in referred_patients_query.items
#     ]
    
#     response = {
#         "referrals": {
#             "data": referral_data,
#             "pagination": {
#                 "page": referred_patients_query.page,
#                 "per_page": referred_patients_query.per_page,
#                 "total": referred_patients_query.total
#             }
#         }
#     }
#     cache_set(cache_key, response)
    
#     return jsonify(response)

@app.route("/api/admin/<int:doctor_id>/availabilities", methods=["GET"])
@role_required("admin")
def get_doctor_availabilities(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    today = datetime.now().date()
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=6)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= start_date,
        DoctorAvailability.date <= end_date
    ).order_by(DoctorAvailability.date.asc()).all()
    
    availability_map = {}
    for a in availabilities:
        if a.date in availability_map:
            availability_map[a.date].append(a)
        else:
            availability_map[a.date] = [a]
    
    data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        if date in availability_map:
            data.append({
                "date": date.isoformat(),
                "status": "set"
            })
        else:
            data.append({
                "date": date.isoformat(),
                "status": "not set"
            })
    return jsonify(data)

@app.route("/api/admin/<int:doctor_id>/availabilities_by_date", methods=["GET"])
@role_required("admin")
def get_availabilities_by_date(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    date_str = request.args.get("date")
    
    if not date_str:
        return jsonify({"error": "Date is required"}), 400
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    #Now we get the availabilities for THIS DOCTOR for THIS DATE
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date == date_obj
    ).order_by(DoctorAvailability.start_time.asc()).all()
    
    data = [
        {
            "id": a.id,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.user.username,
            "department_id": a.department_id,
            "department_name": a.department.department_name,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M")
        } for a in availabilities
    ]
    
    return jsonify(data)
        

@app.route("/api/add_department", methods=["POST"])
@role_required("admin")
def add_dept():
    data = request.json
    
    department_name = data.get("department_name")
    description = data.get("description")
    
    if not department_name:
        return jsonify({"error": "Missing fields"}), 400
    
    existing_dept = SpecializationDept.query.filter_by(department_name=department_name).first()
    if existing_dept:
        return jsonify({"error": "Department already exists"}), 400
    try:
        new_dept = SpecializationDept(department_name=department_name, description=description)
        
        db.session.add(new_dept)
        db.session.commit()
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_departments_page_*")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("doctor_departments_page_*")
        cache_delete_pattern("patient_departments_page_*")
    
        return jsonify({
            "id": new_dept.id,
            "department_name": new_dept.department_name,
            "description": new_dept.description
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Couldn't create a new department"}), 500
    
@app.route("/api/delete_department/<int:dept_id>", methods=["DELETE"])
@role_required("admin")
def delete_dept(dept_id):
    dept = SpecializationDept.query.get(dept_id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404
    
    try:
        DoctorDepartment.query.filter_by(dept_id=dept_id).delete()
        
        db.session.delete(dept)
        db.session.commit()
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_departments_page_*")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("doctor_departments_page_*")
        cache_delete_pattern("patient_departments_page_*")
        
        return jsonify({"message": "Department deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete department", "Details": str(e)}), 500
    
@app.route("/api/edit_department/<int:dept_id>", methods=["PATCH"])
@role_required("admin")
def edit_dept(dept_id):
    data = request.json
    
    department_name = data.get("department_name")
    description = data.get("description")
    
    department = SpecializationDept.query.get(dept_id)
    if not department:
        return jsonify({"error": "Department not found"}), 404
    
    if department_name:
        existing = SpecializationDept.query.filter(
            SpecializationDept.department_name == department_name,
            SpecializationDept.id != dept_id
        ).first()
        if existing:
            return jsonify({"error": "Another department with that name already exists"}), 400
        department.department_name = department_name
    
    if description:
        department.description = description
    try:
        db.session.commit()
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_departments_page_*")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("doctor_departments_page_*")
        cache_delete_pattern("patient_departments_page_*")
        
        return jsonify({
            "message": "Department updated successfully",
            "department": {
                "id": department.id,
                "department_name": department.department_name,
                "description": department.description
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Couldn't update department", "details": str(e)}), 500
    

@app.route("/api/add_doctor", methods=["POST"])
@role_required("admin")
def add_doctor():
    data = request.json
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    department_ids = data.get("department_ids")
    
    if not username or username.strip() == "":
        return jsonify({"error": "Username cannot be empty"}), 400
    if not email or email.strip() == "":
        return jsonify({"error": "Email cannot be empty"}), 400
    if not password or password.strip() == "":
        return jsonify({"error": "Password cannot be empty"}), 400
    if department_ids is None or len(department_ids) == 0:
        return jsonify({"error": "Atleast one department required"}), 400
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email in use"}), 400
    
    depts = SpecializationDept.query.filter(SpecializationDept.id.in_(department_ids)).all()
    if len(depts) != len(department_ids):
        return jsonify({"error": "One or more departments not found"}), 400
    
    
    try:
        new_user = User(username=username, email=email, role=RoleEnum.doctor)
        new_user.set_password(password)
        db.session.add(new_user)
        
        new_doctor = Doctor() #inside parenthesis, new_user.doctor doesn't work since we haven't commited it yet
        new_doctor.departments = depts
        new_user.doctor = new_doctor
        db.session.add(new_user)
        
        db.session.commit()  # commit everything at once
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("patient_doctors_page_*")
        
    except Exception as e:
        db.session.rollback()  # undo everything
        return jsonify({"error": "Failed to add doctor", "details": str(e)}), 500
    
    return jsonify({
        "message": "Doctor added successfully",
        "doctor": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "departments": [d.department_name for d in depts]
        }
    }), 201

@app.route("/api/edit_doctor/<int:doctor_id>", methods=["PUT"])
@role_required("admin")
def edit_doctor(doctor_id):
    data = request.json
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    department_ids = data.get("department_ids")
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    user = doctor.user
    
    if not username or username.strip() == "":
        return jsonify({"error": "username cannot be empty"}), 400
    
    if not email or email.strip() == "":
        return jsonify({"error": "Email cannot be empty"}), 400
    
    existing = User.query.filter(User.email == email, User.id != user.id).first()
    if existing:
        print("existing block print is working")
        return jsonify({"error": "Email already in use"}), 400
    
    user.email = email
    user.username = username
    if password:
        user.set_password(password)
        
    if department_ids is not None:
        depts = SpecializationDept.query.filter(SpecializationDept.id.in_(department_ids)).all()
        if len(depts) != len(department_ids):
            return jsonify({"error": "One or more departments not found"}), 400
        doctor.departments = depts
    
    try:
        db.session.commit()
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("patient_doctors_page_*")
        return jsonify({
        "message": "Doctor updated successfully",
        "doctor": {
            "id": doctor.id,
            "username": user.username,
            "email": user.email,
            "departments": [d.department_name for d in doctor.departments]
        }
    }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update doctor", "details": str(e)}), 500
    
    

@app.route("/api/delete_doctor/<int:doctor_id>", methods=["DELETE"])
@role_required("admin")
def delete_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    try:
        DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()

        Appointment.query.filter_by(doctor_id=doctor_id).delete()

        AssignedPatient.query.filter_by(doctor_id=doctor_id).delete()

        PatientHistory.query.filter_by(doctor_id=doctor_id).delete()

        doctor.departments.clear()

        db.session.delete(doctor)

        user = User.query.get(doctor_id)
        if user:
            db.session.delete(user)

        db.session.commit()
        cache_delete("admin_summary")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("patient_doctors_page_*")
        return jsonify({"message": "Doctor deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to delete doctor",
            "details": str(e)
        }), 500

@app.route("/api/admin/availability/<int:doctor_id>/create", methods=["POST"])
@role_required("admin")
def create_availability(doctor_id):
    data = request.json
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    date_str = data.get("date")
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    selected_department = data.get("selected_department")
    
    if not all([date_str, start_time_str, end_time_str, selected_department]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try: #this is for if the payload for any date is sent like "banana" or something like that, then the route will break if we directly use strptime
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400
    
    if end_time <= start_time:
        return jsonify({"error": "End time must be later than start time"}), 400
    
    department = SpecializationDept.query.get_or_404(selected_department)
    
    if department not in doctor.departments:
        return jsonify({"error": "The doctor doesn't belong from the selected department"}), 400
    
    existing = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date == date,
        DoctorAvailability.start_time < end_time,
        DoctorAvailability.end_time > start_time,
    ).first()
    
    if existing:
        return jsonify({"error": "Doctor already has availability in another department during this time"}), 409
    
    new_slot = DoctorAvailability(
        doctor_id=doctor_id,
        department_id=department.id,
        date=date,
        start_time=start_time,
        end_time=end_time
        )

    try:
        db.session.add(new_slot)
        db.session.commit()
        return jsonify({"message": "New slot created"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Slot already created"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@app.route("/api/admin/availability/<int:availability_id>/update", methods=["PATCH"])
@role_required("admin")
def update_availability(availability_id):
    slot = DoctorAvailability.query.get_or_404(availability_id)
    
    data = request.json
    
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    selected_department = data.get("selected_department")
    
    start_time = slot.start_time
    end_time = slot.end_time

    if start_time_str:
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid start time format"}), 400
    if end_time_str:
        try:
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid end time format"}), 400
    
    if end_time <= start_time:
        return jsonify({"error": "End time must be later than start time"}), 400
    
    start_dt = datetime.combine(slot.date, start_time)
    end_dt = datetime.combine(slot.date, end_time)

    conflict = Appointment.query.filter(
        Appointment.doctor_id == slot.doctor_id,
        Appointment.appointment_datetime >= start_dt,
        Appointment.appointment_datetime < end_dt,
        Appointment.department_id == slot.department_id,
        Appointment.status == AppointmentStatusEnum.booked
    ).first()

    if conflict:
        return jsonify({
            "error": "Cannot update availability because booked appointments exist for this date"
        }), 400
    
    existing = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == slot.doctor.id,
        DoctorAvailability.date == slot.date,
        DoctorAvailability.start_time < end_time,
        DoctorAvailability.end_time > start_time,
        DoctorAvailability.id != slot.id #So that it doesn't detect itself!
    ).first()
    
    if existing: #This check is for making sure the doctor is not set to be in two departments at once. This includes overlapping times or the same time but different departments
        return jsonify({"error": "Doctor already has availability in another department during this time"}), 409
    
    slot.start_time = start_time
    slot.end_time = end_time
    if selected_department:
        department = SpecializationDept.query.get_or_404(selected_department)
        
        if department not in slot.doctor.departments:
            return jsonify({"error": "Doctor doesn't belong from the selected department"}), 409
        
        slot.department_id = department.id
        
    try:
        db.session.commit()
        return jsonify({"message": "Updated"}), 200 
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Slot already created"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@app.route("/api/admin/availability/<int:availability_id>/delete", methods=["DELETE"])
@role_required("admin")
def delete_availability(availability_id):
    slot = DoctorAvailability.query.get_or_404(availability_id)
    
    start_dt = datetime.combine(slot.date, slot.start_time)
    end_dt = datetime.combine(slot.date, slot.end_time)

    conflict = Appointment.query.filter(
        Appointment.doctor_id == slot.doctor_id,
        Appointment.appointment_datetime >= start_dt,
        Appointment.appointment_datetime < end_dt,
        Appointment.department_id == slot.department_id,
        Appointment.status == AppointmentStatusEnum.booked
    ).first()

    if conflict:
        return jsonify({
            "error": "Cannot delete availability because booked appointments exist"
        }), 400
    
    try:
        db.session.delete(slot)
        db.session.commit()
        return jsonify({"message": "Slot deleted successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "error deleting slot"}), 500


#This route will return - 1) Histories from history services 
                        # 2) The last 5 past appointments
                        # 3) The upcoming appointments and pending referrals
                        # 4) And ofcourse the basic information about the patient
                        
from sqlalchemy import desc
from sqlalchemy import asc
@app.route("/api/admin/<int:patient_id>/view", methods=["GET"])
@role_required("admin")
def admin_view_patient(patient_id):
    patient = User.query.get_or_404(patient_id)
    
    past_appointments = (
        Appointment.query.options(
            joinedload(Appointment.patient).joinedload(Patient.user),
            joinedload(Appointment.doctor).joinedload(Doctor.user),
            joinedload(Appointment.department)
        ).filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_datetime <= datetime.today()
        ).order_by(desc(Appointment.appointment_datetime)).limit(5).all()
    )
    
    upcoming_appointments = (
        Appointment.query.options(
            joinedload(Appointment.patient).joinedload(Patient.user),
            joinedload(Appointment.doctor).joinedload(Doctor.user),
            joinedload(Appointment.department)
        ).filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_datetime >= datetime.today()
        ).order_by(asc(Appointment.appointment_datetime)).all()
    )
    
    pending_referrals = (
        Referrals.query.options(
            joinedload(Referrals.patient).joinedload(Patient.user),
            joinedload(Referrals.referred_by).joinedload(Doctor.user),
            joinedload(Referrals.referred_to).joinedload(Doctor.user),
            joinedload(Referrals.department)
        ).filter(
            Referrals.patient_id == patient.id,
            Referrals.referral_status == ReferralStatusEnum.pending
        ).all()
    )
    
    assigned_departments = [
        department.department_name 
        for department in patient.patient.assigned_to.doctor.departments
    ] if patient.patient.assigned_to else []
        
    past_appointments_data = []
    for p in past_appointments:
        past_appointments_data.append({
            "id": p.id,
            "patient_id": p.patient_id,
            "patient_name": p.patient.user.username,
            "doctor_id": p.doctor_id,
            "doctor_name": p.doctor.user.username,
            "department_id": p.department_id, 
            "department_name": p.department.department_name,
            "datetime": p.appointment_datetime.isoformat(),
            "status": p.status.value
        })
    
    upcoming_appointments_data = []
    for p in upcoming_appointments:
        upcoming_appointments_data.append({
            "id": p.id,
            "patient_id": p.patient_id,
            "patient_name": p.patient.user.username,
            "doctor_id": p.doctor_id,
            "doctor_name": p.doctor.user.username,
            "department_id": p.department_id, 
            "department_name": p.department.department_name,
            "datetime": p.appointment_datetime.isoformat(),
            "status": p.status.value
        })
        
    pending_referrals_data = []
    for r in pending_referrals:
        pending_referrals_data.append({
            "id": r.id,
            "patient_id": r.patient_id,
            "referred_by_doctor_id": r.referred_by_doctor_id,
            "referred_by_doctor_name": r.referred_by.user.username,
            "referred_to_department_id": r.referred_to_dept_id,
            "referred_to_department_name": r.department.department_name,
            "referred_to_doctor_id": r.referred_to_doctor_id if r.referred_to else None,
            "referred_to_doctor_name": r.referred_to.user.username if r.referred_to else None,
            "referral_date": r.referral_date.isoformat()
        })
        
    return jsonify({
        "patient_details": {
            "id": patient.id,
            "name": patient.username,
            "email": patient.email,
            "blacklisted": patient.blacklisted,
            "age": patient.patient.age,
            "gender": patient.patient.gender,
            "is_admitted": patient.patient.is_admitted,
            "assigned_doctor_id": patient.patient.assigned_to.doctor_id if patient.patient.assigned_to else None,
            "assigned_doctor_name": patient.patient.assigned_to.doctor.user.username if patient.patient.assigned_to else None,
            "assigned_department": assigned_departments
        },
        "past_appointments": past_appointments_data,
        "upcoming_appointments": upcoming_appointments_data,
        "pending_referrals": pending_referrals_data
    }), 200

@app.route("/api/add_patient", methods=["POST"])
@role_required("admin")
def admin_add_patient():
    data = request.json
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age")
    gender = data.get("gender")
    admission = bool(data.get("admission", False))#this is false by default and True if the user selects yes
    
    if not username or not email or not password or not age or not gender:
        return jsonify({"error": "Missing required field(s)"}), 400
    
    existing_patient = User.query.filter_by(email=email).first()
    if existing_patient:
        return jsonify({"error": "Email in use"}), 400
    
    try:
        new_user = User(username=username, email=email, role=RoleEnum.patient)
        new_user.set_password(password)
        db.session.add(new_user)
        
        new_patient = Patient() #inside parenthesis, new_user.doctor doesn't work since we haven't commited it yet
        new_patient.age = age
        new_patient.gender = gender
        new_patient.is_admitted = admission
        new_user.patient = new_patient
        db.session.add(new_user)
        
        db.session.commit()  # commit everything at once
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_patients_page_*")
        
    except Exception as e:
        db.session.rollback()  # undo everything
        return jsonify({"error": "Failed to add patient", "details": str(e)}), 500
    
    return jsonify({
        "message": "Patient added successfully",
        "patient": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    }), 201
    
# @app.route("/api/delete_patient/<int:patient_id>", methods=["DELETE"])
# @role_required("admin")
# def admin_delete_patients(patient_id):
#     patient = Patient.query.get(patient_id)
#     if not patient:
#         return jsonify({"error": "Patient not found"}), 404
    
#     try:
#         db.session.delete(patient)
        
#         user = User.query.get(patient_id)
#         if user:
#             db.session.delete(user)
            
#         db.session.commit()
        
#         cache_delete("admin_summary")
#         cache_delete_pattern("admin_patients_page_*")
        
#         return jsonify({"message": "Patient deleted successfully"}), 200
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": "Failed to delete patient", "details": str(e)}), 500
    
@app.route("/api/admin/patient/<int:patient_id>/edit", methods=["PUT"])
@role_required("admin")
def admin_edit_patient(patient_id):
    data = request.json
    
    username = data.get("username")
    email = data.get("email")
    age = data.get("age")
    gender = data.get("gender")
    admission = data.get("admission")
    
    patient = (
        Patient.query
        .filter(Patient.id == patient_id)
        .with_for_update()
        .first_or_404()
    )
    user = patient.user
    
    if not username or username.strip() == "":
        return jsonify({"error": "Username cannot be empty"}), 400
    if not email or email.strip() == "":
        return jsonify({"error": "Email cannot be empty"}), 400
    existing = User.query.filter(User.email == email, User.id != user.id).first()
    if existing:
        return jsonify({"error": "Email already in use"}), 400
    user.email = email
    user.username = username
    
    if age is None:
        return jsonify({"error": "Age required"}), 400
    
    if not gender or gender.strip() == "":
        return jsonify({"error": "Gender required"}), 400
    
    patient.age = age
    patient.gender = gender
    
    #The admin can only admit and not discharge. The discharge power stays in the hands of the assigned doctor
    if admission is True and patient.is_admitted is False:
        #set all the OPD referrals for this patient to "cancelled" (if any)
        Referrals.query.filter(
            Referrals.patient_id == patient.id,
            Referrals.referral_type == ReferralTypeEnum.OPD,
            Referrals.referral_status == ReferralStatusEnum.pending
        ).update({
            "referral_status": ReferralStatusEnum.cancelled
        })
        #And also cancel all the future appointments made by the patient since he/she is now admitted.
        Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == AppointmentStatusEnum.booked,
            Appointment.appointment_datetime > datetime.now()
        ).update({
            "status": AppointmentStatusEnum.cancelled
        })
        patient.is_admitted = admission
    
    try:
        db.session.commit()
        
        cache_delete_pattern("admin_patients_page_*")
        cache_delete_pattern("admin_opd_referrals_page_*")
        cache_delete_pattern("admin_admitted_patients_page_*")
        
        return jsonify({
            "message": "Patient updated successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Failed to update patient"}), 500
    
@app.route("/api/admin/<int:user_id>/toggle_blacklist", methods=["PATCH"])
@role_required("admin")
def toggle_blacklist(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role.value == "admin":
        return jsonify({"error": "Cannot blacklist admin"}), 400
    
    #check if the user is a doctor and if yes, then check if he has any appointments or patients assigned to him. If yes, then we don't allow soft delete
    if user.role == RoleEnum.doctor:
        doctor = user.doctor
        
        active_appointments_count = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_datetime >= datetime.now(),
            Appointment.status == AppointmentStatusEnum.booked
        ).count()
        
        if active_appointments_count > 0:
            return jsonify({"error": f"Dr. {user.username} has {active_appointments_count} active appointments"}), 400
        
        active_assigned_patients_count = AssignedPatient.query.filter(
            AssignedPatient.doctor_id == doctor.id
        ).count()
        
        if active_assigned_patients_count > 0:
            return jsonify({"error": f"Dr. {user.username} has {active_assigned_patients_count} IPD patients assigned"}), 400
        
    #check if the user is a patient and don't soft delete if the user is IPD or has an appointment or referral
    if user.role == RoleEnum.patient:
        patient = user.patient
        
        print(patient.is_admitted)
        print(patient.id)
        print(patient.user.username)
        if patient.is_admitted:
            return jsonify({"error": f"Patient {user.username} is currently admitted"}), 400
        
        active_appointments_count = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_datetime >= datetime.now(),
            Appointment.status == AppointmentStatusEnum.booked
        ).count()
        
        if active_appointments_count > 0:
            return jsonify({"error": f"Patient {user.username} has {active_appointments_count} active appointments"}), 400
        
        active_referrals_count = Referrals.query.filter(
            Referrals.patient_id == patient.id,
            Referrals.referral_type == ReferralTypeEnum.OPD,
            Referrals.referral_status == ReferralStatusEnum.pending
        ).count()
        
        if active_referrals_count > 0:
            return jsonify({"error": f"Patient {user.username} has {active_referrals_count} pending referrals"}), 400
        
    user.blacklisted = not user.blacklisted
    if user.blacklisted:
        action = "blacklisted" 
    else:
        action = "unblacklisted"
    
    try:
        db.session.commit()
        cache_delete("admin_summary")
        cache_delete_pattern("admin_doctors_page_*")
        cache_delete_pattern("admin_patients_page_*")
        return jsonify({
            "message": f"User {action} successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "blacklisted": user.blacklisted
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Error blacklisting user", "details": str(e)}), 500

    
@app.route("/api/admin/get_patient_histories/<int:patient_id>", methods=["GET"])
@role_required("admin")
def admin_patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    page = int(request.args.get("histories_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    histories = get_patient_history(patient.id, page, per_page)
    
    response = {
        "patient_id": patient.id,
        "patient_name": patient.user.username,
        "histories": histories
    }
    
    return jsonify(response)

# @app.route("/api/admin/get_assign_data/<int:patient_id>", methods=["GET"])
# @role_required("admin")
# def get_assign_data(patient_id):
#     assignment = AssignedPatient.query.filter_by(patient_id=patient_id).first()

#     if not assignment:
#         return jsonify({
#             "assigned_doctor": None
#         }), 200

#     doctor = assignment.doctor

#     return jsonify({
#         "assigned_doctor": {
#             "doctor_id": doctor.id,
#             "username": doctor.user.username
#         }
#     }), 200

@app.route("/api/admin/<int:patient_id>/assign", methods=["PATCH"])
@role_required("admin")
def assign_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "patient doesn't exist"}), 404
    data = request.json
    doctor_id = data.get("doctor_id")
    if not doctor_id:
        return jsonify({"error": "Doctor ID is required"}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    
    if patient.assigned_to:
        patient.assigned_to.doctor_id = doctor_id
    else:
        new_assignment = AssignedPatient(doctor_id=doctor_id, patient_id=patient.id)
        db.session.add(new_assignment)
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Patient assigned successfully",
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500
    
@app.route("/api/admin/ipd_referral_approval", methods=["GET"])
@role_required("admin")
def pending_referral_approvals():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    pending_approvals = Referrals.query.options(
        joinedload(Referrals.patient)
            .joinedload(Patient.user),
        joinedload(Referrals.referred_by)
            .joinedload(Doctor.user),
        joinedload(Referrals.referred_to)
            .joinedload(Doctor.user),
        joinedload(Referrals.department)
    ).filter(
        Referrals.referral_type == ReferralTypeEnum.IPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).order_by(
        Referrals.referral_date.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    data = [
        {
            "referral_id": a.id,
            "patient_id": a.patient_id,
            "patient_name": a.patient.user.username,
            "referred_by_doctor_id": a.referred_by_doctor_id,
            "referred_by_doctor_name": a.referred_by.user.username,
            "referred_to_dept_id": a.referred_to_dept_id,
            "referred_to_dept_name": a.department.department_name,
            "referred_to_doctor_id": a.referred_to_doctor_id,
            "referred_to_doctor_name": a.referred_to.user.username if a.referred_to else None,
            "referral_date": a.referral_date.isoformat() if a.referral_date else None
        } for a in pending_approvals.items
    ]
    
    return jsonify({
        "data": data,
        "pagination": {
            "page": pending_approvals.page,
            "per_page": pending_approvals.per_page,
            "total": pending_approvals.total
        }
    })
    
@app.route("/api/check_ipd_referral/<int:referral_id>", methods=["GET"])
def check_ipd_referral(referral_id):
    referral = Referrals.query.options(
        joinedload(Referrals.patient).joinedload(Patient.user),
        joinedload(Referrals.referred_by).joinedload(Doctor.user).joinedload(Doctor.departments),
        joinedload(Referrals.referred_to).joinedload(Doctor.user),
        joinedload(referrals.department)
    ).filter_by(id=referral_id).first_or_404()
    
    if referral.referral_type != ReferralTypeEnum.IPD or referral.referral_status != ReferralStatusEnum.pending:
        return jsonify({"error": "Wrong patient"}), 400
    
    docs_in_department = doctors_belonging_from_the_department(referral.referred_to_dept_id)
    
    response = {
        "referral": {
            "referral_id": referral.id,
            "referral_date": referral.referral_date.isoformat(),

            "patient": {
                "id": referral.patient_id,
                "name": referral.patient.user.username,
                "age": referral.patient.age,
                "gender": referral.patient.gender
            },

            "from_doctor": {
                "id": referral.referred_by_doctor_id,
                "name": referral.referred_by.user.username,
                "department": [dept.department_name for dept in referral.referred_by.departments]
            },

            "requested_department": {
                "id": referral.referred_to_dept_id,
                "name": referral.department.department_name
            },

            "suggested_doctor": {
                "id": referral.referred_to_doctor_id,
                "name": referral.referred_to.user.username if referral.referred_to else None
            }
        },

        "available_doctors": docs_in_department
    }
    
    return jsonify(response)

@app.route("/api/admin/ipd_referral/complete/<int:referral_id>", methods=["PATCH"])
@role_required("admin")
def complete_ipd_referral(referral_id):
    referral = Referrals.query.get_or_404(referral_id)
    
    patient = (
        Patient.query
        .filter(Patient.id == referral.patient_id)
        .with_for_update() #locking in the patient object
        .first_or_404()
    )
    
    db.session.refresh(referral) #after say admin A is doing work on this patient, and the me(admin) is waiting for the lock, so after the lock has been opened I will still have the previous referral obj cause we fetched referral before we locked the patient, so we sort of refresh it so that we don't get the "previous" fetched data
    
    if referral.referral_status != ReferralStatusEnum.pending:
        return jsonify({"error": "The referral isn't pending anymore"}), 409
        
    if referral.referral_type != ReferralTypeEnum.IPD:
        return jsonify({"error": "The referral is not for an IPD patient"}), 409
    
    if not patient.is_admitted:
        return jsonify({"error": "Patient has been discharged"}), 409
    
    assignment = (
        AssignedPatient.query
        .filter(AssignedPatient.patient_id == patient.id)
        .first()
    )
    
    referred_by_doctor = Doctor.query.get_or_404(referral.referred_by_doctor_id)
    department = SpecializationDept.query.get_or_404(referral.referred_to_dept_id)
    referred_to_doctor = None
    if referral.referred_to_doctor_id:
        referred_to_doctor = Doctor.query.get_or_404(referral.referred_to_doctor_id)
        belongs = DoctorDepartment.query.filter(
            DoctorDepartment.doctor_id == referred_to_doctor.id,
            DoctorDepartment.department_id == department.id
        ).first() #This prevents loading everything
        
        if not belongs:
            return jsonify({"error": "The doctor being referred to doesn't belong to the referred department"}), 400
    
    if not assignment or assignment.doctor_id != referred_by_doctor.id:
        return jsonify({"error": "The doctor making the referral request is not assigned to this patient"}), 409
    

    #The referred_to_doctor actually exists in the referral object
    if referred_to_doctor:
        #Now we do the assignment logic
        assignment.doctor_id = referred_to_doctor.id
        #mark the referral as completed
        referral.referral_status = ReferralStatusEnum.completed
        
    #else we get the payload that will be sent by the admin
    else:
        data = request.json
        
        if not data:
            return jsonify({"error": "Missing payload"}), 400
        
        doctor_id = data.get("admin_doctor_selection")
        if not doctor_id:
            return jsonify({"error": "Doctor selection required"}), 400
        selected_doctor = Doctor.query.get_or_404(doctor_id)
        
        belongs = DoctorDepartment.query.filter(
            DoctorDepartment.doctor_id == selected_doctor.id,
            DoctorDepartment.department_id == department.id
        ).first()
        if not belongs:
            return jsonify({"error": "The doctor selected doesn't belong to the suggested department"}), 400
        
        assignment.doctor_id = selected_doctor.id
        
        #mark the referral as completed
        referral.referral_status = ReferralStatusEnum.completed
        
    try:
        db.session.commit()
        return jsonify({
            "message": "Referral completed successfully",
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500
    
@app.route("/api/admin/ipd_referral/cancel/<int:referral_id>", methods=["PATCH"])
@role_required("admin")
def cancel_ipd_referral(referral_id):
    referral = Referrals.query.get_or_404(referral_id)
    
    patient = (
        Patient.query
        .filter(Patient.id == referral.patient_id)
        .with_for_update()
        .first_or_404()
    )
    db.session.refresh(referral)
    
    if referral.referral_status != ReferralStatusEnum.pending:
        return jsonify({"error": "This referral isn't pending anymore"}), 409
    if referral.referral_type != ReferralTypeEnum.IPD:
        return jsonify({"error": "This referral doesn't belong to an IPD patient"}), 409
    
    if not patient.is_admitted:
        return jsonify({"error": "Patient has been discharged"}), 409
    
    referral.referral_status = ReferralStatusEnum.cancelled
    
    try:
        db.session.commit()
        return jsonify({
            "message": "Referral cancelled successfully",
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500
    

#This is the pop up that fills the pop up with the name of all the departments
@app.route("/api/admin/all_departments", methods=["GET"])
@role_required("admin")
def all_departments():
    all_departments = get_all_departments()
    response = all_departments
    return jsonify(response)

#The second pop up that the admin finds after clicking on the department name
@app.route("/api/admin/departments/<int:department_id>/doctors", methods=["GET"])
@role_required("admin")
def doctors_from_department(department_id):
    response = doctors_belonging_from_the_department(department_id)
    return jsonify(response)

# @app.route("/api/admin/doctors_list", methods=["GET"]) #for the pop up of doctors name when assigning them
# @role_required("admin")
# def doctors_list():
#     doctors = Doctor.query.all()
#     if not doctors:
#         return jsonify({"doctors": []}), 200

#     return jsonify({
#         "doctors": [
#             {
#                 "id": d.id,
#                 "name": d.user.username,
#                 "departments": [dept.department_name for dept in d.departments]
#             } for d in doctors
#         ]
#     }), 200
    
#Search Doctors and Patients
@app.route("/api/find_doctor_page/<int:doctor_id>", methods=["GET"])
@role_required("admin")
def find_doctor_page(doctor_id):
    per_page = request.args.get("per_page", 10, type=int)

    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    doctor_ids = [d.id for d in doctors]

    if doctor_id not in doctor_ids:
        return jsonify({"error": "Doctor not found", "page": 1}), 404

    index = doctor_ids.index(doctor_id)
    page = (index // per_page) + 1

    return jsonify({"page": page}), 200


@app.route("/api/find_patient_page/<int:patient_id>", methods=["GET"])
@role_required("admin")
def find_patient_page(patient_id):
    per_page = request.args.get("per_page", 10, type=int)

    patients = Patient.query.order_by(Patient.id.asc()).all()
    patient_ids = [p.id for p in patients]

    if patient_id not in patient_ids:
        return jsonify({"error": "Patient not found", "page": 1}), 404

    index = patient_ids.index(patient_id)
    page = (index // per_page) + 1

    return jsonify({"page": page}), 200

@app.route("/api/admin_search", methods=["GET"])
@role_required("admin")
def admin_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    # Search doctors
    doctor_results = User.query.filter(
        User.role == RoleEnum.doctor,
        User.username.ilike(f"%{q}%")
    ).all()

    # Search patients
    patient_results = User.query.filter(
        User.role == RoleEnum.patient,
        User.username.ilike(f"%{q}%")
    ).all()

    results = []

    for d in doctor_results:
        results.append({
            "id": d.id,
            "name": d.username,
            "type": "doctor"
        })

    for p in patient_results:
        results.append({
            "id": p.id,
            "name": p.username,
            "type": "patient"
        })

    return jsonify(results), 200



    
####################################### DOCTOR ROUTES ###############################################
@app.route("/api/doctor/dashboard", methods=["GET"])
@role_required("doctor")
@blacklist_check
def doctor_dashboard():
    doctor = current_user.doctor

    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    today_count = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_datetime >= start_of_day,
        Appointment.appointment_datetime < end_of_day
    ).count()

    upcoming_count = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_datetime >= end_of_day
    ).count()

    assigned_count = AssignedPatient.query.filter(
        AssignedPatient.doctor_id == doctor.id
    ).count()

    return jsonify({
        "doctor": {
            "id": doctor.id,
            "name": doctor.user.username
        },
        "summary": {
            "today_appointments": today_count,
            "upcoming_appointments": upcoming_count,
            "assigned_patients": assigned_count
        }
    }), 200

#today's appointments
#add_pagination here
@app.route("/api/doctor/current_day_appointments", methods=["GET"])
@role_required("doctor")
@blacklist_check
def current_day_appointments():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    doctor = current_user.doctor
    
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1) 
    
    todays_appointments = (
        Appointment.query
        .options(
            joinedload(Appointment.patient)
                .joinedload(Patient.user)
        )
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_datetime >= start_of_day,
            Appointment.appointment_datetime < end_of_day,
            Appointment.status == AppointmentStatusEnum.booked
        )
        .order_by(Appointment.appointment_datetime.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    response = {
        "data": [
            {
                "id": appt.id,
                "datetime": appt.appointment_datetime.isoformat(),
                "status": appt.status.value,
                "patient": {
                    "id": appt.patient.id,
                    "name": appt.patient.user.username,
                    "age": appt.patient.age,
                    "gender": appt.patient.gender
                }
            } for appt in todays_appointments.items
        ],
        "pagination": {
            "page": todays_appointments.page,
            "per_page": todays_appointments.per_page,
            "total": todays_appointments.total
        }
    }
    
    return jsonify(response)

#upcomming appointments 
#add pagination here as well
@app.route("/api/doctor/upcoming_appointments", methods=["GET"])
@role_required("doctor")
@blacklist_check
def doctor_upcoming_appointments():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    doctor = current_user.doctor
    
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    upcoming_appointments = (
        Appointment.query
        .options(
            joinedload(Appointment.patient)
                .joinedload(Patient.user)
        )
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_datetime >= end_of_day
        )
        .order_by(Appointment.appointment_datetime.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    response = {
        "data": [
            {
                "id": appt.id,
                "datetime": appt.appointment_datetime.isoformat(),
                "status": appt.status.value,
                "patient": {
                    "id": appt.patient.id,
                    "name": appt.patient.user.username,
                    "age": appt.patient.age,
                    "gender": appt.patient.gender,
                }
            } for appt in upcoming_appointments.items
        ],
        "pagination": {
            "page": upcoming_appointments.page,
            "per_page": upcoming_appointments.per_page,
            "total": upcoming_appointments.total
        }
    }
    return jsonify(response)
    
#Assigned_patients tab
#pagination required
@app.route("/api/doctor/assigned_patients", methods=["GET"])
@role_required("doctor")
@blacklist_check
def doctor_assigned_patients():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    doctor = current_user.doctor

    assigned_patients = (
        AssignedPatient.query
        .options(
            joinedload(AssignedPatient.patient)
                .joinedload(Patient.user)
        )
        .filter(
            AssignedPatient.doctor_id == doctor.id
        )
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    response = {
        "data": [
            {
                "patient_id": p.patient.id,
                "name": p.patient.user.username,
                "age": p.patient.age,
                "gender": p.patient.gender,
            } for p in assigned_patients.items
        ],
        "pagination": {
            "page": assigned_patients.page,
            "per_page": assigned_patients.per_page,
            "total": assigned_patients.total
        }
    }
    return jsonify(response)
    
@app.route("/api/doctor/<int:patient_id>/details", methods=["GET"])
@role_required("doctor")
@blacklist_check
def view_patient_details(patient_id):
    patient = User.query.get_or_404(patient_id)
    doctor = current_user.doctor
    
    pending_ipd_referral = Referrals.query.filter(
        Referrals.patient_id == patient_id,
        Referrals.referred_by_doctor_id == doctor.id,
        Referrals.referral_type == ReferralTypeEnum.IPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).first()
    
    return jsonify({
        "patient_details": {
            "id": patient.id,
            "name": patient.username,
            "age": patient.patient.age,
            "gender": patient.patient.gender
        },
        "pending_ipd_referral": {
            "id": pending_ipd_referral.id if pending_ipd_referral else None,
            "status": pending_ipd_referral.referral_status if pending_ipd_referral else None,
            "referred_to_doctor_name": pending_ipd_referral.referred_to.user.username if pending_ipd_referral else None,
        }
    })

@app.route("/api/doctor/<int:patient_id>/history", methods=["GET"])
@role_required("doctor")
@blacklist_check
def view_patient_history(patient_id):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    patient = Patient.query.get_or_404(patient_id)
    
    doctor = current_user.doctor
    
    has_appointment = Appointment.query.filter(Appointment.doctor_id == doctor.id, Appointment.patient_id == patient.id).first()
    is_assigned = AssignedPatient.query.filter(AssignedPatient.doctor_id == doctor.id, AssignedPatient.patient_id == patient.id).first()
    
    if not has_appointment and not is_assigned:
        return jsonify({"message": "Unauthorized"}), 403
    
    histories = get_patient_history(patient.id, page, per_page)
    response = {
        "patient_id": patient.id,
        "patient_name": patient.user.username,
        "histories": histories
    }
    return jsonify(response)
    
@app.route("/api/doctor/new/<int:patient_id>/history", methods=["POST"])
@role_required("doctor")
@blacklist_check
def update_patient_history(patient_id):
    data = request.get_json()

    diagnosis = data.get("diagnosis")
    medicine = data.get("medicine")
    test_done = data.get("test_done", "")
    #Get the department
    department = data.get("department")
    #Check if doctor belong to that department
    #then make the history

    if not diagnosis or not medicine or not department:
        return jsonify({"error": "Diagnosis and medicine are required"}), 400

    doctor = current_user.doctor
    doctor_id = doctor.id
    
    allowed_departments = [
        dept.department_name for dept in doctor.departments
    ]

    if department not in allowed_departments:
        return jsonify({"error": "You do not belong to this department"}), 403
    
    patient = Patient.query.get_or_404(patient_id)
    visit_type = "IPD" if patient.is_admitted else "OPD"

    diagnosis_date = date.today()

    try:
        new_history = PatientHistory(
            patient_id=patient_id,
            doctor_id=doctor_id,
            department=department,
            visit_type=visit_type,
            test_done=test_done,
            diagnosis_date=diagnosis_date,
            diagnosis=diagnosis,
            medicine=medicine
        )

        db.session.add(new_history)
        db.session.commit()
        
        cache_delete_pattern("admin_patients_page_*")

        return jsonify({
            "message": "History added successfully",
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

#This route is to get all the departments a doctor belongs to, for selecting department while adding histories
@app.route("/api/doctor/departments", methods=["GET"])
@role_required("doctor")
@blacklist_check
def departments_of_doctor():
    doctor = current_user.doctor
    departments = get_departments_belonging_to_a_doctor(doctor.id)
    return jsonify(departments)
    
@app.route("/api/doctor/appointment/<int:appointment_id>/complete", methods=["PATCH"])
@role_required("doctor")
@blacklist_check
def mark_appointment_complete(appointment_id):
    data = request.get_json()
    patient_id = data.get("patient_id")
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = current_user.doctor
    
    try:
        #“Change this appointment to completed only if it is still booked right now.” This is another concurrency control where a doctor might select completed and the patient might select cancelled depending on networks and other stuffs the later one gets saved. So instead of having the checks outside of the fetch, we literally embed it into the query that changes the status, we do it in real time so the time between check and execution isn't there, not even nano seconds. We do it real time. 
        rows = Appointment.query.filter(
            Appointment.id == appointment_id,
            Appointment.patient_id == patient.id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatusEnum.booked
        ).update({
            "status": AppointmentStatusEnum.completed
        })
        db.session.commit()
        
        if rows == 0:
            return jsonify({"error": "Appointment already handled"}), 409
        
        cache_delete_pattern("admin_upcoming_appointments_page_*")
        cache_delete_pattern("admin_passed_appointments_page_*")
        cache_delete("admin_summary")
        
        return jsonify({
            "message": "Appointment marked as complete",
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

#Doctor Referrals
@app.route("/api/department_list", methods=["GET"])
@role_required("doctor")
@blacklist_check
def get_department_list():
    departments_page = int(request.args.get("departments_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"doctor_departments_page_{departments_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    departments = get_departments_paginated(departments_page, per_page)
    
    response = {
        "departments": departments
    }
    
    cache_set(cache_key, response)
    
    return jsonify(response)

#Get the list of doctors based on the department clicked.
@app.route("/api/list_doctors/<int:department_id>", methods=["GET"])
@role_required("doctor")
@blacklist_check
def doctors_from_the_department(department_id):
    doctors_list = doctors_belonging_from_the_department(department_id)
    
    response = {
        "doctors_from_the_department": doctors_list
    }
    
    return jsonify(response)
    
#Now upon clicking the doctor name, we refer the patient
@app.route("/api/refer_OPD_patient/<int:patient_id>", methods=["PATCH"])
@role_required("doctor")
@blacklist_check
def refer_OPD_patient(patient_id):
    doctor = current_user.doctor
    data = request.json
    
    if not data or "referred_to_dept_id" not in data:
        return jsonify({"error": "Department is required"}), 400
    
    dept_id = data.get("referred_to_dept_id")
    referred_to_doc_id = data.get("referred_to_doctor_id")
    
    response, status = create_opd_referral(doctor, patient_id, dept_id, referred_to_doc_id)
    
    return jsonify(response), status    

@app.route("/api/doctor/availabilities", methods=["GET"])
@role_required("doctor")
@blacklist_check
def get_doctor_availabilities_doctor_side():
    doctor = current_user.doctor
    
    today = datetime.now().date()
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=6)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= start_date,
        DoctorAvailability.date <= end_date
    ).order_by(DoctorAvailability.date.asc()).all()
    
    availability_map = {}
    for a in availabilities:
        if a.date in availability_map:
            availability_map[a.date].append(a)
        else:
            availability_map[a.date] = [a]
    
    data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        if date in availability_map:
            data.append({
                "date": date.isoformat(),
                "status": "set"
            })
        else:
            data.append({
                "date": date.isoformat(),
                "status": "not set"
            })
    return jsonify(data)

@app.route("/api/doctor/availabilities_by_date", methods=["GET"])
@role_required("doctor")
@blacklist_check
def get_availabilities_by_date_doctor_side():
    doctor = current_user.doctor
    date_str = request.args.get("date")
    
    if not date_str:
        return jsonify({"error": "Date is required"}), 400
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    #Now we get the availabilities for THIS DOCTOR for THIS DATE
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date == date_obj
    ).order_by(DoctorAvailability.start_time.asc()).all()
    
    data = [
        {
            "id": a.id,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.user.username,
            "department_id": a.department_id,
            "department_name": a.department.department_name,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M")
        } for a in availabilities
    ]
    
    return jsonify(data)

@app.route("/api/doctor/availability/create", methods=["POST"])
@role_required("doctor")
@blacklist_check
def doctor_create_availability():
    doctor = current_user.doctor

    data = request.json

    date_str = data.get("date")
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    selected_department = data.get("selected_department")
    
    if not all([date_str, start_time_str, end_time_str, selected_department]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400
    
    if end_time <= start_time:
        return jsonify({"error": "End time must be later than start time"}), 400
    
    department = SpecializationDept.query.get_or_404(selected_department)
    
    if department not in doctor.departments:
        return jsonify({"error": "The doctor doesn't belong from the selected department"}), 400

    existing = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date == date,
        DoctorAvailability.start_time < end_time,
        DoctorAvailability.end_time > start_time,
    ).first()
    
    if existing:
        return jsonify({"error": "Doctor already has availability in another department during this time"}), 409
    
    new_slot = DoctorAvailability(
        doctor_id=doctor.id,
        department_id=department.id,
        date=date,
        start_time=start_time,
        end_time=end_time
    )

    try:
        db.session.add(new_slot)
        db.session.commit()
        return jsonify({"message": "Created", "id": new_slot.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Slot already created"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@app.route("/api/doctor/availability/<int:availability_id>/update", methods=["PATCH"])
@role_required("doctor")
@blacklist_check
def doctor_update_availability(availability_id):
    slot = DoctorAvailability.query.get_or_404(availability_id)
    
    if current_user.doctor.id != slot.doctor_id:
        return jsonify({"error": "You're not authenticated to edit this"}), 401
    
    data = request.json
    
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    selected_department = data.get("selected_department")
    
    start_time = slot.start_time
    end_time = slot.end_time

    if start_time_str:
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid start time format"}), 400
    if end_time_str:
        try:
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid end time format"}), 400
    
    if end_time <= start_time:
        return jsonify({"error": "End time must be later than start time"}), 400
    
    start_dt = datetime.combine(slot.date, slot.start_time)
    end_dt = datetime.combine(slot.date, slot.end_time)
    conflict = Appointment.query.filter(
        Appointment.doctor_id == slot.doctor_id,
        Appointment.appointment_datetime >= start_dt,
        Appointment.appointment_datetime < end_dt,
        Appointment.department_id == slot.department_id,
        Appointment.status == AppointmentStatusEnum.booked
    ).first()

    if conflict:
        return jsonify({"error": "Cannot update availability with existing booked appointments"}), 400
    
    existing = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == slot.doctor.id,
        DoctorAvailability.date == slot.date,
        DoctorAvailability.start_time < end_time,
        DoctorAvailability.end_time > start_time,
        DoctorAvailability.id != slot.id #So that it doesn't detect itself!
    ).first()
    
    if existing: #This check is for making sure the doctor is not set to be in two departments at once. This includes overlapping times or the same time but different departments
        return jsonify({"error": "Doctor already has availability in another department during this time"}), 409
    
    slot.start_time = start_time
    slot.end_time = end_time
    if selected_department:
        department = SpecializationDept.query.get_or_404(selected_department)
        
        if department not in slot.doctor.departments:
            return jsonify({"error": "Doctor doesn't belong from the selected department"}), 409
        
        slot.department_id = department.id
        
    try:
        db.session.commit()
        return jsonify({"message": "Updated"}), 200 
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Slot already created"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

@app.route("/api/doctor/availability/<int:availability_d>/delete", methods=["DELETE"])
@role_required("doctor")
@blacklist_check
def doctor_delete_availability(availability_id):
    doctor = current_user.doctor
    slot = DoctorAvailability.query.get_or_404(availability_id)

    if slot.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403

    start_dt = datetime.combine(slot.date, slot.start_time)
    end_dt = datetime.combine(slot.date, slot.end_time)

    conflict = Appointment.query.filter(
        Appointment.doctor_id == slot.doctor_id,
        Appointment.appointment_datetime >= start_dt,
        Appointment.appointment_datetime < end_dt,
        Appointment.department_id == slot.department_id,
        Appointment.status == AppointmentStatusEnum.booked
    ).first()

    if conflict:
        return jsonify({
            "error": "Cannot delete availability because booked appointments exist"
        }), 400
    
    try:
        db.session.delete(slot)
        db.session.commit()
        return jsonify({"message": "Slot deleted successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "error deleting slot"}), 500

@app.route("/api/doctor/<int:patient_id>/discharge", methods=["PATCH"])
@role_required("doctor")
@blacklist_check
def discharge_assigned_patient(patient_id):
    doctor = current_user.doctor

    patient = (
        Patient.query
        .filter(Patient.id == patient_id)
        .with_for_update()
        .first_or_404()
    )
    
    if not patient.assigned_to or patient.assigned_to.doctor_id != doctor.id:
        return jsonify({"error": "Patient not assigned to you"}), 403
    
    Referrals.query.filter(
        Referrals.patient_id == patient.id,
        Referrals.referral_type == ReferralTypeEnum.IPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).update({
        "referral_status": ReferralStatusEnum.cancelled
    })
        
    try:
        db.session.delete(patient.assigned_to)
        patient.is_admitted = False
        db.session.commit()
        cache_delete_pattern("admin_patients_page_*")
        return jsonify({"message": "Patient discharged successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while discharging the patient"}), 500

#Hand over admitted patients and this handover is to be approved by the admin
@app.route("/api/refer_IPD_patients/<int:patient_id>", methods=["PATCH"])
@role_required("doctor")
@blacklist_check
def refer_IPD_patients(patient_id):
    doctor = current_user.doctor
    data = request.json
    
    if not data or "referred_to_dept_id" not in data:
        return jsonify({"error": "Missing fields"}), 400
    
    dept_id = data.get("referred_to_dept_id")
    referred_to_doc_id = data.get("referred_to_doctor_id")
    
    response, status = create_ipd_referral(doctor, patient_id, dept_id, referred_to_doc_id)
    
    return jsonify(response), status
    
####################################### PATIENT ROUTES ###############################################
@app.route("/api/patient/patient_registration", methods=["POST"])
def patient_registration():
    data = request.json
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age")
    gender = data.get("gender")
    
    if not username or not email or not password or not age or not gender:
        return jsonify({"error": "Missing required field"}), 400
    
    existing_patient = User.query.filter_by(email=email).first()
    if existing_patient:
        return jsonify({"error": "Email in use"}), 400
    
    try:
        new_user = User(username=username, email=email, role=RoleEnum.patient)
        new_user.set_password(password)
        db.session.add(new_user)
        
        new_patient = Patient()
        new_patient.age = age
        new_patient.gender = gender
        new_user.patient = new_patient
        db.session.add(new_user)
        
        db.session.commit()
        
        cache_delete("admin_summary")
        cache_delete_pattern("admin_patients_page_*")
        
         
        
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": "Failed to register", "details": str(e)}), 500
    
    return jsonify({
        "message": "registration done successfully, login to continue",
        "patient": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    }), 201
    
@app.route("/api/patient/edit_patient", methods=["PATCH"])
@role_required("patient")
@blacklist_check
def edit_patient():
    patient = current_user.patient
    data = request.json
    
    username = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    age = data.get("age")
    gender = data.get("gender")
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    user = patient.user
    
    if username:
        user.username = username
    if email:
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return jsonify({"error": "Email already in use"}), 400
        user.email = email
    if password:
        user.set_password(password)
    if age:
        patient.age = age
    if gender:
        patient.gender = gender
    
    try:
        db.session.commit()
        cache_delete_pattern("admin_patients_page_*")
        return jsonify({
            "message": "Patient updated successfully",
            "patient": {
                "id": patient.id,
                "username": user.username,
                "email": user.email,
                "age": patient.age,
                "gender": patient.gender,
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update patient", "details": str(e)}), 500

@app.route("/api/patient/dashboard", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_dashboard():
    patient = current_user.patient

    return jsonify({
        "patient": {
            "id": patient.id,
            "name": patient.user.username,
            "email": patient.user.email,
            "admission_status": "Admitted" if patient.is_admitted else "OPD"
        }
    }), 200
    
#Appointments Tab
@app.route("/api/patient/appointments", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_dash_appointments_tab():
    patient = current_user.patient
    
    appointments = Appointment.query.options(
        joinedload(Appointment.doctor)
            .joinedload(Doctor.user)
    ).filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_datetime >= datetime.now(),
        Appointment.status != AppointmentStatusEnum.cancelled
    ).order_by(Appointment.appointment_datetime.asc()).limit(5).all()
    
    appointment_list = []
    for a in appointments:
        appointment_list.append({
            "appointment_id": a.id,
            "doctor_id": a.doctor.id,
            "doctor_name": a.doctor.user.username,
            "date": a.appointment_datetime.date().isoformat(),
            "time": a.appointment_datetime.time().strftime("%I:%M %p"),
            "status": a.status.value
        })
        
    #referral data only for OPD patients
    #if the doctor_referred_to present then we send the patient to the doctor details page
    #and if the doctor_referred_to not presenet then we send the patient to the 'doctor from department' list page
    
    OPD_patient_pending_referral = Referrals.query.options(
        joinedload(Referrals.department),
        joinedload(Referrals.referred_by)
            .joinedload(Doctor.user),
        joinedload(Referrals.referred_to)
            .joinedload(Doctor.user)
    ).filter(
        Referrals.patient_id == patient.id,
        Referrals.referral_type == ReferralTypeEnum.OPD,
        Referrals.referral_status == ReferralStatusEnum.pending
    ).first()
    
    referral_data = None
    if OPD_patient_pending_referral:
        referral_data = {
            "referral_id": OPD_patient_pending_referral.id,
            "referred_by_doctor_id": OPD_patient_pending_referral.referred_by_doctor_id,
            "referred_by_doctor_name": OPD_patient_pending_referral.referred_by.user.username,
            "referred_to_dept_id": OPD_patient_pending_referral.referred_to_dept_id,
            "referred_to_dept_name": OPD_patient_pending_referral.department.department_name,
            "referred_to_doctor_id": OPD_patient_pending_referral.referred_to_doctor_id,
            "referred_to_doctor_name": OPD_patient_pending_referral.referred_to.user.username if OPD_patient_pending_referral.referred_to else None,
            "referral_date": OPD_patient_pending_referral.referral_date.isoformat()
        }
        
    return jsonify({
        "appointments": appointment_list,
        "referrals" : referral_data
    }), 200
    
#Departments Tab
@app.route("/api/patient/department_list", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_dash_departments_tab():
    departments_page = int(request.args.get("departments_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"patient_departments_page_{departments_page}_per_{per_page}"
    cached = cache_get(cache_key)
    
    if cached:
        return jsonify(cached)
    
    departments = get_departments_paginated(departments_page, per_page)
    response = {
        "departments": departments
    }
    cache_set(cache_key, response)
    return jsonify(response)

#Doctor List tab
@app.route("/api/patient/doctors_tab", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_dash_doctors_tab():
    doctors_page = int(request.args.get("doctors_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    cache_key = f"patient_doctors_page_{doctors_page}_per_{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    
    doctors = get_doctors_paginated(doctors_page, per_page)
    
    limited_data = [
        {
            "doctor_id": doc["doctor_id"],
            "doctor_name": doc["doctor_name"],
            "departments": doc["departments"]
        } for doc in doctors["data"]
    ]
    
    response = {
        "doctors": {
            "data": limited_data,
            "pagination": doctors["pagination"]
        }
    }
    
    cache_set(cache_key, response)
    
    return jsonify(response)

#Patient_History Tab
@app.route("/api/patient/patient_history", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_dash_history_tab():
    histories_page = int(request.args.get("histories_page", 1))
    per_page = int(request.args.get("per_page", 10))
    
    patient = current_user.patient
    
    histories = get_patient_history(patient.id, histories_page, per_page)
    
    response = {
        "patient_id": patient.id,
        "patient_name": patient.user.username,
        "histories": histories
    }
    
    return jsonify(response)

@app.route("/api/patient/list_doctors/<int:department_id>", methods=["GET"])
@role_required("patient")
@blacklist_check
def patient_doctors_from_the_department(department_id):
    doctors_list = doctors_belonging_from_the_department(department_id)
    
    response = {
        "doctors_from_the_department": doctors_list
    }
    
    return jsonify(response)

@app.route("/api/patient/doctor_details/<int:doctor_id>", methods=["GET"])
@role_required("patient")
@blacklist_check
def doctor_details(doctor_id):
    doctor = Doctor.query.filter(Doctor.id == doctor_id).first()
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    departments = [dept.department_name for dept in doctor.departments] if doctor.departments else []
    return jsonify({
        "doctor_id": doctor.id,
        "doctor_name": doctor.user.username,
        "departments": departments
    }), 200

#This route needs to be redone, cause when the doctor sets which department he's gonna be in we have to effectively send that to the Patient UI as well, just to let them know that the doctor is gonna be in this said department on that day
# @app.route("/api/patient/doctors_availability/<int:doctor_id>", methods=["GET"])
# @role_required("patient")
# def doctors_availability(doctor_id):
#     today = datetime.now().date()
#     start_date = today + timedelta(days=1)
#     end_date = today + timedelta(days=7)
    
#     availabilities = DoctorAvailability.query.filter(
#         DoctorAvailability.doctor_id == doctor_id,
#         DoctorAvailability.date >= start_date,
#         DoctorAvailability.date <= end_date
#     ).order_by(DoctorAvailability.date.asc()).all()
    
#     availability_map = {a.date: a for a in availabilities}
#     data = []
    
#     for i in range(7):
#         date = start_date + timedelta(days=i)

#         if date in availability_map:
#             a = availability_map[date]
            
#             appointments = Appointment.query.filter(
#                 Appointment.doctor_id == doctor_id,
#                 db.func.date(Appointment.appointment_datetime) == date,
#                 Appointment.status == AppointmentStatusEnum.booked
#             ).all()
            
#             booked_start_times = [appt.appointment_datetime.time() for appt in appointments]
            
#             slots = []
#             current = a.start_time
#             while current < a.end_time:
#                 next_slot = (datetime.combine(date, current) + timedelta(minutes=30)).time()

#                 is_booked = current in booked_start_times

#                 slots.append({
#                     "start_time": current.strftime("%H:%M"),
#                     "end_time": next_slot.strftime("%H:%M"),
#                     "status": "booked" if is_booked else "available"
#                 })
#                 current = next_slot

#             data.append({
#                 "date": date.isoformat(),
#                 "status": "set",
#                 "start_time": a.start_time.strftime("%H:%M"),
#                 "end_time": a.end_time.strftime("%H:%M"),
#                 "slots": slots
#             })

#         else:
#             data.append({
#                 "date": date.isoformat(),
#                 "status": "not set",
#                 "start_time": None,
#                 "end_time": None,
#                 "slots": []
#             })

#     return jsonify(data)

@app.route("/api/patient/<int:doctor_id>/availabilities", methods=["GET"])
@role_required("patient")
@blacklist_check
def get_doctor_availabilities_patient_side(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    today = datetime.now().date()
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=6)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= start_date,
        DoctorAvailability.date <= end_date
    ).order_by(DoctorAvailability.date.asc()).all()
    
    availability_map = {}
    for a in availabilities:
        if a.date in availability_map:
            availability_map[a.date].append(a)
        else:
            availability_map[a.date] = [a]
    
    data = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        if date in availability_map:
            data.append({
                "date": date.isoformat(),
                "status": "set"
            })
        else:
            data.append({
                "date": date.isoformat(),
                "status": "not set"
            })
    return jsonify(data)

@app.route("/api/patient/<int:doctor_id>/availabilities_by_date", methods=["GET"])
@role_required("patient")
@blacklist_check
def get_availabilities_by_date_patient_side(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    date_str = request.args.get("date")
    
    if not date_str:
        return jsonify({"error": "Date is required"}), 400
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    #Now we get the availabilities for THIS DOCTOR for THIS DATE
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date == date_obj
    ).order_by(DoctorAvailability.start_time.asc()).all()
    
    data = [
        {
            "id": a.id,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.user.username,
            "department_id": a.department_id,
            "department_name": a.department.department_name,
            "date": a.date.isoformat(),
            "start_time": a.start_time.strftime("%H:%M"),
            "end_time": a.end_time.strftime("%H:%M")
        } for a in availabilities
    ]
    
    return jsonify(data)

@app.route("/api/patient/availability/<int:availability_id>/slots", methods=["GET"])
@role_required("patient")
@blacklist_check
def get_availability_slots_patient_side(availability_id):
    availability = DoctorAvailability.query.get_or_404(availability_id)
    
    doctor = availability.doctor
    department = availability.department
    
    date = availability.date
    start_time = availability.start_time
    end_time = availability.end_time
    
    appointments = Appointment.query.filter(
        Appointment.doctor_id == availability.doctor_id,
        Appointment.department_id == availability.department_id,
        db.func.date(Appointment.appointment_datetime) == date,
        Appointment.status == AppointmentStatusEnum.booked
    ).all()
    
    booked_start_times = {
        appt.appointment_datetime.time() for appt in appointments
    } #set
    
    slots = []
    current = start_time
    while current < end_time:
        next_slot = (datetime.combine(date, current) + timedelta(minutes=30)).time()

        is_booked = current in booked_start_times

        slots.append({
            "start_time": current.strftime("%H:%M"),
            "end_time": next_slot.strftime("%H:%M"),
            "status": "booked" if is_booked else "available"
        })
        current = next_slot
    
    return jsonify({
        "doctor_name": doctor.user.username,
        "department_name": department.department_name,
        "date": availability.date.isoformat(),
        "start_time": availability.start_time.strftime("%H:%M"),
        "end_time": availability.end_time.strftime("%H:%M"),
        "slots": slots
    })

@app.route("/api/patient/cancel_appointment/<int:appointment_id>", methods=["PATCH"])
@role_required("patient")
@blacklist_check
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    try:
        rows = Appointment.query.filter(
            Appointment.id == appointment_id,
            Appointment.status == AppointmentStatusEnum.booked
        ).update({
            "status": AppointmentStatusEnum.cancelled
        })
        
        db.session.commit()
        
        if rows == 0:
            return jsonify({"error": "Appointment already cancelled or completed"}), 409
        
        cache_delete_pattern("admin_upcoming_appointments_page_*")
        cache_delete_pattern("admin_passed_appointments_page_*")
        cache_delete("admin_summary")
        
        return jsonify({
            "message": "Appointment has been cancelled"
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Couldn't cancel the appointment"}), 500
    
@app.route("/api/patient/book", methods=["PATCH"])
@role_required("patient")
@blacklist_check
def book():
    patient = current_user.patient
    data = request.json
    doctor_id = data.get("doctor_id")
    appointment_datetime_str = data.get("appointment_datetime")
    referral_id = data.get("referral_id")
    
    appointment_datetime = datetime.fromisoformat(appointment_datetime_str)
    referral = None
    new_appointment = None
    if not referral_id:
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_datetime.date()
        ).first()
        
        if not availability:
            return jsonify({"error": "Doctor not available on this date"}), 400
        
        if not (availability.start_time <= appointment_datetime.time() < availability.end_time):
            return jsonify({"error": "Doctor not available at this time"}), 400
        
    else:
        referral = Referrals.query.filter(
            Referrals.id == referral_id,
            Referrals.patient_id == patient.id,
            Referrals.referral_status == ReferralStatusEnum.pending,
            Referrals.referral_type == ReferralTypeEnum.OPD
        ).first()
        if not referral:
            return jsonify({"error": "Referral not found or invalid"}), 404
        if referral.referred_to_doctor_id and referral.referred_to_doctor_id != doctor_id:
            return jsonify({"error": "Doctor doesn't match referral"}), 400
        
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_datetime.date()
        ).first()
        if not availability:
            return jsonify({"error": "Doctor not available on this date"}), 400
        
        if not (availability.start_time <= appointment_datetime.time() < availability.end_time):
            return jsonify({"error": "Doctor not available at this time"}), 400
    
    #Now commit everything at once         
    new_appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient.id,
        appointment_datetime=appointment_datetime,
        status=AppointmentStatusEnum.booked
    )
    if referral:
        referral.referral_status = ReferralStatusEnum.completed
    try:
        db.session.add(new_appointment)
        db.session.commit()
        
        cache_delete_pattern("admin_upcoming_appointments_page_*")
        cache_delete_pattern("admin_passed_appointments_page_*")
        cache_delete("admin_summary")
        cache_delete_pattern("admin_opd_referrals_page_*")
        
        return jsonify({
            "message": "Appointment booked successfully",
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        
        error_message = str(e.orig)

        if "unique_doctor_slot" in error_message:
            return jsonify({
                "error": "Doctor slot already booked"
            }), 409

        elif "unique_patient_slot" in error_message:
            return jsonify({
                "error": "You already have an appointment at this time"
            }), 409

        return jsonify({
            "error": "Database integrity error"
        }), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error occurred while booking appointment"
        }), 500
        
@app.route("/api/patient/cancel_referral/<int:referral_id>", methods=["PATCH"])
@role_required("patient")
@blacklist_check
def cancel_referral(referral_id):
    patient = current_user.patient
    referral = Referrals.query.filter(
                Referrals.id == referral_id,
                Referrals.patient_id == patient.id,
                Referrals.referral_status == ReferralStatusEnum.pending,
                Referrals.referral_type == ReferralTypeEnum.OPD
            ).first()
    
    if not referral:
        return jsonify({"error": "Referral not found or aleady handled"}), 400
    
    referral.referral_status = ReferralStatusEnum.cancelled
    
    try:
        db.session.commit()
        cache_delete_pattern("admin_opd_referrals_page_*")
        return jsonify({"message": "Referral cancelled"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error deleting referral"}), 500

        
        
@app.route("/api/patient/search_doctors", methods=["GET"])
@role_required("patient")
@blacklist_check
def search_doctors():
    query = request.args.get("q", "")

    if not query:
        return jsonify([]), 200

    doctors = User.query.filter(
        User.role == RoleEnum.doctor,
        User.username.ilike(f"%{query}%")
    ).all()

    return jsonify([
        {
            "doctor_id": d.doctor.id,
            "doctor_name": d.username
        }
        for d in doctors
    ]), 200
    
@app.route("/api/patient/history_exists", methods=["GET"])
@role_required("patient")
@blacklist_check
def history_exists():
    patient = current_user.patient
    count = PatientHistory.query.filter_by(patient_id=patient.id).count()

    return jsonify({
        "exists": count > 0,
        "count": count
    })



#Backend jobs manual triggers
from celery.result import AsyncResult
from .tasks import csv_report, monthly_report, daily_appointment_reminder
from flask import send_from_directory



@app.route('/export_patient_csv', methods=["GET"])
@role_required("patient")
@blacklist_check
def export_patient_history():
    patient = current_user.patient
    
    task = csv_report.delay(patient.id)
    
    return jsonify({
        "message": "Your report is being prepared.",
        "task_id": task.id
    }), 202
    
@app.route('/task_status/<task_id>')
def task_status(task_id):
    result = AsyncResult(task_id)

    if result.state == "SUCCESS":
        return jsonify({
            "state": result.state,
            "csv_file": result.result
        })

    return jsonify({"state": result.state})

@app.route('/download_csv/<filename>')
def download_csv(filename):
    return send_from_directory("static", filename, as_attachment=True)


@app.route('/api/send_mail')
def send_mail():
    task = monthly_report.delay()
    return {
        "task_id": task.id,
        "message": "Monthly report generation started"
    }    
    