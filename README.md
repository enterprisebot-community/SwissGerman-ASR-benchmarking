## **SwissGerman-ASR-Benchmarking**
**Comparing Speech-to-Text Model Performances on Swiss German Speech**


## Overview

This project benchmarks multiple Speech-to-Text systems on Swiss German speech data. It evaluates Google Speech-to-Text, Amazon Transcribe, Microsoft Azure Speech, and OpenAI Whisper on metrics like WER (Word Error Rate), MER (Match Error Rate), Real-Time Factor (RTF), and processing speed. Another evaluation was done with the mentioned models, using live Swiss German as input audio and transcribing in real-time. The evaluations measure transcription delay, identifying which model processes speech the fastest.

This is particularly important for voice-based AI assistants and customer service voice bots, where low-latency transcription is crucial for providing natural, real-time interactions.

The benchmarking process includes:
- Each model transcribing Swiss German speech data.
- Extracting, cleaning, and normalizing the transcriptions.
- Computing performance metrics.
- Analyzing speaker demographics 
- real-time transcription performance.

---

## Project Structure

```
SwissGerman-ASR-Benchmarking/
│── README.md                      # Project overview & setup
│── requirements/                   
│   ├── requirements.txt            # Dependencies
│── .gitignore                      
│── src/                             # Core scripts
│   ├── transcribe/   
│   │   ├── transcribe_google.py      
│   │   ├── transcribe_aws.py
│   │   ├── extract_transcriptions_aws.py             
│   │   ├── transcribe_microsoft.py      
│   │   ├── transcribe_whisper.py        
│   ├── speaker_statistics.py          # Dataset - Speaker demographics analysis
│   ├── add_metrics_to_csv.py          # Compute WER, MER, RTF (jiwer)
│   ├── summarize_metrics.py           # Summarize results from csv file
│   ├── realtime/   
│   │   ├── realtime_google.py         
│   │   ├── realtime_aws.py          
│   │   ├── realtime_microsoft.py      
│   │   ├── realtime_whisper.py        
│── data/                              
│   ├── analysis/                        
│   │   ├── speaker_statistics.txt 
│   ├── audio/     
│   │   ├── wav_audio_durations.csv     
│   ├── transcripts/                 
│   │   ├── sds_200_50h.tsv                      
│── results/                            # Benchmark results
│   ├── metrics/ 
│   │   ├── aws_results.py         
│   │   ├── google_results.py           
│   │   ├── microsoft_results.py       
│   │   ├── whisper_results.py     
│   ├── transcriptions/    
│   │   ├── aws_added_metrics.csv   
│   │   ├── aws_transcriptions.csv     
│   │   ├── google_added_metrics.csv   
│   │   ├── google_transcriptions.csv  
│   │   ├── microsoft_added_metrics.csv   
│   │   ├── microsoft_transcriptions.csv  
│   │   ├── whisper_added_metrics.csv   
│   │   ├── whisper_transcriptions.csv    
```

---

## Installation

### 1️) **Clone the Repository**
```bash
git clone https://github.com/your-repo-url/SwissGerman-ASR-Benchmarking.git
cd SwissGerman-ASR-Benchmarking
```

### 2️) **Set Up Virtual Environment**
It is recommended to use Python **3.11** or **3.10**, but Python **3.13** should also work.
```bash
python -m venv myenv
source myenv/bin/activate   # macOS/Linux
myenv\Scripts\activate      # Windows
```

### 3️) **Install Dependencies**
```bash
pip install -r requirements/requirements.txt
```

### 4️) **API Key Configuration**
Some model providers require authentication. **Create a `.env` file** and add the following:
```bash
AWS_ACCESS_KEY_ID=<your_aws_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret>
AZURE_SPEECH_KEY=<your_azure_key>
GOOGLE_APPLICATION_CREDENTIALS=<path-to-your-google-json>
OPENAI_API_KEY=<your_openai_key>
```
For **Google**, place the JSON file in a safe location and set:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-google-key.json"
```



## Usage

### **1️) Running ASR Transcriptions**
Run each model transcription script separately:

```bash
python src/transcriptions/transcribe_google.py
python src/transcriptions/transcribe_aws.py
python src/transcriptions/transcribe_microsoft.py
python src/transcriptions/transcribe_whisper.py
```
**Inputs:** Swiss German `.wav` files  
**Outputs:** Transcribed text stored in `results/transcriptions/`



### **2️) Extract AWS Transcriptions**
Since AWS transcriptions are stored in JSON, extract them using:
```bash
python src/extract_transcriptions_aws.py
```
**Outputs:** `AWS_transcriptions.csv`




### **3) Compute Metrics (WER, MER, RTF)**
Calculate word error rate and processing speed:
```bash
python src/add_metrics_to_csv.py
```
**Outputs:**  
- Google: `google_added_metrics.csv`  
- AWS: `aws_added_metrics.csv`  
- Microsoft: `microsoft_added_metrics.csv`  
- Whisper: `whisper_added_metrics.csv`



### **4) Summarize Benchmarking Results**
```bash
python src/summarize_metrics.py
```
**Output:**  
`results/metrics/google_results.csv` (Same for AWS, Microsoft, Whisper)



### **5) Speaker Demographics Analysis**
```bash
python src/speaker_statistics.py
```
**Outputs:** Speaker-based audio duration per **canton, age group, gender**.



### **6) Real-Time ASR Performance**
Test real-time ASR performance with microphone:
```bash
python src/realtime/real_time_google.py
python src/realtime/real_time_aws.py
python src/realtime/real_time_microsoft.py
python src/realtime/real_time_whisper.py
```



## Results & Analysis

All benchmarking results are stored in the **results/** directory.



## Customization

- **Modify File Paths:** Update `INPUT_FOLDER` and `OUTPUT_CSV` variables inside scripts.
- **Change ASR Providers:** Modify API keys and authentication methods in `.env`.
- **Adjust Metrics Computation:** Modify `add_metrics_to_csv.py` for different **WER normalization** settings.


## References

- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text?hl=en#transcribe-audio)
- [AWS Transcribe](https://aws.amazon.com/transcribe/)
- [Microsoft Azure Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text)
- [OpenAI Whisper](https://openai.com/research/whisper)
