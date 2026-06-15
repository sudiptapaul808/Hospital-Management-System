# HMS Backend – Model & ORM Design Notes

This document explains the backend data model, how entities relate to each other,
and why certain design decisions were made.  
It is written for future reference and clarity, not as an API reference.

---

## Core Identity Layer

### User
Represents authentication and identity only.

**Responsibilities**
- Login credentials
- Role management (patient / doctor / admin)
- Account-level flags (blacklisted)

**Non-responsibilities**
- Medical data
- Appointments
- Referrals

**Relationships**
- One-to-one with `Patient`
- One-to-one with `Doctor`

User is intentionally kept clean and generic.

---

## Medical Domain Entities

### Patient
Represents the medical subject of the system.

**Responsibilities**
- Medical attributes (age, gender)
- Admission state
- Referral state
- Appointment ownership
- Assignment to doctor

**Key Fields**
- `is_admitted`: whether patient is currently admitted
- `is_referred`: whether patient currently has an active referral

---

### Doctor
Represents a medical provider.

**Responsibilities**
- Belongs to one or more departments
- Sets availability
- Can be assigned patients
- Can refer patients

Doctors do NOT:
- own referral state
- book appointments for patients

---

### SpecializationDept
Represents hospital departments (e.g., Cardiology, Emergency).

**Used for**
- Doctor affiliations
- Referral destinations
- Availability context

Emergency is treated as a department.

---

## Referral Design

### Concept
Referral is modeled as **patient state**, not appointment state.

Doctors do not book appointments.
They only give direction.

---

### Referral Fields (on Patient)

- `referred_by_doctor_id`
- `referred_to_dept_id`
- `referred_to_doctor_id` (nullable – especially for Emergency)
- `referral_date`
- `is_referred`

---

### Referral Lifecycle

1. Doctor refers patient  
   → `is_referred = True`
2. Patient sees referral in dashboard
3. Patient books appointment on their own
4. Appointment completes
5. Referral resolved  
   → `is_referred = False`

Referral data is **never deleted**.

---

### Emergency Referral

For Emergency:
- `referred_to_dept_id = Emergency`
- `referred_to_doctor_id = NULL`

Emergency handles assignment internally.

---

## Appointment Design

### Appointment
Represents a scheduled visit between patient and doctor.

**Responsibilities**
- Scheduling
- Visit lifecycle

**Status Enum**
- `booked`
- `completed`
- `cancelled`

Referral is **not** an appointment status.

Appointments do not carry referral meaning.

---

## Assignment & Admission

### AssignedPatient
Represents active assignment of patient to doctor.

- One active assignment per patient
- Used for admitted or emergency care

---

## History & Records

### PatientHistory
Represents completed medical records.

**Used for**
- Diagnoses
- Treatments
- Audit trail

This table is append-only by nature.

---

## Availability & Presence

### DoctorAvailability
Represents when and where a doctor is available.

**Fields**
- doctor
- date
- start_time
- end_time

Availability is used to:
- compute doctor presence
- show booking slots
- determine department presence

---

### Presence Design

Doctor presence is **derived**, not stored.

Computed using:
- current date
- current time
- availability windows

No polling.
No background jobs.
Admin-only visibility.

---

## Department Membership

### DoctorDepartment
Join table for many-to-many relationship between:
- Doctor
- SpecializationDept

Doctors may belong to multiple departments.

---

## ORM Rules of Thumb

- ForeignKey lives where the ID is stored
- Relationships exist for convenience, not symmetry
- Multiple FKs to the same table require `foreign_keys`
- Avoid unnecessary backrefs
- Model real-world ownership, not UI convenience

---

## Explicit Non-Goals

- No auto-booking on referral
- No real-time doctor tracking
- No deletion of referral history
- No appointment-based referrals

---

## Mental Model Summary

- User = identity
- Patient = medical state
- Doctor = medical actor
- Appointment = visit
- Referral = instruction
- Availability = presence context
