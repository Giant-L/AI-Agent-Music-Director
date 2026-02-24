# app.py

import streamlit as st
import os
from pathlib import Path

# 🌟 Import our Agent Core
from agent.core import run_agent_workflow

# ==========================================
# 1. Page Configuration & UI Setup
# ==========================================
st.set_page_config(page_title="Music-Agent AI", page_icon="🎵", layout="wide")

st.title("🎵 Music-Agent: AI Audio Assistant")
st.markdown("Upload an audio track and command the AI to separate vocals, drums, or bass using natural language!")

# Ensure workspace directories exist for uploaded files
INPUT_DIR = Path("workspace/inputs")
INPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Sidebar: File Upload & Management
# ==========================================
with st.sidebar:
    st.header("📁 Audio Upload")
    uploaded_file = st.file_uploader("Upload your MP3/WAV file here", type=["mp3", "wav"])
    
    current_file_path = None
    if uploaded_file is not None:
        # Save the uploaded file from browser memory to our local workspace
        file_path = INPUT_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"File ready: {uploaded_file.name}")
        current_file_path = str(file_path.absolute())
        
        # Display an audio player for the original track
        st.audio(current_file_path)

# ==========================================
# 3. Main Chat Interface
# ==========================================
# Initialize session state to keep track of conversation history in the UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input Box
if prompt := st.chat_input("E.g., Please separate the vocals and instruments from the uploaded song."):
    
    # Render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Execution Block
    with st.chat_message("assistant"):
        # Show a spinning loading indicator while the Agent and Demucs are working
        with st.spinner("🧠 Agent is thinking and processing... (This may take 1-2 minutes for audio separation)"):
            
            # 🌟 THE MAGIC TRICK: Context Injection
            # We silently append the absolute path of the uploaded file to the user's prompt
            # so the LLM knows exactly where to find the file without the user typing it.
            agent_prompt = prompt
            if current_file_path:
                agent_prompt += f"\n\n[System Context: The user has uploaded an audio file located at '{current_file_path}'. If the user asks to process the file, extract and use this exact path for the tool.]"
            
            try:
                # 1. Call our backend LLM Agent
                response_text = run_agent_workflow(agent_prompt)
                
                # 2. Display the LLM's final markdown response
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                # 3. Bonus UI Feature: Auto-render separated audio players
                if current_file_path and uploaded_file:
                    stem_name = Path(uploaded_file.name).stem
                    separated_dir = Path(f"workspace/separated/htdemucs/{stem_name}")
                    
                    if separated_dir.exists():
                        st.write("### 🎧 Separated Audio Tracks")
                        cols = st.columns(4)
                        tracks = ["vocals.wav", "other.wav", "drums.wav", "bass.wav"]
                        
                        for i, track in enumerate(tracks):
                            track_path = separated_dir / track
                            if track_path.exists():
                                with cols[i]:
                                    st.write(f"**{track.split('.')[0].capitalize()}**")
                                    st.audio(str(track_path))
                                    
            except Exception as e:
                st.error(f"❌ An error occurred during Agent execution: {str(e)}")