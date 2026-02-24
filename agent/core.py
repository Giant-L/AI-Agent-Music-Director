# agent/core.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Securely load environment variables from the .env file
load_dotenv()

# 2. Initialize the LLM client (Using DeepSeek via OpenAI SDK format)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. Core: Define the Tool Schema (Function Signature for the LLM)
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

def test_llm_intent_parsing(user_prompt: str):
    """
    Tests whether the LLM can understand natural language and correctly decide to call the tool.
    """
    print(f"\n[User] Prompting the LLM: '{user_prompt}'\n")
    
    # Construct the system and user messages
    messages = [
        {"role": "system", "content": "You are Music-Agent, a professional AI audio processing assistant. You have access to audio processing tools. You MUST use the tools if the user asks for audio separation. Do not apologize, just call the tool."},
        {"role": "user", "content": user_prompt}
    ]

    # Send the request to the LLM, passing the tool schema
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[SEPARATE_TOOL_SCHEMA],
        tool_choice="auto"  # Let the model decide whether to use a tool or reply with text
    )

    # Capture the LLM's thought process
    response_message = response.choices[0].message
    
    # Check if the LLM decided to call a tool
    if response_message.tool_calls:
        print("🤖 [Agent Brain] Thought complete: I have decided to call an external tool!")
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            print(f"   🎯 Target Tool Name: {function_name}")
            print(f"   📦 Extracted Parameters: {function_args}")
    else:
        print("🤖 [Agent Brain] Thought complete: No tool needed. Replying directly:")
        print(f"   💬 {response_message.content}")

# ==========================================
# Local Testing Block
# ==========================================
if __name__ == "__main__":
    # Test Case 1: Clear intent to use the tool
    test_llm_intent_parsing("Help me extract the vocals from the test.mp3 file in the current directory.")
    
    print("-" * 50)
    
    # Test Case 2: Chit-chat intent (Should NOT trigger the tool)
    test_llm_intent_parsing("Hello, can you write a poem about spring?")