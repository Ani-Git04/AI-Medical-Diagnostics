"""
Constants and configuration values for the Medical Diagnostics System.
"""

# Default model configurations
DEFAULT_HF_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OPENAI_MODEL = "gpt-4-turbo"

# Model parameters
HF_MAX_TOKENS = 600
HF_TEMPERATURE = 0.7
OPENAI_TEMPERATURE = 0

# File paths
MEDICAL_REPORTS_DIR = "Medical Reports"
RESULTS_DIR = "results"
DEFAULT_OUTPUT_FILE = "final_diagnosis.txt"

# Validation constants
MIN_REPORT_LENGTH = 100
MIN_REPORT_LENGTH_WARNING = 50

# Medical keywords for validation
MEDICAL_KEYWORDS = [
    'patient', 'medical', 'diagnosis', 'symptoms', 'treatment', 'health',
    'hospital', 'doctor', 'condition', 'disease', 'exam', 'test', 'report',
    'clinical', 'history', 'age', 'complaint', 'vital'
]

# Agent roles
AGENT_ROLES = {
    'CARDIOLOGIST': 'Cardiologist',
    'PSYCHOLOGIST': 'Psychologist',
    'PULMONOLOGIST': 'Pulmonologist',
    'MULTIDISCIPLINARY_TEAM': 'MultidisciplinaryTeam'
}

# OpenAI model options
OPENAI_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo-preview"
]

# Repetition detection
MAX_REPETITION_COUNT = 2
MAX_CONTENT_LENGTH = 2000
REPETITION_PATTERN = "However, given"

