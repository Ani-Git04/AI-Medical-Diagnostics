"""
Main script for running medical diagnostics analysis from command line.

This script processes a medical report using specialized AI agents
and generates a final diagnosis report.
"""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from Utils.Agents import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam
from Utils.constants import RESULTS_DIR, DEFAULT_OUTPUT_FILE
from Utils.logger import logger
from config import Config


def load_medical_report(report_path: str) -> str:
    """
    Load a medical report from a file.
    
    Args:
        report_path: Path to the medical report file
        
    Returns:
        Content of the medical report as a string
        
    Raises:
        FileNotFoundError: If the report file doesn't exist
        IOError: If there's an error reading the file
    """
    report_file = Path(report_path)
    
    # If relative path, check in Medical Reports directory
    if not report_file.is_absolute():
        report_file = Config.MEDICAL_REPORTS_DIR / report_path
    
    if not report_file.exists():
        raise FileNotFoundError(f"Medical report not found: {report_file}")
    
    logger.info(f"Loading medical report from: {report_file}")
    with open(report_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if not content.strip():
        raise ValueError("Medical report file is empty")
    
    logger.info(f"Loaded medical report ({len(content)} characters)")
    return content


def get_response(agent_name: str, agent) -> tuple:
    """
    Run an agent and get its response.
    
    Args:
        agent_name: Name of the agent
        agent: Agent instance to run
        
    Returns:
        Tuple of (agent_name, response)
    """
    logger.info(f"Running {agent_name} agent...")
    response = agent.run()
    logger.info(f"{agent_name} agent completed")
    return agent_name, response


def run_analysis(medical_report: str, use_huggingface: bool = False, hf_model: str = None) -> dict:
    """
    Run the complete medical analysis with all agents.
    
    Args:
        medical_report: The medical report to analyze
        use_huggingface: Whether to use Hugging Face models
        hf_model: Hugging Face model identifier
        
    Returns:
        Dictionary containing responses from all agents
    """
    logger.info("Initializing medical diagnostic agents...")
    
    # Initialize agents
    if use_huggingface:
        agents = {
            "Cardiologist": Cardiologist(medical_report, use_huggingface=True, hf_model=hf_model),
            "Psychologist": Psychologist(medical_report, use_huggingface=True, hf_model=hf_model),
            "Pulmonologist": Pulmonologist(medical_report, use_huggingface=True, hf_model=hf_model)
        }
    else:
        agents = {
            "Cardiologist": Cardiologist(medical_report),
            "Psychologist": Psychologist(medical_report),
            "Pulmonologist": Pulmonologist(medical_report)
        }
    
    # Run agents in parallel
    logger.info("Running specialist consultations in parallel...")
    responses = {}
    
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_response, name, agent): name for name, agent in agents.items()}
        
        for future in as_completed(futures):
            try:
                agent_name, response = future.result()
                responses[agent_name] = response
                
                # Check for errors
                if response and "ERROR:" in str(response):
                    logger.error(f"{agent_name} returned an error: {response}")
            except Exception as e:
                agent_name = futures[future]
                error_msg = f"ERROR: Exception in {agent_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                responses[agent_name] = error_msg
    
    return responses


def generate_final_diagnosis(responses: dict, use_huggingface: bool = False, hf_model: str = None) -> str:
    """
    Generate final diagnosis from multidisciplinary team.
    
    Args:
        responses: Dictionary of agent responses
        use_huggingface: Whether to use Hugging Face models
        hf_model: Hugging Face model identifier
        
    Returns:
        Final diagnosis as a string
    """
    logger.info("Generating final diagnosis from multidisciplinary team...")
    
    if use_huggingface:
        team_agent = MultidisciplinaryTeam(
            cardiologist_report=responses.get("Cardiologist", "No report"),
            psychologist_report=responses.get("Psychologist", "No report"),
            pulmonologist_report=responses.get("Pulmonologist", "No report"),
            use_huggingface=True,
            hf_model=hf_model
        )
    else:
        team_agent = MultidisciplinaryTeam(
            cardiologist_report=responses.get("Cardiologist", "No report"),
            psychologist_report=responses.get("Psychologist", "No report"),
            pulmonologist_report=responses.get("Pulmonologist", "No report")
        )
    
    final_diagnosis = team_agent.run()
    logger.info("Final diagnosis generated successfully")
    return final_diagnosis


def save_results(final_diagnosis: str, responses: dict, output_path: str = None) -> Path:
    """
    Save the final diagnosis to a file.
    
    Args:
        final_diagnosis: The final diagnosis text
        responses: Dictionary of all agent responses
        output_path: Optional custom output path
        
    Returns:
        Path to the saved file
    """
    if output_path is None:
        output_path = RESULTS_DIR / DEFAULT_OUTPUT_FILE
    
    output_file = Path(output_path)
    
    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Format the output
    final_diagnosis_text = "### Final Diagnosis:\n\n" + final_diagnosis
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as txt_file:
        txt_file.write(final_diagnosis_text)
    
    logger.info(f"Final diagnosis saved to: {output_file}")
    return output_file


def main():
    """Main entry point for the script."""
    # Load environment variables
    env_file = Config.get_env_file_path()
    if env_file:
        load_dotenv(dotenv_path=env_file)
        logger.info(f"Loaded environment variables from: {env_file}")
    else:
        logger.warning("No .env file found. Using system environment variables.")
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Example usage - you can modify this to accept command line arguments
    # For now, using a sample report from Medical Reports directory
    try:
        # Check if Medical Reports directory has any files
        report_files = list(Config.MEDICAL_REPORTS_DIR.glob("*.txt"))
        
        if not report_files:
            logger.error(f"No medical reports found in {Config.MEDICAL_REPORTS_DIR}")
            print(f"Error: No medical reports found in {Config.MEDICAL_REPORTS_DIR}")
            print("Please add medical report files (.txt) to the 'Medical Reports' directory.")
            sys.exit(1)
        
        # Use the first available report (or specify one)
        sample_report = report_files[0]
        logger.info(f"Using sample report: {sample_report.name}")
        
        # Load medical report
        medical_report = load_medical_report(sample_report.name)
        
        # Determine which provider to use
        use_huggingface = Config.HUGGINGFACEHUB_API_TOKEN is not None
        hf_model = Config.DEFAULT_HF_MODEL if use_huggingface else None
        
        if not use_huggingface and not Config.OPENAI_API_KEY:
            logger.error("No API keys found. Please set OPENAI_API_KEY or HUGGINGFACEHUB_API_TOKEN")
            print("Error: No API keys found.")
            print("Please set OPENAI_API_KEY or HUGGINGFACEHUB_API_TOKEN in your .env file or environment.")
            sys.exit(1)
        
        # Run analysis
        responses = run_analysis(medical_report, use_huggingface=use_huggingface, hf_model=hf_model)
        
        # Generate final diagnosis
        final_diagnosis = generate_final_diagnosis(responses, use_huggingface=use_huggingface, hf_model=hf_model)
        
        # Save results
        output_file = save_results(final_diagnosis, responses)
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Final diagnosis saved to: {output_file}")
        print(f"\nFinal Diagnosis:\n{final_diagnosis}\n")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
