import pandas as pd
import os
from datetime import datetime, timedelta
from config import PATIENT_DB_FILE, SCHEDULE_FILE, APPOINTMENTS_FILE, DATA_DIR

class MedicalDatabase:
    def __init__(self):
        """Initialize the medical database"""
        self.patients_file = PATIENT_DB_FILE
        self.schedules_file = SCHEDULE_FILE
        self.appointments_file = APPOINTMENTS_FILE
        
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Initialize dataframes
        self._load_data()
    
    def _load_data(self):
        """Load data from files or create empty dataframes"""
        try:
            self.patients_df = pd.read_csv(self.patients_file)
        except FileNotFoundError:
            self.patients_df = pd.DataFrame(columns=[
                'patient_id', 'first_name', 'last_name', 'middle_initial', 'date_of_birth', 'gender', 
                'home_phone', 'cell_phone', 'email', 'street_address', 'city', 'state', 'zip_code',
                'emergency_contact_name', 'relationship', 'emergency_phone',
                'primary_insurance_company', 'primary_member_id', 'primary_group_number',
                'secondary_insurance_company', 'secondary_member_id', 'secondary_group_number',
                'primary_reason', 'duration', 'sneezing', 'runny_nose', 'stuffy_nose', 'itchy_eyes', 
                'watery_eyes', 'skin_rash', 'wheezing', 'shortness_breath', 'coughing', 'chest_tightness', 
                'sinus_pressure', 'headaches', 'has_allergies', 'known_allergies', 'allergy_testing_yes', 
                'testing_date', 'allergy_testing_no', 'epipen_usage', 'current_medications', 'claritin', 
                'zyrtec', 'allegra', 'benadryl', 'nasal_sprays', 'other_medication', 'other_medication_name',
                'asthma', 'eczema', 'sinus_infections', 'pneumonia', 'bronchitis', 'high_blood_pressure', 
                'heart_disease', 'diabetes', 'other_condition', 'other_condition_name', 'family_history',
                'understand_instructions', 'patient_signature', 'signature_date', 'created_date', 'is_new_patient'
            ])
        
        try:
            self.schedules_df = pd.read_excel(self.schedules_file)
        except FileNotFoundError:
            self.schedules_df = pd.DataFrame(columns=[
                'doctor_name', 'specialty', 'location', 'date', 'day_of_week',
                'time_slot', 'is_available', 'appointment_id'
            ])
        
        try:
            self.appointments_df = pd.read_excel(self.appointments_file)
        except FileNotFoundError:
            self.appointments_df = pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'doctor_name', 'appointment_date',
                'appointment_time', 'duration', 'status', 'insurance_carrier',
                'member_id', 'group_number', 'created_date', 'reminder_sent_1',
                'reminder_sent_2', 'reminder_sent_3', 'intake_form_sent'
            ])
    
    def save_data(self):
        """Save all data to files"""
        self.patients_df.to_csv(self.patients_file, index=False)
        self.schedules_df.to_excel(self.schedules_file, index=False)
        self.appointments_df.to_excel(self.appointments_file, index=False)
    
    def find_patient(self, first_name=None, last_name=None, phone=None, email=None):
        """Find patient by various criteria"""
        if first_name and last_name:
            mask = (self.patients_df['first_name'].str.lower() == first_name.lower()) & \
                   (self.patients_df['last_name'].str.lower() == last_name.lower())
            return self.patients_df[mask]
        
        if phone:
            mask = self.patients_df['phone'] == phone
            return self.patients_df[mask]
        
        if email:
            mask = self.patients_df['email'].str.lower() == email.lower()
            return self.patients_df[mask]
        
        return pd.DataFrame()
    
    def add_patient(self, patient_data):
        """Add a new patient to the database"""
        # Generate patient ID
        if len(self.patients_df) == 0:
            patient_id = "P0001"
        else:
            last_id = self.patients_df['patient_id'].max()
            last_num = int(last_id[1:])
            patient_id = f"P{str(last_num + 1).zfill(4)}"
        
        patient_data['patient_id'] = patient_id
        patient_data['created_date'] = datetime.now().strftime('%Y-%m-%d')
        patient_data['is_new_patient'] = True
        patient_data['last_visit'] = None
        
        # Convert all values to strings to avoid serialization issues
        cleaned_data = {}
        for key, value in patient_data.items():
            if value is None:
                cleaned_data[key] = ''
            elif isinstance(value, bool):
                cleaned_data[key] = str(value)
            elif isinstance(value, (int, float)):
                cleaned_data[key] = str(value) if not pd.isna(value) else ''
            else:
                cleaned_data[key] = str(value)
        
        self.patients_df = pd.concat([self.patients_df, pd.DataFrame([cleaned_data])], ignore_index=True)
        self.save_data()
        
        return patient_id
    
    def update_patient(self, patient_id, updates):
        """Update patient information"""
        mask = self.patients_df['patient_id'] == patient_id
        if mask.any():
            for key, value in updates.items():
                if key in self.patients_df.columns:
                    self.patients_df.loc[mask, key] = value
            self.save_data()
            return True
        return False
    
    def get_available_slots(self, doctor_name, date):
        """Get available time slots for a doctor on a specific date"""
        mask = (self.schedules_df['doctor_name'] == doctor_name) & \
               (self.schedules_df['date'] == date) & \
               (self.schedules_df['is_available'] == True)
        
        available_slots = self.schedules_df[mask]
        return available_slots[['time_slot', 'location']].to_dict('records')
    
    def book_appointment(self, appointment_data):
        """Book an appointment"""
        # Generate appointment ID
        if len(self.appointments_df) == 0:
            appointment_id = "A0001"
        else:
            last_id = self.appointments_df['appointment_id'].max()
            last_num = int(last_id[1:])
            appointment_id = f"A{str(last_num + 1).zfill(4)}"
        
        appointment_data['appointment_id'] = appointment_id
        appointment_data['created_date'] = datetime.now().strftime('%Y-%m-%d')
        appointment_data['status'] = 'confirmed'
        appointment_data['reminder_sent_1'] = False
        appointment_data['reminder_sent_2'] = False
        appointment_data['reminder_sent_3'] = False
        appointment_data['intake_form_sent'] = False
        
        # Add appointment to appointments table
        self.appointments_df = pd.concat([self.appointments_df, pd.DataFrame([appointment_data])], ignore_index=True)
        
        # Update schedule to mark slot as unavailable
        mask = (self.schedules_df['doctor_name'] == appointment_data['doctor_name']) & \
               (self.schedules_df['date'] == appointment_data['appointment_date']) & \
               (self.schedules_df['time_slot'] == appointment_data['appointment_time'])
        
        self.schedules_df.loc[mask, 'is_available'] = False
        self.schedules_df.loc[mask, 'appointment_id'] = appointment_id
        
        # Update patient's last visit and new patient status
        patient_mask = self.patients_df['patient_id'] == appointment_data['patient_id']
        self.patients_df.loc[patient_mask, 'last_visit'] = appointment_data['appointment_date']
        self.patients_df.loc[patient_mask, 'is_new_patient'] = False
        
        self.save_data()
        
        return appointment_id
    
    def cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        mask = self.appointments_df['appointment_id'] == appointment_id
        if mask.any():
            appointment = self.appointments_df[mask].iloc[0]
            
            # Update appointment status
            self.appointments_df.loc[mask, 'status'] = 'cancelled'
            
            # Free up the time slot
            schedule_mask = (self.schedules_df['doctor_name'] == appointment['doctor_name']) & \
                           (self.schedules_df['date'] == appointment['appointment_date']) & \
                           (self.schedules_df['time_slot'] == appointment['appointment_time'])
            
            self.schedules_df.loc[schedule_mask, 'is_available'] = True
            self.schedules_df.loc[schedule_mask, 'appointment_id'] = None
            
            self.save_data()
            return True
        return False
    
    def get_patient_appointments(self, patient_id):
        """Get all appointments for a patient"""
        mask = self.appointments_df['patient_id'] == patient_id
        return self.appointments_df[mask].sort_values('appointment_date', ascending=False)
    
    def get_doctor_appointments(self, doctor_name, date=None):
        """Get appointments for a doctor on a specific date"""
        mask = self.appointments_df['doctor_name'] == doctor_name
        if date:
            mask &= self.appointments_df['appointment_date'] == date
        
        return self.appointments_df[mask].sort_values('appointment_time')
    
    def get_upcoming_appointments(self, days=7):
        """Get upcoming appointments within specified days"""
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        mask = (self.appointments_df['appointment_date'] >= today.strftime('%Y-%m-%d')) & \
               (self.appointments_df['appointment_date'] <= end_date.strftime('%Y-%m-%d')) & \
               (self.appointments_df['status'] == 'confirmed')
        
        return self.appointments_df[mask].sort_values(['appointment_date', 'appointment_time'])
    
    def update_reminder_status(self, appointment_id, reminder_number):
        """Update reminder sent status"""
        mask = self.appointments_df['appointment_id'] == appointment_id
        if mask.any():
            column_name = f'reminder_sent_{reminder_number}'
            if column_name in self.appointments_df.columns:
                self.appointments_df.loc[mask, column_name] = True
                self.save_data()
                return True
        return False
    
    def mark_intake_form_sent(self, appointment_id):
        """Mark intake form as sent"""
        mask = self.appointments_df['appointment_id'] == appointment_id
        if mask.any():
            self.appointments_df.loc[mask, 'intake_form_sent'] = True
            self.save_data()
            return True
        return False
    
    def create_appointment(self, patient_id, doctor_name, appointment_date, appointment_time, location, status='confirmed'):
        """Create a new appointment"""
        try:
            # Generate unique appointment ID
            appointment_id = f"APT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine duration based on patient type
            duration = 60 if patient_id == 'NEW' else 30  # New patients get 60 min, returning get 30 min
            
            # Create new appointment record
            new_appointment = {
                'appointment_id': appointment_id,
                'patient_id': patient_id,
                'doctor_name': doctor_name,
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'duration': duration,
                'status': status,
                'insurance_carrier': '',
                'member_id': '',
                'group_number': '',
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'reminder_sent_1': False,
                'reminder_sent_2': False,
                'reminder_sent_3': False,
                'intake_form_sent': False
            }
            
            # Add to appointments dataframe
            self.appointments_df = pd.concat([self.appointments_df, pd.DataFrame([new_appointment])], ignore_index=True)
            
            # Save to file
            self.save_data()
            
            print(f"DEBUG: Appointment created successfully with ID: {appointment_id}")
            return appointment_id
            
        except Exception as e:
            print(f"DEBUG: Error creating appointment: {str(e)}")
            return None
    
    def export_appointments_report(self, filename=None):
        """Export appointments report for admin review"""
        if filename is None:
            filename = f"appointments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create a comprehensive report
        report_data = self.appointments_df.copy()
        
        # Add patient information
        patient_info = self.patients_df[['patient_id', 'first_name', 'last_name', 'phone', 'email']]
        report_data = report_data.merge(patient_info, on='patient_id', how='left')
        
        # Add doctor information
        doctor_info = self.schedules_df[['doctor_name', 'specialty', 'location']].drop_duplicates()
        report_data = report_data.merge(doctor_info, on='doctor_name', how='left')
        
        # Reorder columns for better readability
        columns_order = [
            'appointment_id', 'appointment_date', 'appointment_time', 'duration',
            'doctor_name', 'specialty', 'location', 'patient_id', 'first_name', 'last_name',
            'phone', 'email', 'status', 'insurance_carrier', 'member_id', 'group_number',
            'created_date', 'reminder_sent_1', 'reminder_sent_2', 'reminder_sent_3',
            'intake_form_sent'
        ]
        
        report_data = report_data[columns_order]
        
        # Save to Excel
        report_path = os.path.join(DATA_DIR, filename)
        report_data.to_excel(report_path, index=False)
        
        return report_path

# Global database instance
db = MedicalDatabase()
