"""Nhận diện tiếng Việt bằng Google Speech-to-Text; âm thanh chỉ ở RAM."""
import asyncio
import base64
import io
import os
import wave
from pathlib import Path

import google.auth
import google.auth.transport.requests
import httpx


def google_stt_configured():
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    return bool(path and Path(path).is_file())


def check_wav(data):
    if not 6_400 <= len(data) <= 2_000_000:
        raise ValueError("wav_size")
    try:
        with wave.open(io.BytesIO(data), "rb") as audio:
            if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != 16000:
                raise ValueError("wav_format")
            if not 3200 <= audio.getnframes() <= 16000 * 55:
                raise ValueError("wav_duration")
            frames = audio.readframes(audio.getnframes())
            if not any(frames):
                raise ValueError("wav_silence")
    except (EOFError, wave.Error):
        raise ValueError("wav_invalid") from None


def google_token():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not credentials.valid:
        credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


async def transcribe(data):
    token = await asyncio.to_thread(google_token)
    payload = {"config": {"languageCode": "vi-VN", "sampleRateHertz": 16000,
                          "encoding": "LINEAR16", "enableAutomaticPunctuation": True},
               "audio": {"content": base64.b64encode(data).decode("ascii")}}
    async with httpx.AsyncClient(timeout=httpx.Timeout(30, connect=8)) as client:
        response = await client.post("https://speech.googleapis.com/v1/speech:recognize", json=payload,
                                     headers={"Authorization": "Bearer " + token})
        response.raise_for_status()
        data = response.json()
    return " ".join(item["alternatives"][0]["transcript"].strip() for item in data.get("results", [])
                    if item.get("alternatives") and item["alternatives"][0].get("transcript")).strip()[:2000]
