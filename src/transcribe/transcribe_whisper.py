import os
import time
import csv
import openai
from pydub.utils import mediainfo

"""
OpenAI Whisper Speech-to-Text Transcription Script

Input:
- WAV audio files stored in a local folder.
- OpenAI API key set via environment variable.
Output:
- Transcriptions are saved into a structured CSV file.
- Columns: `FileID`, `Time`, `Transcript`.
"""

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OpenAI API key not set. Please set OPENAI_API_KEY.")
    exit(1)  # Exit if API key is missing

openai.api_key = OPENAI_API_KEY

def get_audio_duration(file_path):
    """Get the duration of the audio file in seconds using pydub.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        float: Duration of the audio file in seconds.
    """
    try:
        info = mediainfo(file_path)
        return float(info['duration'])
    except Exception as e:
        print(f"Error reading audio file {file_path}: {e}")
        return 0  # Return 0 duration in case of an error

def transcribe_audio(file_path):
    """Transcribe a given WAV audio file using OpenAI Whisper API.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        tuple: (transcript text, processing time)
    """
    start_time = time.time()
    try:
        with open(file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file, language="de")  # Using 'de' as 'de-CH' is unsupported
        
        if "text" not in response:
            raise ValueError("No 'text' key found in OpenAI response.")

        transcript = response.get("text", "").strip()
    except Exception as e:
        print(f"Error transcribing {file_path}: {e}")
        transcript = "Error: Transcription failed"

    end_time = time.time()
    return transcript, round(end_time - start_time, 2)

def process_audio_files(input_dir, output_csv):
    """Process all WAV files in the input directory and save results to a CSV file.
    Args:
        input_dir (str): Path to the directory containing WAV files.
        output_csv (str): Path to save the CSV transcription results.
    """
    if not os.path.exists(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist.")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(".wav")]

    if not files:
        print(f"No WAV files found in '{input_dir}'. Exiting.")
        return

    print(f"Found {len(files)} audio files for transcription.")

    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["FileID", "Time", "Transcript"])  # Write CSV header

        for file_name in files:
            file_path = os.path.join(input_dir, file_name)

            # Check audio duration
            duration = get_audio_duration(file_path)
            if duration < 0.1: # specifically fro Whisper as it does not process files < 1 seconds
                print(f"Skipping: {file_name} (too short, {duration:.2f} secs)")
                continue

            transcript, time_taken = transcribe_audio(file_path)
            writer.writerow([file_name, time_taken, transcript])

    print(f"Transcription completed. Results saved to {output_csv}.")

# Example usage (Modify these paths as needed)
AUDIO_FOLDER = "data/wav_audio_files"
OUTPUT_CSV = "Whisper_transcripts_de.csv"

if __name__ == "__main__":
    process_audio_files(AUDIO_FOLDER, OUTPUT_CSV)
