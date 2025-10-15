"""
Function Calling Client (Client-Server Separated)

Demonstrates client-server separation with Gemini function calling:
- Server provides tools via HTTP endpoints
- Gemini LLM decides which tool to call
- Client executes tools by calling server endpoints (manual function calling)
"""

import os
import array
from pathlib import Path
import httpx
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Server URL
SERVER_URL = "http://localhost:8000"

# ============================================================================
# Audio Recording (Client-side)
# ============================================================================


def record_audio(output_path: str = "/tmp/fc_client_recording.wav") -> Path:
    """Record audio from microphone until user presses Enter.

    Args:
        output_path: Path where the recorded audio file will be saved.
            Defaults to "/tmp/fc_client_recording.wav".

    Returns:
        Path: Path object pointing to the saved audio file (WAV format, 16kHz).
    """
    audio_path = Path(output_path)
    sample_rate = 16000
    recording = []

    print("\n🎤 Recording... Press Enter to stop")

    def callback(indata, *_):
        recording.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        input()

    audio_data = array.array("f")
    for chunk in recording:
        audio_data.extend(chunk.flatten())

    sf.write(str(audio_path), audio_data, sample_rate)
    print("✅ Recording saved\n")

    return audio_path


# ============================================================================
# Server Communication
# ============================================================================


def fetch_tools_from_server():
    """Fetch available tools metadata from server.

    Returns:
        list: List of tool metadata dictionaries from the server.
            Each dict contains: name, description, parameters.
    """
    response = httpx.get(f"{SERVER_URL}/tools", timeout=5.0)
    response.raise_for_status()
    return response.json()


def convert_to_gemini_tool(tool_metadata: dict):
    """Convert server tool metadata to Gemini FunctionDeclaration format.

    Args:
        tool_metadata: Tool metadata dictionary containing name, description,
            and parameters fields.

    Returns:
        types.FunctionDeclaration: Gemini-compatible function declaration.
    """
    return types.FunctionDeclaration(
        name=tool_metadata["name"],
        description=tool_metadata["description"],
        parameters=tool_metadata["parameters"],
    )


def execute_tool_on_server(tool_name: str, arguments: dict) -> dict:
    """Execute tool by calling server endpoint.

    Args:
        tool_name: Name of the tool to execute (e.g., "translate", "stt").
        arguments: Dictionary of arguments to pass to the tool.

    Returns:
        dict: JSON response from the server containing the tool execution result.
    """
    print(f"📡 Calling server endpoint: /tools/{tool_name}")

    if tool_name == "stt":
        # Record audio locally and upload to server
        audio_path = record_audio("/tmp/fc_client_recording.wav")
        with open(audio_path, "rb") as f:
            files = {"audio": (audio_path.name, f, "audio/wav")}
            response = httpx.post(
                f"{SERVER_URL}/tools/{tool_name}", files=files, timeout=30.0
            )
        audio_path.unlink(missing_ok=True)
    else:
        # JSON request for translation
        response = httpx.post(
            f"{SERVER_URL}/tools/{tool_name}", json=arguments, timeout=30.0
        )

    response.raise_for_status()
    return response.json()


# ============================================================================
# Gemini Function Calling (Manual)
# ============================================================================


def generate_with_remote_tools(user_input: str, tools_metadata: list) -> str:
    """Use Gemini with manual function calling and remote tool execution.

    Flow:
    1. Gemini decides which tool to call (no auto-execution)
    2. Client calls server endpoint to execute the tool
    3. Client sends result back to Gemini for final response

    Args:
        user_input: The user's input text or command.
        tools_metadata: List of tool metadata from the server.

    Returns:
        str: The final text response from Gemini after tool execution.
    """
    # Convert server tool metadata to Gemini format
    gemini_tools = [convert_to_gemini_tool(t) for t in tools_metadata]

    # Step 1: Let Gemini decide which tool to call (no auto-execution)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You must always use tools. "
                "For text input: use translate tool to convert to Thai. "
                "For 'record' requests: use stt tool."
            ),
            tools=[types.Tool(function_declarations=gemini_tools)],
            # NOTE: No automatic_function_calling - we handle execution manually
        ),
    )

    # Step 2: Check if Gemini wants to call a function
    if not response.candidates:
        return "No response from Gemini"

    first_part = response.candidates[0].content.parts[0]

    # If it's a direct text response (no function call)
    if hasattr(first_part, "text") and first_part.text:
        return first_part.text

    # If Gemini wants to call a function
    if hasattr(first_part, "function_call"):
        func_call = first_part.function_call
        print(f"🔧 Tool selected: {func_call.name}")

        # Step 3: Execute tool on server
        tool_result = execute_tool_on_server(func_call.name, dict(func_call.args))

        # Step 4: Send result back to Gemini for final response
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_input)]),
                types.Content(
                    role="model", parts=[types.Part(function_call=func_call)]
                ),
                types.Content(
                    role="function",
                    parts=[
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=func_call.name, response=tool_result
                            )
                        )
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction="Extract and return only the translated_text or transcribed_text value from the function result."
            ),
        )

        return final_response.text or "No response"

    return "Unexpected response format"


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: Set GEMINI_API_KEY in .env file")
        exit(1)

    print("🎯 Function Calling Client (Client-Server Separated)")
    print("=" * 60)
    print(f"📡 Connecting to server: {SERVER_URL}")

    # Fetch tools from server
    try:
        tools_metadata = fetch_tools_from_server()
        print(f"✅ Discovered {len(tools_metadata)} tools from server:")
        for tool in tools_metadata:
            print(f"  - {tool['name']}: {tool['description']}")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        print("💡 Make sure server is running: python server/fc.py")
        exit(1)

    print("\n Enter text to translate or 'record' to transcribe audio")
    print("   Type 'exit' to quit\n")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        try:
            result = generate_with_remote_tools(user_input, tools_metadata)
            print(f"✅ Result: {result}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
