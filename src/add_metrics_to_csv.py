import os
import pandas as pd
from jiwer import wer, mer, Compose, ToLowerCase, RemovePunctuation, Strip, RemoveMultipleSpaces

"""
ASR Performance Evaluation (WER & MER)

Input:
- Ground truth transcriptions (TSV file).
- ASR-generated transcriptions (CSV file).
- Audio duration metadata (CSV file).
Output:
- Computes Word Error Rate (WER) and Match Error Rate (MER).
- Calculates Real-Time Factor (RTF) and estimated transcription cost.
- Saves structured evaluation results to a CSV file.
"""

# Set file paths (Modify as needed)
TRANSCRIPTION_FILE = "data/transcriptions/sds_200_50h.tsv"  # Ground truth transcriptions
ASR_RESULTS_FILE = "transcripts.csv"  # ASR transcription results
AUDIO_DURATION_FILE = "data/audio/wav_audio_durations.csv"  # Audio durations
OUTPUT_FILE = "Results.csv"  # Output file with evaluation metrics

# Ensure files exist before proceeding
for file in [TRANSCRIPTION_FILE, ASR_RESULTS_FILE, AUDIO_DURATION_FILE]:
    if not os.path.exists(file):
        print(f"Error: Required file '{file}' not found.")
        exit(1)

# Load transcription ground truth
ground_truth_df = pd.read_csv(TRANSCRIPTION_FILE, sep="\t")
ground_truth_df["FileID"] = ground_truth_df["clip_path"].apply(lambda x: os.path.splitext(os.path.basename(x))[0])

# Load audio durations
audio_duration_df = pd.read_csv(AUDIO_DURATION_FILE)
audio_duration_df["FileID"] = audio_duration_df["File Name"].str.replace(".wav", "", regex=False)

# Define text normalization transformation for WER/MER calculations
text_normalization = Compose([
    ToLowerCase(),       # Convert text to lowercase
    RemovePunctuation(), # Remove punctuation
    Strip(),             # Remove leading/trailing spaces
    RemoveMultipleSpaces() # Normalize spaces
])

def evaluate_asr_transcriptions(asr_csv, ground_truth_df, audio_duration_df, cost_per_second):
    """Evaluates ASR transcriptions against ground truth data.
    Args:
        asr_csv (str): Path to the ASR results CSV.
        ground_truth_df (DataFrame): DataFrame containing ground truth transcriptions.
        audio_duration_df (DataFrame): DataFrame containing audio durations.
        cost_per_second (float): Cost per second of transcription.
    Returns:
        DataFrame: Processed ASR evaluation results.
    """
    # Load ASR results
    asr_df = pd.read_csv(asr_csv)

    # Normalize FileID (remove ".wav" extension)
    asr_df["FileID"] = asr_df["FileID"].str.replace(".wav", "", regex=False)

    # Merge ASR data with audio duration metadata
    asr_df = asr_df.merge(audio_duration_df[["FileID", "Audio Duration (s)"]], on="FileID", how="left")

    print(f"Processing {len(asr_df)} ASR transcriptions...")

    # Add ground truth transcription by matching FileID
    asr_df["GroundTruth"] = asr_df["FileID"].map(
        lambda x: ground_truth_df.loc[ground_truth_df["FileID"] == x, "sentence"].values[0]
        if x in ground_truth_df["FileID"].values else None
    )

    # Drop rows with missing GroundTruth, Transcript, or Audio Duration
    asr_df = asr_df.dropna(subset=["GroundTruth", "Transcript", "Audio Duration (s)"])

    # Normalize text for WER/MER calculations
    asr_df["GroundTruth_Norm"] = asr_df["GroundTruth"].apply(lambda x: text_normalization(x))
    asr_df["Transcript_Norm"] = asr_df["Transcript"].apply(lambda x: text_normalization(x))

    # Calculate WER (Word Error Rate)
    asr_df["WER"] = asr_df.apply(
        lambda row: wer(row["GroundTruth_Norm"], row["Transcript_Norm"])
        if pd.notnull(row["GroundTruth_Norm"]) and pd.notnull(row["Transcript_Norm"]) else None,
        axis=1
    )

    # Calculate MER (Match Error Rate)
    asr_df["MER"] = asr_df.apply(
        lambda row: mer(row["GroundTruth_Norm"], row["Transcript_Norm"])
        if pd.notnull(row["GroundTruth_Norm"]) and pd.notnull(row["Transcript_Norm"]) else None,
        axis=1
    )

    # Process transcription times (handle timestamps in "2.08-4.9" format)
    asr_df["Time"] = asr_df["Time"].apply(
        lambda x: float(x.split("-")[1]) - float(x.split("-")[0]) if isinstance(x, str) and "-" in x else float(x)
    )

    # Calculate Real-Time Factor (RTF)
    asr_df["RTF"] = asr_df["Time"] / asr_df["Audio Duration (s)"]

    # Calculate Cost
    asr_df["Cost (CHF)"] = asr_df["Audio Duration (s)"] * cost_per_second

    return asr_df

# Constants for transcription costs (CHF per second)
TRANSCRIPTION_COSTS = {
    "Google": 0.003,
    "Microsoft": 0.0003,
    "AWS": 0.0004,
    "Whisper": 0.0001
}

# Process ASR transcriptions and evaluate performance
asr_results = evaluate_asr_transcriptions(ASR_RESULTS_FILE, ground_truth_df, audio_duration_df, TRANSCRIPTION_COSTS["Google"]) # change Service accordingly 

# Save results to CSV
asr_results.to_csv(OUTPUT_FILE, index=False)
print(f"evaluation results saved to {OUTPUT_FILE}")