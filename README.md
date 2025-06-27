# TeRed_DataReduction
Data reduction framework

python 3.10.13

# TeRed_DataReduction - Data Reduction Framework

![Python Version](https://img.shields.io/badge/python-3.10.13-blue.svg)

A framework for log reduction via policy template matching. This project learns policy behavior templates from normal behavior logs and uses them for subgraph matching and reduction of attack logs, resulting in more concise provenance graphs.

## 🌟 Features

- Automatically extracts common behavior templates from normal behavior logs
- reduces attack behavior logs using learned templates
- Outputs template data and reduced logs for subsequent analysis

## 📂 Project Structure
.\
├── main.py # Main program entry\
├── settings.py # Configuration file\
├── template_file/ # Output directory for learned templates\
├── test_data/ # Directory for raw log data (normal & attack behaviors)\
└── reduced_output/ # Directory for reduced logs


## ⚙️ Configuration (`settings.py`)

Before running the project, modify the following settings in `settings.py`:

```python
# Normal behavior data filename (located in test_data/)
DATA_TO_LEARN = "cve-2016-4971-small"  

# Attack log to be reduced (with full path)
DATA_TO_REDUCE = "test_data/cve-2016-4971-attack/cve-2016-4971-attack.json"

TEMPLATE_DIR = "template_file"          # Template output directory
DATA_DIR = "test_data/"                 # Raw data directory
REDUCED_FOLDER = "reduced_output/"      # reduced results 
```
## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.10.13

### 🛠 Installation

1.Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-folder>

```

2.(Optional) Install dependencies:
   ```bash
pip install -r requirements.txt

```
3.Run the program:
   ```bash
python main.py

```
### 🔍 Anomaly Detection with DeepLog

We provide an example for performing anomaly detection based on the **compressed logs** using the [DeepLog](https://github.com/wuyifan18/DeepLog) method.

#### 📘 Usage

1. Change directory:
   ```bash
   cd deeplog
   ```
2. Configure the input:
Edit the source_folder variable in the script to point to the directory containing your compressed logs.

3. Run the detection:
   ```bash
   python main.py
   ```
4. Check the results:
Detection outputs will be saved in the output/predict_result.log.

### 🔍 Anomaly Detection with ProvDetector

We provide an example for performing anomaly detection based on the **compressed logs** using the [ProvDetector] method.

#### 📘 Usage

1. Change directory:
   ```bash
   cd provdetector
   ```
2. Make input data:
Use paser.py to make .json files to .log files
2. Configure the input:
Edit the source_folder variable in the provdetector.py to point to the .log files' directory.

3. Run the detection:
   ```bash
   python provdetector.py
   ```
4. Check the results