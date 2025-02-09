import os
import time
import csv
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason

"""
Azure Speech-to-Text Transcription Script

Input:
- WAV audio files stored in a local folder.
- Azure Speech Service credentials set via environment variables.
Output:
- Transcriptions are saved into a structured CSV file.
- Columns: `File Name`, `Time`, `Transcription`.
"""

# Load Azure credentials from environment variables
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SERVICE_REGION = os.getenv("AZURE_REGION")

if not SPEECH_KEY or not SERVICE_REGION:
    print("Error: Azure Speech API credentials not set. Please set AZURE_SPEECH_KEY and AZURE_REGION.")
    exit(1)  # Exit if credentials are missing

# Set file paths (Modify as needed)
AUDIO_FOLDER = "data/wav_audio_files" # change path accordingly
OUTPUT_CSV = "MS_transcription_results.csv"

def transcribe_audio(file_path):
    """Transcribes a single audio file using Azure Speech-to-Text.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        tuple: (File Name, Time, Transcription Text or Error Message)
    """
    try:
        # Create a speech configuration
        speech_config = SpeechConfig(subscription=SPEECH_KEY, region=SERVICE_REGION)
        speech_config.speech_recognition_language = "de-CH"

        # Configure the audio file
        audio_input = AudioConfig(filename=file_path)
        recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        # Start transcription timing
        start_time = time.time()
        result = recognizer.recognize_once()
        end_time = time.time()

        transcription_time = round(end_time - start_time, 2)

        if result.reason == ResultReason.RecognizedSpeech:
            return os.path.basename(file_path), transcription_time, result.text
        elif result.reason == ResultReason.NoMatch:
            return os.path.basename(file_path), transcription_time, "No speech recognized"
        elif result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Transcription canceled: {cancellation_details.reason}"
            if cancellation_details.reason == "Error":
                error_message += f" | Details: {cancellation_details.error_details}" # debugging error message
            return os.path.basename(file_path), transcription_time, error_message

    except Exception as e:
        return os.path.basename(file_path), 0, f"Error: {str(e)}"

def transcribe_audio_with_retry(file_path, retries=3):
    """Retries audio transcription up to a specified number of times in case of errors.
    Args:
        file_path (str): Path to the audio file.
        retries (int, optional): Maximum retry attempts. Defaults to 3.
    Returns:
        tuple: (File Name, Transcription Time (s), Transcription Text or Error Message)
    """
    for attempt in range(retries):
        try:
            return transcribe_audio(file_path)
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {file_path}: {e}")
            time.sleep(5)  # Wait before retrying

    return os.path.basename(file_path), 0, "Error: Max retries exceeded"

def main():
    """Processes all WAV files in the specified folder and saves transcriptions to a CSV file."""
    if not os.path.exists(AUDIO_FOLDER):
        print(f"Error: The audio folder '{AUDIO_FOLDER}' does not exist.")
        return

    # Get all audio files
    files = [os.path.join(AUDIO_FOLDER, file) for file in os.listdir(AUDIO_FOLDER) if file.endswith(".wav")]

    if not files:
        print(f"No WAV files found in '{AUDIO_FOLDER}'. Exiting.")
        return

    print(f"Found {len(files)} audio files for transcription.")

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["File Name", "Time", "Transcription"])  # Write CSV header

        for idx, file_path in enumerate(files):
            print(f"Processing file {idx + 1}/{len(files)}: {os.path.basename(file_path)}") # take out - prints every processing file
            result = transcribe_audio_with_retry(file_path)
            writer.writerow(result)
            time.sleep(0.5)  # Optional throttling to avoid rate limiting

    print(f"Transcriptions completed. Results saved to {OUTPUT_CSV}.")

if __name__ == "__main__":
    main()
