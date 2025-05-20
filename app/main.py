
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
import uuid
import os

# Import modul internal (karena semua ada di folder yang sama, cukup import langsung)
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fungsi dependency untuk menyimpan file upload
async def save_uploaded_file(file: UploadFile = File(...)) -> str:
    audio_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{audio_id}.wav")
    with open(input_path, "wb") as f:
        f.write(await file.read())
    return input_path

@app.post("/voice-chat")
async def voice_chat(input_path: str = Depends(save_uploaded_file)):
    try:
    # 1. STT - Ubah suara ke teks
        text = transcribe_speech_to_text(open(input_path, "rb").read())

        # 2. LLM - Kirim ke Gemini
        response_text = generate_response(text)

        # 3. TTS - Ubah teks jawaban ke suara
        output_path = transcribe_text_to_speech(response_text)
        if not output_path:
            return JSONResponse(content={"error": "Gagal generate audio"}, status_code=500)

        return FileResponse(output_path, media_type="audio/wav")
    except Exception as e:
        print(f"[ERROR Endpoint] {e}")
        return JSONResponse(content={"error": "Terjadi kesalahan di server"}, status_code=500)

    # # 4. Kirim file audio ke frontend
    # return FileResponse(output_path, media_type="audio/wav", filename="response.wav")
