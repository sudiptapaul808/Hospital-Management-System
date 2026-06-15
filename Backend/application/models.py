from enum import unique
import enum
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash

class RoleEnum(enum.Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"

class AppointmentStatusEnum(enum.Enum):
    booked = "booked"
    completed = "completed"
    cancelled = "cancelled"
    
class ReferralTypeEnum(enum.Enum):
    OPD = "OPD"
    IPD = "IPD"
    
class ReferralStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.Text, nullable = False)
    email = db.Column(db.Text, unique = True, nullable = False)
    password = db.Column(db.Text, nullable = False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.patient)  #send it to json as user.role.value
    blacklisted = db.Column(db.Boolean, default=False)
    
    patient = db.relationship("Patient", backref="user", uselist=False)
    doctor = db.relationship("Doctor", backref="user", uselist=False)
    
    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)

    def check_password(self, input_password):
        return check_password_hash(self.password, input_password)
    
class Doctor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    departments = db.relationship("SpecializationDept", secondary="doctordepartment", backref="doctors")
    assigned_patients = db.relationship('AssignedPatient', backref='doctor', cascade="all, delete-orphan")
    
class Patient(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    age = db.Column(db.Integer, nullable = False)
    gender = db.Column(db.Text, nullable = False) 
    is_admitted = db.Column(db.Boolean, default=False)
    assigned_to = db.relationship("AssignedPatient", backref="patient", uselist=False, cascade="all, delete-orphan")
    
class AssignedPatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    
class PatientHistory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable = False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable = False)
    department = db.Column(db.Text, nullable = False)
    visit_type = db.Column(db.Text, nullable = False) 
    test_done = db.Column(db.Text)
    diagnosis_date = db.Column(db.Date, nullable = False)
    diagnosis = db.Column(db.Text, nullable = False)
    medicine = db.Column(db.Text, nullable = False)
    patient = db.relationship("Patient", backref = "patient_histories")
    doctor = db.relationship("Doctor", backref = "patient_histories")  
    
class Appointment(db.Model):
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'appointment_datetime', name='unique_doctor_slot'), #a doctor cannot have two appointment at the same time. This also ensures safety for race conditions
        db.UniqueConstraint('patient_id', 'appointment_datetime', name='unique_patient_slot') #patient cannot attend two appointment at the same time
    )
    id = db.Column(db.Integer, primary_key = True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable = False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable = False)
    department_id = db.Column(db.Integer, db.ForeignKey("specialization_dept.id"), nullable = False) #This has been added later, once the availabilities were assiciated with departments
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatusEnum), nullable=False)
    
    patient = db.relationship("Patient", backref="appointments")
    doctor = db.relationship("Doctor", backref="appointments")
    department = db.relationship("SpecializationDept", backref="appointments") 
    
class Referrals(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable = False)
    referred_by_doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable = False)
    referred_to_dept_id = db.Column(db.Integer, db.ForeignKey("specialization_dept.id"), nullable = False) 
    referred_to_doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable = True) #Might be null in case of emergency referrals
    referral_date = db.Column(db.DateTime, nullable = False)
    
    #flags
    referral_type = db.Column(db.Enum(ReferralTypeEnum), nullable = False)
    referral_status = db.Column(db.Enum(ReferralStatusEnum), nullable = False, default = ReferralStatusEnum.pending)
    
    #relationships
    patient = db.relationship("Patient", backref = "referrals")
    referred_by = db.relationship("Doctor", foreign_keys = [referred_by_doctor_id], backref = "referrals_made")
    referred_to = db.relationship("Doctor", foreign_keys = [referred_to_doctor_id], backref = "referrals_received")
    department = db.relationship("SpecializationDept", backref = "referrals")
    
class SpecializationDept(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    department_name = db.Column(db.Text, nullable = False, unique = True)
    description = db.Column(db.Text)
    
class DoctorDepartment(db.Model):
    __tablename__ = "doctordepartment"
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), primary_key=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('specialization_dept.id'), primary_key=True)
    
class DoctorAvailability(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "doctor_id",
            "department_id",
            "date",
            name="unique_doctor_department_day"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("specialization_dept.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)        
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)    

    doctor = db.relationship("Doctor", backref="availabilities")
    department = db.relationship("SpecializationDept", backref="availabilities")

