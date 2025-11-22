# AI Medical Diagnostics System

A multi-agent AI system for comprehensive medical case analysis using specialized AI agents. This system uses three specialist agents (Cardiologist, Psychologist, and Pulmonologist) that work in parallel to analyze medical reports, followed by a multidisciplinary team that synthesizes the findings into a final diagnosis.

## ⚠️ Disclaimer

**This system is for research and educational purposes only. It is NOT intended for clinical use or medical decision-making. Always consult qualified healthcare professionals for actual medical diagnosis and treatment.**

## Features

- **Multi-Agent Architecture**: Three specialized AI agents analyze medical reports from different perspectives
- **Parallel Processing**: Agents run concurrently for faster analysis
- **Multiple LLM Support**: Works with Hugging Face (free), OpenAI, and Ollama
- **Web Interface**: Beautiful Streamlit-based web application
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Configurable**: Easy configuration through environment variables

## Architecture

The system consists of:

1. **Cardiologist Agent**: Analyzes cardiac workups, ECGs, blood tests, Holter monitor results, and echocardiograms
2. **Psychologist Agent**: Evaluates mental health issues such as anxiety, depression, and trauma
3. **Pulmonologist Agent**: Assesses respiratory issues like asthma, COPD, and lung infections
4. **Multidisciplinary Team**: Synthesizes all reports into a final diagnosis with 3 possible health issues

## Project Structure

```
Agent/
├── app.py                    # Streamlit web application
├── Main.py                   # Command-line script
├── config.py                 # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
├── Utils/
│   ├── __init__.py          # Package initialization
│   ├── Agents.py            # Agent classes
│   ├── constants.py         # Constants and configuration
│   └── logger.py            # Logging configuration
├── Medical Reports/          # Sample medical case reports
├── results/                 # Generated diagnosis reports
└── logs/                    # Application logs
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # For Hugging Face (FREE - Recommended)
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
   
   # OR for OpenAI (Paid)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Get API Keys**:
   
   **Hugging Face (Free)**:
   - Go to https://huggingface.co/settings/tokens
   - Click "New token"
   - Give it a name (e.g., "medical-app")
   - Select "Read" permission
   - Copy the token to your `.env` file
   
   **OpenAI (Paid)**:
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy it to your `.env` file

## Usage

### Web Interface (Recommended)

Run the Streamlit web application:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

**Features**:
- Upload or paste medical reports
- Real-time progress tracking
- View individual specialist reports
- Download full reports or final diagnosis
- Sample reports for testing

### Command Line

Run the analysis from command line:

```bash
python Main.py
```

The script will:
1. Look for medical reports in the `Medical Reports/` directory
2. Process the first available report
3. Save the final diagnosis to `results/final_diagnosis.txt`

**Custom Report**:
To analyze a specific report, modify `Main.py` to specify the report path:

```python
medical_report = load_medical_report("your-report.txt")
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
# LLM Provider (choose one)
HUGGINGFACEHUB_API_TOKEN=your_token_here
# OR
OPENAI_API_KEY=your_key_here

# Optional: Custom model settings
# HF_MODEL=meta-llama/Llama-3.2-3B-Instruct
# OPENAI_MODEL=gpt-4-turbo
```

### Model Options

**Hugging Face Models** (Free):
- `meta-llama/Llama-3.2-3B-Instruct` (default)

**OpenAI Models** (Paid):
- `gpt-3.5-turbo` (cheapest, fastest)
- `gpt-4o-mini` (balanced)
- `gpt-4o` (most capable)
- `gpt-4-turbo-preview` (latest)

## Medical Report Format

A good medical report should include:

- **Patient Information**: Age, gender, patient ID
- **Chief Complaint**: Main symptoms and concerns
- **Medical History**: Past conditions, medications, family history
- **Vital Signs**: Blood pressure, heart rate, temperature, etc.
- **Test Results**: Lab work, imaging, diagnostic tests
- **Physical Examination**: Doctor's observations and findings

See the `Medical Reports/` directory for sample reports.

## Logging

The system generates detailed logs in the `logs/` directory:

- Log files are named: `medical_diagnostics_YYYYMMDD.log`
- Logs include: agent execution, errors, warnings, and info messages
- Useful for debugging and monitoring system performance

## Output

### Results Directory

All generated diagnoses are saved to `results/`:
- `final_diagnosis.txt`: Final diagnosis and recommendations

### Report Format

The final diagnosis includes:
1. Individual specialist consultations (Cardiologist, Psychologist, Pulmonologist)
2. Final diagnosis with 3 possible health issues
3. Reasoning for each identified issue
4. Recommended next steps

## Troubleshooting

### Common Issues

1. **"No API keys found"**
   - Ensure your `.env` file exists and contains valid API keys
   - Check that the keys are correctly named (no typos)

2. **"Medical report not found"**
   - Ensure medical reports are in the `Medical Reports/` directory
   - Check file extensions (.txt)

3. **"ERROR: Invalid API key"**
   - Verify your API key is correct
   - For Hugging Face: Check token permissions
   - For OpenAI: Verify account has credits

4. **Rate Limit Errors**
   - Wait a few minutes and try again
   - Consider using a different model or provider

5. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

## Development

### Adding New Agents

To add a new specialist agent:

1. Create a new class in `Utils/Agents.py`:
   ```python
   class Neurologist(Agent):
       def __init__(self, medical_report, ...):
           super().__init__(medical_report, "Neurologist", ...)
   ```

2. Add the role to `Utils/constants.py`:
   ```python
   AGENT_ROLES['NEUROLOGIST'] = 'Neurologist'
   ```

3. Update the prompt template in `Agent.create_prompt_template()`

4. Add to agent initialization in `Main.py` and `app.py`

### Code Structure

- **Utils/Agents.py**: Core agent classes and logic
- **Utils/constants.py**: All constants and configuration values
- **Utils/logger.py**: Logging setup and configuration
- **config.py**: Environment and configuration management
- **app.py**: Streamlit web interface
- **Main.py**: Command-line interface

## Dependencies

- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration
- `langchain-ollama`: Ollama integration
- `huggingface_hub`: Hugging Face API
- `streamlit`: Web interface
- `python-dotenv`: Environment variable management

See `requirements.txt` for complete list.

## Contributing

This is an educational project. Suggestions and improvements are welcome!

## License

This project is for educational purposes only.

## Version

Current version: 2.0

## Deployment

### Deploy to Render (Free)

See `DEPLOYMENT.md` for detailed instructions or `RENDER_QUICKSTART.md` for a quick start guide.

**Quick steps:**
1. Push code to GitHub
2. Connect to Render
3. Add API keys as environment variables
4. Deploy!

### Deploy to Streamlit Cloud (Alternative)

1. Go to https://streamlit.io/cloud
2. Connect GitHub repository
3. Set main file: `app.py`
4. Add secrets (API keys)
5. Deploy!

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review the troubleshooting section
3. Ensure all dependencies are installed correctly
4. See `DEPLOYMENT.md` for deployment help

---

**Remember**: This system is for educational purposes only. Always consult qualified healthcare professionals for medical diagnosis and treatment.

