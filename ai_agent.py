import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.tools import tool
from langchain.schema import HumanMessage, AIMessage
import json

from config import OPENAI_API_KEY, DOCTORS, NEW_PATIENT_DURATION, RETURNING_PATIENT_DURATION
from database import db
from communication import comm_manager

# Initialize LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo",
    temperature=0.1
)

# Define state structure
class AgentState:
    def __init__(self):
        self.messages = []
        self.current_step = "greeting"
        self.patient_info = {}
        self.appointment_info = {}
        self.available_slots = []
        self.insurance_info = {}
        self.confirmation_sent = False
        self.intake_form_sent = False
        self.error_message = None

# Tools for the AI agent
@tool
def search_patient(first_name: str, last_name: str) -> str:
    """Search for existing patient in the database"""
    try:
        patients = db.find_patient(first_name=first_name, last_name=last_name)
        if len(patients) > 0:
            patient = patients.iloc[0]
            return json.dumps({
                "found": True,
                "patient_id": patient['patient_id'],
                "is_new_patient": patient['is_new_patient'],
                "phone": patient['phone'],
                "email": patient['email'],
                "insurance_carrier": patient['insurance_carrier'],
                "member_id": patient['member_id'],
                "group_number": patient['group_number']
            })
        else:
            return json.dumps({"found": False})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def add_new_patient(patient_data: str) -> str:
    """Add a new patient to the database"""
    try:
        data = json.loads(patient_data)
        patient_id = db.add_patient(data)
        return json.dumps({"success": True, "patient_id": patient_id})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def get_available_slots(doctor_name: str, date: str) -> str:
    """Get available time slots for a doctor on a specific date"""
    try:
        slots = db.get_available_slots(doctor_name, date)
        return json.dumps({"slots": slots})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def book_appointment(appointment_data: str) -> str:
    """Book an appointment in the database"""
    try:
        data = json.loads(appointment_data)
        appointment_id = db.book_appointment(data)
        return json.dumps({"success": True, "appointment_id": appointment_id})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def send_confirmation(appointment_data: str, patient_data: str) -> str:
    """Send appointment confirmation email and SMS"""
    try:
        app_data = json.loads(appointment_data)
        pat_data = json.loads(patient_data)
        email_sent, sms_sent = comm_manager.send_appointment_confirmation(app_data, pat_data)
        return json.dumps({"email_sent": email_sent, "sms_sent": sms_sent})
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def send_intake_form(appointment_data: str, patient_data: str) -> str:
    """Send intake form to patient"""
    try:
        app_data = json.loads(appointment_data)
        pat_data = json.loads(patient_data)
        success = comm_manager.send_intake_form(app_data, pat_data)
        return json.dumps({"success": success})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Create tool executor
tools = [search_patient, add_new_patient, get_available_slots, book_appointment, send_confirmation, send_intake_form]

# Define the conversation flow
def greeting_node(state: AgentState) -> AgentState:
    """Initial greeting and patient identification"""
    messages = state.messages
    if not messages:
        response = """Hello! Welcome to HealthFirst Medical Center. I'm your AI scheduling assistant. 
        
I can help you schedule an appointment with one of our doctors. To get started, I'll need some basic information.

Could you please provide:
1. Your first name
2. Your last name
3. Your date of birth (MM/DD/YYYY format)
4. Your phone number
5. Your email address

Once I have this information, I can check if you're an existing patient or help you register as a new patient."""
        
        state.messages.append(AIMessage(content=response))
        state.current_step = "collecting_patient_info"
    
    return state

def collect_patient_info_node(state: AgentState) -> AgentState:
    """Collect and validate patient information"""
    messages = state.messages
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        # Extract patient information using regex patterns
        name_pattern = r"my name is (\w+) (\w+)|i'm (\w+) (\w+)|i am (\w+) (\w+)"
        dob_pattern = r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
        phone_pattern = r"(\d{3})[-.]?(\d{3})[-.]?(\d{4})"
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        
        # Extract information
        name_match = re.search(name_pattern, user_input)
        dob_match = re.search(dob_pattern, user_input)
        phone_match = re.search(phone_pattern, user_input)
        email_match = re.search(email_pattern, user_input)
        
        if name_match:
            groups = name_match.groups()
            if groups[0] and groups[1]:
                state.patient_info['first_name'] = groups[0]
                state.patient_info['last_name'] = groups[1]
            elif groups[2] and groups[3]:
                state.patient_info['first_name'] = groups[2]
                state.patient_info['last_name'] = groups[3]
            elif groups[4] and groups[5]:
                state.patient_info['first_name'] = groups[4]
                state.patient_info['last_name'] = groups[5]
        
        if dob_match:
            month, day, year = dob_match.groups()
            state.patient_info['date_of_birth'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        if phone_match:
            state.patient_info['phone'] = f"+1-{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"
        
        if email_match:
            state.patient_info['email'] = email_match.group(0)
        
        # Check if we have all required information
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email']
        missing_fields = [field for field in required_fields if field not in state.patient_info]
        
        if missing_fields:
            response = f"I have the following information:\n"
            for field in required_fields:
                if field in state.patient_info:
                    response += f"✓ {field.replace('_', ' ').title()}: {state.patient_info[field]}\n"
                else:
                    response += f"✗ {field.replace('_', ' ').title()}: Please provide\n"
            
            response += f"\nI still need: {', '.join(missing_fields).replace('_', ' ').title()}"
        else:
            # Search for existing patient
            search_result = json.loads(search_patient(
                first_name=state.patient_info['first_name'],
                last_name=state.patient_info['last_name']
            ))
            
            if search_result.get('found'):
                # Existing patient
                state.patient_info['patient_id'] = search_result['patient_id']
                state.patient_info['is_new_patient'] = search_result['is_new_patient']
                state.patient_info['insurance_carrier'] = search_result['insurance_carrier']
                state.patient_info['member_id'] = search_result['member_id']
                state.patient_info['group_number'] = search_result['group_number']
                
                response = f"Welcome back, {state.patient_info['first_name']}! I found your existing record. "
                response += f"You're scheduled to see Dr. {search_result.get('doctor_name', 'TBD')} on {search_result.get('appointment_date', 'TBD')}.\n\n"
                response += "What would you like to do?\n1. Schedule a new appointment\n2. Modify existing appointment\n3. Cancel appointment"
                
                state.current_step = "existing_patient_options"
            else:
                # New patient
                response = f"Thank you, {state.patient_info['first_name']}! I don't see you in our system, so I'll register you as a new patient.\n\n"
                response += "Now I need to know which doctor you'd like to see. Here are our available doctors:\n"
                
                for doctor_name, doctor_info in DOCTORS.items():
                    response += f"• {doctor_name} - {doctor_info['specialty']} ({doctor_info['location']})\n"
                
                response += "\nWhich doctor would you prefer to see?"
                
                state.current_step = "select_doctor"
        
        state.messages.append(AIMessage(content=response))
    
    return state

def select_doctor_node(state: AgentState) -> AgentState:
    """Handle doctor selection"""
    messages = state.messages
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        # Match doctor name
        selected_doctor = None
        for doctor_name in DOCTORS.keys():
            if doctor_name.lower() in user_input or any(word in user_input for word in doctor_name.lower().split()):
                selected_doctor = doctor_name
                break
        
        if selected_doctor:
            state.appointment_info['doctor_name'] = selected_doctor
            doctor_info = DOCTORS[selected_doctor]
            
            response = f"Great choice! Dr. {selected_doctor} is a {doctor_info['specialty']} specialist.\n\n"
            response += "When would you like to schedule your appointment? Please provide a date (MM/DD/YYYY format) or you can say 'earliest available'."
            
            state.current_step = "select_date"
        else:
            response = "I didn't recognize that doctor's name. Please choose from our available doctors:\n"
            for doctor_name, doctor_info in DOCTORS.items():
                response += f"• {doctor_name} - {doctor_info['specialty']}\n"
        
        state.messages.append(AIMessage(content=response))
    
    return state

def select_date_node(state: AgentState) -> AgentState:
    """Handle date selection"""
    messages = state.messages
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        # Extract date
        date_pattern = r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
        date_match = re.search(date_pattern, user_input)
        
        if date_match:
            month, day, year = date_match.groups()
            selected_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Check if date is valid and in the future
            try:
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
                if date_obj.date() < datetime.now().date():
                    response = "That date is in the past. Please select a future date."
                    state.messages.append(AIMessage(content=response))
                    return state
                
                state.appointment_info['appointment_date'] = selected_date
                
                # Get available slots
                slots_result = json.loads(get_available_slots(
                    doctor_name=state.appointment_info['doctor_name'],
                    date=selected_date
                ))
                
                if slots_result.get('slots'):
                    state.available_slots = slots_result['slots']
                    
                    response = f"Great! Here are the available time slots for {selected_date}:\n"
                    for i, slot in enumerate(state.available_slots, 1):
                        response += f"{i}. {slot['time_slot']} ({slot['location']})\n"
                    
                    response += "\nWhich time slot would you prefer?"
                    state.current_step = "select_time"
                else:
                    response = f"I'm sorry, but Dr. {state.appointment_info['doctor_name']} doesn't have any available slots on {selected_date}. "
                    response += "Would you like to try a different date?"
                    state.current_step = "select_date"
                
            except ValueError:
                response = "I couldn't understand that date format. Please use MM/DD/YYYY format."
                state.current_step = "select_date"
        elif "earliest" in user_input or "soonest" in user_input:
            # Find earliest available date
            today = datetime.now()
            for i in range(30):  # Check next 30 days
                check_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
                slots_result = json.loads(get_available_slots(
                    doctor_name=state.appointment_info['doctor_name'],
                    date=check_date
                ))
                if slots_result.get('slots'):
                    state.appointment_info['appointment_date'] = check_date
                    state.available_slots = slots_result['slots']
                    
                    response = f"The earliest available appointment with Dr. {state.appointment_info['doctor_name']} is on {check_date}.\n\n"
                    response += "Available time slots:\n"
                    for i, slot in enumerate(state.available_slots, 1):
                        response += f"{i}. {slot['time_slot']} ({slot['location']})\n"
                    
                    response += "\nWhich time slot would you prefer?"
                    state.current_step = "select_time"
                    break
            else:
                response = "I'm sorry, but Dr. {state.appointment_info['doctor_name']} doesn't have any available appointments in the next 30 days."
        else:
            response = "I didn't understand that date. Please provide a date in MM/DD/YYYY format or say 'earliest available'."
        
        state.messages.append(AIMessage(content=response))
    
    return state

def select_time_node(state: AgentState) -> AgentState:
    """Handle time slot selection"""
    messages = state.messages
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        # Extract time selection
        selected_slot = None
        
        # Check for number selection
        number_match = re.search(r"(\d+)", user_input)
        if number_match:
            slot_index = int(number_match.group(1)) - 1
            if 0 <= slot_index < len(state.available_slots):
                selected_slot = state.available_slots[slot_index]
        
        # Check for time selection
        if not selected_slot:
            for slot in state.available_slots:
                if slot['time_slot'] in user_input:
                    selected_slot = slot
                    break
        
        if selected_slot:
            state.appointment_info['appointment_time'] = selected_slot['time_slot']
            state.appointment_info['location'] = selected_slot['location']
            
            # Determine appointment duration
            if state.patient_info.get('is_new_patient', True):
                state.appointment_info['duration'] = NEW_PATIENT_DURATION
            else:
                state.appointment_info['duration'] = RETURNING_PATIENT_DURATION
            
            response = f"Perfect! I've selected {selected_slot['time_slot']} for your appointment.\n\n"
            response += f"Appointment Summary:\n"
            response += f"• Doctor: Dr. {state.appointment_info['doctor_name']}\n"
            response += f"• Date: {state.appointment_info['appointment_date']}\n"
            response += f"• Time: {state.appointment_info['appointment_time']}\n"
            response += f"• Duration: {state.appointment_info['duration']} minutes\n"
            response += f"• Location: {state.appointment_info['location']}\n\n"
            
            response += "Now I need to collect your insurance information. What is your insurance carrier?"
            state.current_step = "collect_insurance"
        else:
            response = "I didn't understand your time selection. Please choose a number from the list or specify the time."
        
        state.messages.append(AIMessage(content=response))
    
    return state

def collect_insurance_node(state: AgentState) -> AgentState:
    """Collect insurance information"""
    messages = state.messages
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        user_input = last_message.content.lower()
        
        # Extract insurance information
        if 'insurance' not in state.insurance_info:
            state.insurance_info['insurance_carrier'] = user_input.strip()
            
            response = "Thank you! What is your member ID number?"
            state.current_step = "collect_insurance"
        elif 'member_id' not in state.insurance_info:
            state.insurance_info['member_id'] = user_input.strip()
            
            response = "Great! What is your group number?"
            state.current_step = "collect_insurance"
        elif 'group_number' not in state.insurance_info:
            state.insurance_info['group_number'] = user_input.strip()
            
            # Complete appointment booking
            response = "Excellent! I have all the information I need. Let me book your appointment now.\n\n"
            
            # Prepare appointment data
            appointment_data = {
                'patient_id': state.patient_info.get('patient_id'),
                'doctor_name': state.appointment_info['doctor_name'],
                'appointment_date': state.appointment_info['appointment_date'],
                'appointment_time': state.appointment_info['appointment_time'],
                'duration': state.appointment_info['duration'],
                'insurance_carrier': state.insurance_info['insurance_carrier'],
                'member_id': state.insurance_info['member_id'],
                'group_number': state.insurance_info['group_number']
            }
            
            # If new patient, add to database first
            if not state.patient_info.get('patient_id'):
                patient_data = {
                    'first_name': state.patient_info['first_name'],
                    'last_name': state.patient_info['last_name'],
                    'date_of_birth': state.patient_info['date_of_birth'],
                    'phone': state.patient_info['phone'],
                    'email': state.patient_info['email'],
                    'insurance_carrier': state.insurance_info['insurance_carrier'],
                    'member_id': state.insurance_info['member_id'],
                    'group_number': state.insurance_info['group_number']
                }
                
                add_result = json.loads(add_new_patient(json.dumps(patient_data)))
                if add_result.get('success'):
                    appointment_data['patient_id'] = add_result['patient_id']
                    state.patient_info['patient_id'] = add_result['patient_id']
            
            # Book appointment
            book_result = json.loads(book_appointment(json.dumps(appointment_data)))
            if book_result.get('success'):
                appointment_data['appointment_id'] = book_result['appointment_id']
                
                response += f"✅ Your appointment has been successfully booked!\n\n"
                response += f"Appointment ID: {book_result['appointment_id']}\n"
                response += f"Doctor: Dr. {appointment_data['doctor_name']}\n"
                response += f"Date: {appointment_data['appointment_date']}\n"
                response += f"Time: {appointment_data['appointment_time']}\n"
                response += f"Duration: {appointment_data['duration']} minutes\n"
                response += f"Location: {state.appointment_info['location']}\n\n"
                
                response += "I'll now send you a confirmation email and SMS with all the details. "
                response += "You'll also receive a pre-appointment intake form to complete before your visit.\n\n"
                response += "Is there anything else I can help you with?"
                
                state.current_step = "confirmation"
                state.confirmation_sent = True
            else:
                response = f"I'm sorry, but there was an error booking your appointment: {book_result.get('error', 'Unknown error')}. "
                response += "Please try again or contact our office directly."
                state.error_message = book_result.get('error')
        
        state.messages.append(AIMessage(content=response))
    
    return state

def confirmation_node(state: AgentState) -> AgentState:
    """Handle post-booking confirmation and communications"""
    if state.confirmation_sent and not state.intake_form_sent:
        # Send confirmation and intake form
        try:
            # Send confirmation
            appointment_data = {
                'doctor_name': state.appointment_info['doctor_name'],
                'appointment_date': state.appointment_info['appointment_date'],
                'appointment_time': state.appointment_info['appointment_time'],
                'duration': state.appointment_info['duration']
            }
            
            patient_data = {
                'first_name': state.patient_info['first_name'],
                'last_name': state.patient_info['last_name'],
                'phone': state.patient_info['phone'],
                'email': state.patient_info['email']
            }
            
            # Send confirmation
            send_confirmation(json.dumps(appointment_data), json.dumps(patient_data))
            
            # Send intake form
            send_intake_form(json.dumps(appointment_data), json.dumps(patient_data))
            
            state.intake_form_sent = True
            
        except Exception as e:
            print(f"Error sending communications: {str(e)}")
    
    return state

# Create the workflow graph
def create_workflow():
    """Create the LangGraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("collect_patient_info", collect_patient_info_node)
    workflow.add_node("select_doctor", select_doctor_node)
    workflow.add_node("select_date", select_date_node)
    workflow.add_node("select_time", select_time_node)
    workflow.add_node("collect_insurance", collect_insurance_node)
    workflow.add_node("confirmation", confirmation_node)
    
    # Add edges
    workflow.add_edge("greeting", "collect_patient_info")
    workflow.add_edge("collect_patient_info", "select_doctor")
    workflow.add_edge("select_doctor", "select_date")
    workflow.add_edge("select_date", "select_time")
    workflow.add_edge("select_time", "collect_insurance")
    workflow.add_edge("collect_insurance", "confirmation")
    workflow.add_edge("confirmation", END)
    
    # Set entry point
    workflow.set_entry_point("greeting")
    
    return workflow.compile()

# Create the workflow instance
workflow = create_workflow()

class MedicalSchedulingAgent:
    def __init__(self):
        """Initialize the medical scheduling agent"""
        self.workflow = workflow
        self.state = AgentState()
    
    def process_message(self, user_message: str) -> str:
        """Process a user message and return the agent's response"""
        try:
            # Add user message to state
            self.state.messages.append(HumanMessage(content=user_message))
            
            # Run the workflow
            result = self.workflow.invoke(self.state)
            
            # Get the last AI message
            if result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content
            
            return "I'm sorry, I didn't understand that. Could you please rephrase?"
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again or contact our office directly."

# Global agent instance
agent = MedicalSchedulingAgent()
