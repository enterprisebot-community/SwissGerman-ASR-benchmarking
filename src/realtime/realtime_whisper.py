import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
from queue import Queue
from time import sleep, time
from datetime import datetime, timedelta

"""
Real-Time Speech Transcription Using OpenAI Whisper

Input:
- Audio stream from the microphone.
- Whisper model for real-time transcription.

Output:
- Prints transcriptions in real-time.
- Logs timestamps and calculates transcription delay.
"""

# Load Whisper model (Uses environment variable or defaults to "base")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # Options: "tiny", "base", "small", "medium", "large"
audio_model = whisper.load_model(WHISPER_MODEL)

# Microphone Settings
ENERGY_THRESHOLD = 1000  # Sensitivity for detecting voice
RECORD_TIMEOUT = 4.5  # Capture audio in longer chunks (seconds)
PHRASE_TIMEOUT = 3.5  # Silence duration before finalizing a phrase (seconds)

# Initialize recognizer
recorder = sr.Recognizer()
recorder.energy_threshold = ENERGY_THRESHOLD  # Set mic sensitivity
recorder.dynamic_energy_threshold = False  # Disable auto-adjustment

# Select Microphone
try:
    source = sr.Microphone(sample_rate=16000)
except OSError:
    print("Error: No microphone found. Please check your device.")
    exit(1)

# Audio Queue for real-time processing
data_queue = Queue()

# Adjust for background noise before starting
with source:
    recorder.adjust_for_ambient_noise(source)

def record_callback(_, audio: sr.AudioData):
    """Callback function to store recorded audio in a queue."""
    data_queue.put(audio.get_raw_data())

# Start background listening
recorder.listen_in_background(source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

print("🎤 Speak into your microphone.")

phrase_time = None  # Last time audio was received
full_transcription = []  # Store the complete conversation
first_transcription_done = False  # Track if first phrase is printed

while True:
    try:
        now = datetime.utcnow()

        if not data_queue.empty():
            phrase_complete = False

            # If enough silence has passed, finalize the phrase
            if phrase_time and now - phrase_time > timedelta(seconds=PHRASE_TIMEOUT):
                phrase_complete = True

            phrase_time = now  # Update phrase timestamp

            # Collect all queued audio data
            audio_data = b''.join(data_queue.queue)
            data_queue.queue.clear()

            # Convert to NumPy array for Whisper
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Capture the time when speech stopped
            last_word_spoken_time = time()

            # Transcribe using Whisper
            start_transcription_time = time()  # When Whisper starts processing
            result = audio_model.transcribe(audio_np, 
                                            language="de",  # Force German
                                            fp16=torch.cuda.is_available(),  
                                            temperature=0.0)  # Reduces hallucinations
            last_word_written_time = time()  # When Whisper finishes processing

            text = result['text'].strip()

            # Calculate delay
            transcription_delay = last_word_written_time - last_word_spoken_time

            # Ensure first phrase is printed separately
            if text and not first_transcription_done:
                print(f"\n Recognized: {text}")
                print(f"Last word spoken timestamp: {last_word_spoken_time:.3f} seconds")
                print(f"Last word written timestamp: {last_word_written_time:.3f} seconds")
                print(f"Transcription delay: {transcription_delay:.3f} seconds\n")
                first_transcription_done = True  # Mark first phrase as printed
                full_transcription.append(text)  # Store first phrase

            # Print each transcription **without breaking sentences too early**
            elif text:
                if phrase_complete:
                    print(f"\n Recognized: {text}")
                    print(f"Last word spoken timestamp: {last_word_spoken_time:.3f} seconds")
                    print(f"Last word written timestamp: {last_word_written_time:.3f} seconds")
                    print(f"Transcription delay: {transcription_delay:.3f} seconds\n")
                    
                    full_transcription.append(text)  # Store the full transcription
                else:
                    if full_transcription:
                        full_transcription[-1] += " " + text  # Merge with last line
                    else:
                        full_transcription.append(text)  # First line

        else:
            sleep(0.25)  # Prevent CPU overuse

    except KeyboardInterrupt:
        break

print("\n\n✅ Final Transcription Complete!")
print("\n".join(full_transcription))