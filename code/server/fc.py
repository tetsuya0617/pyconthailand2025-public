"""
Function Calling Server (Client-Server Separated)

Provides translate and stt tools via HTTP endpoints.
Client fetches tool metadata from this server and calls tools via HTTP.
"""

from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from googletrans import Translator
from faster_whisper import WhisperModel

app = FastAPI(title="Function Calling Server")

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


class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters: dict


# ============================================================================
# Tool Endpoints
# ============================================================================


@app.post("/tools/translate", response_model=TranslateResponse)
async def translate_endpoint(request: TranslateRequest):
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


@app.post("/tools/stt", response_model=STTResponse)
async def stt_endpoint(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file to text.

    Args:
        audio: Uploaded audio file (WAV format).

    Returns:
        STTResponse: Response containing the transcribed text.

    Raises:
        HTTPException: If transcription fails (status code 500).
    """
    try:
        audio_path = Path(f"/tmp/fc_server_{audio.filename}")

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        segments, _ = whisper_model.transcribe(str(audio_path))
        text = " ".join([segment.text for segment in segments])

        audio_path.unlink(missing_ok=True)

        return STTResponse(transcribed_text=text.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tool Discovery
# ============================================================================


@app.get("/tools", response_model=list[ToolMetadata])
async def list_tools():
    """Returns available tools metadata for Gemini API.

    Returns:
        list[ToolMetadata]: List of available tools with their metadata.
            Each tool includes name, description, and JSON Schema parameters.
    """
    return [
        ToolMetadata(
            name="translate",
            description="Translates the given text to Thai language.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to translate to Thai",
                    }
                },
                "required": ["text"],
            },
        ),
        ToolMetadata(
            name="stt",
            description="Transcribes audio to text.",
            parameters={"type": "object", "properties": {}},
        ),
    ]


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Function Calling Server (Client-Server Separated)")
    print("=" * 60)
    print("📡 Server: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
