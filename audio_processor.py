import logging
import os
import io
from pydub import AudioSegment
from google.cloud import speech
from google.cloud.speech_v1 import types


def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    return audio


def convert_audio_to_text(audio_path, language_code='en-US', progress_callback=None):
    try:
        # Ensure ffmpeg is used
        AudioSegment.converter = "ffmpeg"

        # Convert audio to WAV format if not already in WAV format
        audio = AudioSegment.from_file(audio_path)
        wav_path = "temp_audio.wav"
        audio.export(wav_path, format="wav")

        client = speech.SpeechClient()

        transcript = ""
        chunk_length_ms = 60000  # 60 seconds
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")

            with io.open(chunk_path, "rb") as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
            )

            response = client.recognize(config=config, audio=audio)

            for result in response.results:
                transcript += result.alternatives[0].transcript

            os.remove(chunk_path)

            # Update progress
            if progress_callback:
                progress_callback((i + 1) / total_chunks * 100)

        os.remove(wav_path)

        return transcript
    except Exception as e:
            logging.error(f"Failed to parse eBook: {e}")
            raise