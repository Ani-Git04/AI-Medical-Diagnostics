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

---

**Remember**: This system is for educational purposes only. Always consult qualified healthcare professionals for medical diagnosis and treatment.

