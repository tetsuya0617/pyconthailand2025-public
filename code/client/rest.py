"""
REST API Client

Simple HTTP client calling REST API endpoints directly.
No LLM - client must know which endpoint to call.

Problem with REST API approach:
1. Client must know the exact endpoint URL
2. Each new feature requires knowing a new endpoint URL
3. If server changes endpoint URLs, client code must be updated
4. Tight coupling between client and server implementation

Contrast with MCP:
- MCP: call_tool("translate", args) - no URL management needed
- REST: POST to specific URL - must know exact endpoint path
"""

import array
from pathlib import Path
import httpx
import sounddevice as sd
import soundfile as sf


# ============================================================================
# Audio Recording (Client-side)
# ============================================================================


def record_audio(output_path: str = "/tmp/rest_client_recording.wav") -> Path:
    """Record audio from microphone until user presses Enter.

    Args:
        output_path: Path where the recorded audio file will be saved.
            Defaults to "/tmp/rest_client_recording.wav".

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
# Direct API Calls
# ============================================================================


def translate_text(text: str) -> dict:
    """Call translation endpoint directly.

    ❌ Problem: Must know exact endpoint URL

    Args:
        text: The text to translate to Thai language.

    Returns:
        dict: JSON response containing the translated text.
            Example: {"translated_text": "สวัสดี"}
    """
    url = "http://localhost:8000/api/translate"
    print(f"📡 Calling: {url}")

    response = httpx.post(url, json={"text": text}, timeout=30.0)
    response.raise_for_status()
    return response.json()


def transcribe_audio() -> dict:
    """Call STT endpoint directly.

    ❌ Problem: Must know exact endpoint URL

    Returns:
        dict: JSON response containing the transcribed text.
            Example: {"transcribed_text": "Hello world"}
    """
    url = "http://localhost:8000/api/stt"
    print(f"📡 Calling: {url}")

    audio_path = record_audio("/tmp/rest_client_recording.wav")
    with open(audio_path, "rb") as f:
        files = {"audio": (audio_path.name, f, "audio/wav")}
        response = httpx.post(url, files=files, timeout=30.0)
    audio_path.unlink(missing_ok=True)

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("Enter text to translate or 'record' to transcribe audio")
    print("   Type 'exit' to quit\n")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        try:
            # Call endpoint directly based on user input
            if user_input.lower() == "record":
                result = transcribe_audio()
                print(f"✅ Result: {result['transcribed_text']}\n")
            else:
                result = translate_text(user_input)
                print(f"✅ Result: {result['translated_text']}\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")
