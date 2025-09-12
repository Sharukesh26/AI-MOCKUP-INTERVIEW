import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import difflib
import re
import base64
from io import BytesIO
import sounddevice as sd
import numpy as np
import wave

# Function to record audio
def record_audio(duration=5, sample_rate=44100):
    st.write("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    st.write("Recording complete!")
    
    # Save as WAV
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    
    return buffer.getvalue()

# Function to calculate match percentage
def calculate_match(job_desc, resume, criteria):
    job_text = job_desc.lower()
    resume_text = resume.lower()

    if criteria == "skills":
        job_skills = set(re.findall(r'\b[a-zA-Z]+\b', job_text))
        resume_skills = set(re.findall(r'\b[a-zA-Z]+\b', resume_text))
        match = len(job_skills & resume_skills) / len(job_skills) if job_skills else 0
    
    elif criteria == "keywords":
        job_keywords = job_text.split()
        resume_keywords = resume_text.split()
        match = len(set(job_keywords) & set(resume_keywords)) / len(set(job_keywords)) if job_keywords else 0
    
    elif criteria == "experience":
        job_exp = re.findall(r'\d+\+?\s*years?', job_text)
        resume_exp = re.findall(r'\d+\+?\s*years?', resume_text)
        match = 1 if any(exp in resume_text for exp in job_exp) else 0
    
    elif criteria == "education":
        edu_keywords = ["bachelor", "master", "phd", "degree", "diploma"]
        job_edu = set(word for word in job_text.split() if word in edu_keywords)
        resume_edu = set(word for word in resume_text.split() if word in edu_keywords)
        match = len(job_edu & resume_edu) / len(job_edu) if job_edu else 0
    
    return round(match * 100, 2)

# Function to generate interview questions
def generate_interview_questions(job_desc, resume, company_name, candidate_name):
    prompt = (
        f"Generate a list of interview questions based on the following job description and resume.\n\n"
        f"Then directly ask questions without any sections or extra text.\n\n"
        f"Job Description:\n{job_desc}\n\n"
        f"Resume:\n{resume}\n\n"
        f"Start with general questions like 'Describe yourself' and then make them more challenging."
    )
    
    genai.configure(api_key="AIzaSyDXdLKOVJULP1DK3GnmttEK0eGO4A3212o")  # Replace with your actual API Key
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    
    return [line.strip() for line in response.text.split("\n") if line.strip()]

# Streamlit App
st.title("🎙️ AR PrepZone's AI Interview App")
st.write("Upload the job description and resume to generate interview questions. Answer questions using your voice!")

# Inputs
candidate_name = st.text_input("Enter Candidate Name")
company_name = st.text_input("Company Name (Optional)")
job_description = st.text_area("Job Description", height=200)
resume_text = st.text_area("Paste your Resume", height=300)

# Calculate Match Scores
if job_description and resume_text:
    skill_match = calculate_match(job_description, resume_text, "skills")
    keyword_match = calculate_match(job_description, resume_text, "keywords")
    experience_match = calculate_match(job_description, resume_text, "experience")
    education_match = calculate_match(job_description, resume_text, "education")
    overall_match = round((skill_match + keyword_match + experience_match + education_match) / 4, 2)

    st.success("🔍 **Match Analysis:**")
    st.write(f"- **Skill Match:** {skill_match}%")
    st.write(f"- **Keyword Match:** {keyword_match}%")
    st.write(f"- **Experience Match:** {experience_match}%")
    st.write(f"- **Education Match:** {education_match}%")
    st.write(f"- **Overall Match Score:** {overall_match}%")

# Session State Initialization
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Generate Questions
if st.button("Generate Questions"):
    if not candidate_name or not job_description or not resume_text:
        st.error("Please enter candidate name, job description, and resume.")
    else:
        st.session_state.interview_questions = generate_interview_questions(job_description, resume_text, company_name, candidate_name)
        st.session_state.current_question_index = 0
        st.session_state.answers = []
        st.success("Questions generated! Click 'Next' to start.")

# Question and Answer Section
if st.session_state.interview_questions:
    current_index = st.session_state.current_question_index

    if current_index < len(st.session_state.interview_questions):
        question = st.session_state.interview_questions[current_index]
        st.write(f"**Question {current_index + 1}:** {question}")
        
        if st.button("Record Answer 🎤"):
            audio = record_audio()
            st.session_state.answers.append((question, audio))
            st.session_state.current_question_index += 1  # Move to next question automatically
        
    else:
        st.success("🎉 Thank you! Your interview is over.")
        st.write("Your responses have been recorded successfully!")

# Reset Session
if st.button("Reset"):
    st.session_state.interview_questions = []
    st.session_state.current_question_index = 0
    st.session_state.answers = []
    st.success("Session reset!")