import pandas as pd
import random
import string
from datetime import datetime, timedelta
import os
from config import DATA_DIR, PATIENT_DB_FILE, SCHEDULE_FILE, DOCTORS, INSURANCE_CARRIERS

def generate_patient_data(num_patients=50):
    """Generate synthetic patient data"""
    
    # Sample data for realistic patient generation
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria",
        "William", "Jennifer", "Richard", "Linda", "Thomas", "Patricia", "Christopher", "Barbara", "Daniel", "Elizabeth",
        "Matthew", "Susan", "Anthony", "Jessica", "Mark", "Sarah", "Donald", "Karen", "Steven", "Nancy",
        "Paul", "Betty", "Andrew", "Helen", "Joshua", "Sandra", "Kenneth", "Donna", "Kevin", "Carol",
        "Brian", "Ruth", "George", "Sharon", "Timothy", "Michelle", "Ronald", "Laura", "Jason", "Kimberly"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
    ]
    
    patients = []
    
    for i in range(num_patients):
        # Generate patient ID
        patient_id = f"P{str(i+1).zfill(4)}"
        
        # Generate name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate DOB (18-80 years old)
        start_date = datetime(1943, 1, 1)
        end_date = datetime(2005, 12, 31)
        dob = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        
        # Generate phone number
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        # Generate address
        street_numbers = [str(random.randint(100, 9999))]
        street_names = ["Main St", "Oak Ave", "Pine Rd", "Elm St", "Maple Dr", "Cedar Ln", "Birch Way", "Willow Ct"]
        cities = ["Springfield", "Riverside", "Fairview", "Greenfield", "Oakland", "Sunset", "Mountain View", "Lake City"]
        states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
        zip_codes = [f"{random.randint(10000, 99999)}"]
        
        address = f"{random.choice(street_numbers)} {random.choice(street_names)}, {random.choice(cities)}, {random.choice(states)} {random.choice(zip_codes)}"
        
        # Generate insurance info
        insurance_carrier = random.choice(INSURANCE_CARRIERS)
        member_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        group_number = ''.join(random.choices(string.digits, k=6))
        
        # Determine if new or returning patient (70% returning, 30% new)
        is_new_patient = random.random() < 0.3
        
        # Generate emergency contact
        emergency_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        emergency_phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        emergency_relation = random.choice(["Spouse", "Parent", "Child", "Sibling", "Friend"])
        
        patient = {
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': dob.strftime('%Y-%m-%d'),
            'phone': phone,
            'email': email,
            'address': address,
            'insurance_carrier': insurance_carrier,
            'member_id': member_id,
            'group_number': group_number,
            'is_new_patient': is_new_patient,
            'emergency_contact_name': emergency_name,
            'emergency_contact_phone': emergency_phone,
            'emergency_contact_relation': emergency_relation,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'last_visit': None if is_new_patient else (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        }
        
        patients.append(patient)
    
    return pd.DataFrame(patients)

def generate_doctor_schedules():
    """Generate doctor availability schedules"""
    
    # Create directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    schedules = []
    
    # Generate schedules for next 30 days
    start_date = datetime.now()
    
    for day_offset in range(30):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime('%A')
        date_str = current_date.strftime('%Y-%m-%d')
        
        for doctor_name, doctor_info in DOCTORS.items():
            if day_name in doctor_info['available_days']:
                # Generate time slots (9 AM to 5 PM, excluding lunch break)
                time_slots = []
                
                # Morning slots (9 AM to 12 PM)
                for hour in range(9, 12):
                    for minute in [0, 30]:
                        time_slots.append(f"{hour:02d}:{minute:02d}")
                
                # Afternoon slots (1 PM to 5 PM)
                for hour in range(13, 17):
                    for minute in [0, 30]:
                        time_slots.append(f"{hour:02d}:{minute:02d}")
                
                # Add some random unavailability (10% chance)
                available_slots = []
                for slot in time_slots:
                    if random.random() > 0.1:  # 90% availability
                        available_slots.append(slot)
                
                for slot in available_slots:
                    schedule_entry = {
                        'doctor_name': doctor_name,
                        'specialty': doctor_info['specialty'],
                        'location': doctor_info['location'],
                        'date': date_str,
                        'day_of_week': day_name,
                        'time_slot': slot,
                        'is_available': True,
                        'appointment_id': None
                    }
                    schedules.append(schedule_entry)
    
    return pd.DataFrame(schedules)

def create_sample_data():
    """Create all sample data files"""
    
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Generate patient data
    print("Generating patient data...")
    patients_df = generate_patient_data(50)
    patients_df.to_csv(PATIENT_DB_FILE, index=False)
    print(f"Patient data saved to {PATIENT_DB_FILE}")
    
    # Generate doctor schedules
    print("Generating doctor schedules...")
    schedules_df = generate_doctor_schedules()
    schedules_df.to_excel(SCHEDULE_FILE, index=False)
    print(f"Doctor schedules saved to {SCHEDULE_FILE}")
    
    # Create empty appointments file
    appointments_df = pd.DataFrame(columns=[
        'appointment_id', 'patient_id', 'doctor_name', 'appointment_date', 
        'appointment_time', 'duration', 'status', 'insurance_carrier', 
        'member_id', 'group_number', 'created_date', 'reminder_sent_1', 
        'reminder_sent_2', 'reminder_sent_3', 'intake_form_sent'
    ])
    appointments_df.to_excel(os.path.join(DATA_DIR, "appointments.xlsx"), index=False)
    print(f"Appointments file created at {os.path.join(DATA_DIR, 'appointments.xlsx')}")
    
    print("Sample data generation completed!")

if __name__ == "__main__":
    create_sample_data()
