import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Sample data for generating patients
first_names = [
    "John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Jennifer", "William", "Linda",
    "James", "Patricia", "Richard", "Elizabeth", "Charles", "Barbara", "Thomas", "Susan", "Christopher", "Jessica",
    "Daniel", "Karen", "Matthew", "Nancy", "Anthony", "Betty", "Mark", "Helen", "Donald", "Sandra",
    "Steven", "Donna", "Paul", "Carol", "Andrew", "Ruth", "Joshua", "Sharon", "Kenneth", "Michelle",
    "Kevin", "Laura", "Brian", "Sarah", "George", "Kimberly", "Edward", "Deborah", "Ronald", "Dorothy",
    "Timothy", "Amy", "Jason", "Angela", "Jeffrey", "Ashley", "Ryan", "Brenda", "Jacob", "Emma",
    "Gary", "Olivia", "Nicholas", "Cynthia", "Eric", "Marie", "Jonathan", "Janet", "Stephen", "Catherine",
    "Larry", "Frances", "Justin", "Christine", "Scott", "Samantha", "Brandon", "Debra", "Benjamin", "Rachel",
    "Samuel", "Carolyn", "Gregory", "Janet", "Alexander", "Virginia", "Patrick", "Maria", "Jack", "Heather"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson"
]

cities = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
    "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "San Francisco",
    "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City",
    "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno",
    "Sacramento", "Mesa", "Kansas City", "Atlanta", "Long Beach", "Colorado Springs", "Raleigh", "Miami", "Virginia Beach",
    "Omaha", "Oakland", "Minneapolis", "Tulsa", "Arlington", "Tampa", "New Orleans", "Wichita", "Cleveland", "Bakersfield",
    "Aurora", "Anaheim", "Honolulu", "Santa Ana", "Corpus Christi", "Riverside", "Lexington", "Stockton", "Henderson", "Saint Paul",
    "St. Louis", "Milwaukee", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington", "Boston"
]

states = [
    "NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "TX", "FL", "TX", "OH", "NC", "CA",
    "IN", "WA", "CO", "DC", "MA", "TX", "TN", "MI", "OK", "OR", "NV", "TN", "KY", "MD", "WI", "NM",
    "AZ", "CA", "CA", "AZ", "MO", "GA", "CA", "CO", "NC", "FL", "VA", "NE", "CA", "MN", "OK", "TX",
    "FL", "LA", "KS", "OH", "CA", "CO", "CA", "HI", "CA", "TX", "CA", "KY", "CA", "NV", "MN", "MO",
    "WI", "OH", "NC", "CA", "IN", "WA", "CO", "DC", "MA", "TX", "TN", "MI", "OK", "OR", "NV", "TN"
]

insurance_companies = [
    "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth Group", "Humana", "Kaiser Permanente", 
    "Molina Healthcare", "Anthem", "Other"
]

genders = ["Male", "Female", "Other"]

# Generate patient data
patients_data = []

for i in range(50):
    patient_id = f"P{str(i+1).zfill(4)}"
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    middle_initial = random.choice([chr(ord('A') + j) for j in range(26)] + [''])
    
    # Generate date of birth (ages 18-80)
    birth_year = random.randint(1944, 2006)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    gender = random.choice(genders)
    
    # Generate phone numbers
    home_phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    cell_phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    # Generate email
    email = f"{first_name.lower()}.{last_name.lower()}@email.com"
    
    # Generate address
    street_number = random.randint(100, 9999)
    street_names = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Birch Way", "Willow Ct"]
    street_name = random.choice(street_names)
    street_address = f"{street_number} {street_name}"
    
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = f"{random.randint(10000, 99999)}"
    
    # Emergency contact
    emergency_first = random.choice(first_names)
    emergency_last = random.choice(last_names)
    emergency_contact_name = f"{emergency_first} {emergency_last}"
    relationships = ["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"]
    relationship = random.choice(relationships)
    emergency_phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    # Insurance
    primary_insurance = random.choice(insurance_companies)
    primary_member_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
    primary_group_number = random.randint(100000, 999999)
    
    # Secondary insurance (optional)
    secondary_insurance = random.choice([random.choice(insurance_companies), ''])
    secondary_member_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10)) if secondary_insurance else ''
    secondary_group_number = random.randint(100000, 999999) if secondary_insurance else ''
    
    # Medical information
    primary_reasons = [
        "Seasonal allergies", "Food allergies", "Asthma symptoms", "Skin rash", "Sinus problems",
        "Allergic reaction", "Breathing difficulties", "Eye irritation", "Chest tightness", "General consultation"
    ]
    primary_reason = random.choice(primary_reasons)
    
    durations = ["Less than 1 week", "1-4 weeks", "1-6 months", "More than 6 months"]
    duration = random.choice(durations)
    
    # Symptoms (random selection)
    symptoms = ['sneezing', 'runny_nose', 'stuffy_nose', 'itchy_eyes', 'watery_eyes', 'skin_rash', 
                'wheezing', 'shortness_breath', 'coughing', 'chest_tightness', 'sinus_pressure', 'headaches']
    symptom_values = {symptom: random.choice([True, False]) for symptom in symptoms}
    
    # Allergies
    has_allergies = random.choice(["Yes", "No", "Not sure"])
    known_allergies = random.choice([
        "Peanuts, Shellfish", "Pollen, Dust mites", "Penicillin", "Latex", "Bee stings", 
        "Tree nuts", "Dairy products", "None", ""
    ]) if has_allergies == "Yes" else ""
    
    allergy_testing_yes = random.choice([True, False])
    testing_date = f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" if allergy_testing_yes else ""
    allergy_testing_no = not allergy_testing_yes
    epipen_usage = random.choice(["Yes", "No"])
    
    # Medications
    current_medications = random.choice([
        "Lisinopril 10mg daily", "Metformin 500mg twice daily", "Albuterol inhaler as needed",
        "Multivitamin daily", "Omega-3 supplements", "None", ""
    ])
    
    allergy_meds = ['claritin', 'zyrtec', 'allegra', 'benadryl', 'nasal_sprays', 'other_medication']
    allergy_med_values = {med: random.choice([True, False]) for med in allergy_meds}
    other_medication_name = random.choice(["Flonase", "Nasacort", "Xyzal", ""]) if allergy_med_values['other_medication'] else ""
    
    # Medical conditions
    conditions = ['asthma', 'eczema', 'sinus_infections', 'pneumonia', 'bronchitis', 
                  'high_blood_pressure', 'heart_disease', 'diabetes', 'other_condition']
    condition_values = {condition: random.choice([True, False]) for condition in conditions}
    other_condition_name = random.choice(["Migraine", "Arthritis", "Depression", ""]) if condition_values['other_condition'] else ""
    
    # Family history
    family_history = random.choice([
        "Mother has asthma, father has seasonal allergies", "No known family history of allergies",
        "Sister has food allergies", "Grandmother had eczema", "Father has hay fever",
        "Mother and sister both have asthma", ""
    ])
    
    # Form completion
    understand_instructions = random.choice(["Yes, I understand and will follow instructions", "I have questions about these instructions"])
    patient_signature = f"{first_name} {last_name}"
    signature_date = f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    
    # Dates
    created_date = f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    is_new_patient = random.choice([True, False])
    
    # Create patient record
    patient_record = {
        'patient_id': patient_id,
        'first_name': first_name,
        'last_name': last_name,
        'middle_initial': middle_initial,
        'date_of_birth': date_of_birth,
        'gender': gender,
        'home_phone': home_phone,
        'cell_phone': cell_phone,
        'email': email,
        'street_address': street_address,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'emergency_contact_name': emergency_contact_name,
        'relationship': relationship,
        'emergency_phone': emergency_phone,
        'primary_insurance_company': primary_insurance,
        'primary_member_id': primary_member_id,
        'primary_group_number': primary_group_number,
        'secondary_insurance_company': secondary_insurance,
        'secondary_member_id': secondary_member_id,
        'secondary_group_number': secondary_group_number,
        'primary_reason': primary_reason,
        'duration': duration,
        **symptom_values,
        'has_allergies': has_allergies,
        'known_allergies': known_allergies,
        'allergy_testing_yes': allergy_testing_yes,
        'testing_date': testing_date,
        'allergy_testing_no': allergy_testing_no,
        'epipen_usage': epipen_usage,
        'current_medications': current_medications,
        **allergy_med_values,
        'other_medication_name': other_medication_name,
        **condition_values,
        'other_condition_name': other_condition_name,
        'family_history': family_history,
        'understand_instructions': understand_instructions,
        'patient_signature': patient_signature,
        'signature_date': signature_date,
        'created_date': created_date,
        'is_new_patient': is_new_patient
    }
    
    patients_data.append(patient_record)

# Create DataFrame and save to CSV
df = pd.DataFrame(patients_data)
df.to_csv('data/patients.csv', index=False)

print(f"Generated {len(patients_data)} patients successfully!")
print("CSV file saved to data/patients.csv")
