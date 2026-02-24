# agent/core.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import logging

# 🌟 Import our physical audio processing tool
from tools.separator import separate_audio

# 1. Securely load environment variables
load_dotenv()

# 2. Initialize the LLM client (DeepSeek)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# additional logging configuration to reduce noise from the httpx library used by OpenAI SDK
logging.getLogger("httpx").setLevel(logging.WARNING)

# 3. Define the Tool Schema
SEPARATE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "separate_audio_stems",
        "description": "Extract and separate an audio file into distinct stems: vocals, drums, bass, and other instruments. Use this when the user wants to isolate human voice, extract background music, or get specific instrumental tracks from a song.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file_path": {
                    "type": "string",
                    "description": "The relative or absolute file path to the target audio file (e.g., 'test.mp3')."
                }
            },
            "required": ["input_file_path"]
        }
    }
}

# 🌟 Tool Registry: Map the string name from LLM to the actual Python function
AVAILABLE_TOOLS = {
    "separate_audio_stems": separate_audio
}

def run_agent_workflow(user_prompt: str):
    """
    The complete Agent execution loop: 
    Receive Prompt -> LLM Thinks -> Execute Python Tool -> LLM Summarizes
    """
    print(f"\n[User] {user_prompt}\n")
    print("-" * 50)
    
    # Initialize message history with System Prompt
    messages = [
        {
            "role": "system", 
            "content": "You are Music-Agent, a professional AI audio processing assistant. You have access to audio processing tools. You MUST use the tools if the user asks for audio separation. Do not apologize, just call the tool. After the tool returns a result, summarize the output file paths for the user clearly and concisely."
        },
        {"role": "user", "content": user_prompt}
    ]

    # [Round 1]: Let the LLM decide if it needs to use a tool
    print("🧠 [Agent Brain] Analyzing intent and planning...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[SEPARATE_TOOL_SCHEMA],
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message) # Add LLM's thought to the context memory

    # Check if the LLM decided to call a tool
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🛠️  [Execution] LLM triggered tool: '{function_name}'")
            print(f"   📦 Parsed Arguments: {function_args}")
            
            # 1. Retrieve the actual Python function from our registry
            function_to_call = AVAILABLE_TOOLS.get(function_name)
            
            if function_to_call:
                print("⚙️  [Execution] Running actual Python code (This may take a minute)...")
                # 2. Execute the tool with the arguments provided by the LLM
                tool_result = function_to_call(
                    input_file_path=function_args.get("input_file_path")
                )
                print(f"✅ [Execution] Tool finished successfully.")
                
                # 3. Package the JSON result and send it back to the LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result)
                })
            else:
                error_msg = f"Tool {function_name} not found in registry."
                print(f"❌ [Error] {error_msg}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps({"error": error_msg})
                })

        # [Round 2]: The LLM reads the tool's result and generates a final human-readable answer
        print("🧠 [Agent Brain] Reading tool output and generating final response...")
        second_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        print("\n✨ [Final Answer]")
        print(second_response.choices[0].message.content)

    else:
        # If no tool was needed (e.g., general chat)
        print("\n✨ [Final Answer]")
        print(response_message.content)

# ==========================================
# Local Testing Block
# ==========================================
if __name__ == "__main__":
    # Note: We also changed the test prompt to English to keep everything consistent!
    run_agent_workflow("Please separate the vocals and instruments from the test.mp3 file.")