import os
import pandas as pd

"""
Model Performance Metrics Calculation

Input:
- CSV file containing ASR evaluation metrics (`WER`, `MER`, `RTF`, etc.).
Output:
- Computes total transcription time and audio duration.
- Calculates averages for WER, MER, and RTF.
- Determines real-time factor and transcription speed.
- Saves structured evaluation results to a text file.
"""

# Set file paths (Modify as needed)
INPUT_CSV = "Results.csv" # output csv file from add_metrics_to_csv.py
OUTPUT_FILE = "Results_Metrics.txt"

# Ensure the results file exists
if not os.path.exists(INPUT_CSV):
    print(f"Error: The input CSV file '{INPUT_CSV}' does not exist.")
    exit(1)

# Load ASR results
asr_results = pd.read_csv(INPUT_CSV)

# Ensure necessary columns exist
required_columns = {"WER", "MER", "RTF", "Cost (CHF)", "Audio Duration (s)", "Time"}
missing_columns = required_columns - set(asr_results.columns)
if missing_columns:
    print(f"Error: Missing required columns: {missing_columns}")
    exit(1)

# Sum transcription times
time_trans = asr_results["Time"].sum()
time_trans_hours = time_trans / 3600

# Sum total audio duration
time_audio = asr_results["Audio Duration (s)"].sum()
time_audio_hours = time_audio / 3600

# Calculate average WER, MER, and RTF
average_wer = asr_results["WER"].mean()
average_mer = asr_results["MER"].mean()
average_rtf = asr_results["RTF"].mean()

# Compute total RTF (Real-Time Factor)
total_rtf = time_trans / time_audio if time_audio else 0

# Calculate transcription speed (hours of audio processed per hour)
transcription_speed = 1 / total_rtf if total_rtf else 0

# Format and save results
output_text = (
    "Performance Metrics:\n\n"
    f"Total Transcription Time: {time_trans_hours:.2f} hours\n"
    f"Total Audio Time: {time_audio_hours:.2f} hours\n\n"
    f"Average WER: {average_wer:.2%}\n"
    f"Average MER: {average_mer:.2%}\n"
    f"Average RTF: {average_rtf:.2%}\n\n"
    f"Total RTF: {total_rtf:.2%}\n"
    f"Hours Processed per Hour: {transcription_speed:.2f}\n"
)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(output_text)

print(f"Metrics saved to {OUTPUT_FILE}")