from fastapi import FastAPI
from src.routers import transcribe

app = FastAPI(
    title="Speech-to-Text API",
    description="OpenAI-powered transcription service with multi-language support",
    version="1.0.0"
)

# Register routers with /v1 prefix
app.include_router(transcribe.router, prefix="/v1")

@app.get("/")
async def root():
    return {
        "message": "Speech-to-Text API",
        "version": "1.0.0",
        "endpoints": ["/v1/transcribe"]
    }
