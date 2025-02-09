import os
import pandas as pd

"""
Transcription file (tsv) - Statistics Analysis
Input:
- TSV file containing transcription metadata (`transcr_file_path`).
- CSV file containing audio durations (`audio_duration_path`).

Output:
- Computes total audio duration per `canton`, `age group`, and `gender`.
- Calculates duration percentages within each category.
- Saves a formatted summary to a text file.
"""

# Set file paths (Modify as needed)
TRANSCRIPTION_FILE = "data/transcriptions/sds_200_50h.tsv"
AUDIO_DURATION_FILE = "data/audio/wav_audio_durations.csv"
OUTPUT_FILE = "statistics_summary.txt"  # change accordingly

# Check if files exist before proceeding
if not os.path.exists(TRANSCRIPTION_FILE):
    print(f"Error: Transcription file '{TRANSCRIPTION_FILE}' not found.")
    exit(1)
if not os.path.exists(AUDIO_DURATION_FILE):
    print(f"Error: Audio duration file '{AUDIO_DURATION_FILE}' not found.")
    exit(1)

# Load transcription data
df_trans = pd.read_csv(TRANSCRIPTION_FILE, delimiter="\t")

# Load audio duration data
df_audio = pd.read_csv(AUDIO_DURATION_FILE, delimiter=",", skipinitialspace=True)

# Extract only the filename from `clip_path`, ignoring the extension
df_trans["FileID"] = df_trans["clip_path"].apply(lambda x: x.split("/")[-1].split(".")[0])

# Ensure `FileID` is correctly formatted in df_audio (ignoring extensions)
df_audio.columns = ["FileID", "Audio Duration"]  # Set correct column names
df_audio["FileID"] = df_audio["FileID"].apply(lambda x: x.split(".")[0])  # Remove file extensions

# Merge transcription and audio duration data
df_merged = df_trans.merge(df_audio, on="FileID", how="left")

# Validate required columns exist
required_columns = {"canton", "age", "gender", "Audio Duration"}
missing_columns = required_columns - set(df_merged.columns)
if missing_columns:
    print(f"Error: Missing required columns: {missing_columns}")
    exit(1)

# Debug: Print unique age groups to verify they exist
print("\nDEBUG: Unique Age Categories Found:\n", df_merged["age"].unique())

# Compute total audio duration per category (Convert to minutes)
canton_durations = (df_merged.groupby("canton")["Audio Duration"].sum() / 60).round(2).sort_values(ascending=False)
age_durations = (df_merged.groupby("age")["Audio Duration"].sum() / 60).round(2).fillna(0)  # Handle NaN values
gender_durations = (df_merged.groupby("gender")["Audio Duration"].sum() / 60).round(2).sort_values(ascending=False)

# Compute percentages
total_duration = canton_durations.sum()
canton_percentages = ((canton_durations / total_duration) * 100).round(2).fillna(0)

total_age_duration = age_durations.sum()
age_percentages = ((age_durations / total_age_duration) * 100).round(2).fillna(0)

total_gender_duration = gender_durations.sum()
gender_percentages = ((gender_durations / total_gender_duration) * 100).round(2).fillna(0)

# Prepare text output
output_text = "Data Transcription Statistics:\n\n"

output_text += "Total Audio Duration per Canton (minutes) with Percentages:\n"
output_text += (canton_durations.astype(str) + " min (" + canton_percentages.astype(str) + "%)").to_string() + "\n\n"

output_text += "Total Audio Duration per Age Group (minutes) with Percentages:\n"
output_text += (age_durations.astype(str) + " min (" + age_percentages.astype(str) + "%)").to_string() + "\n\n"

output_text += "Total Audio Duration per Gender (minutes) with Percentages:\n"
output_text += (gender_durations.astype(str) + " min (" + gender_percentages.astype(str) + "%)").to_string() + "\n\n"

# Save to text file
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(output_text)

print(f"Statistics saved to {OUTPUT_FILE}")