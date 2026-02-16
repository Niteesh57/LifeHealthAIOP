"""
Appointment Summarize Agent
AI agent that analyzes patient descriptions and suggests appointment details
"""
import os
from typing import Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai
from google.genai import types

from app.agent.Tools.doctorTools import get_doctors_with_availability
from app.agent.models.summarizeModel import AppointmentSummary, ConversationSummary


class AppointmentAgent:
    """
    AI Agent for analyzing patient descriptions and suggesting appointments.
    Uses Google Gemini to understand symptoms and match with appropriate doctors.
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"  # Use available Gemini model
    
    async def analyze_and_suggest_appointment(
        self,
        description: str,
        hospital_id: str,
        appointment_date: date,
        db: AsyncSession,
        patient_id: Optional[str] = None
    ) -> AppointmentSummary:
        """
        Analyze patient description and suggest appointment details.
        
        Args:
            description: Patient's description of symptoms/reason for visit
            hospital_id: Hospital ID to search for doctors
            appointment_date: Date for the appointment
            db: Database session
            patient_id: Optional patient ID
        
        Returns:
            AppointmentSummary with doctor_id, slot_time, severity, enhanced_description
        """
        
        # Get available doctors from the hospital
        doctors = await get_doctors_with_availability(
            hospital_id=hospital_id,
            db=db,
            target_date=appointment_date
        )
        
        if not doctors:
            raise ValueError("No doctors available at this hospital")
        
        # Prepare doctor information for the AI
        doctor_info = self._format_doctor_info(doctors)
        
        # Create prompt for Gemini
        prompt = self._create_analysis_prompt(description, doctor_info, appointment_date)
        
        # Call Gemini API with structured output
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=AppointmentSummary
            )
        )
        
        # Parse the structured response
        import json
        result = json.loads(response.text)
        
        # Create AppointmentSummary object
        appointment_summary = AppointmentSummary(
            doctor_id=result["doctor_id"],
            slot_time=result["slot_time"],
            severity=result["severity"],
            enhanced_description=result["enhanced_description"],
            appointment_date=appointment_date,
            patient_id=patient_id
        )
        
        return appointment_summary
    
    def _format_doctor_info(self, doctors: list) -> str:
        """Format doctor information for AI prompt."""
        info_lines = []
        for doctor in doctors:
            available_slots = ", ".join(doctor["available_slots"][:10])  # Show first 10 slots
            info_lines.append(
                f"- Doctor ID: {doctor['doctor_id']}\n"
                f"  Name: {doctor['name']}\n"
                f"  Specialization: {doctor['specialization']}\n"
                f"  Experience: {doctor['experience_years']} years\n"
                f"  Available Slots: {available_slots}\n"
                f"  Free Slots Count: {doctor['free_count']}"
            )
        return "\n\n".join(info_lines)
    
    def _create_analysis_prompt(
        self, 
        description: str, 
        doctor_info: str,
        appointment_date: date
    ) -> str:
        """Create prompt for Gemini analysis."""
        return f"""You are a medical appointment assistant. Analyze the patient's description and suggest the most appropriate doctor and appointment details.

Patient Description:
{description}

Appointment Date: {appointment_date}

Available Doctors:
{doctor_info}

Instructions:
1. Analyze the symptoms/condition described
2. Match with the most appropriate doctor based on specialization
3. Suggest a suitable time slot from their available slots
4. Determine severity level (low, medium, high, critical) based on:
   - low: routine checkups, minor issues
   - medium: persistent symptoms, moderate concerns
   - high: severe symptoms, urgent but not life-threatening
   - critical: emergency situations, severe pain, life-threatening
5. Create an enhanced description that summarizes the condition professionally

Provide your response as JSON with:
- doctor_id: The ID of the most suitable doctor
- slot_time: A recommended time slot (HH:MM format)
- severity: The severity level (low/medium/high/critical)
- enhanced_description: A professional summary of the patient's condition
"""


async def create_appointment_suggestion(
    description: str,
    hospital_id: str,
    db: AsyncSession,
    appointment_date: Optional[date] = None,
    patient_id: Optional[str] = None
) -> AppointmentSummary:
    """
    Convenience function to create appointment suggestion.
    
    Args:
        description: Patient's description
        hospital_id: Hospital ID
        db: Database session
        appointment_date: Date for appointment (defaults to today)
        patient_id: Optional patient ID
    
    Returns:
        AppointmentSummary with suggested appointment details
    """
    if appointment_date is None:
        appointment_date = date.today()
    
    agent = AppointmentAgent()
    return await agent.analyze_and_suggest_appointment(
        description=description,
        hospital_id=hospital_id,
        appointment_date=appointment_date,
        db=db,
        patient_id=patient_id
    )