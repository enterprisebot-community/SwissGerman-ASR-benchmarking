import os
import time
import azure.cognitiveservices.speech as speechsdk

"""
Azure Speech-to-Text Live Transcription with Timestamp Logging

Input:
- Audio stream from the microphone.
- Azure Speech-to-Text API for real-time transcription.
Output:
- Prints real-time transcriptions.
- Logs timestamps and calculates transcription delay.
"""

# Load Azure credentials from environment variables
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")  # Default to 'northeurope' if not set

if not AZURE_SPEECH_KEY:
    print("Error: Azure Speech API key not set. Please set AZURE_SPEECH_KEY.")
    exit(1)

def transcribe_from_microphone():
    """Performs live transcription from microphone using Azure Speech SDK."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    speech_config.speech_recognition_language = "de-CH"  # Swiss German

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    last_word_spoken_time = None  # Timestamp of last spoken word
    last_word_written_time = None  # Timestamp when transcription appears

    def recognizing_callback(evt):
        """Handles detecting speech and logs when the last word was spoken."""
        nonlocal last_word_spoken_time
        last_word_spoken_time = time.time()  # Timestamp when speech is detected

    def recognized_callback(evt):
        """Handles recognized speech and logs timestamps and transcription delay."""
        nonlocal last_word_spoken_time, last_word_written_time

        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            last_word_written_time = time.time()  # Timestamp when transcription is finalized
            transcript = evt.result.text

            print(f"Recognized: {transcript}")

            # Log timestamps
            if last_word_spoken_time:
                print(f"Last word spoken timestamp: {last_word_spoken_time:.3f} seconds")
                print(f"Last word written timestamp: {last_word_written_time:.3f} seconds")

                # Calculate transcription delay
                delay = last_word_written_time - last_word_spoken_time
                print(f"Transcription delay: {delay:.3f} seconds\n")

    # Connect callbacks
    speech_recognizer.recognizing.connect(recognizing_callback)
    speech_recognizer.recognized.connect(recognized_callback)

    print("Speak into your microphone.")

    # Start continuous recognition
    speech_recognizer.start_continuous_recognition()

    try:
        while True:
            time.sleep(0.1)  # Keep script running
    except KeyboardInterrupt:
        print("\n Stopping transcription...")
        speech_recognizer.stop_continuous_recognition()

if __name__ == "__main__":
    transcribe_from_microphone()
