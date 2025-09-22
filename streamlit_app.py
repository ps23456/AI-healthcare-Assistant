import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_agent import agent
from database import db
from data_generator import create_sample_data
from communication import comm_manager
from config import DOCTORS

# Page configuration
st.set_page_config(
    page_title="HealthFirst Medical Center - AI Scheduling Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 500px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .ai-message {
        background-color: #e9ecef;
        color: #212529;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: left;
    }
    .sidebar-header {
        background: linear-gradient(90deg, #28a745, #20c997);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .form-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .form-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.75rem;
    }
    .calendar-slot-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .time-slot-item {
        background-color: white;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        border: 1px solid #e9ecef;
    }
    .time-slot-button {
        background-color: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0.25rem;
        color: #007bff;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .time-slot-button:hover {
        background-color: #007bff;
        color: white;
    }
    .time-slot-button.selected {
        background-color: #007bff;
        color: white;
        border-color: #0056b3;
    }
    .calendar-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 HealthFirst Medical Center</h1>
        <h3>AI-Powered Appointment Scheduling Assistant</h3>
        <p>Streamline your healthcare experience with intelligent appointment booking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h4>📊 System Dashboard</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize data if needed
        if st.button("🔄 Initialize Sample Data"):
            with st.spinner("Creating sample data..."):
                create_sample_data()
            st.success("Sample data created successfully!")
        
        # System metrics
        try:
            total_patients = len(db.patients_df)
            total_appointments = len(db.appointments_df)
            confirmed_appointments = len(db.appointments_df[db.appointments_df['status'] == 'confirmed'])
            pending_appointments = len(db.appointments_df[db.appointments_df['status'] == 'pending'])
            
            st.markdown("""
            <div class="metric-card">
                <h5>👥 Total Patients</h5>
                <h3>{}</h3>
            </div>
            """.format(total_patients), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h5>📅 Total Appointments</h5>
                <h3>{}</h3>
            </div>
            """.format(total_appointments), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h5>⏳ Pending Appointments</h5>
                <h3>{}</h3>
            </div>
            """.format(pending_appointments), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h5>✅ Confirmed Appointments</h5>
                <h3>{}</h3>
            </div>
            """.format(confirmed_appointments), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("📋 View All Appointments"):
            st.session_state.show_appointments = True
            st.session_state.show_patients = False
            st.session_state.show_chat = False
        
        if st.button("👥 View All Patients"):
            st.session_state.show_patients = True
            st.session_state.show_appointments = False
            st.session_state.show_chat = False
        
        if st.button("💬 Start New Chat"):
            st.session_state.show_chat = True
            st.session_state.show_appointments = False
            st.session_state.show_patients = False
            if 'messages' not in st.session_state:
                st.session_state.messages = []
        
        # Patient Intake Forms
        st.markdown("### 📋 Patient Intake Forms")
        if st.button("📋 Open Patient Intake Form"):
            st.session_state.show_patient_intake = True
            st.session_state.show_appointments = False
            st.session_state.show_patients = False
            st.session_state.show_chat = False
            st.rerun()
        
        # Export functionality
        st.markdown("### 📤 Export Data")
        if st.button("📊 Export Appointments Report"):
            try:
                report_path = db.export_appointments_report()
                with open(report_path, 'rb') as file:
                    st.download_button(
                        label="📥 Download Report",
                        data=file.read(),
                        file_name=os.path.basename(report_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error exporting report: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Default to chat interface
        if 'show_chat' not in st.session_state:
            st.session_state.show_chat = True
            st.session_state.show_appointments = False
            st.session_state.show_patients = False
        
        if st.session_state.show_chat or st.session_state.get('show_patient_intake', False):
            # Show patient intake form if requested
            if st.session_state.get('show_patient_intake', False):
                # Back button to return to appointments
                if st.button("⬅️ Back to Appointments"):
                    st.session_state.show_patient_intake = False
                    st.session_state.show_appointments = True
                    st.rerun()
                
                # Complete Patient Intake Form - Step by Step
                st.markdown("""
                <div class="form-container">
                    <div class="form-title">📋 Complete Patient Intake Form</div>
                    <p>Please fill out all required information step by step:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Step indicator
                current_intake_step = st.session_state.get('intake_step', 1)
                total_steps = 8
                
                st.progress(current_intake_step / total_steps)
                st.markdown(f"**Step {current_intake_step} of {total_steps}**")
                
                # Patient intake form with proper structure
                with st.form(key=f"patient_intake_form_{current_intake_step}"):
                    # Form content based on current step
                    if current_intake_step == 1:
                        st.markdown("### 👤 PATIENT INFORMATION")
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            # Get stored data for pre-population
                            stored_data = st.session_state.get('intake_data', {})
                            last_name = st.text_input("Last Name *", key="intake_last_name", value=stored_data.get('last_name', ''))
                            first_name = st.text_input("First Name *", key="intake_first_name", value=stored_data.get('first_name', ''))
                            middle_initial = st.text_input("Middle Initial", key="intake_middle_initial", value=stored_data.get('middle_initial', ''))
                            
                            # Handle date of birth
                            dob_value = stored_data.get('date_of_birth', None)
                            if dob_value:
                                try:
                                    from datetime import datetime
                                    dob_date = datetime.strptime(dob_value, '%Y-%m-%d').date()
                                except:
                                    dob_date = None
                            else:
                                dob_date = None
                            date_of_birth = st.date_input("Date of Birth *", key="intake_dob", value=dob_date)
                            
                            # Pre-populate gender selection
                            gender_options = ["Male", "Female", "Other"]
                            stored_gender = stored_data.get('gender', '')
                            gender_index = gender_options.index(stored_gender) if stored_gender in gender_options else 0
                            gender = st.radio("Gender *", gender_options, key="intake_gender", horizontal=True, index=gender_index)
                            home_phone = st.text_input("Home Phone", key="intake_home_phone", value=stored_data.get('home_phone', ''))
                            cell_phone = st.text_input("Cell Phone *", key="intake_cell_phone", value=stored_data.get('cell_phone', ''))
                        
                        with col2_form:
                            email = st.text_input("Email Address *", key="intake_email", value=stored_data.get('email', ''))
                            street_address = st.text_input("Street Address *", key="intake_street_address", value=stored_data.get('street_address', ''))
                            city = st.text_input("City *", key="intake_city", value=stored_data.get('city', ''))
                            state = st.text_input("State *", key="intake_state", value=stored_data.get('state', ''))
                            zip_code = st.text_input("ZIP Code *", key="intake_zip_code", value=stored_data.get('zip_code', ''))
                    
                    elif current_intake_step == 2:
                        st.markdown("### 🚨 EMERGENCY CONTACT")
                        col1_form, col2_form, col3_form = st.columns(3)
                        
                        with col1_form:
                            stored_data = st.session_state.get('intake_data', {})
                            emergency_contact_name = st.text_input("Emergency Contact Name *", key="intake_emergency_name", value=stored_data.get('emergency_contact_name', ''))
                        
                        with col2_form:
                            relationship = st.text_input("Relationship *", key="intake_relationship", value=stored_data.get('relationship', ''))
                        
                        with col3_form:
                            emergency_phone = st.text_input("Phone Number *", key="intake_emergency_phone", value=stored_data.get('emergency_phone', ''))
                    
                    elif current_intake_step == 3:
                        st.markdown("### 🛡️ INSURANCE INFORMATION")
                        
                        # Primary Insurance
                        st.markdown("#### Primary Insurance")
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            stored_data = st.session_state.get('intake_data', {})
                            primary_insurance_company = st.text_input("Insurance Company:", key="intake_primary_insurance_company", value=stored_data.get('primary_insurance_company', ''))
                            primary_member_id = st.text_input("Member ID:", key="intake_primary_member_id", value=stored_data.get('primary_member_id', ''))
                        
                        with col2_form:
                            primary_group_number = st.text_input("Group Number:", key="intake_primary_group_number", value=stored_data.get('primary_group_number', ''))
                        
                        st.markdown("---")
                        
                        # Secondary Insurance
                        st.markdown("#### Secondary Insurance (if applicable)")
                        col3_form, col4_form = st.columns(2)
                        
                        with col3_form:
                            secondary_insurance_company = st.text_input("Insurance Company:", key="intake_secondary_insurance_company", value=stored_data.get('secondary_insurance_company', ''))
                            secondary_member_id = st.text_input("Member ID:", key="intake_secondary_member_id", value=stored_data.get('secondary_member_id', ''))
                        
                        with col4_form:
                            secondary_group_number = st.text_input("Group Number:", key="intake_secondary_group_number", value=stored_data.get('secondary_group_number', ''))
                        
                        st.markdown("**Note:** Please bring insurance cards and photo ID to your appointment.")
                    
                    elif current_intake_step == 4:
                        st.markdown("### 🏥 CHIEF COMPLAINT & SYMPTOMS")
                        
                        stored_data = st.session_state.get('intake_data', {})
                        
                        # Primary reason for visit
                        st.markdown("**What is the primary reason for your visit today? ***")
                        primary_reason = st.text_area("Please describe your main concern or symptoms...", key="intake_primary_reason", value=stored_data.get('primary_reason', ''), height=100)
                        
                        # Duration of symptoms
                        st.markdown("**How long have you been experiencing these symptoms?**")
                        duration_options = ["Less than 1 week", "1-4 weeks", "1-6 months", "More than 6 months"]
                        stored_duration = stored_data.get('duration', '')
                        duration_index = duration_options.index(stored_duration) if stored_duration in duration_options else 0
                        duration = st.radio("Select duration:", duration_options, key="intake_duration", horizontal=True, index=duration_index)
                        
                        # Current symptoms checklist
                        st.markdown("**Please check all symptoms you are currently experiencing:**")
                        
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            sneezing = st.checkbox("Sneezing", key="intake_sneezing", value=stored_data.get('sneezing', False))
                            runny_nose = st.checkbox("Runny nose", key="intake_runny_nose", value=stored_data.get('runny_nose', False))
                            stuffy_nose = st.checkbox("Stuffy nose", key="intake_stuffy_nose", value=stored_data.get('stuffy_nose', False))
                            itchy_eyes = st.checkbox("Itchy eyes", key="intake_itchy_eyes", value=stored_data.get('itchy_eyes', False))
                            watery_eyes = st.checkbox("Watery eyes", key="intake_watery_eyes", value=stored_data.get('watery_eyes', False))
                            skin_rash = st.checkbox("Skin rash/hives", key="intake_skin_rash", value=stored_data.get('skin_rash', False))
                        
                        with col2_form:
                            wheezing = st.checkbox("Wheezing", key="intake_wheezing", value=stored_data.get('wheezing', False))
                            shortness_breath = st.checkbox("Shortness of breath", key="intake_shortness_breath", value=stored_data.get('shortness_breath', False))
                            coughing = st.checkbox("Coughing", key="intake_coughing", value=stored_data.get('coughing', False))
                            chest_tightness = st.checkbox("Chest tightness", key="intake_chest_tightness", value=stored_data.get('chest_tightness', False))
                            sinus_pressure = st.checkbox("Sinus pressure", key="intake_sinus_pressure", value=stored_data.get('sinus_pressure', False))
                            headaches = st.checkbox("Headaches", key="intake_headaches", value=stored_data.get('headaches', False))
                    
                    elif current_intake_step == 5:
                        st.markdown("### 🚨 ALLERGY HISTORY")
                        
                        stored_data = st.session_state.get('intake_data', {})
                        
                        # Known allergies question
                        st.markdown("**Do you have any known allergies? ***")
                        allergy_options = ["Yes", "No", "Not sure"]
                        stored_allergies = stored_data.get('has_allergies', '')
                        allergy_index = allergy_options.index(stored_allergies) if stored_allergies in allergy_options else 0
                        has_allergies = st.radio("Select option:", allergy_options, key="intake_has_allergies", horizontal=True, index=allergy_index)
                        
                        # Conditional allergy listing
                        if has_allergies == "Yes":
                            st.markdown("**If yes, please list all known allergies and reactions:**")
                            known_allergies = st.text_area("Include foods, medications, environmental allergens, etc.", key="intake_known_allergies", value=stored_data.get('known_allergies', ''), height=100)
                        
                        # Previous allergy testing
                        st.markdown("**Have you ever had allergy testing before?**")
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            allergy_testing_yes = st.checkbox("Yes - When:", key="intake_allergy_testing_yes", value=stored_data.get('allergy_testing_yes', False))
                            if allergy_testing_yes:
                                testing_date = st.text_input("Date of testing:", key="intake_testing_date", value=stored_data.get('testing_date', ''))
                        
                        with col2_form:
                            allergy_testing_no = st.checkbox("No", key="intake_allergy_testing_no", value=stored_data.get('allergy_testing_no', False))
                        
                        # EpiPen usage
                        st.markdown("**Have you ever used an EpiPen or had a severe allergic reaction?**")
                        epipen_options = ["Yes", "No"]
                        stored_epipen = stored_data.get('epipen_usage', '')
                        epipen_index = epipen_options.index(stored_epipen) if stored_epipen in epipen_options else 0
                        epipen_usage = st.radio("Select option:", epipen_options, key="intake_epipen_usage", horizontal=True, index=epipen_index)
                    
                    elif current_intake_step == 6:
                        st.markdown("### 💊 CURRENT MEDICATIONS")
                        
                        stored_data = st.session_state.get('intake_data', {})
                        
                        # General medications
                        st.markdown("**Please list ALL current medications, vitamins, and supplements:**")
                        current_medications = st.text_area("Include prescription medications, over-the-counter drugs, vitamins, and herbal supplements. Include dosage if known.", key="intake_current_medications", value=stored_data.get('current_medications', ''), height=120)
                        
                        # Specific allergy medications
                        st.markdown("**Are you currently taking any of these allergy medications?**")
                        
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            claritin = st.checkbox("Claritin (loratadine)", key="intake_claritin", value=stored_data.get('claritin', False))
                            zyrtec = st.checkbox("Zyrtec (cetirizine)", key="intake_zyrtec", value=stored_data.get('zyrtec', False))
                            allegra = st.checkbox("Allegra (fexofenadine)", key="intake_allegra", value=stored_data.get('allegra', False))
                        
                        with col2_form:
                            benadryl = st.checkbox("Benadryl (diphenhydramine)", key="intake_benadryl", value=stored_data.get('benadryl', False))
                            nasal_sprays = st.checkbox("Flonase/Nasacort (nasal sprays)", key="intake_nasal_sprays", value=stored_data.get('nasal_sprays', False))
                            other_medication = st.checkbox("Other:", key="intake_other_medication", value=stored_data.get('other_medication', False))
                            if other_medication:
                                other_medication_name = st.text_input("Specify other medication:", key="intake_other_medication_name", value=stored_data.get('other_medication_name', ''))
                    
                    elif current_intake_step == 7:
                        st.markdown("### 🏥 MEDICAL HISTORY")
                        
                        stored_data = st.session_state.get('intake_data', {})
                        
                        # Current or past conditions
                        st.markdown("**Please check any conditions you have or have had:**")
                        
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            asthma = st.checkbox("Asthma", key="intake_asthma", value=stored_data.get('asthma', False))
                            eczema = st.checkbox("Eczema", key="intake_eczema", value=stored_data.get('eczema', False))
                            sinus_infections = st.checkbox("Sinus infections", key="intake_sinus_infections", value=stored_data.get('sinus_infections', False))
                            pneumonia = st.checkbox("Pneumonia", key="intake_pneumonia", value=stored_data.get('pneumonia', False))
                            bronchitis = st.checkbox("Bronchitis", key="intake_bronchitis", value=stored_data.get('bronchitis', False))
                            high_blood_pressure = st.checkbox("High blood pressure", key="intake_high_blood_pressure", value=stored_data.get('high_blood_pressure', False))
                        
                        with col2_form:
                            heart_disease = st.checkbox("Heart disease", key="intake_heart_disease", value=stored_data.get('heart_disease', False))
                            diabetes = st.checkbox("Diabetes", key="intake_diabetes", value=stored_data.get('diabetes', False))
                            other_condition = st.checkbox("Other:", key="intake_other_condition", value=stored_data.get('other_condition', False))
                            if other_condition:
                                other_condition_name = st.text_input("Specify other condition:", key="intake_other_condition_name", value=stored_data.get('other_condition_name', ''))
                        
                        # Family history
                        st.markdown("**Family history of allergies or asthma:**")
                        family_history = st.text_area("Please describe any family history of allergies, asthma, or related conditions", key="intake_family_history", value=stored_data.get('family_history', ''), height=100)
                    
                    elif current_intake_step == 8:
                        st.markdown("### ⚠️ IMPORTANT PRE-VISIT INSTRUCTIONS")
                        
                        stored_data = st.session_state.get('intake_data', {})
                        
                        # Critical warning box
                        st.markdown("""
                        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0;">
                            <strong>CRITICAL:</strong> If allergy testing is planned, you MUST stop the following medications 7 days before your appointment:
                            <ul>
                                <li>All antihistamines (Claritin, Zyrtec, Allegra, Benadryl)</li>
                                <li>Cold medications containing antihistamines</li>
                                <li>Sleep aids like Tylenol PM</li>
                            </ul>
                            <strong>You MAY continue:</strong> Nasal sprays (Flonase, Nasacort), asthma inhalers, and prescription medications
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Understanding instructions
                        st.markdown("**I understand the pre-visit medication instructions: ***")
                        instruction_options = ["Yes, I understand and will follow instructions", "I have questions about these instructions"]
                        stored_instructions = stored_data.get('understand_instructions', '')
                        instruction_index = instruction_options.index(stored_instructions) if stored_instructions in instruction_options else 0
                        understand_instructions = st.radio("Select option:", instruction_options, key="intake_understand_instructions", horizontal=True, index=instruction_index)
                        
                        st.markdown("---")
                        
                        # Patient acknowledgment
                        st.markdown("### 📝 PATIENT ACKNOWLEDGMENT")
                        st.markdown("I certify that the information provided is accurate and complete to the best of my knowledge. I understand that providing false information may affect my treatment and care.")
                        
                        col1_form, col2_form = st.columns(2)
                        
                        with col1_form:
                            patient_signature = st.text_input("Patient Signature:", key="intake_patient_signature", value=stored_data.get('patient_signature', ''))
                        
                        with col2_form:
                            signature_date = st.date_input("Date:", key="intake_signature_date")
                    
                    # Navigation buttons - INSIDE the form
                    col_prev, col_next, col_submit = st.columns([1, 1, 1])
                    
                    with col_prev:
                        if current_intake_step > 1:
                            prev_clicked = st.form_submit_button("⬅️ Previous")
                            if prev_clicked:
                                # Store current form data before going back
                                st.session_state.intake_data = st.session_state.get('intake_data', {})
                                
                                # Store current step data before going back
                                if current_intake_step == 1:
                                    st.session_state.intake_data.update({
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'middle_initial': st.session_state.get('intake_middle_initial', ''),
                                        'date_of_birth': date_of_birth.strftime('%Y-%m-%d') if date_of_birth else '',
                                        'gender': gender,
                                        'home_phone': st.session_state.get('intake_home_phone', ''),
                                        'cell_phone': cell_phone,
                                        'email': email,
                                        'street_address': street_address,
                                        'city': city,
                                        'state': state,
                                        'zip_code': zip_code
                                    })
                                elif current_intake_step == 2:
                                    st.session_state.intake_data.update({
                                        'emergency_contact_name': emergency_contact_name,
                                        'relationship': relationship,
                                        'emergency_phone': emergency_phone
                                    })
                                elif current_intake_step == 3:
                                    st.session_state.intake_data.update({
                                        'primary_insurance_company': primary_insurance_company,
                                        'primary_member_id': primary_member_id,
                                        'primary_group_number': primary_group_number,
                                        'secondary_insurance_company': secondary_insurance_company,
                                        'secondary_member_id': secondary_member_id,
                                        'secondary_group_number': secondary_group_number
                                    })
                                elif current_intake_step == 4:
                                    st.session_state.intake_data.update({
                                        'primary_reason': primary_reason,
                                        'duration': duration,
                                        'sneezing': sneezing,
                                        'runny_nose': runny_nose,
                                        'stuffy_nose': stuffy_nose,
                                        'itchy_eyes': itchy_eyes,
                                        'watery_eyes': watery_eyes,
                                        'skin_rash': skin_rash,
                                        'wheezing': wheezing,
                                        'shortness_breath': shortness_breath,
                                        'coughing': coughing,
                                        'chest_tightness': chest_tightness,
                                        'sinus_pressure': sinus_pressure,
                                        'headaches': headaches
                                    })
                                elif current_intake_step == 5:
                                    st.session_state.intake_data.update({
                                        'has_allergies': has_allergies,
                                        'known_allergies': st.session_state.get('intake_known_allergies', ''),
                                        'allergy_testing_yes': allergy_testing_yes,
                                        'testing_date': st.session_state.get('intake_testing_date', ''),
                                        'allergy_testing_no': allergy_testing_no,
                                        'epipen_usage': epipen_usage
                                    })
                                elif current_intake_step == 6:
                                    st.session_state.intake_data.update({
                                        'current_medications': current_medications,
                                        'claritin': claritin,
                                        'zyrtec': zyrtec,
                                        'allegra': allegra,
                                        'benadryl': benadryl,
                                        'nasal_sprays': nasal_sprays,
                                        'other_medication': other_medication,
                                        'other_medication_name': st.session_state.get('intake_other_medication_name', '')
                                    })
                                elif current_intake_step == 7:
                                    st.session_state.intake_data.update({
                                        'asthma': asthma,
                                        'eczema': eczema,
                                        'sinus_infections': sinus_infections,
                                        'pneumonia': pneumonia,
                                        'bronchitis': bronchitis,
                                        'high_blood_pressure': high_blood_pressure,
                                        'heart_disease': heart_disease,
                                        'diabetes': diabetes,
                                        'other_condition': other_condition,
                                        'other_condition_name': st.session_state.get('intake_other_condition_name', ''),
                                        'family_history': family_history
                                    })
                                elif current_intake_step == 8:
                                    st.session_state.intake_data.update({
                                        'understand_instructions': understand_instructions,
                                        'patient_signature': patient_signature,
                                        'signature_date': signature_date.strftime('%Y-%m-%d') if signature_date else ''
                                    })
                                
                                st.session_state.intake_step = current_intake_step - 1
                    
                    with col_next:
                        if current_intake_step < total_steps:
                            next_clicked = st.form_submit_button("➡️ Next")
                            if next_clicked:
                                # Validate current step before proceeding
                                if current_intake_step == 1:
                                    if not first_name or not last_name or not date_of_birth or not cell_phone or not email or not street_address or not city or not state or not zip_code:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        # Store step 1 data
                                        st.session_state.intake_data = st.session_state.get('intake_data', {})
                                        st.session_state.intake_data.update({
                                            'first_name': first_name,
                                            'last_name': last_name,
                                            'middle_initial': st.session_state.get('intake_middle_initial', ''),
                                            'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                                            'gender': st.session_state.get('intake_gender', ''),
                                            'home_phone': st.session_state.get('intake_home_phone', ''),
                                            'cell_phone': cell_phone,
                                            'email': email,
                                            'street_address': street_address,
                                            'city': city,
                                            'state': state,
                                            'zip_code': zip_code
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 2:
                                    if not emergency_contact_name or not relationship or not emergency_phone:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        # Store step 2 data
                                        st.session_state.intake_data = st.session_state.get('intake_data', {})
                                        st.session_state.intake_data.update({
                                            'emergency_contact_name': emergency_contact_name,
                                            'relationship': relationship,
                                            'emergency_phone': emergency_phone
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 3:
                                    # Store step 3 data (no required fields for insurance)
                                    st.session_state.intake_data = st.session_state.get('intake_data', {})
                                    st.session_state.intake_data.update({
                                        'primary_insurance_company': primary_insurance_company,
                                        'primary_member_id': primary_member_id,
                                        'primary_group_number': primary_group_number,
                                        'secondary_insurance_company': secondary_insurance_company,
                                        'secondary_member_id': secondary_member_id,
                                        'secondary_group_number': secondary_group_number
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 4:
                                    if not primary_reason:
                                        st.error("Please describe the primary reason for your visit")
                                    else:
                                        # Store step 4 data
                                        st.session_state.intake_data = st.session_state.get('intake_data', {})
                                        st.session_state.intake_data.update({
                                            'primary_reason': primary_reason,
                                            'duration': duration,
                                            'sneezing': sneezing,
                                            'runny_nose': runny_nose,
                                            'stuffy_nose': stuffy_nose,
                                            'itchy_eyes': itchy_eyes,
                                            'watery_eyes': watery_eyes,
                                            'skin_rash': skin_rash,
                                            'wheezing': wheezing,
                                            'shortness_breath': shortness_breath,
                                            'coughing': coughing,
                                            'chest_tightness': chest_tightness,
                                            'sinus_pressure': sinus_pressure,
                                            'headaches': headaches
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 5:
                                    # Store step 5 data
                                    st.session_state.intake_data = st.session_state.get('intake_data', {})
                                    st.session_state.intake_data.update({
                                        'has_allergies': has_allergies,
                                        'known_allergies': st.session_state.get('intake_known_allergies', ''),
                                        'allergy_testing_yes': allergy_testing_yes,
                                        'testing_date': st.session_state.get('intake_testing_date', ''),
                                        'allergy_testing_no': allergy_testing_no,
                                        'epipen_usage': epipen_usage
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 6:
                                    # Store step 6 data
                                    st.session_state.intake_data = st.session_state.get('intake_data', {})
                                    st.session_state.intake_data.update({
                                        'current_medications': current_medications,
                                        'claritin': claritin,
                                        'zyrtec': zyrtec,
                                        'allegra': allegra,
                                        'benadryl': benadryl,
                                        'nasal_sprays': nasal_sprays,
                                        'other_medication': other_medication,
                                        'other_medication_name': st.session_state.get('intake_other_medication_name', '')
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 7:
                                    # Store step 7 data
                                    st.session_state.intake_data = st.session_state.get('intake_data', {})
                                    st.session_state.intake_data.update({
                                        'asthma': asthma,
                                        'eczema': eczema,
                                        'sinus_infections': sinus_infections,
                                        'pneumonia': pneumonia,
                                        'bronchitis': bronchitis,
                                        'high_blood_pressure': high_blood_pressure,
                                        'heart_disease': heart_disease,
                                        'diabetes': diabetes,
                                        'other_condition': other_condition,
                                        'other_condition_name': st.session_state.get('intake_other_condition_name', ''),
                                        'family_history': family_history
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                elif current_intake_step == 8:
                                    if not understand_instructions or not patient_signature:
                                        st.error("Please complete all required fields marked with *")
                                    else:
                                        # Store step 8 data
                                        st.session_state.intake_data = st.session_state.get('intake_data', {})
                                        st.session_state.intake_data.update({
                                            'understand_instructions': understand_instructions,
                                            'patient_signature': patient_signature,
                                            'signature_date': signature_date.strftime('%Y-%m-%d') if signature_date else ''
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                    
                    with col_submit:
                        if current_intake_step == total_steps:
                            submit_clicked = st.form_submit_button("✅ Submit Form")
                            if submit_clicked:
                                try:
                                    # Store current step (Step 8) data before submitting
                                    st.session_state.intake_data = st.session_state.get('intake_data', {})
                                    st.session_state.intake_data.update({
                                        'understand_instructions': understand_instructions,
                                        'patient_signature': patient_signature,
                                        'signature_date': signature_date.strftime('%Y-%m-%d') if signature_date else ''
                                    })
                                    
                                    # Get stored intake data
                                    patient_data = st.session_state.get('intake_data', {})
                                    
                                    # Ensure required fields are present
                                    required_fields = ['first_name', 'last_name', 'cell_phone', 'email']
                                    for field in required_fields:
                                        if field not in patient_data or not patient_data[field]:
                                            patient_data[field] = 'Not Provided'
                                    
                                    # Debug: Show collected data
                                    st.write("🔍 Debug - Collected patient data:")
                                    st.write(patient_data)
                                    
                                    # Debug: Show appointment linking info
                                    appointment_id = agent.conversation_state.get("appointment_info", {}).get("appointment_id")
                                    st.write(f"🔗 Debug - Appointment ID to link: {appointment_id}")
                                    
                                    # Add patient to database
                                    patient_id = db.add_patient(patient_data)
                                    
                                    # Link the appointment with the new patient and CONFIRM it
                                    # Get the appointment ID from the verified appointment
                                    verified_appointment = st.session_state.get('verified_appointment', {})
                                    appointment_id = verified_appointment.get('appointment_id')
                                    
                                    if appointment_id:
                                        # Update the specific appointment with patient ID and confirm it
                                        db.appointments_df.loc[db.appointments_df['appointment_id'] == appointment_id, 'patient_id'] = patient_id
                                        db.appointments_df.loc[db.appointments_df['appointment_id'] == appointment_id, 'status'] = 'confirmed'
                                        db.mark_intake_form_sent(appointment_id)
                                        db.save_data()
                                        
                                        st.success(f"🔗 Appointment {appointment_id} linked to Patient {patient_id}")
                                        
                                        # Clear verification state after successful submission
                                        st.session_state['appointment_verified'] = False
                                        st.session_state['verified_appointment'] = {}
                                        st.session_state['intake_step'] = 1
                                        st.session_state['intake_data'] = {}
                                    else:
                                        st.error("❌ No verified appointment found to link with patient")
                                    
                                    st.success(f"✅ Patient intake form submitted successfully!")
                                    st.success(f"📋 Patient ID: {patient_id} - Added to patient database")
                                    st.success(f"🎉 Appointment CONFIRMED - You're all set!")
                                    
                                    # Clear form data
                                    for key in list(st.session_state.keys()):
                                        if key.startswith('intake_'):
                                            del st.session_state[key]
                                    
                                    st.session_state.show_patient_intake = False
                                    st.session_state.show_appointments = True
                                    # Don't call st.rerun() here - let Streamlit handle the rerun naturally
                                    
                                except Exception as e:
                                    st.error(f"Error submitting form: {str(e)}")
                                    st.error("Please try again or contact support.")
            else:
                # Regular chat interface
                st.markdown("### 💬 AI Scheduling Assistant")
                st.markdown("""
                Welcome! I'm your AI scheduling assistant. I can help you:
                - Schedule new appointments
                - Check existing appointments
                - Update patient information
                - Handle insurance details
                
                **Start by saying hello or providing your information!**
                """)
            
            # Initialize chat history
            if 'messages' not in st.session_state:
                st.session_state.messages = []
                # Add initial greeting
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Hello! Welcome to HealthFirst Medical Center. I'm your AI scheduling assistant. I can help you schedule an appointment with one of our doctors. To get started, I'll need some basic information.\n\nCould you please provide:\n1. Your first name\n2. Your last name\n3. Your date of birth (MM/DD/YYYY format)\n4. Your phone number\n5. Your email address\n\nOnce I have this information, I can check if you're an existing patient or help you register as a new patient."
                })
            
            # Display chat messages (only when patient intake form is not open)
            if not st.session_state.get('show_patient_intake', False):
                chat_container = st.container()
                with chat_container:
                    for message in st.session_state.messages:
                        if message["role"] == "user":
                            st.markdown(f"""
                            <div class="user-message">
                                <strong>You:</strong> {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="ai-message">
                                <strong>AI Assistant:</strong> {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
            
            # Dynamic form based on conversation step
            current_step = agent.conversation_state.get("step", "greeting")
            
            # Check if conversation state was updated and force rerun
            if st.session_state.get('conversation_updated', False):
                st.session_state.conversation_updated = False
                st.rerun()
            
            # Also check if we need to force rerun based on agent state
            if agent.conversation_state.get("step") == "patient_intake_form" and current_step != "patient_intake_form":
                st.rerun()
            
            
            # Always show the appropriate form based on current step (but not when patient intake form is open)
            if (current_step == "greeting" or current_step == "collecting_patient_info") and not st.session_state.get('show_patient_intake', False):
                # Initial patient information form
                st.markdown("""
                <div class="form-container">
                    <div class="form-title">📝 Patient Information Form</div>
                    <p>Please provide your information to get started:</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form(key="patient_info_form"):
                    # Use dynamic keys to clear form after submission
                    form_key = st.session_state.get('form_key', 0)
                    first_name = st.text_input("First Name", key=f"form_first_name_{form_key}", placeholder="Enter your first name")
                    last_name = st.text_input("Last Name", key=f"form_last_name_{form_key}", placeholder="Enter your last name")
                    date_of_birth = st.text_input("Date of Birth (MM/DD/YYYY)", key=f"form_dob_{form_key}", placeholder="MM/DD/YYYY")
                    phone = st.text_input("Phone Number", key=f"form_phone_{form_key}", placeholder="Enter your phone number")
                    email = st.text_input("Email Address", key=f"form_email_{form_key}", placeholder="Enter your email address")
                    
                    # Submit button
                    submit_button = st.form_submit_button("🚀 Submit Information")
                    
                    if submit_button:
                        # Validate form data
                        if not first_name or not last_name or not date_of_birth or not phone or not email:
                            st.error("Please fill in all fields before submitting.")
                        else:
                            # Combine all information into a single string
                            user_input = f"{first_name} {last_name} {date_of_birth} {phone} {email}"
                            
                            # Add user message to chat
                            st.session_state.messages.append({"role": "user", "content": user_input})
                            
                            # Get AI response
                            with st.spinner("Processing..."):
                                try:
                                    ai_response = agent.process_message(user_input)
                                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                                    st.success("Information submitted successfully!")
                                    
                                    # Debug: Show the agent's conversation state after processing
                                    st.write(f"🔍 Debug - Agent step after processing: {agent.conversation_state.get('step', 'unknown')}")
                                    
                                    # Increment form key to clear form
                                    st.session_state.form_key = form_key + 1
                                    
                                    # Force conversation state update
                                    st.session_state.conversation_updated = True
                                    
                                except Exception as e:
                                    error_response = f"I encountered an error: {str(e)}. Please try again or contact our office directly."
                                    st.session_state.messages.append({"role": "assistant", "content": error_response})
                                    st.error(f"Error: {str(e)}")
                            
                            # Clear form and rerun
                            st.rerun()
            
            elif current_step == "select_doctor":
                # Doctor selection form
                st.markdown("""
                <div class="form-container">
                    <div class="form-title">👨‍⚕️ Doctor Selection</div>
                    <p>Please select which doctor you'd like to see:</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form(key="doctor_selection_form"):
                    doctor_options = list(DOCTORS.keys())
                    selected_doctor = st.selectbox("Choose a Doctor", doctor_options, key="doctor_select")
                    
                    submit_button = st.form_submit_button("👨‍⚕️ Select Doctor")
                    
                    if submit_button:
                        user_input = f"I want to see {selected_doctor}"
                        
                        # Add user message to chat
                        st.session_state.messages.append({"role": "user", "content": user_input})
                        
                        # Get AI response
                        with st.spinner("Processing..."):
                            try:
                                ai_response = agent.process_message(user_input)
                                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                                st.success("Doctor selected successfully!")
                            except Exception as e:
                                error_response = f"I encountered an error: {str(e)}. Please try again."
                                st.session_state.messages.append({"role": "assistant", "content": error_response})
                                st.error(f"Error: {str(e)}")
                        
                        st.rerun()
            
            elif current_step == "select_date":
                # Date selection form with calendar and slots side by side
                st.markdown("""
                <div class="form-container">
                    <div class="form-title">📅 Appointment Scheduling</div>
                    <p>Select your preferred date and time slot:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create two columns for calendar and slots
                cal_col1, cal_col2 = st.columns(2)
                
                with cal_col1:
                    st.markdown("### 📅 Date")
                    
                    # Use Streamlit's date picker for calendar
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    min_date = today.date()
                    max_date = today.date() + timedelta(days=90)  # 3 months ahead
                    
                    selected_date = st.date_input(
                        "Select Appointment Date",
                        value=today.date(),
                        min_value=min_date,
                        max_value=max_date,
                        key="calendar_date_picker"
                    )
                    
                    # When date is selected, update agent state
                    if 'last_selected_date' not in st.session_state or st.session_state.last_selected_date != selected_date:
                        st.session_state.last_selected_date = selected_date
                        # Call agent to populate available slots
                        date_input = selected_date.strftime('%Y-%m-%d')
                        try:
                            agent_response = agent.process_message(date_input)
                            st.session_state.messages.append({"role": "assistant", "content": agent_response})
                        except Exception as e:
                            st.error(f"Error processing date: {str(e)}")
                
                with cal_col2:
                    st.markdown("### ⏰ Available Times")
                    
                    # Get available slots for selected date
                    try:
                        doctor_name = agent.conversation_state.get("appointment_info", {}).get("doctor_name", "Dr. Sarah Johnson")
                        slots = db.get_available_slots(doctor_name=doctor_name, date=selected_date.strftime('%Y-%m-%d'))
                        
                        if slots:
                            st.markdown(f"**Available slots for {selected_date.strftime('%B %d, %Y')}:**")
                            
                            # Create time slot selection form
                            with st.form(key="time_slot_selection_form"):
                                st.markdown("**Select your preferred time slot:**")
                                
                                # Create radio buttons for time slots
                                time_options = [f"{slot['time_slot']} - {slot['location']}" for slot in slots]
                                selected_time = st.radio(
                                    "Available Time Slots:",
                                    options=time_options,
                                    key="time_slot_radio"
                                )
                                
                                # Submit button
                                submit_button = st.form_submit_button("📅 Confirm Time Slot")
                                
                                if submit_button and selected_time:
                                    # Process the time selection
                                    user_input = f"I want to schedule for {selected_date.strftime('%B %d, %Y')} at {selected_time}"
                                    
                                    # Add user message to chat
                                    st.session_state.messages.append({"role": "user", "content": user_input})
                                    
                                    # Get AI response
                                    with st.spinner("Processing..."):
                                        try:
                                            ai_response = agent.process_message(user_input)
                                            st.session_state.messages.append({"role": "assistant", "content": ai_response})
                                            st.success("✅ Appointment scheduled successfully!")
                                            
                                            # Show additional confirmation message
                                            st.info("📋 Your appointment has been saved to the system. You can view it in the 'Total Appointments' section.")
                                            
                                            # Force conversation state update
                                            st.session_state.conversation_updated = True
                                            
                                        except Exception as e:
                                            error_response = f"I encountered an error: {str(e)}. Please try again."
                                            st.session_state.messages.append({"role": "assistant", "content": error_response})
                                            st.error(f"Error: {str(e)}")
                        else:
                            st.warning(f"No available slots for {selected_date.strftime('%B %d, %Y')}")
                            st.info("Try selecting a different date")
                            selected_time = None
                    except Exception as e:
                        st.error(f"Error loading slots: {str(e)}")
                        selected_time = None
                
                # Instructions for user
                st.info("💡 **Tip:** Select a time slot from the form above and click 'Confirm Time Slot' to save your appointment.")
            
            # Patient intake form is now handled in the main chat section above
                
                # Complete Patient Intake Form - Step by Step
                st.markdown("""
                <div class="form-container">
                    <div class="form-title">📋 Complete Patient Intake Form</div>
                    <p>Please fill out all required information step by step:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Step indicator
                current_intake_step = st.session_state.get('intake_step', 1)
                total_steps = 8
                
                st.progress(current_intake_step / total_steps)
                st.markdown(f"**Step {current_intake_step} of {total_steps}**")
                
                # Patient intake form with proper structure
                with st.form(key="patient_intake_form"):
                    # Form content based on current step
                    if current_intake_step == 1:
                        st.markdown("### 👤 Personal Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            first_name = st.text_input("First Name *", key="intake_first_name", placeholder="Enter first name")
                            middle_name = st.text_input("Middle Name", key="intake_middle_name", placeholder="Enter middle name")
                            date_of_birth = st.date_input("Date of Birth *", key="intake_dob")
                            gender = st.selectbox("Gender *", ["", "Male", "Female", "Other", "Prefer not to say"], key="intake_gender")
                        
                        with col2:
                            last_name = st.text_input("Last Name *", key="intake_last_name", placeholder="Enter last name")
                            marital_status = st.selectbox("Marital Status", ["", "Single", "Married", "Divorced", "Widowed", "Separated"], key="intake_marital")
                            ssn = st.text_input("Social Security Number", key="intake_ssn", placeholder="XXX-XX-XXXX")
                            emergency_contact = st.text_input("Emergency Contact Name", key="intake_emergency_name", placeholder="Emergency contact name")
                    
                    elif current_intake_step == 2:
                        st.markdown("### 📞 Contact Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            phone = st.text_input("Phone Number *", key="intake_phone", placeholder="(555) 123-4567")
                            work_phone = st.text_input("Work Phone", key="intake_work_phone", placeholder="(555) 123-4567")
                            email = st.text_input("Email Address *", key="intake_email", placeholder="your.email@example.com")
                        
                        with col2:
                            emergency_phone = st.text_input("Emergency Contact Phone", key="intake_emergency_phone", placeholder="(555) 123-4567")
                            preferred_contact = st.selectbox("Preferred Contact Method", ["Phone", "Email", "Text", "Mail"], key="intake_preferred_contact")
                            language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "Other"], key="intake_language")
                    
                    elif current_intake_step == 3:
                        st.markdown("### 🏠 Address Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            street_address = st.text_input("Street Address *", key="intake_street", placeholder="123 Main Street")
                            city = st.text_input("City *", key="intake_city", placeholder="City")
                            state = st.text_input("State *", key="intake_state", placeholder="State")
                        
                        with col2:
                            zip_code = st.text_input("ZIP Code *", key="intake_zip", placeholder="12345")
                            county = st.text_input("County", key="intake_county", placeholder="County")
                            country = st.text_input("Country", key="intake_country", value="United States")
                    
                    elif current_intake_step == 4:
                        st.markdown("### 👨‍⚕️ Medical Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            primary_care = st.text_input("Primary Care Physician", key="intake_primary_care", placeholder="Dr. Name")
                            referring_physician = st.text_input("Referring Physician", key="intake_referring", placeholder="Dr. Name")
                            allergies = st.text_area("Allergies", key="intake_allergies", placeholder="List any allergies (medications, foods, etc.)")
                        
                        with col2:
                            current_medications = st.text_area("Current Medications", key="intake_medications", placeholder="List current medications")
                            medical_conditions = st.text_area("Medical Conditions", key="intake_conditions", placeholder="List any medical conditions")
                            family_history = st.text_area("Family Medical History", key="intake_family_history", placeholder="Relevant family medical history")
                    
                    elif current_intake_step == 5:
                        st.markdown("### 🏥 Insurance Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            insurance_provider = st.text_input("Insurance Provider", key="intake_insurance_provider", placeholder="Insurance company name")
                            policy_number = st.text_input("Policy Number", key="intake_policy_number", placeholder="Policy number")
                            group_number = st.text_input("Group Number", key="intake_group_number", placeholder="Group number")
                        
                        with col2:
                            subscriber_name = st.text_input("Subscriber Name", key="intake_subscriber", placeholder="Name on insurance card")
                            relationship = st.selectbox("Relationship to Subscriber", ["Self", "Spouse", "Child", "Parent", "Other"], key="intake_relationship")
                            secondary_insurance = st.text_input("Secondary Insurance", key="intake_secondary", placeholder="Secondary insurance info")
                    
                    elif current_intake_step == 6:
                        st.markdown("### 📋 Employment & Lifestyle")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            employer = st.text_input("Employer", key="intake_employer", placeholder="Employer name")
                            occupation = st.text_input("Occupation", key="intake_occupation", placeholder="Job title")
                            work_address = st.text_input("Work Address", key="intake_work_address", placeholder="Work address")
                        
                        with col2:
                            smoking_status = st.selectbox("Smoking Status", ["Never", "Former", "Current", "Prefer not to say"], key="intake_smoking")
                            alcohol_use = st.selectbox("Alcohol Use", ["None", "Occasional", "Moderate", "Heavy", "Prefer not to say"], key="intake_alcohol")
                            exercise_frequency = st.selectbox("Exercise Frequency", ["Never", "Rarely", "1-2 times/week", "3-4 times/week", "Daily"], key="intake_exercise")
                    
                    elif current_intake_step == 7:
                        st.markdown("### 🚨 Emergency & Legal")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            emergency_contact_name = st.text_input("Emergency Contact Name *", key="intake_emergency_name_final", placeholder="Emergency contact name")
                            emergency_contact_phone = st.text_input("Emergency Contact Phone *", key="intake_emergency_phone_final", placeholder="(555) 123-4567")
                            emergency_contact_relationship = st.selectbox("Relationship to Emergency Contact", ["Spouse", "Parent", "Child", "Sibling", "Friend", "Other"], key="intake_emergency_relationship")
                        
                        with col2:
                            advance_directive = st.selectbox("Advance Directive", ["Yes", "No", "Don't know"], key="intake_advance_directive")
                            power_of_attorney = st.selectbox("Power of Attorney", ["Yes", "No", "Don't know"], key="intake_power_attorney")
                            organ_donor = st.selectbox("Organ Donor Status", ["Yes", "No", "Don't know"], key="intake_organ_donor")
                    
                    elif current_intake_step == 8:
                        st.markdown("### ✅ Review & Consent")
                        
                        st.markdown("**Please review your information and provide consent:**")
                        
                        # Display summary of collected information
                        if 'intake_data' in st.session_state:
                            st.markdown("**Information Summary:**")
                            summary_data = st.session_state.intake_data
                            for key, value in summary_data.items():
                                if value:  # Only show non-empty fields
                                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        consent_1 = st.checkbox("I consent to treatment and authorize the release of medical information as necessary", key="intake_consent_1")
                        consent_2 = st.checkbox("I understand my rights and responsibilities as a patient", key="intake_consent_2")
                        consent_3 = st.checkbox("I authorize payment of insurance benefits to the provider", key="intake_consent_3")
                        
                        signature = st.text_input("Digital Signature", key="intake_signature", placeholder="Type your full name to sign")
                        date_signed = st.date_input("Date Signed", key="intake_date_signed", value=datetime.now().date())
                    
                    # Navigation buttons inside the form
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if current_intake_step > 1:
                            if st.form_submit_button("⬅️ Previous"):
                                st.session_state.intake_step = current_intake_step - 1
                                st.rerun()
                    
                    with col2:
                        if current_intake_step < total_steps:
                            if st.form_submit_button("Next ➡️"):
                                # Validate current step
                                if current_intake_step == 1:
                                    if not first_name or not last_name or not date_of_birth or not gender:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        # Save data and move to next step
                                        if 'intake_data' not in st.session_state:
                                            st.session_state.intake_data = {}
                                        st.session_state.intake_data.update({
                                            'First Name': first_name,
                                            'Middle Name': middle_name,
                                            'Last Name': last_name,
                                            'Date of Birth': str(date_of_birth),
                                            'Gender': gender,
                                            'Marital Status': marital_status,
                                            'SSN': ssn,
                                            'Emergency Contact': emergency_contact
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                        st.rerun()
                                elif current_intake_step == 2:
                                    if not phone or not email:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        st.session_state.intake_data.update({
                                            'Phone': phone,
                                            'Work Phone': work_phone,
                                            'Email': email,
                                            'Emergency Phone': emergency_phone,
                                            'Preferred Contact': preferred_contact,
                                            'Language': language
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                        st.rerun()
                                elif current_intake_step == 3:
                                    if not street_address or not city or not state or not zip_code:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        st.session_state.intake_data.update({
                                            'Street Address': street_address,
                                            'City': city,
                                            'State': state,
                                            'ZIP Code': zip_code,
                                            'County': county,
                                            'Country': country
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                        st.rerun()
                                elif current_intake_step == 4:
                                    st.session_state.intake_data.update({
                                        'Primary Care': primary_care,
                                        'Referring Physician': referring_physician,
                                        'Allergies': allergies,
                                        'Current Medications': current_medications,
                                        'Medical Conditions': medical_conditions,
                                        'Family History': family_history
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                    st.rerun()
                                elif current_intake_step == 5:
                                    st.session_state.intake_data.update({
                                        'Insurance Provider': insurance_provider,
                                        'Policy Number': policy_number,
                                        'Group Number': group_number,
                                        'Subscriber Name': subscriber_name,
                                        'Relationship': relationship,
                                        'Secondary Insurance': secondary_insurance
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                    st.rerun()
                                elif current_intake_step == 6:
                                    st.session_state.intake_data.update({
                                        'Employer': employer,
                                        'Occupation': occupation,
                                        'Work Address': work_address,
                                        'Smoking Status': smoking_status,
                                        'Alcohol Use': alcohol_use,
                                        'Exercise Frequency': exercise_frequency
                                    })
                                    st.session_state.intake_step = current_intake_step + 1
                                    st.rerun()
                                elif current_intake_step == 7:
                                    if not emergency_contact_name or not emergency_contact_phone:
                                        st.error("Please fill in all required fields marked with *")
                                    else:
                                        st.session_state.intake_data.update({
                                            'Emergency Contact Name': emergency_contact_name,
                                            'Emergency Contact Phone': emergency_contact_phone,
                                            'Emergency Contact Relationship': emergency_contact_relationship,
                                            'Advance Directive': advance_directive,
                                            'Power of Attorney': power_of_attorney,
                                            'Organ Donor': organ_donor
                                        })
                                        st.session_state.intake_step = current_intake_step + 1
                                        st.rerun()
                    
                    with col3:
                        if current_intake_step == total_steps:
                            if st.form_submit_button("✅ Submit Form"):
                                if not consent_1 or not consent_2 or not consent_3 or not signature:
                                    st.error("Please provide all consents and signature")
                                else:
                                    # Final submission
                                    st.session_state.intake_data.update({
                                        'Consent 1': consent_1,
                                        'Consent 2': consent_2,
                                        'Consent 3': consent_3,
                                        'Signature': signature,
                                        'Date Signed': str(date_signed)
                                    })
                                    
                                    # Create comprehensive user input
                                    user_input = f"Patient Intake Form Completed: {st.session_state.intake_data.get('First Name', '')} {st.session_state.intake_data.get('Last Name', '')}"
                                    
                                    # Add user message to chat
                                    st.session_state.messages.append({"role": "user", "content": user_input})
                                    
                                    # Get AI response
                                    with st.spinner("Processing intake form..."):
                                        try:
                                            ai_response = agent.process_message(user_input)
                                            st.session_state.messages.append({"role": "assistant", "content": ai_response})
                                            st.success("Patient intake form completed successfully!")
                                            
                                            # Clear intake form data
                                            if 'intake_data' in st.session_state:
                                                del st.session_state.intake_data
                                            if 'intake_step' in st.session_state:
                                                del st.session_state.intake_step
                                            
                                        except Exception as e:
                                            error_response = f"I encountered an error: {str(e)}. Please try again."
                                            st.session_state.messages.append({"role": "assistant", "content": error_response})
                                            st.error(f"Error: {str(e)}")
                                    
                                    st.rerun()
        
        elif st.session_state.show_appointments:
            st.markdown("### 📅 Appointment Management")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "confirmed", "cancelled", "completed"])
            with col2:
                doctor_filter = st.selectbox("Filter by Doctor", ["All"] + list(DOCTORS.keys()))
            with col3:
                date_filter = st.date_input("Filter by Date", value=None)
            
            # Display appointments
            try:
                appointments_df = db.appointments_df.copy()
                
                # Apply filters
                if status_filter != "All":
                    appointments_df = appointments_df[appointments_df['status'] == status_filter]
                if doctor_filter != "All":
                    appointments_df = appointments_df[appointments_df['doctor_name'] == doctor_filter]
                if date_filter:
                    appointments_df = appointments_df[appointments_df['appointment_date'] == date_filter.strftime('%Y-%m-%d')]
                
                if len(appointments_df) > 0:
                    st.dataframe(appointments_df, use_container_width=True)
                else:
                    st.info("No appointments found matching the selected criteria.")
                    
            except Exception as e:
                st.error(f"Error loading appointments: {str(e)}")
        
        elif st.session_state.show_patients:
            st.markdown("### 👥 Patient Management")
            
            # Search functionality
            search_term = st.text_input("Search patients by name or ID:", placeholder="Enter patient name or ID...")
            
            try:
                patients_df = db.patients_df.copy()
                
                if search_term:
                    mask = (
                        patients_df['first_name'].str.contains(search_term, case=False, na=False) |
                        patients_df['last_name'].str.contains(search_term, case=False, na=False) |
                        patients_df['patient_id'].str.contains(search_term, case=False, na=False)
                    )
                    patients_df = patients_df[mask]
                
                if len(patients_df) > 0:
                    # Display patient count
                    st.info(f"📊 Found {len(patients_df)} patient(s)")
                    
                    # Show comprehensive patient info with all intake form fields
                    st.markdown("#### 📋 Complete Patient Database")
                    
                    # Create a comprehensive view with all important fields
                    comprehensive_info = patients_df[[
                        'patient_id', 'first_name', 'last_name', 'middle_initial', 'date_of_birth', 'gender',
                        'home_phone', 'cell_phone', 'email', 'street_address', 'city', 'state', 'zip_code',
                        'emergency_contact_name', 'relationship', 'emergency_phone',
                        'primary_insurance_company', 'primary_member_id', 'primary_group_number',
                        'primary_reason', 'duration', 'has_allergies', 'known_allergies',
                        'current_medications', 'asthma', 'eczema', 'sinus_infections', 'pneumonia', 'bronchitis',
                        'high_blood_pressure', 'heart_disease', 'diabetes', 'family_history',
                        'patient_signature', 'signature_date', 'created_date', 'is_new_patient'
                    ]].copy()
                    
                    # Replace NaN values with empty strings for better display
                    comprehensive_info = comprehensive_info.fillna('')
                    
                    # Rename columns for better display
                    comprehensive_info.columns = [
                        'Patient ID', 'First Name', 'Last Name', 'Middle Initial', 'Date of Birth', 'Gender',
                        'Home Phone', 'Cell Phone', 'Email', 'Street Address', 'City', 'State', 'ZIP Code',
                        'Emergency Contact', 'Relationship', 'Emergency Phone',
                        'Primary Insurance', 'Member ID', 'Group Number',
                        'Primary Reason', 'Duration', 'Has Allergies', 'Known Allergies',
                        'Current Medications', 'Asthma', 'Eczema', 'Sinus Infections', 'Pneumonia', 'Bronchitis',
                        'High Blood Pressure', 'Heart Disease', 'Diabetes', 'Family History',
                        'Patient Signature', 'Signature Date', 'Created Date', 'New Patient'
                    ]
                    
                    st.dataframe(comprehensive_info, use_container_width=True)
                    
                    # Add expandable section for complete medical data
                    with st.expander("🔍 View Complete Medical Data (All 8-Step Form Fields)"):
                        st.markdown("#### 📊 All Intake Form Fields")
                        
                        # Show all fields including symptoms, medications, etc.
                        all_fields = patients_df[[
                            'patient_id', 'first_name', 'last_name', 'middle_initial', 'date_of_birth', 'gender',
                            'home_phone', 'cell_phone', 'email', 'street_address', 'city', 'state', 'zip_code',
                            'emergency_contact_name', 'relationship', 'emergency_phone',
                            'primary_insurance_company', 'primary_member_id', 'primary_group_number',
                            'secondary_insurance_company', 'secondary_member_id', 'secondary_group_number',
                            'primary_reason', 'duration',
                            'sneezing', 'runny_nose', 'stuffy_nose', 'itchy_eyes', 'watery_eyes', 'skin_rash',
                            'wheezing', 'shortness_breath', 'coughing', 'chest_tightness', 'sinus_pressure', 'headaches',
                            'has_allergies', 'known_allergies', 'allergy_testing_yes', 'testing_date', 'allergy_testing_no', 'epipen_usage',
                            'current_medications', 'claritin', 'zyrtec', 'allegra', 'benadryl', 'nasal_sprays', 'other_medication', 'other_medication_name',
                            'asthma', 'eczema', 'sinus_infections', 'pneumonia', 'bronchitis', 'high_blood_pressure', 'heart_disease', 'diabetes', 'other_condition', 'other_condition_name',
                            'family_history', 'understand_instructions', 'patient_signature', 'signature_date', 'created_date', 'is_new_patient'
                        ]].copy()
                        
                        all_fields = all_fields.fillna('')
                        
                        # Rename all columns for better display
                        all_fields.columns = [
                            'Patient ID', 'First Name', 'Last Name', 'Middle Initial', 'Date of Birth', 'Gender',
                            'Home Phone', 'Cell Phone', 'Email', 'Street Address', 'City', 'State', 'ZIP Code',
                            'Emergency Contact', 'Relationship', 'Emergency Phone',
                            'Primary Insurance', 'Primary Member ID', 'Primary Group Number',
                            'Secondary Insurance', 'Secondary Member ID', 'Secondary Group Number',
                            'Primary Reason', 'Duration',
                            'Sneezing', 'Runny Nose', 'Stuffy Nose', 'Itchy Eyes', 'Watery Eyes', 'Skin Rash',
                            'Wheezing', 'Shortness of Breath', 'Coughing', 'Chest Tightness', 'Sinus Pressure', 'Headaches',
                            'Has Allergies', 'Known Allergies', 'Allergy Testing Yes', 'Testing Date', 'Allergy Testing No', 'EpiPen Usage',
                            'Current Medications', 'Claritin', 'Zyrtec', 'Allegra', 'Benadryl', 'Nasal Sprays', 'Other Medication', 'Other Medication Name',
                            'Asthma', 'Eczema', 'Sinus Infections', 'Pneumonia', 'Bronchitis', 'High Blood Pressure', 'Heart Disease', 'Diabetes', 'Other Condition', 'Other Condition Name',
                            'Family History', 'Understand Instructions', 'Patient Signature', 'Signature Date', 'Created Date', 'New Patient'
                        ]
                        
                        st.dataframe(all_fields, use_container_width=True)
                    
                    # Allow user to select a patient for detailed view
                    if len(patients_df) == 1:
                        selected_patient = patients_df.iloc[0]
                        show_detailed_view = True
                    else:
                        st.markdown("#### 🔍 Select Patient for Detailed View")
                        patient_options = [f"{row['patient_id']} - {row['first_name']} {row['last_name']}" for _, row in patients_df.iterrows()]
                        selected_option = st.selectbox("Choose a patient:", patient_options)
                        if selected_option:
                            selected_patient_id = selected_option.split(" - ")[0]
                            selected_patient = patients_df[patients_df['patient_id'] == selected_patient_id].iloc[0]
                            show_detailed_view = True
                        else:
                            show_detailed_view = False
                    
                    if show_detailed_view:
                        st.markdown("---")
                        st.markdown(f"#### 👤 Detailed Patient Information - {selected_patient['patient_id']}")
                        
                        # Personal Information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**👤 Personal Information**")
                            st.write(f"**Name:** {selected_patient['first_name']} {selected_patient.get('middle_initial', '')} {selected_patient['last_name']}")
                            st.write(f"**Date of Birth:** {selected_patient['date_of_birth']}")
                            st.write(f"**Gender:** {selected_patient.get('gender', 'Not specified')}")
                            st.write(f"**Home Phone:** {selected_patient.get('home_phone', 'Not provided')}")
                            st.write(f"**Cell Phone:** {selected_patient.get('cell_phone', 'Not provided')}")
                            st.write(f"**Email:** {selected_patient['email']}")
                        
                        with col2:
                            st.markdown("**🏠 Address**")
                            st.write(f"**Street:** {selected_patient.get('street_address', 'Not provided')}")
                            st.write(f"**City:** {selected_patient.get('city', 'Not provided')}")
                            st.write(f"**State:** {selected_patient.get('state', 'Not provided')}")
                            st.write(f"**ZIP:** {selected_patient.get('zip_code', 'Not provided')}")
                        
                        # Emergency Contact
                        st.markdown("**🚨 Emergency Contact**")
                        col3, col4, col5 = st.columns(3)
                        with col3:
                            st.write(f"**Name:** {selected_patient.get('emergency_contact_name', 'Not provided')}")
                        with col4:
                            st.write(f"**Relationship:** {selected_patient.get('relationship', 'Not provided')}")
                        with col5:
                            st.write(f"**Phone:** {selected_patient.get('emergency_phone', 'Not provided')}")
                        
                        # Insurance Information
                        st.markdown("**🛡️ Insurance Information**")
                        col6, col7 = st.columns(2)
                        with col6:
                            st.markdown("*Primary Insurance*")
                            st.write(f"**Company:** {selected_patient.get('primary_insurance_company', 'Not provided')}")
                            st.write(f"**Member ID:** {selected_patient.get('primary_member_id', 'Not provided')}")
                            st.write(f"**Group Number:** {selected_patient.get('primary_group_number', 'Not provided')}")
                        
                        with col7:
                            st.markdown("*Secondary Insurance*")
                            st.write(f"**Company:** {selected_patient.get('secondary_insurance_company', 'Not provided')}")
                            st.write(f"**Member ID:** {selected_patient.get('secondary_member_id', 'Not provided')}")
                            st.write(f"**Group Number:** {selected_patient.get('secondary_group_number', 'Not provided')}")
                        
                        # Medical Information
                        st.markdown("**🏥 Medical Information**")
                        
                        # Chief Complaint
                        if selected_patient.get('primary_reason'):
                            st.markdown("*Chief Complaint*")
                            st.write(f"**Reason for Visit:** {selected_patient['primary_reason']}")
                            st.write(f"**Duration:** {selected_patient.get('duration', 'Not specified')}")
                        
                        # Symptoms
                        symptoms = []
                        symptom_fields = ['sneezing', 'runny_nose', 'stuffy_nose', 'itchy_eyes', 'watery_eyes', 'skin_rash', 
                                        'wheezing', 'shortness_breath', 'coughing', 'chest_tightness', 'sinus_pressure', 'headaches']
                        for symptom in symptom_fields:
                            if selected_patient.get(symptom):
                                symptoms.append(symptom.replace('_', ' ').title())
                        
                        if symptoms:
                            st.markdown("*Current Symptoms*")
                            st.write(", ".join(symptoms))
                        
                        # Allergy History
                        if selected_patient.get('has_allergies'):
                            st.markdown("*Allergy History*")
                            st.write(f"**Has Allergies:** {selected_patient['has_allergies']}")
                            if selected_patient.get('known_allergies'):
                                st.write(f"**Known Allergies:** {selected_patient['known_allergies']}")
                            if selected_patient.get('epipen_usage'):
                                st.write(f"**EpiPen Usage:** {selected_patient['epipen_usage']}")
                        
                        # Current Medications
                        if selected_patient.get('current_medications'):
                            st.markdown("*Current Medications*")
                            st.write(selected_patient['current_medications'])
                        
                        # Medical Conditions
                        conditions = []
                        condition_fields = ['asthma', 'eczema', 'sinus_infections', 'pneumonia', 'bronchitis', 
                                          'high_blood_pressure', 'heart_disease', 'diabetes']
                        for condition in condition_fields:
                            if selected_patient.get(condition):
                                conditions.append(condition.replace('_', ' ').title())
                        
                        if conditions:
                            st.markdown("*Medical Conditions*")
                            st.write(", ".join(conditions))
                        
                        # Family History
                        if selected_patient.get('family_history'):
                            st.markdown("*Family History*")
                            st.write(selected_patient['family_history'])
                        
                        # Form Completion Status
                        st.markdown("**📋 Form Status**")
                        col8, col9 = st.columns(2)
                        with col8:
                            st.write(f"**Created Date:** {selected_patient['created_date']}")
                            st.write(f"**New Patient:** {'Yes' if selected_patient['is_new_patient'] else 'No'}")
                        with col9:
                            if selected_patient.get('patient_signature'):
                                st.write(f"**Form Signed:** Yes")
                                st.write(f"**Signature Date:** {selected_patient.get('signature_date', 'Not provided')}")
                            else:
                                st.write("**Form Signed:** No")
                
                else:
                    st.info("No patients found matching the search criteria.")
                    
            except Exception as e:
                st.error(f"Error loading patients: {str(e)}")
    
    with col2:
        # Only show these sections in the main chat interface, not in appointment/patient management
        if st.session_state.show_chat:
            st.markdown("### 📋 Available Doctors")
            try:
                doctors_info = []
                for doctor_name, doctor_info in DOCTORS.items():
                    doctors_info.append({
                        "Doctor": doctor_name,
                        "Specialty": doctor_info['specialty'],
                        "Location": doctor_info['location'],
                        "Available Days": ", ".join(doctor_info['available_days'])
                    })
                
                doctors_df = pd.DataFrame(doctors_info)
                st.dataframe(doctors_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading doctor information: {str(e)}")
            
            st.markdown("### 📞 Contact Information")
            st.markdown("""
            **HealthFirst Medical Center**  
            📍 123 Medical Drive, Healthcare City, HC 12345  
            📞 +1-555-123-4567  
            📧 appointments@healthfirst.com  
            
            **Hours:** Monday-Friday, 9:00 AM - 5:00 PM
            """)
            
            st.markdown("### ⚡ Quick Tips")
            st.markdown("""
            - **New patients:** 60-minute appointments
            - **Returning patients:** 30-minute appointments
            - **Insurance required:** Please have your card ready
            - **Forms:** Complete intake forms before your visit
            - **Cancellations:** 24-hour notice required
            """)

if __name__ == "__main__":
    main()
