from celery import shared_task
import csv
from jinja2 import Template
from .mail import send_email
from .models import *
from datetime import date, timedelta, datetime
import requests

#TASK 1: download csv patient history report for the patient_side
#the patient triggers this async task
@shared_task(ignore_results=False, name="download_medical_history")
def csv_report(patient_id):
    histories = (
        PatientHistory.query
        .filter_by(patient_id=patient_id)
        .order_by(PatientHistory.diagnosis_date.desc())
        .all()
    )

    csv_file_name = f"Medical_Report_{datetime.now().strftime('%f')}.csv"
    file_path = f"static/{csv_file_name}"

    with open(file_path, 'w', newline="") as csvfile:
        card_csv = csv.writer(csvfile, delimiter=',')

        card_csv.writerow([
            'Sr No.',
            'Doctor Name',
            'Department',
            'Tests',
            'Diagnosis Date',
            'Diagnosis',
            'Medicine'
        ])

        if not histories:
            card_csv.writerow([
                "-",
                "No Data",                
                "-",                  
                "-",                      
                "-",                      
                "No medical history found for this patient.", 
                "Contact hospital support if you think this is incorrect." 
            ])
            return csv_file_name

        sr_no = 1
        for h in histories:
            card_csv.writerow([
                sr_no,
                h.doctor.user.username,
                h.department,
                h.test_done or "-",
                h.diagnosis_date,
                h.diagnosis,
                h.medicine
            ])
            sr_no += 1

    return csv_file_name

#Monthly report for the doctors (the diagnosis done, patients they treated/diagnosed)
#scheduled job via crontab (start the job at the first of every month and send it on the last day of the month)
@shared_task(ignore_results=False, name="monthly_doctor_report")
def monthly_report():

    today = date.today()
    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    doctors = Doctor.query.all()
    reports_sent = 0

    for doctor in doctors:

        histories = (
            PatientHistory.query
            .filter(
                PatientHistory.doctor_id == doctor.id
                # PatientHistory.diagnosis_date >= first_day_prev_month,
                # PatientHistory.diagnosis_date <= last_day_prev_month
            )
            .order_by(PatientHistory.diagnosis_date)
            .all()
        )

        if not histories:
            continue
        
        doctor_data = {
            "username": doctor.user.username,
            "details": []
        }

        for history in histories:
            doctor_data["details"].append({
                "patient_name": history.patient.user.username,
                "test_done": history.test_done,
                "diagnosis_date": history.diagnosis_date,
                "diagnosis": history.diagnosis,
                "medicine": history.medicine,
            })

        mail_template = """
        <html>
        <body>

        <h3>Monthly Report for Dr. {{ doctor_data.username }}</h3>

        <p>Here is your monthly report for {{ first_day_prev_month }} to {{ last_day_prev_month }}:</p>

        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>#</th>
                <th>Patient Name</th>
                <th>Test Done</th>
                <th>Diagnosis Date</th>
                <th>Diagnosis</th>
                <th>Medicine</th>
            </tr>

            {% for h in doctor_data.details %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ h.patient_name }}</td>
                <td>{{ h.test_done }}</td>
                <td>{{ h.diagnosis_date }}</td>
                <td>{{ h.diagnosis }}</td>
                <td>{{ h.medicine }}</td>
            </tr>
            {% endfor %}
        </table>

        <hr>
        <p>This is an automated monthly summary from the Hospital Management System.</p>

        </body>
        </html>
        """

        body = Template(mail_template).render(
            doctor_data=doctor_data,
            first_day_prev_month=first_day_prev_month,
            last_day_prev_month=last_day_prev_month
        )

        send_email(doctor.user.email, subject="Monthly Doctor Report", message=body)
        reports_sent += 1
    
    return f"{reports_sent} monthly doctor reports sent."

#Daily reminders for the patients who have upcoming appointments (sent via G-chat webhook)
#schedule job again, maybe every morning at 10 am, the notification or the mail is sent
# @shared_task(ignore_results = False, name = "generate_msg")
# def generate_msg(patient_id):
#     patient = Patient.query.filter_by(Patient.id=patient_id).first()
#     text = f"Hi {patient.user.username}, your appointment with {doctor_username} is on {appointment_date}. Login to check at http://127.0.0.1:5000"
#     response = request.post("")
#     print(response.status_code)
#     return "Notification sent to the patient"

GOOGLE_CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAYWaFaRE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=9dz8cdZaPuBDhsAhjXAL20nt8htJK5kPXiB2VtrvVkQ"

def send_gchat_message(text: str):
    payload = {"text": text}
    response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=payload)
    print("GChat response:", response.status_code)
    return response.status_code


@shared_task(ignore_results=False, name="daily_appointment_reminder")
def daily_appointment_reminder():
    today = datetime.now().date()

    # All booked appointments that are scheduled for today
    appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_datetime) == today,
        Appointment.status == AppointmentStatusEnum.booked
    ).all()

    for app in appointments:
        patient_name = app.patient.user.username
        doctor_name = app.doctor.user.username
        appointment_time = app.appointment_datetime.strftime("%H:%M")  # time only

        text = (
            f"Hi {patient_name}, you have a hospital visit scheduled today.\n"
            f"Doctor: Dr. {doctor_name}\n"
            f"Time: {appointment_time}\n"
            "Please visit the hospital at the scheduled time. "
            "You can check details at http://127.0.0.1:5000"
        )

        send_gchat_message(text)

    return f"{len(appointments)} reminders sent for {today}"