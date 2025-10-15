"""
REST API Server

Simple REST API providing translate and speech-to-text endpoints.
No LLM integration - just standard HTTP endpoints.

Problem with REST API:
- Each feature requires a dedicated endpoint
- Client must know exact endpoint URLs
- Adding/changing endpoints requires client code updates
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from googletrans import Translator
from faster_whisper import WhisperModel

app = FastAPI(title="Translation & STT API")

# Initialize models
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")


# ============================================================================
# Translation (Server-side)
# ============================================================================


async def translate_text(text: str, dest: str = "th") -> str:
    """Translate text to target language using Google Translate.

    Args:
        text: The text to translate.
        dest: Target language code. Defaults to "th" (Thai).

    Returns:
        str: The translated text.
    """
    translator = Translator()
    result = await translator.translate(text, dest=dest)
    return result.text


# ============================================================================
# Request/Response Models
# ============================================================================


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    translated_text: str


class STTResponse(BaseModel):
    transcribed_text: str


# ============================================================================
# REST API Endpoints
# Each feature = one endpoint (client must know the URL)
# ============================================================================


@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """Translate text to Thai.

    Args:
        request: TranslateRequest containing the text to translate.

    Returns:
        TranslateResponse: Response containing the translated text.

    Raises:
        HTTPException: If translation fails (status code 500).
    """
    try:
        result = await translate_text(request.text, dest="th")
        return TranslateResponse(translated_text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stt", response_model=STTResponse)
async def speech_to_text(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file to text.

    Args:
        audio: Uploaded audio file (WAV format).

    Returns:
        STTResponse: Response containing the transcribed text.

    Raises:
        HTTPException: If transcription fails (status code 500).
    """
    try:
        audio_path = Path(f"/tmp/rest_server_{audio.filename}")

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        segments, _ = whisper_model.transcribe(str(audio_path))
        text = " ".join([segment.text for segment in segments])

        audio_path.unlink(missing_ok=True)

        return STTResponse(transcribed_text=text.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting REST API Server")
    print("=" * 60)
    print("📡 Server: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 60)
    print("\nEndpoints:")
    print("  POST /api/translate - Translate text to Thai")
    print("  POST /api/stt - Transcribe audio file (upload required)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
