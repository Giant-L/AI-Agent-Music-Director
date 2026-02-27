import os
import json
import logging
import warnings
from dotenv import load_dotenv
from openai import OpenAI

# 🌟 Import ALL our physical audio processing tools
from tools.separator import separate_audio
from tools.transcriber import audio_to_midi
from tools.generator import generate_music  # 🌟 NEW: Generator tool

# Suppress noisy httpx network logs from the OpenAI SDK
logging.getLogger("httpx").setLevel(logging.WARNING)

# Securely load environment variables
load_dotenv()

# Initialize the LLM client (DeepSeek/Gemini compatible)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ==========================================
# 🌟 The Tool Registry & Schemas
# ==========================================

SEPARATE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "separate_audio_stems",
        "description": "Extract and separate an audio file into distinct stems (vocals, accompaniment). Use this as the FIRST step for any mixed song.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file_path": {
                    "type": "string",
                    "description": "The relative or absolute file path to the target audio file."
                }
            },
            "required": ["input_file_path"]
        }
    }
}

TRANSCRIBE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "audio_to_midi",
        "description": "Convert an audio track into a MIDI file. Use this to understand the melody/structure of a stem.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file_path": {
                    "type": "string",
                    "description": "The path to the audio stem (e.g., 'other.wav' or 'vocals.wav')."
                }
            },
            "required": ["input_file_path"]
        }
    }
}

# 🌟 NEW: Generation Tool Schema
GENERATE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_music",
        "description": "Generate a new audio track from a text prompt. This is the FINAL step of the creative process.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A detailed English description of the music to generate. Include style, mood, and any melodic cues inferred from previous analysis."
                }
            },
            "required": ["prompt"]
        }
    }
}

AVAILABLE_TOOLS = {
    "separate_audio_stems": separate_audio,
    "audio_to_midi": audio_to_midi,
    "generate_music": generate_music
}

# ==========================================
# 🌟 The Core Agentic Loop
# ==========================================

def run_agent_workflow(user_prompt: str) -> str:
    """
    Advanced Agentic Workflow: Supports Complex Orchestration (Separation -> Transcription -> Generation)
    """
    print(f"\n[User] {user_prompt}\n")
    print("-" * 50)
    
    # 🌟 CRITICAL: Instructing the LLM on 'Chain of Thought' for music creation
    system_prompt = (
        "You are Music-Agent, an expert AI musician. You follow a 3-step pipeline to fulfill creative requests: "
        "1. ANALYSIS: Separate stems using 'separate_audio_stems'. "
        "2. UNDERSTANDING: Convert key stems to MIDI using 'audio_to_midi' to learn the structure. "
        "3. CREATION: Based on the MIDI info and user's style preference, write a high-quality music prompt "
        "and call 'generate_music'. "
        "Always summarize the workflow and output paths at the end."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    max_turns = 10 # Increased turns to accommodate 3-step workflows
    for turn in range(max_turns):
        print(f"🧠 [Agent Brain - Turn {turn + 1}] Planning next move...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=[SEPARATE_TOOL_SCHEMA, TRANSCRIBE_TOOL_SCHEMA, GENERATE_TOOL_SCHEMA],
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"🛠️  [Execution] Triggered: '{function_name}'")
                
                function_to_call = AVAILABLE_TOOLS.get(function_name)
                if function_to_call:
                    # Execute the physical code
                    tool_result = function_to_call(**function_args)
                    print(f"✅ [Execution] '{function_name}' returned a result.")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })
                else:
                    print(f"❌ Error: Tool {function_name} not found.")
        else:
            final_answer = response_message.content
            print("\n✨ [Final Answer]")
            print(final_answer)
            return final_answer
            
    return "❌ Error: Workflow timeout."

# ==========================================
# Creative Testing Block
# ==========================================
if __name__ == "__main__":
    # Test a full creative chain: Separate -> Transcribe -> Generate Cyberpunk Remix
    query = "Help me extract the accompaniment from 'test.mp3', analyze it, and then generate a 10-second Cyberpunk-style remix."
    run_agent_workflow(query)