import asyncio
import os
import time
import pyaudio
from queue import Queue
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

"""
Amazon Transcribe Real-Time Speech-to-Text with Live Audio Stream

Input:
- Audio stream from the microphone.
- AWS Transcribe real-time API for speech-to-text conversion.
Output:
- Prints real-time transcriptions.
- Logs timestamps and calculates transcription delay.
"""

# Load AWS region from environment variable
AWS_REGION = os.getenv("AWS_REGION")  # change Region accordingly

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 20)  # 100ms chunks

class MicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks."""
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk
        self.buff = Queue()
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
            yield chunk

class MyEventHandler(TranscriptResultStreamHandler):
    """Handles real-time transcription events."""
    def __init__(self, output_stream):
        super().__init__(output_stream)
        self.last_word_spoken_time = None  # Timestamp when last word was spoken
        self.last_word_written_time = None  # Timestamp when last word is displayed

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """Handles transcript events and calculates transcription delay."""
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                words = result.alternatives[0].transcript.split()
                if words:
                    self.last_word_spoken_time = time.time()  # Timestamp when last spoken word is detected
            else:
                self.last_word_written_time = time.time()  # Timestamp when final transcript is displayed
                
                transcript = result.alternatives[0].transcript
                print(f"Recognized: {transcript}")

                # Log timestamps
                if self.last_word_spoken_time:
                    print(f"Last word spoken timestamp: {self.last_word_spoken_time:.3f} seconds")
                    print(f"Last word written timestamp: {self.last_word_written_time:.3f} seconds")

                    # Calculate transcription delay
                    delay = self.last_word_written_time - self.last_word_spoken_time
                    print(f"Transcription delay: {delay:.3f} seconds\n")

                self.last_word_spoken_time = None  # Reset timing for next phrase

async def main():
    """Handles the streaming transcription from microphone to AWS Transcribe."""
    try:
        client = TranscribeStreamingClient(region=AWS_REGION)
        stream = await client.start_stream_transcription(
            language_code="de-CH",
            media_sample_rate_hz=RATE,
            media_encoding="pcm",
        )

        async def write_chunks(stream):
            """Reads microphone input and sends it to AWS Transcribe."""
            with MicrophoneStream(RATE, CHUNK) as mic_stream:
                audio_generator = mic_stream.generator()
                for audio_chunk in audio_generator:
                    await stream.input_stream.send_audio_event(audio_chunk)
                await stream.input_stream.end_stream()

        handler = MyEventHandler(stream.output_stream)
        await asyncio.gather(write_chunks(stream), handler.handle_events())

    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())
