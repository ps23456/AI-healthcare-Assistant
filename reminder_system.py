import schedule
import time
import threading
from datetime import datetime, timedelta
from database import db
from communication import comm_manager
from config import REMINDER_SCHEDULE

class ReminderSystem:
    def __init__(self):
        """Initialize the reminder system"""
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the reminder system"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
            print("Reminder system started")
    
    def stop(self):
        """Stop the reminder system"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Reminder system stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule daily reminder check
        schedule.every().day.at("08:00").do(self.check_and_send_reminders)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def check_and_send_reminders(self):
        """Check for appointments that need reminders and send them"""
        try:
            today = datetime.now().date()
            
            # Get upcoming appointments
            upcoming_appointments = db.get_upcoming_appointments(days=7)
            
            for _, appointment in upcoming_appointments.iterrows():
                appointment_date = datetime.strptime(appointment['appointment_date'], '%Y-%m-%d').date()
                days_until_appointment = (appointment_date - today).days
                
                # Get patient information
                patient_mask = db.patients_df['patient_id'] == appointment['patient_id']
                if patient_mask.any():
                    patient = db.patients_df[patient_mask].iloc[0]
                    
                    # Check which reminders need to be sent
                    self._check_and_send_reminder(appointment, patient, days_until_appointment)
                    
        except Exception as e:
            print(f"Error in reminder system: {str(e)}")
    
    def _check_and_send_reminder(self, appointment, patient, days_until_appointment):
        """Check and send appropriate reminder based on days until appointment"""
        
        appointment_data = {
            'appointment_id': appointment['appointment_id'],
            'doctor_name': appointment['doctor_name'],
            'appointment_date': appointment['appointment_date'],
            'appointment_time': appointment['appointment_time'],
            'duration': appointment['duration']
        }
        
        patient_data = {
            'first_name': patient['first_name'],
            'last_name': patient['last_name'],
            'phone': patient['phone'],
            'email': patient['email']
        }
        
        # First reminder (3 days before)
        if days_until_appointment == REMINDER_SCHEDULE['first_reminder'] and not appointment['reminder_sent_1']:
            try:
                email_sent, sms_sent = comm_manager.send_reminder(appointment_data, patient_data, 1)
                if email_sent or sms_sent:
                    db.update_reminder_status(appointment['appointment_id'], 1)
                    print(f"First reminder sent for appointment {appointment['appointment_id']}")
            except Exception as e:
                print(f"Error sending first reminder: {str(e)}")
        
        # Second reminder (1 day before)
        elif days_until_appointment == REMINDER_SCHEDULE['second_reminder'] and not appointment['reminder_sent_2']:
            try:
                email_sent, sms_sent = comm_manager.send_reminder(appointment_data, patient_data, 2)
                if email_sent or sms_sent:
                    db.update_reminder_status(appointment['appointment_id'], 2)
                    print(f"Second reminder sent for appointment {appointment['appointment_id']}")
            except Exception as e:
                print(f"Error sending second reminder: {str(e)}")
        
        # Third reminder (2 hours before)
        elif days_until_appointment == 0:
            appointment_time = datetime.strptime(appointment['appointment_time'], '%H:%M').time()
            current_time = datetime.now().time()
            
            # Check if appointment is within 2 hours
            appointment_datetime = datetime.combine(datetime.now().date(), appointment_time)
            current_datetime = datetime.now()
            hours_until_appointment = (appointment_datetime - current_datetime).total_seconds() / 3600
            
            if 0 <= hours_until_appointment <= 2 and not appointment['reminder_sent_3']:
                try:
                    email_sent, sms_sent = comm_manager.send_reminder(appointment_data, patient_data, 3)
                    if email_sent or sms_sent:
                        db.update_reminder_status(appointment['appointment_id'], 3)
                        print(f"Third reminder sent for appointment {appointment['appointment_id']}")
                except Exception as e:
                    print(f"Error sending third reminder: {str(e)}")
    
    def send_intake_form_reminder(self, appointment_id):
        """Send a reminder to complete intake forms"""
        try:
            # Get appointment and patient data
            appointment_mask = db.appointments_df['appointment_id'] == appointment_id
            if appointment_mask.any():
                appointment = db.appointments_df[appointment_mask].iloc[0]
                
                patient_mask = db.patients_df['patient_id'] == appointment['patient_id']
                if patient_mask.any():
                    patient = db.patients_df[patient_mask].iloc[0]
                    
                    appointment_data = {
                        'appointment_id': appointment['appointment_id'],
                        'doctor_name': appointment['doctor_name'],
                        'appointment_date': appointment['appointment_date'],
                        'appointment_time': appointment['appointment_time'],
                        'duration': appointment['duration']
                    }
                    
                    patient_data = {
                        'first_name': patient['first_name'],
                        'last_name': patient['last_name'],
                        'phone': patient['phone'],
                        'email': patient['email']
                    }
                    
                    # Send intake form if not already sent
                    if not appointment['intake_form_sent']:
                        success = comm_manager.send_intake_form(appointment_data, patient_data)
                        if success:
                            db.mark_intake_form_sent(appointment_id)
                            print(f"Intake form sent for appointment {appointment_id}")
                            return True
                    
        except Exception as e:
            print(f"Error sending intake form reminder: {str(e)}")
            return False
    
    def send_cancellation_notice(self, appointment_id, reason=None):
        """Send cancellation notice for an appointment"""
        try:
            # Get appointment and patient data
            appointment_mask = db.appointments_df['appointment_id'] == appointment_id
            if appointment_mask.any():
                appointment = db.appointments_df[appointment_mask].iloc[0]
                
                patient_mask = db.patients_df['patient_id'] == appointment['patient_id']
                if patient_mask.any():
                    patient = db.patients_df[patient_mask].iloc[0]
                    
                    appointment_data = {
                        'appointment_id': appointment['appointment_id'],
                        'doctor_name': appointment['doctor_name'],
                        'appointment_date': appointment['appointment_date'],
                        'appointment_time': appointment['appointment_time'],
                        'duration': appointment['duration']
                    }
                    
                    patient_data = {
                        'first_name': patient['first_name'],
                        'last_name': patient['last_name'],
                        'phone': patient['phone'],
                        'email': patient['email']
                    }
                    
                    # Send cancellation notice
                    email_sent, sms_sent = comm_manager.send_cancellation_notice(appointment_data, patient_data, reason)
                    print(f"Cancellation notice sent for appointment {appointment_id}")
                    return email_sent or sms_sent
                    
        except Exception as e:
            print(f"Error sending cancellation notice: {str(e)}")
            return False
    
    def get_reminder_status(self, appointment_id):
        """Get the reminder status for an appointment"""
        try:
            appointment_mask = db.appointments_df['appointment_id'] == appointment_id
            if appointment_mask.any():
                appointment = db.appointments_df[appointment_mask].iloc[0]
                return {
                    'reminder_sent_1': appointment['reminder_sent_1'],
                    'reminder_sent_2': appointment['reminder_sent_2'],
                    'reminder_sent_3': appointment['reminder_sent_3'],
                    'intake_form_sent': appointment['intake_form_sent']
                }
        except Exception as e:
            print(f"Error getting reminder status: {str(e)}")
            return None
    
    def manual_reminder_check(self):
        """Manually trigger reminder check (for testing)"""
        print("Manual reminder check triggered")
        self.check_and_send_reminders()

# Global reminder system instance
reminder_system = ReminderSystem()

def start_reminder_system():
    """Start the reminder system"""
    reminder_system.start()

def stop_reminder_system():
    """Stop the reminder system"""
    reminder_system.stop()

if __name__ == "__main__":
    # Test the reminder system
    print("Starting reminder system...")
    start_reminder_system()
    
    try:
        # Keep the system running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping reminder system...")
        stop_reminder_system()
