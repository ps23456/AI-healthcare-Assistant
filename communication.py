import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client
from datetime import datetime, timedelta
import os
from config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
    CLINIC_NAME, CLINIC_ADDRESS, CLINIC_PHONE, CLINIC_EMAIL,
    INTAKE_FORM_PATH
)

class CommunicationManager:
    def __init__(self):
        """Initialize communication manager"""
        self.email_user = EMAIL_USER
        self.email_password = EMAIL_PASSWORD
        self.clinic_name = CLINIC_NAME
        self.clinic_address = CLINIC_ADDRESS
        self.clinic_phone = CLINIC_PHONE
        self.clinic_email = CLINIC_EMAIL
        
        # Initialize Twilio client for SMS
        try:
            self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        except:
            self.twilio_client = None
            print("Warning: Twilio not configured. SMS functionality will be disabled.")
    
    def send_email(self, to_email, subject, body, attachment_path=None):
        """Send email with optional attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach file if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_sms(self, to_phone, message):
        """Send SMS using Twilio"""
        if not self.twilio_client:
            print("SMS not sent: Twilio not configured")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            print(f"SMS sent successfully to {to_phone}")
            return True
            
        except Exception as e:
            print(f"Error sending SMS to {to_phone}: {str(e)}")
            return False
    
    def send_appointment_confirmation(self, appointment_data, patient_data):
        """Send appointment confirmation email and SMS"""
        
        # Email confirmation
        subject = f"Appointment Confirmation - {self.clinic_name}"
        
        body = f"""
        <html>
        <body>
            <h2>Appointment Confirmation</h2>
            <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
            
            <p>Your appointment has been confirmed with the following details:</p>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['doctor_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_date']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_time']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Duration:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['duration']} minutes</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Location:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{self.clinic_address}</td>
                </tr>
            </table>
            
            <p><strong>Important Reminders:</strong></p>
            <ul>
                <li>Please arrive 15 minutes before your appointment time</li>
                <li>Bring your insurance card and photo ID</li>
                <li>Complete any pre-appointment forms sent to your email</li>
            </ul>
            
            <p>If you need to reschedule or cancel your appointment, please call us at {self.clinic_phone} at least 24 hours in advance.</p>
            
            <p>We look forward to seeing you!</p>
            
            <p>Best regards,<br>
            {self.clinic_name}<br>
            {self.clinic_phone}<br>
            {self.clinic_email}</p>
        </body>
        </html>
        """
        
        email_sent = self.send_email(patient_data['email'], subject, body)
        
        # SMS confirmation
        sms_message = f"""
        {self.clinic_name} - Appointment Confirmed
        Dr. {appointment_data['doctor_name']}
        {appointment_data['appointment_date']} at {appointment_data['appointment_time']}
        Duration: {appointment_data['duration']} min
        Location: {self.clinic_address}
        Call {self.clinic_phone} for changes
        """
        
        sms_sent = self.send_sms(patient_data['phone'], sms_message)
        
        return email_sent, sms_sent
    
    def send_intake_form(self, appointment_data, patient_data):
        """Send intake form to patient"""
        
        subject = f"Pre-Appointment Forms - {self.clinic_name}"
        
        body = f"""
        <html>
        <body>
            <h2>Pre-Appointment Forms</h2>
            <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
            
            <p>Please complete the attached intake form before your appointment on {appointment_data['appointment_date']} at {appointment_data['appointment_time']}.</p>
            
            <p><strong>Instructions:</strong></p>
            <ol>
                <li>Download and print the attached form</li>
                <li>Fill out all required information</li>
                <li>Bring the completed form to your appointment</li>
            </ol>
            
            <p>Completing this form in advance will help us serve you more efficiently.</p>
            
            <p>If you have any questions, please contact us at {self.clinic_phone}.</p>
            
            <p>Thank you!</p>
            
            <p>Best regards,<br>
            {self.clinic_name}<br>
            {self.clinic_phone}<br>
            {self.clinic_email}</p>
        </body>
        </html>
        """
        
        return self.send_email(patient_data['email'], subject, body, INTAKE_FORM_PATH)
    
    def send_reminder(self, appointment_data, patient_data, reminder_number):
        """Send appointment reminder"""
        
        appointment_date = datetime.strptime(appointment_data['appointment_date'], '%Y-%m-%d')
        appointment_time = appointment_data['appointment_time']
        
        if reminder_number == 1:
            # First reminder (3 days before)
            subject = f"Appointment Reminder - {self.clinic_name}"
            email_body = f"""
            <html>
            <body>
                <h2>Appointment Reminder</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>This is a friendly reminder of your upcoming appointment:</p>
                
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['doctor_name']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_time']}</td>
                    </tr>
                </table>
                
                <p>Please ensure you have completed your pre-appointment forms.</p>
                
                <p>Call {self.clinic_phone} if you need to reschedule.</p>
                
                <p>Best regards,<br>
                {self.clinic_name}</p>
            </body>
            </html>
            """
            
            sms_message = f"""
            {self.clinic_name} - Appointment Reminder
            {appointment_data['appointment_date']} at {appointment_data['appointment_time']}
            Dr. {appointment_data['doctor_name']}
            Please complete forms before visit
            """
            
        elif reminder_number == 2:
            # Second reminder (1 day before) - with form completion check
            subject = f"Final Appointment Reminder - {self.clinic_name}"
            email_body = f"""
            <html>
            <body>
                <h2>Final Appointment Reminder</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>Your appointment is tomorrow:</p>
                
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['doctor_name']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_time']}</td>
                    </tr>
                </table>
                
                <p><strong>Important:</strong> Have you completed your intake forms?</p>
                <p>If not, please download and complete them before your visit.</p>
                
                <p>Please confirm your appointment by replying to this email or calling {self.clinic_phone}.</p>
                
                <p>Best regards,<br>
                {self.clinic_name}</p>
            </body>
            </html>
            """
            
            sms_message = f"""
            {self.clinic_name} - Final Reminder
            Tomorrow: {appointment_data['appointment_date']} at {appointment_data['appointment_time']}
            Have you completed your forms?
            Reply YES to confirm or call {self.clinic_phone}
            """
            
        elif reminder_number == 3:
            # Third reminder (2 hours before) - with confirmation check
            subject = f"Appointment Today - {self.clinic_name}"
            email_body = f"""
            <html>
            <body>
                <h2>Appointment Today</h2>
                <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
                
                <p>Your appointment is in 2 hours:</p>
                
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['doctor_name']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_time']}</td>
                    </tr>
                </table>
                
                <p><strong>Please confirm:</strong> Are you still planning to attend?</p>
                <p>If you need to cancel or reschedule, please call {self.clinic_phone} immediately.</p>
                
                <p>We look forward to seeing you!</p>
                
                <p>Best regards,<br>
                {self.clinic_name}</p>
            </body>
            </html>
            """
            
            sms_message = f"""
            {self.clinic_name} - Appointment in 2 hours
            {appointment_data['appointment_time']} with Dr. {appointment_data['doctor_name']}
            Please confirm attendance
            Call {self.clinic_phone} for changes
            """
        
        # Send email and SMS
        email_sent = self.send_email(patient_data['email'], subject, email_body)
        sms_sent = self.send_sms(patient_data['phone'], sms_message)
        
        return email_sent, sms_sent
    
    def send_cancellation_notice(self, appointment_data, patient_data, reason=None):
        """Send appointment cancellation notice"""
        
        subject = f"Appointment Cancelled - {self.clinic_name}"
        
        body = f"""
        <html>
        <body>
            <h2>Appointment Cancellation</h2>
            <p>Dear {patient_data['first_name']} {patient_data['last_name']},</p>
            
            <p>Your appointment has been cancelled:</p>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Doctor:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['doctor_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_date']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Time:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{appointment_data['appointment_time']}</td>
                </tr>
            </table>
            """
        
        if reason:
            body += f"<p><strong>Reason:</strong> {reason}</p>"
        
        body += f"""
            <p>To reschedule, please call {self.clinic_phone} or reply to this email.</p>
            
            <p>We apologize for any inconvenience.</p>
            
            <p>Best regards,<br>
            {self.clinic_name}<br>
            {self.clinic_phone}<br>
            {self.clinic_email}</p>
        </body>
        </html>
        """
        
        email_sent = self.send_email(patient_data['email'], subject, body)
        
        sms_message = f"""
        {self.clinic_name} - Appointment Cancelled
        {appointment_data['appointment_date']} at {appointment_data['appointment_time']}
        Call {self.clinic_phone} to reschedule
        """
        
        sms_sent = self.send_sms(patient_data['phone'], sms_message)
        
        return email_sent, sms_sent

# Global communication manager instance
comm_manager = CommunicationManager()
