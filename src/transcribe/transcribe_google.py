import os
import time
import csv
from google.cloud import speech

"""
Google Cloud Speech-to-Text Transcription Script

Input:
- WAV audio files stored in a local folder.
- Google Cloud credentials JSON file (set via environment variable).

Output:
- Transcriptions are saved into a structured CSV file.
- Columns: `FileID`, `Time`, `Transcript`.
"""

# Ensure the Google Cloud credentials JSON is set
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if GOOGLE_CREDENTIALS_PATH:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH  # Explicitly set it
else:
    print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
    exit(1)  # Exit the script if credentials are missing

def transcribe_all_audio_files(audio_folder_path, output_csv_path):
    """Transcribes all WAV audio files in a folder using Google Speech-to-Text.

    Args:
        audio_folder_path (str): Path to the folder containing WAV files.
        output_csv_path (str): Path to save the transcriptions in CSV format.
    """
    if not os.path.exists(audio_folder_path):
        print(f"Error: The audio folder '{audio_folder_path}' does not exist.") # debug
        return

    client = speech.SpeechClient()

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["FileID", "Time", "Transcript"])  # Write CSV header

        for filename in os.listdir(audio_folder_path):
            if filename.endswith(".wav"):
                file_path = os.path.join(audio_folder_path, filename)
                print(f"Processing: {filename}") # debug

                try:
                    # Read the audio file content
                    with open(file_path, "rb") as audio_file:
                        content = audio_file.read()

                    # Prepare the audio configuration
                    audio = speech.RecognitionAudio(content=content)
                    config = speech.RecognitionConfig(language_code="de-CH")

                    # Start transcription timing
                    start_time = time.time()
                    response = client.recognize(config=config, audio=audio)
                    end_time = time.time()

                    # Calculate transcription time
                    transcription_time = round(end_time - start_time, 2)

                    # Extract the transcript
                    transcript = " ".join(
                        result.alternatives[0].transcript for result in response.results
                    ) if response.results else ""

                    writer.writerow([filename, transcription_time, transcript])

                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    print(f"All transcriptions saved to {output_csv_path}.")

# Modify these paths as needed
AUDIO_FOLDER = "ata/wav_audio_files" # change 
OUTPUT_CSV = "Google_transcription_results.csv" # change

if __name__ == "__main__":
    transcribe_all_audio_files(AUDIO_FOLDER, OUTPUT_CSV)
