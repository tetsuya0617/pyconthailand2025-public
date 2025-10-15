"""
MCP Client Demo with Gemini Integration

Demonstrates Model Context Protocol where:
- MCP server provides tool discovery and execution
- Gemini LLM decides which tool to call (like Claude Desktop)
- Client records audio and sends to server as base64
"""

import os
import array
import base64
import asyncio
from pathlib import Path
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


# ============================================================================
# Audio Recording (Client-side)
# ============================================================================


def record_audio(output_path: str = "/tmp/mcp_client_recording.wav") -> Path:
    """Record audio from microphone until user presses Enter.

    Args:
        output_path: Path where the recorded audio file will be saved.
            Defaults to "/tmp/mcp_client_recording.wav".

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


def llm_decide_tool(user_input: str, available_tools: list) -> dict:
    """Use LLM to decide which tool to call based on user input.

    This mimics how Claude Desktop and other MCP hosts work.

    Args:
        user_input: User's input text.
        available_tools: List of available tools from MCP server.

    Returns:
        dict: Dictionary with tool name and arguments.
            Example: {"name": "translate", "arguments": {"text": "Hello"}}
    """
    tool_descriptions = "\n".join(
        [f"- {tool.name}: {tool.description}" for tool in available_tools]
    )

    prompt = f"""You are a tool selector. Based on the user input, decide which tool to call.

Available tools:
{tool_descriptions}

User input: {user_input}

Respond with ONLY a JSON object in this format:
{{"name": "tool_name", "arguments": {{"arg1": "value1"}}}}

If the tool takes no arguments, use empty object: {{"arguments": {{}}}}
For stt tool, return: {{"name": "stt", "arguments": {{"audio_base64": "PLACEHOLDER"}}}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    import json

    return json.loads(response.text)


async def main():
    """Main function to run MCP client demo.

    Demonstrates:
    - Automatic MCP server startup via stdio
    - Tool discovery from MCP server
    - LLM-based tool selection (like Claude Desktop)
    - Tool execution via MCP protocol
    """

    # Server parameters for MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server/mcp_server.py"],
    )

    print("🚀 Starting MCP Client with Gemini Integration")
    print("=" * 60)
    print("MCP server: Provides tool discovery and execution")
    print("Gemini LLM: Decides which tool to call (like Claude Desktop)")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        print("✅ Connected to MCP server via stdio")

        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("✅ MCP session initialized")

            # Discover available tools
            tools = (await session.list_tools()).tools
            print(f"\n📋 Discovered {len(tools)} tools from MCP server:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            print("=" * 60)

            print("\n Enter text to translate or 'record' to transcribe audio")
            print("   Type 'exit' to quit\n")

            while True:
                user_input = input("> ").strip()

                if user_input.lower() == "exit":
                    break

                if not user_input:
                    continue

                try:
                    # LLM decides which tool to call (like Claude Desktop)
                    print("🤔 LLM deciding which tool to use...")
                    tool_decision = llm_decide_tool(user_input, tools)

                    print(f"🔧 Tool selected: {tool_decision['name']}")

                    # If stt tool, record audio and encode to base64
                    if tool_decision["name"] == "stt":
                        audio_path = record_audio("/tmp/mcp_client_recording.wav")

                        # Read and encode audio file
                        with open(audio_path, "rb") as f:
                            audio_data = f.read()
                            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

                        audio_path.unlink(missing_ok=True)

                        # Update arguments with actual audio data
                        tool_decision["arguments"] = {"audio_base64": audio_base64}

                    # Call the selected tool via MCP
                    result = await session.call_tool(
                        tool_decision["name"], tool_decision.get("arguments", {})
                    )

                    # Display result
                    if result.content:
                        print(f"✅ Result: {result.content[0].text}\n")
                    else:
                        print("❌ No response from tool\n")

                except Exception as e:
                    print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
