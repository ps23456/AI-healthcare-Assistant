#!/usr/bin/env python3
"""
Test script for Medical Appointment Scheduling AI Agent
This script tests all major components of the system
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from config import OPENAI_API_KEY, DOCTORS, NEW_PATIENT_DURATION
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config module import failed: {e}")
        return False
    
    try:
        from database import db
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    try:
        from communication import comm_manager
        print("✅ Communication module imported successfully")
    except Exception as e:
        print(f"❌ Communication module import failed: {e}")
        return False
    
    try:
        from ai_agent import agent
        print("✅ AI Agent module imported successfully")
    except Exception as e:
        print(f"❌ AI Agent module import failed: {e}")
        return False
    
    try:
        from data_generator import create_sample_data
        print("✅ Data Generator module imported successfully")
    except Exception as e:
        print(f"❌ Data Generator module import failed: {e}")
        return False
    
    try:
        from reminder_system import reminder_system
        print("✅ Reminder System module imported successfully")
    except Exception as e:
        print(f"❌ Reminder System module import failed: {e}")
        return False
    
    return True

def test_data_generation():
    """Test sample data generation"""
    print("\n🔍 Testing data generation...")
    
    try:
        from data_generator import create_sample_data
        
        # Create sample data
        create_sample_data()
        
        # Check if files were created
        from config import PATIENT_DB_FILE, SCHEDULE_FILE, APPOINTMENTS_FILE
        
        if os.path.exists(PATIENT_DB_FILE):
            patients_df = pd.read_csv(PATIENT_DB_FILE)
            print(f"✅ Patient data created: {len(patients_df)} patients")
        else:
            print("❌ Patient data file not created")
            return False
        
        if os.path.exists(SCHEDULE_FILE):
            schedules_df = pd.read_excel(SCHEDULE_FILE)
            print(f"✅ Schedule data created: {len(schedules_df)} schedule entries")
        else:
            print("❌ Schedule data file not created")
            return False
        
        if os.path.exists(APPOINTMENTS_FILE):
            appointments_df = pd.read_excel(APPOINTMENTS_FILE)
            print(f"✅ Appointments file created: {len(appointments_df)} appointments")
        else:
            print("❌ Appointments file not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n🔍 Testing database operations...")
    
    try:
        from database import db
        
        # Test patient search
        if len(db.patients_df) > 0:
            sample_patient = db.patients_df.iloc[0]
            search_result = db.find_patient(
                first_name=sample_patient['first_name'],
                last_name=sample_patient['last_name']
            )
            if len(search_result) > 0:
                print("✅ Patient search working")
            else:
                print("❌ Patient search failed")
                return False
        else:
            print("⚠️  No patients in database to test search")
        
        # Test available slots
        if len(db.schedules_df) > 0:
            sample_schedule = db.schedules_df.iloc[0]
            slots = db.get_available_slots(
                doctor_name=sample_schedule['doctor_name'],
                date=sample_schedule['date']
            )
            print(f"✅ Available slots found: {len(slots)} slots")
        else:
            print("⚠️  No schedules in database to test slot lookup")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False

def test_ai_agent():
    """Test AI agent functionality"""
    print("\n🔍 Testing AI agent...")
    
    try:
        from ai_agent import agent
        
        # Test basic message processing
        test_message = "Hello, I need to schedule an appointment"
        response = agent.process_message(test_message)
        
        if response and len(response) > 0:
            print("✅ AI agent responding to messages")
            print(f"Sample response: {response[:100]}...")
        else:
            print("❌ AI agent not responding")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI agent test failed: {e}")
        return False

def test_communication():
    """Test communication system"""
    print("\n🔍 Testing communication system...")
    
    try:
        from communication import comm_manager
        
        # Test email configuration
        if comm_manager.email_user and comm_manager.email_user != "your-email@gmail.com":
            print("✅ Email configuration set")
        else:
            print("⚠️  Email not configured (using default)")
        
        # Test Twilio configuration
        if comm_manager.twilio_client:
            print("✅ Twilio SMS configured")
        else:
            print("⚠️  Twilio SMS not configured (using email only)")
        
        return True
        
    except Exception as e:
        print(f"❌ Communication test failed: {e}")
        return False

def test_reminder_system():
    """Test reminder system"""
    print("\n🔍 Testing reminder system...")
    
    try:
        from reminder_system import reminder_system
        
        # Test reminder system initialization
        if reminder_system:
            print("✅ Reminder system initialized")
        else:
            print("❌ Reminder system initialization failed")
            return False
        
        # Test manual reminder check
        reminder_system.manual_reminder_check()
        print("✅ Manual reminder check completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Reminder system test failed: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import (
            OPENAI_API_KEY, DOCTORS, NEW_PATIENT_DURATION, 
            RETURNING_PATIENT_DURATION, CLINIC_NAME, CLINIC_ADDRESS
        )
        
        # Check OpenAI API key
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here":
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key not configured (using default)")
        
        # Check doctors configuration
        if DOCTORS and len(DOCTORS) > 0:
            print(f"✅ Doctors configured: {len(DOCTORS)} doctors")
        else:
            print("❌ No doctors configured")
            return False
        
        # Check appointment durations
        if NEW_PATIENT_DURATION == 60 and RETURNING_PATIENT_DURATION == 30:
            print("✅ Appointment durations configured correctly")
        else:
            print("❌ Appointment durations not configured correctly")
            return False
        
        # Check clinic information
        if CLINIC_NAME and CLINIC_ADDRESS:
            print("✅ Clinic information configured")
        else:
            print("❌ Clinic information not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'config.py',
        'database.py',
        'ai_agent.py',
        'communication.py',
        'data_generator.py',
        'reminder_system.py',
        'streamlit_app.py',
        'requirements.txt',
        'README.md',
        'TECHNICAL_APPROACH.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🏥 Medical Appointment Scheduling AI Agent - System Test")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Module Imports", test_imports),
        ("Data Generation", test_data_generation),
        ("Database Operations", test_database_operations),
        ("AI Agent", test_ai_agent),
        ("Communication", test_communication),
        ("Reminder System", test_reminder_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the application:")
        print("   streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set up environment variables in .env file")
        print("   3. Configure OpenAI API key")
        print("   4. Set up email/SMS credentials")

if __name__ == "__main__":
    main()
