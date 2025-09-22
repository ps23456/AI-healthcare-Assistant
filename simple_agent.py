import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

from config import DOCTORS, NEW_PATIENT_DURATION, RETURNING_PATIENT_DURATION
from database import db

class SimpleMedicalAgent:
    def __init__(self):
        """Initialize the simple medical scheduling agent"""
        self.conversation_state = {
            "step": "greeting",
            "patient_info": {},
            "appointment_info": {},
            "available_slots": [],
            "insurance_info": {}
        }
    
    def process_message(self, user_message: str) -> str:
        """Process a user message and return the agent's response"""
        try:
            user_input = user_message.lower().strip()
            
            if self.conversation_state["step"] == "greeting":
                # If this is the first message, transition to collecting patient info
                self.conversation_state["step"] = "collecting_patient_info"
                return self._handle_patient_info(user_input)
            
            elif self.conversation_state["step"] == "collecting_patient_info":
                return self._handle_patient_info(user_input)
            
            elif self.conversation_state["step"] == "select_doctor":
                return self._handle_doctor_selection(user_input)
            
            elif self.conversation_state["step"] == "select_date":
                return self._handle_date_selection(user_input)
            elif self.conversation_state["step"] == "patient_intake_form":
                return self._handle_patient_intake_form(user_input)
            
            elif self.conversation_state["step"] == "select_time":
                return self._handle_time_selection(user_input)
            
            elif self.conversation_state["step"] == "collect_insurance":
                return self._handle_insurance_collection(user_input)
            
            elif self.conversation_state["step"] == "confirmation":
                return self._handle_confirmation()
            
            else:
                return "I'm sorry, I didn't understand that. Let me start over."
                
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    def _handle_greeting(self) -> str:
        """Handle initial greeting"""
        self.conversation_state["step"] = "collecting_patient_info"
        return """Hello! Welcome to HealthFirst Medical Center. I'm your AI scheduling assistant.

I can help you schedule an appointment with one of our doctors. To get started, I'll need some basic information.

Could you please provide:
1. Your first name
2. Your last name
3. Your date of birth (MM/DD/YYYY format)
4. Your phone number
5. Your email address

Once I have this information, I can check if you're an existing patient or help you register as a new patient."""
    
    def _handle_patient_info(self, user_input: str) -> str:
        """Handle patient information collection"""
        # Extract patient information using regex patterns
        name_pattern = r"my name is (\w+) (\w+)|i'm (\w+) (\w+)|i am (\w+) (\w+)|^(\w+) (\w+)"
        dob_pattern = r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
        phone_pattern = r"(\d{10})|(\d{3})[-.]?(\d{3})[-.]?(\d{4})"
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        
        # Extract information
        name_match = re.search(name_pattern, user_input)
        dob_match = re.search(dob_pattern, user_input)
        phone_match = re.search(phone_pattern, user_input)
        email_match = re.search(email_pattern, user_input)
        
        if name_match:
            groups = name_match.groups()
            # Find the first non-None pair of groups
            for i in range(0, len(groups), 2):
                if i+1 < len(groups) and groups[i] and groups[i+1]:
                    self.conversation_state["patient_info"]['first_name'] = groups[i]
                    self.conversation_state["patient_info"]['last_name'] = groups[i+1]
                    break
        
        if dob_match:
            month, day, year = dob_match.groups()
            self.conversation_state["patient_info"]['date_of_birth'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        if phone_match:
            if phone_match.group(1):  # 10-digit format
                phone = phone_match.group(1)
                self.conversation_state["patient_info"]['phone'] = f"+1-{phone[:3]}-{phone[3:6]}-{phone[6:]}"
            else:  # 3-3-4 format
                self.conversation_state["patient_info"]['phone'] = f"+1-{phone_match.group(2)}-{phone_match.group(3)}-{phone_match.group(4)}"
        
        if email_match:
            self.conversation_state["patient_info"]['email'] = email_match.group(0)
        
        # Check if we have all required information
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email']
        missing_fields = [field for field in required_fields if field not in self.conversation_state["patient_info"]]
        
        if missing_fields:
            response = f"I have the following information:\n"
            for field in required_fields:
                if field in self.conversation_state["patient_info"]:
                    response += f"✓ {field.replace('_', ' ').title()}: {self.conversation_state['patient_info'][field]}\n"
                else:
                    response += f"✗ {field.replace('_', ' ').title()}: Please provide\n"
            
            response += f"\nI still need: {', '.join(missing_fields).replace('_', ' ').title()}"
            return response
        else:
            # Search for existing patient
            patients = db.find_patient(
                first_name=self.conversation_state["patient_info"]['first_name'],
                last_name=self.conversation_state["patient_info"]['last_name']
            )
            
            if len(patients) > 0:
                # Existing patient
                patient = patients.iloc[0]
                self.conversation_state["patient_info"]['patient_id'] = patient['patient_id']
                self.conversation_state["patient_info"]['is_new_patient'] = False
                
                response = f"Welcome back, {self.conversation_state['patient_info']['first_name']}! I found your existing record.\n\n"
                response += "Now I need to know which doctor you'd like to see. Here are our available doctors:\n"
                
                for doctor_name, doctor_info in DOCTORS.items():
                    response += f"• {doctor_name} - {doctor_info['specialty']} ({doctor_info['location']})\n"
                
                response += "\nWhich doctor would you prefer to see?"
                self.conversation_state["step"] = "select_doctor"
            else:
                # New patient
                response = f"Thank you, {self.conversation_state['patient_info']['first_name']}! I don't see you in our system, so I'll register you as a new patient.\n\n"
                response += "Now I need to know which doctor you'd like to see. Here are our available doctors:\n"
                
                for doctor_name, doctor_info in DOCTORS.items():
                    response += f"• {doctor_name} - {doctor_info['specialty']} ({doctor_info['location']})\n"
                
                response += "\nWhich doctor would you prefer to see?"
                self.conversation_state["step"] = "select_doctor"
            
            return response
    
    def _handle_doctor_selection(self, user_input: str) -> str:
        """Handle doctor selection"""
        # Match doctor name
        selected_doctor = None
        user_input_lower = user_input.lower()
        
        for doctor_name in DOCTORS.keys():
            doctor_name_lower = doctor_name.lower()
            # Check if the full doctor name is in the input
            if doctor_name_lower in user_input_lower:
                selected_doctor = doctor_name
                break
            # Check if individual words match (for partial matches)
            elif any(word in user_input_lower for word in doctor_name_lower.split()):
                # Make sure it's not a false positive by checking if it's a meaningful match
                if len(doctor_name_lower.split()) > 1:  # Multi-word names
                    words = doctor_name_lower.split()
                    if any(word in user_input_lower for word in words):
                        selected_doctor = doctor_name
                        break
        
        if selected_doctor:
            self.conversation_state["appointment_info"]['doctor_name'] = selected_doctor
            doctor_info = DOCTORS[selected_doctor]
            
            response = f"Great choice! Dr. {selected_doctor} is a {doctor_info['specialty']} specialist.\n\n"
            response += "When would you like to schedule your appointment? Please provide a date (MM/DD/YYYY format) or you can say 'earliest available'."
            
            self.conversation_state["step"] = "select_date"
        else:
            response = "I didn't recognize that doctor's name. Please choose from our available doctors:\n"
            for doctor_name, doctor_info in DOCTORS.items():
                response += f"• {doctor_name} - {doctor_info['specialty']}\n"
        
        return response
    
    def _handle_date_selection(self, user_input: str) -> str:
        """Handle date selection and time slot selection"""
        # Debug: Print the actual user input to understand the format
        print(f"DEBUG: User input in _handle_date_selection: '{user_input}'")
        
        # Check if this is a time slot selection (contains "at" and time)
        # Pattern to match: "I want to schedule for {date} at {time} - {location}"
        time_pattern = r"at (\d{1,2}:\d{2}) - (.+)"
        time_match = re.search(time_pattern, user_input)
        
        # Debug: Print regex match result
        print(f"DEBUG: Regex match result: {time_match}")
        
        if time_match:
            # This is a time slot selection, handle it
            selected_time = time_match.group(1)
            selected_location = time_match.group(2)
            
            # Update appointment info
            self.conversation_state["appointment_info"]['appointment_time'] = selected_time
            self.conversation_state["appointment_info"]['location'] = selected_location
            
            # Store the appointment in the database with PENDING status
            try:
                appointment_id = db.create_appointment(
                    patient_id=self.conversation_state["patient_info"].get('patient_id', 'NEW'),
                    doctor_name=self.conversation_state["appointment_info"]['doctor_name'],
                    appointment_date=self.conversation_state["appointment_info"]['appointment_date'],
                    appointment_time=selected_time,
                    location=selected_location,
                    status='pending'  # Changed to pending - not confirmed yet
                )
                self.conversation_state["appointment_info"]['appointment_id'] = appointment_id
                print(f"DEBUG: Appointment created with ID: {appointment_id}")
            except Exception as e:
                print(f"DEBUG: Error creating appointment: {str(e)}")
            
            response = f"📅 Appointment scheduled for {self.conversation_state['appointment_info']['appointment_date']} at {selected_time}.\n\n"
            response += f"⚠️ **IMPORTANT**: Your appointment is PENDING confirmation.\n\n"
            response += f"To confirm your appointment, please complete the Patient Intake Form.\n"
            response += f"You can access it from the 'Patient Intake Forms' section in the sidebar."
            
            # Set the conversation step back to greeting for new interactions
            self.conversation_state["step"] = "greeting"
            return response
        
        # If no time match found, check if this is a general time slot selection
        # Pattern to match: "I want to schedule for {date} at {full_time_string}"
        if "I want to schedule for" in user_input and " at " in user_input:
            # Extract the time part after "at "
            parts = user_input.split(" at ")
            if len(parts) > 1:
                time_part = parts[1].strip()
                # Extract time and location from the time part
                time_location_match = re.search(r"(\d{1,2}:\d{2}) - (.+)", time_part)
                if time_location_match:
                    selected_time = time_location_match.group(1)
                    selected_location = time_location_match.group(2)
                    
                    # Update appointment info
                    self.conversation_state["appointment_info"]['appointment_time'] = selected_time
                    self.conversation_state["appointment_info"]['location'] = selected_location
                    
                    # Store the appointment in the database
                    try:
                        appointment_id = db.create_appointment(
                            patient_id=self.conversation_state["patient_info"].get('patient_id', 'NEW'),
                            doctor_name=self.conversation_state["appointment_info"]['doctor_name'],
                            appointment_date=self.conversation_state["appointment_info"]['appointment_date'],
                            appointment_time=selected_time,
                            location=selected_location,
                            status='confirmed'
                        )
                        self.conversation_state["appointment_info"]['appointment_id'] = appointment_id
                        print(f"DEBUG: Appointment created with ID: {appointment_id}")
                    except Exception as e:
                        print(f"DEBUG: Error creating appointment: {str(e)}")
                    
                    response = f"Great! I've scheduled your appointment for {self.conversation_state['appointment_info']['appointment_date']} at {selected_time}.\n\n"
                    response += f"Your appointment has been confirmed and stored in our system.\n\n"
                    response += "You can now complete the patient intake form to provide additional medical information. "
                    response += "This will help us provide you with the best care possible.\n\n"
                    response += "To access the patient intake form, go to the 'View All Appointments' section and click on 'Patient Intake Form' for your appointment."
                    
                    # Set the conversation step back to greeting for new interactions
                    self.conversation_state["step"] = "greeting"
                    return response
        
        # If still no match, check if this is just a time selection (e.g., "15:30")
        time_only_pattern = r"^(\d{1,2}:\d{2})$"
        time_only_match = re.search(time_only_pattern, user_input.strip())
        if time_only_match:
            selected_time = time_only_match.group(1)
            
            # Update appointment info
            self.conversation_state["appointment_info"]['appointment_time'] = selected_time
            self.conversation_state["appointment_info"]['location'] = 'Main Campus'  # Default location
            
            # Store the appointment in the database
            try:
                appointment_id = db.create_appointment(
                    patient_id=self.conversation_state["patient_info"].get('patient_id', 'NEW'),
                    doctor_name=self.conversation_state["appointment_info"]['doctor_name'],
                    appointment_date=self.conversation_state["appointment_info"]['appointment_date'],
                    appointment_time=selected_time,
                    location='Main Campus',
                    status='confirmed'
                )
                self.conversation_state["appointment_info"]['appointment_id'] = appointment_id
                print(f"DEBUG: Appointment created with ID: {appointment_id}")
            except Exception as e:
                print(f"DEBUG: Error creating appointment: {str(e)}")
            
            response = f"✅ Appointment confirmed for {self.conversation_state['appointment_info']['appointment_date']} at {selected_time}.\n\n"
            response += f"Your appointment has been saved to the system. You can view it in the 'Total Appointments' section."
            
            # Set the conversation step back to greeting for new interactions
            self.conversation_state["step"] = "greeting"
            return response
        
        # Original date selection logic
        # Extract date - support multiple formats
        date_patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",  # MM/DD/YYYY or MM-DD-YYYY
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",  # YYYY/MM/DD or YYYY-MM-DD
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{2})",   # MM/DD/YY or MM-DD-YY
        ]
        
        date_match = None
        for pattern in date_patterns:
            date_match = re.search(pattern, user_input)
            if date_match:
                break
        
        if date_match:
            groups = date_match.groups()
            if len(groups) == 3:
                if len(groups[0]) == 4:  # YYYY-MM-DD format
                    year, month, day = groups[0], groups[1], groups[2]
                elif len(groups[2]) == 4:  # MM-DD-YYYY format
                    month, day, year = groups[0], groups[1], groups[2]
                elif len(groups[2]) == 2:  # MM-DD-YY format
                    month, day, year = groups[0], groups[1], "20" + groups[2]
                else:
                    return "I couldn't understand that date format. Please use MM/DD/YYYY format."
                
                selected_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Check if date is valid and in the future
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
                if date_obj.date() < datetime.now().date():
                    return "That date is in the past. Please select a future date."
                
                self.conversation_state["appointment_info"]['appointment_date'] = selected_date
                
                # Get available slots
                doctor_name = self.conversation_state["appointment_info"].get('doctor_name', 'Dr. Sarah Johnson')
                slots = db.get_available_slots(
                    doctor_name=doctor_name,
                    date=selected_date
                )
                
                if slots:
                    self.conversation_state["available_slots"] = slots
                    print(f"DEBUG: Stored {len(slots)} slots in agent state")
                    
                    response = f"Great! I found available slots for {selected_date}.\n\n"
                    response += f"Here are the available time slots for Dr. {self.conversation_state['appointment_info']['doctor_name']}:\n\n"
                    
                    for i, slot in enumerate(slots, 1):
                        response += f"{i}. {slot['time_slot']} - {slot['location']}\n"
                    
                    response += f"\nPlease select your preferred time slot by saying the time (e.g., '15:30') or 'I want to schedule for {selected_date} at 15:30 - Main Campus'."
                    
                    # Stay in select_date step to allow time slot selection
                    self.conversation_state["step"] = "select_date"
                else:
                    response = f"I'm sorry, but Dr. {self.conversation_state['appointment_info']['doctor_name']} doesn't have any available slots on {selected_date}. "
                    response += "Would you like to try a different date?"
                
            except ValueError:
                response = "I couldn't understand that date format. Please use MM/DD/YYYY format."
        elif "earliest" in user_input or "soonest" in user_input:
            # Find earliest available date
            today = datetime.now()
            for i in range(30):  # Check next 30 days
                check_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
                slots = db.get_available_slots(
                    doctor_name=self.conversation_state["appointment_info"]['doctor_name'],
                    date=check_date
                )
                if slots:
                    self.conversation_state["appointment_info"]['appointment_date'] = check_date
                    self.conversation_state["available_slots"] = slots
                    
                    response = f"Great! I've scheduled your appointment for {check_date}.\n\n"
                    response += "Now I need to collect your complete patient information. This will help us provide you with the best care possible.\n\n"
                    response += "I'll guide you through a comprehensive patient intake form step by step. This includes:\n"
                    response += "• Personal Information\n"
                    response += "• Contact Information\n"
                    response += "• Address Information\n"
                    response += "• Medical Information\n"
                    response += "• Insurance Information\n"
                    response += "• Employment & Lifestyle\n"
                    response += "• Emergency & Legal Information\n"
                    response += "• Review & Consent\n\n"
                    response += "Please proceed with the patient intake form below."
                    
                    self.conversation_state["step"] = "patient_intake_form"
                    break
            else:
                response = f"I'm sorry, but Dr. {self.conversation_state['appointment_info']['doctor_name']} doesn't have any available appointments in the next 30 days."
        else:
            response = "I didn't understand that date. Please provide a date in MM/DD/YYYY format or say 'earliest available'."
        
        return response
    
    def _handle_time_selection(self, user_input: str) -> str:
        """Handle time slot selection"""
        # Extract time selection
        selected_slot = None
        
        # Check for number selection
        number_match = re.search(r"(\d+)", user_input)
        if number_match:
            slot_index = int(number_match.group(1)) - 1
            if 0 <= slot_index < len(self.conversation_state["available_slots"]):
                selected_slot = self.conversation_state["available_slots"][slot_index]
        
        # Check for time selection
        if not selected_slot:
            for slot in self.conversation_state["available_slots"]:
                if slot['time_slot'] in user_input:
                    selected_slot = slot
                    break
        
        if selected_slot:
            self.conversation_state["appointment_info"]['appointment_time'] = selected_slot['time_slot']
            self.conversation_state["appointment_info"]['location'] = selected_slot['location']
            
            # Determine appointment duration
            if self.conversation_state["patient_info"].get('is_new_patient', True):
                self.conversation_state["appointment_info"]['duration'] = NEW_PATIENT_DURATION
            else:
                self.conversation_state["appointment_info"]['duration'] = RETURNING_PATIENT_DURATION
            
            response = f"Perfect! I've selected {selected_slot['time_slot']} for your appointment.\n\n"
            response += f"Appointment Summary:\n"
            response += f"• Doctor: Dr. {self.conversation_state['appointment_info']['doctor_name']}\n"
            response += f"• Date: {self.conversation_state['appointment_info']['appointment_date']}\n"
            response += f"• Time: {self.conversation_state['appointment_info']['appointment_time']}\n"
            response += f"• Duration: {self.conversation_state['appointment_info']['duration']} minutes\n"
            response += f"• Location: {self.conversation_state['appointment_info']['location']}\n\n"
            
            response += "Now I need to collect your insurance information. What is your insurance carrier?"
            self.conversation_state["step"] = "collect_insurance"
        else:
            response = "I didn't understand your time selection. Please choose a number from the list or specify the time."
        
        return response
    
    def _handle_insurance_collection(self, user_input: str) -> str:
        """Handle insurance information collection"""
        if 'insurance_carrier' not in self.conversation_state["insurance_info"]:
            self.conversation_state["insurance_info"]['insurance_carrier'] = user_input.strip()
            return "Thank you! What is your member ID number?"
        elif 'member_id' not in self.conversation_state["insurance_info"]:
            self.conversation_state["insurance_info"]['member_id'] = user_input.strip()
            return "Great! What is your group number?"
        elif 'group_number' not in self.conversation_state["insurance_info"]:
            self.conversation_state["insurance_info"]['group_number'] = user_input.strip()
            
            # Complete appointment booking
            response = "Excellent! I have all the information I need. Let me book your appointment now.\n\n"
            
            # Prepare appointment data
            appointment_data = {
                'doctor_name': self.conversation_state["appointment_info"]['doctor_name'],
                'appointment_date': self.conversation_state["appointment_info"]['appointment_date'],
                'appointment_time': self.conversation_state["appointment_info"]['appointment_time'],
                'duration': self.conversation_state["appointment_info"]['duration'],
                'insurance_carrier': self.conversation_state["insurance_info"]['insurance_carrier'],
                'member_id': self.conversation_state["insurance_info"]['member_id'],
                'group_number': self.conversation_state["insurance_info"]['group_number']
            }
            
            # If new patient, add to database first
            if not self.conversation_state["patient_info"].get('patient_id'):
                patient_data = {
                    'first_name': self.conversation_state["patient_info"]['first_name'],
                    'last_name': self.conversation_state["patient_info"]['last_name'],
                    'date_of_birth': self.conversation_state["patient_info"]['date_of_birth'],
                    'phone': self.conversation_state["patient_info"]['phone'],
                    'email': self.conversation_state["patient_info"]['email'],
                    'insurance_carrier': self.conversation_state["insurance_info"]['insurance_carrier'],
                    'member_id': self.conversation_state["insurance_info"]['member_id'],
                    'group_number': self.conversation_state["insurance_info"]['group_number']
                }
                
                patient_id = db.add_patient(patient_data)
                appointment_data['patient_id'] = patient_id
                self.conversation_state["patient_info"]['patient_id'] = patient_id
            else:
                appointment_data['patient_id'] = self.conversation_state["patient_info"]['patient_id']
            
            # Book appointment
            appointment_id = db.book_appointment(appointment_data)
            
            response += f"✅ Your appointment has been successfully booked!\n\n"
            response += f"Appointment ID: {appointment_id}\n"
            response += f"Doctor: Dr. {appointment_data['doctor_name']}\n"
            response += f"Date: {appointment_data['appointment_date']}\n"
            response += f"Time: {appointment_data['appointment_time']}\n"
            response += f"Duration: {appointment_data['duration']} minutes\n"
            response += f"Location: {self.conversation_state['appointment_info']['location']}\n\n"
            
            response += "Your appointment has been confirmed and saved to our system. "
            response += "You'll receive a confirmation email with all the details and a pre-appointment intake form.\n\n"
            response += "Is there anything else I can help you with?"
            
            self.conversation_state["step"] = "confirmation"
        
        return response
    
    def _handle_confirmation(self) -> str:
        """Handle post-booking confirmation"""
        return "Thank you for choosing HealthFirst Medical Center! Your appointment has been successfully scheduled. Please check your email for confirmation details and the intake form. Have a great day!"

    def _handle_patient_intake_form(self, user_input: str) -> str:
        """Handle patient intake form completion"""
        if "completed" in user_input.lower():
            response = "Excellent! Your patient intake form has been completed successfully.\n\n"
            response += "Your appointment is now fully scheduled and your information has been recorded in our system.\n\n"
            response += "**Next Steps:**\n"
            response += "1. You will receive a confirmation email with your appointment details\n"
            response += "2. Please arrive 15 minutes before your scheduled appointment time\n"
            response += "3. Bring your ID and insurance card with you\n"
            response += "4. If you need to reschedule, please call us at least 24 hours in advance\n\n"
            response += "**Reminder:** You will receive automated reminders via email and SMS before your appointment.\n\n"
            response += "Thank you for choosing HealthFirst Medical Center. We look forward to seeing you!"
            
            # Reset conversation state for next patient
            self.conversation_state = {
                "step": "greeting",
                "patient_info": {},
                "appointment_info": {},
                "available_slots": [],
                "insurance_info": {}
            }
            
            return response
        else:
            return "Please complete the patient intake form to proceed with your appointment scheduling."

# Global agent instance
agent = SimpleMedicalAgent()
