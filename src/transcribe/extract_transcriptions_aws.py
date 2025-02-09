import os
import json
import csv

"""
AWS Transcription JSON to CSV Converter

Input:
- JSON files containing transcription results (stored in a folder).
- Each JSON file includes job details, timestamps, and transcriptions.

Output:
- Extracted transcription data is saved into a structured CSV file.
- Columns: `JobName`, `Time (Start-End)`, `Transcript`.
"""

# Set input and output paths (Modify as needed)
INPUT_FOLDER = "AWS_json_files"  # Folder containing JSON files
OUTPUT_CSV = "AWS_transcriptions.csv"  # Output CSV file

def extract_json_details(json_file):
    """Extract transcription details from a single JSON file.

    Args:
        json_file (str): Path to the JSON file.

    Returns:
        tuple: (job_name, time_range, transcript_text) or (None, None, None) if an error occurs.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract job name (unique file name)
        job_name = data.get("jobName", "Unknown")

        # Extract time range
        audio_segments = data.get("results", {}).get("audio_segments", [])
        if audio_segments:
            start_time = float(audio_segments[0].get("start_time", 0))
            end_time = float(audio_segments[-1].get("end_time", 0))
            time_range = f"{start_time}-{end_time}"
        else:
            time_range = None

        # Extract transcription text
        transcripts = data.get("results", {}).get("transcripts", [])
        transcript_text = transcripts[0]["transcript"] if transcripts else ""

        return job_name, time_range, transcript_text

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error processing {json_file}: {e}")
        return None, None, None

def process_json_files(input_folder, output_csv):
    """Process all JSON files in the folder and save the extracted data to a CSV file.

    Args:
        input_folder (str): Directory containing JSON files.
        output_csv (str): Path to the output CSV file.
    """
    files_processed = 0

    # Ensure the output directory exists (if applicable)
    if os.path.dirname(output_csv):  # Only create a directory if one exists in the path
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["JobName", "Time (Start-End)", "Transcript"])  # Write header row

        # Process each JSON file
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".json"):  # Only process JSON files
                json_file_path = os.path.join(input_folder, file_name)
                job_name, time_range, transcript = extract_json_details(json_file_path)

                if job_name:  # Only write valid data
                    writer.writerow([job_name, time_range, transcript])
                    files_processed += 1

    print(f"Successfully processed {files_processed} files. Data saved to {output_csv}")

if __name__ == "__main__":
    process_json_files(INPUT_FOLDER, OUTPUT_CSV)
