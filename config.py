import os

# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with your actual API key

# Email Configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")

# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your-twilio-account-sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your-twilio-auth-token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

# Appointment Settings
NEW_PATIENT_DURATION = 60  # minutes
RETURNING_PATIENT_DURATION = 30  # minutes
WORKING_HOURS = {
    "start": "09:00",
    "end": "17:00"
}
BREAK_TIME = "12:00-13:00"  # Lunch break

# Clinic Information
CLINIC_NAME = "HealthFirst Medical Center"
CLINIC_ADDRESS = "123 Medical Drive, Healthcare City, HC 12345"
CLINIC_PHONE = "+1-555-123-4567"
CLINIC_EMAIL = "appointments@healthfirst.com"

# Doctor Information
DOCTORS = {
    "Dr. Sarah Johnson": {
        "specialty": "Cardiology",
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "location": "Main Campus"
    },
    "Dr. Michael Chen": {
        "specialty": "Orthopedics", 
        "available_days": ["Monday", "Tuesday", "Thursday", "Friday"],
        "location": "Main Campus"
    },
    "Dr. Emily Rodriguez": {
        "specialty": "Pediatrics",
        "available_days": ["Monday", "Wednesday", "Friday"],
        "location": "Pediatric Wing"
    },
    "Dr. David Thompson": {
        "specialty": "Neurology",
        "available_days": ["Tuesday", "Wednesday", "Thursday"],
        "location": "Main Campus"
    }
}

# File Paths
DATA_DIR = "data"
PATIENT_DB_FILE = os.path.join(DATA_DIR, "patients.csv")
SCHEDULE_FILE = os.path.join(DATA_DIR, "doctor_schedules.xlsx")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.xlsx")
INTAKE_FORM_PATH = "New Patient Intake Form.pdf"

# Reminder Settings
REMINDER_SCHEDULE = {
    "first_reminder": 3,  # days before appointment
    "second_reminder": 1,  # day before appointment
    "third_reminder": 2   # hours before appointment
}

# Insurance Carriers
INSURANCE_CARRIERS = [
    "Blue Cross Blue Shield",
    "Aetna", 
    "Cigna",
    "UnitedHealth Group",
    "Humana",
    "Kaiser Permanente",
    "Anthem",
    "Molina Healthcare",
    "Other"
]
