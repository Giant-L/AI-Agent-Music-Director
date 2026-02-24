# Music-Agent: An LLM-Powered Multimodal Audio Processing Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Introduction
**Music-Agent** is an intelligent workflow automation system driven by Large Language Models (LLMs). It acts as a virtual "Music Producer," capable of understanding complex natural language instructions from users and orchestrating various advanced audio processing models via **Function Calling / Tool Use**. 

Instead of relying on monolithic models, this Agent dynamically routes tasks such as stem separation, audio-to-MIDI transcription, and audio-conditioned generation, providing users with fine-grained control over their music creation process.

## ✨ Core Features (Functional Modules)
*  **LLM Agent Brain:** Parses complex natural language prompts, decomposes tasks, and sequentially triggers the right audio tools.
*  **Smart Stem Separation:** Automatically isolates vocals, drums, bass, and other instruments (e.g., piano, guitar) from a mixed audio track.
*  **Audio-to-MIDI Transcription:** Converts isolated instrumental audio tracks directly into playable and editable MIDI sheet music.
*  **Conditioned Audio Generation:** (WIP) Synthesizes new audio segments based on both text prompts and isolated audio conditions.
*  **Interactive Web UI:** A clean, user-friendly interface built for seamless audio uploading and text interaction.

## 📂 Project Structure
```text
music-agent/
├── app.py                 # Main UI entry point (Streamlit/Gradio)
├── agent/
│   ├── __init__.py
│   └── core.py            # LLM intent parsing and Function Calling logic
├── tools/
│   ├── __init__.py
│   ├── separator.py       # Demucs stem separation wrapper
│   ├── transcriber.py     # Basic-Pitch MIDI conversion wrapper
│   └── generator.py       # (Optional) Audio generation API integration
├── workspace/             # Temporary directory for I/O audio files
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation

```

## 🛠️ Quick Start
*(To be updated: Installation instructions, API key setup, and execution commands will be added as the project develops.)*

## 🙏 Acknowledgements
This project stands on the shoulders of giants. We deeply appreciate the open-source community for providing the underlying audio algorithms:
* **[Demucs](https://github.com/facebookresearch/demucs):** State-of-the-art music source separation by Meta Research.
* **[Basic-Pitch](https://github.com/spotify/basic-pitch):** A lightweight, fast audio-to-MIDI converter by Spotify.
* **[Qwen / DeepSeek]:** For providing robust LLM reasoning and Function Calling capabilities.
* **[Streamlit](https://streamlit.io/):** For the rapid development of the interactive Web UI.

## ⚠️ Disclaimer
This project is developed solely for **educational and research purposes**. The developers do not host or distribute any copyrighted audio material. Users are strictly responsible for ensuring they have the appropriate rights, licenses, and permissions for any audio files processed or generated using this tool.
Basic-Pitch: A lightweight, fast audio-to-MIDI converter by Spotify.

[Qwen / DeepSeek]: For providing robust LLM reasoning and Function Calling capabilities.

Streamlit: For the rapid development of the interactive Web UI.