import boto3
import time
import os
from dotenv import load_dotenv

"""
AWS Transcription Automation Script

Input:
- Audio files (`.wav`) stored in an AWS S3 bucket.
- AWS credentials and bucket names set in `.env` file.

Output: -> json files in S3 bucket
- Starts an AWS Transcribe job for each `.wav` file.
- Transcription results are stored in the specified output S3 bucket.
"""

# Load environment variables from .env file
load_dotenv()

# AWS Configuration (Use environment variables for security)
REGION = os.getenv("AWS_REGION", "your-region")
BUCKET_NAME = os.getenv("AWS_INPUT_BUCKET", "your-input-bucket-name")
OUTPUT_BUCKET = os.getenv("AWS_OUTPUT_BUCKET", "your-output-bucket-name")

# Initialize AWS clients
s3 = boto3.client("s3", region_name=REGION)
transcribe = boto3.client("transcribe", region_name=REGION)

def list_audio_files(bucket_name):
    """Retrieve a list of all .wav audio files in the specified S3 bucket.
    Args:
        bucket_name (str): The name of the S3 bucket.
    Returns:
        list: A list of .wav file names.
    """
    files = []
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)

        while True:
            if "Contents" in response:
                files.extend(obj["Key"] for obj in response["Contents"] if obj["Key"].lower().endswith(".wav"))

            if response.get("IsTruncated"):  # Handle pagination if needed
                response = s3.list_objects_v2(
                    Bucket=bucket_name, ContinuationToken=response["NextContinuationToken"]
                )
            else:
                break

    except Exception as e:
        print(f"Error accessing S3 bucket '{bucket_name}': {e}")
        return []

    if not files:
        print(f"No audio files found in bucket '{bucket_name}'.")
    return files

def start_transcription_job(file_key):
    """Start an AWS Transcribe job for a given audio file.
    Args:
        file_key (str): The S3 key (file path) of the audio file.
    Returns:
        bool: True if the job started successfully, False otherwise.
    """
    job_name = file_key.replace(".", "-")  # Ensure unique job name
    media_uri = f"s3://{BUCKET_NAME}/{file_key}"

    while True:  # Keep retrying until successful
        try:
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": media_uri},
                MediaFormat="wav",
                LanguageCode="de-CH",
                OutputBucketName=OUTPUT_BUCKET,
            )
            print(f"Started transcription job for: {file_key}")
            return True
        except transcribe.exceptions.LimitExceededException:
            print(f"⚠️ Too many jobs running. Retrying in 60 seconds...")
            time.sleep(60)  # Wait and retry
        except Exception as e:
            print(f"Error starting transcription job for {file_key}: {e}")
            return False

def process_files():
    """Fetch audio files from S3 and process each for transcription."""
    files = list_audio_files(BUCKET_NAME)

    if not files:
        print("No new files to process.")
        return

    print(f"Found {len(files)} audio files to process.")

    for file_key in files:
        start_transcription_job(file_key)

if __name__ == "__main__":
    process_files()