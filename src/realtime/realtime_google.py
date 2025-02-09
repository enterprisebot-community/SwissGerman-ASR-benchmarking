import os
import time
import sys
from google.cloud import speech
import pyaudio
from six.moves import queue

"""
Google Cloud Streaming Speech-to-Text with Pause Detection

Input:
- Audio stream from the microphone.
- Google Cloud Speech-to-Text API for real-time transcription.
Output:
- Prints real-time transcriptions.
- Detects pauses and restarts the stream automatically. (pauses need to be long for Google to detect)
"""

# Ensure Google credentials are set via environment variable
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_CREDENTIALS:
    print("Error: Google Cloud credentials not set. Please set GOOGLE_APPLICATION_CREDENTIALS.")
    exit(1)

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks
PAUSE_THRESHOLD = 0.5  # Time (seconds) to detect a pause

class MicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks."""
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self.audio_interface = pyaudio.PyAudio()
        self.audio_stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.closed = True
        self.buff.put(None)
        self.audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Callback function to receive audio chunks from the stream."""
        self.buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Yields audio chunks from the buffer."""
        while not self.closed:
            chunk = self.buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)

def transcribe_with_pause_detection():
    """Continuously listens and transcribes, restarting the stream after pauses."""
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="de-CH",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
        enable_voice_activity_events=False,  # Handling pauses manually
        single_utterance=False,  # Keeps listening instead of stopping
    )

    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)

            pause_detected = process_transcriptions(responses, stream)

            if pause_detected:
                print("\n Restarting stream after detected pause...\n")  # Resets stream so it continues

def process_transcriptions(responses, stream):
    """Processes transcription results, detects pauses, and restarts after silence."""
    last_word_spoken_time = None  # Timestamp of last spoken word
    last_word_written_time = None  # Timestamp when transcription appears
    last_transcription = ""  # Store last full transcription

    for response in responses:
        if not response.results:
            continue

        for result in response.results:
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript.strip()

            if result.is_final:  # Process final transcriptions when pause is detected
                last_word_written_time = time.time()  # Timestamp when transcription is finalized

                if transcript != last_transcription:
                    print(f"\nRecognized: {transcript}")

                    # Print timestamps
                    if last_word_spoken_time:
                        print(f"Last word spoken timestamp: {last_word_spoken_time:.3f} seconds")
                        print(f"Last word written timestamp: {last_word_written_time:.3f} seconds")

                        # Calculate transcription delay
                        delay = last_word_written_time - last_word_spoken_time
                        print(f"Transcription delay: {delay:.3f} seconds\n")

                    last_transcription = transcript
                    last_word_spoken_time = None  # Reset for next phrase
                    return True  # ✅ Pause detected → Restart stream
            else:  # Handle partial transcriptions (interim results)
                words = transcript.split()
                if words:
                    last_word_spoken_time = time.time()

        # Pause detection 
        if last_word_spoken_time and (time.time() - last_word_spoken_time) >= PAUSE_THRESHOLD:
            print("\n(Pause detected) Finalizing transcript...\n")
            stream.buff.put(None)  # Force stop the stream so Google finalizes 
            return True  #Restart stream after pause

    return False  # No pause detected → Continue listening

if __name__ == "__main__":
    transcribe_with_pause_detection()
