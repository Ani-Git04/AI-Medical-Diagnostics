"""
Medical Diagnostics Agents Module.

This module contains specialized AI agents for medical case analysis:
- Cardiologist: Cardiac assessment
- Psychologist: Mental health evaluation
- Pulmonologist: Respiratory assessment
- MultidisciplinaryTeam: Final diagnosis synthesis
"""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from huggingface_hub import InferenceClient
import os
from typing import Optional, Dict, Any
from .constants import (
    DEFAULT_HF_MODEL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENAI_MODEL,
    HF_MAX_TOKENS,
    HF_TEMPERATURE,
    OPENAI_TEMPERATURE,
    MAX_REPETITION_COUNT,
    MAX_CONTENT_LENGTH,
    REPETITION_PATTERN,
    AGENT_ROLES
)
from .logger import logger


class Agent:
    """
    Base class for medical diagnostic agents.
    
    This class provides the foundation for specialized medical agents
    that analyze patient reports using various LLM providers.
    """
    
    def __init__(
        self,
        medical_report: Optional[str] = None,
        role: Optional[str] = None,
        extra_info: Optional[Dict[str, Any]] = None,
        use_ollama: bool = False,
        ollama_model: str = DEFAULT_OLLAMA_MODEL,
        use_huggingface: bool = False,
        hf_model: str = DEFAULT_HF_MODEL
    ):
        """
        Initialize the Agent.
        
        Args:
            medical_report: The patient's medical report to analyze
            role: The role/specialty of the agent (e.g., "Cardiologist")
            extra_info: Additional information for specialized agents
            use_ollama: Whether to use Ollama as the LLM provider
            ollama_model: Ollama model name
            use_huggingface: Whether to use Hugging Face as the LLM provider
            hf_model: Hugging Face model identifier
        """
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info or {}
        self.use_ollama = use_ollama
        self.use_huggingface = use_huggingface
        self.ollama_model = ollama_model
        self.hf_model = hf_model

        # Initialize the prompt based on role and other info
        self.prompt_template = self.create_prompt_template()

        # Initialize the model based on provider
        if use_huggingface:
            # Use direct HuggingFace InferenceClient (new API)
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not hf_token:
                logger.warning("HUGGINGFACEHUB_API_TOKEN not found in environment variables")
            self.model = InferenceClient(model=hf_model, token=hf_token)
            self.is_hf = True
            logger.info(f"Initialized {role} agent with Hugging Face model: {hf_model}")
        elif use_ollama:
            self.model = ChatOllama(
                model=ollama_model,
                temperature=OPENAI_TEMPERATURE
            )
            self.is_hf = False
            logger.info(f"Initialized {role} agent with Ollama model: {ollama_model}")
        else:
            self.model = ChatOpenAI(temperature=OPENAI_TEMPERATURE, model=DEFAULT_OPENAI_MODEL)
            self.is_hf = False
            logger.info(f"Initialized {role} agent with OpenAI model: {DEFAULT_OPENAI_MODEL}")

    def create_prompt_template(self) -> PromptTemplate:
        """
        Create a prompt template based on the agent's role.
        
        Returns:
            PromptTemplate configured for the agent's specialty
        """
        if self.role == AGENT_ROLES['MULTIDISCIPLINARY_TEAM']:
            template = """
                Act like a multidisciplinary team of healthcare professionals.
                You will receive a medical report of a patient visited by a Cardiologist, Psychologist, and Pulmonologist.
                Task: Review the patient's medical report from the Cardiologist, Psychologist, and Pulmonologist, analyze them and come up with a list of 3 possible health issues of the patient.
                Just return a list of bullet points of 3 possible health issues of the patient and for each issue provide the reason.

                Cardiologist Report: {cardiologist_report}
                Psychologist Report: {psychologist_report}
                Pulmonologist Report: {pulmonologist_report}
            """
            return PromptTemplate.from_template(template)
        else:
            templates = {
                AGENT_ROLES['CARDIOLOGIST']: """
                    Act like a cardiologist. You will receive a medical report of a patient.
                    Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
                    Focus: Determine if there are any subtle signs of cardiac issues that could explain the patient's symptoms. Rule out any underlying heart conditions, such as arrhythmias or structural abnormalities, that might be missed on routine testing.
                    Recommendation: Provide guidance on any further cardiac testing or monitoring needed to ensure there are no hidden heart-related concerns. Suggest potential management strategies if a cardiac issue is identified.
                    Please only return the possible causes of the patient's symptoms and the recommended next steps.
                    Medical Report: {medical_report}
                """,
                AGENT_ROLES['PSYCHOLOGIST']: """
                    Act like a psychologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a psychological assessment.
                    Focus: Identify any potential mental health issues, such as anxiety, depression, or trauma, that may be affecting the patient's well-being.
                    Recommendation: Offer guidance on how to address these mental health concerns, including therapy, counseling, or other interventions.
                    Please only return the possible mental health issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """,
                AGENT_ROLES['PULMONOLOGIST']: """
                    Act like a pulmonologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a pulmonary assessment.
                    Focus: Identify any potential respiratory issues, such as asthma, COPD, or lung infections, that may be affecting the patient's breathing.
                    Recommendation: Offer guidance on how to address these respiratory concerns, including pulmonary function tests, imaging studies, or other interventions.
                    Please only return the possible respiratory issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """
            }
            template = templates.get(self.role, templates[AGENT_ROLES['CARDIOLOGIST']])
            return PromptTemplate.from_template(template)

    def run(self) -> str:
        """
        Execute the agent's analysis on the medical report.
        
        Returns:
            Analysis results as a string, or error message if execution fails
        """
        logger.info(f"{self.role} agent is running...")
        
        try:
            # Format the prompt
            if self.role == AGENT_ROLES['MULTIDISCIPLINARY_TEAM']:
                prompt = self.prompt_template.format(
                    cardiologist_report=self.extra_info.get('cardiologist_report', ''),
                    psychologist_report=self.extra_info.get('psychologist_report', ''),
                    pulmonologist_report=self.extra_info.get('pulmonologist_report', '')
                )
            else:
                prompt = self.prompt_template.format(medical_report=self.medical_report)
            
            if self.use_huggingface:
                return self._run_huggingface(prompt)
            else:
                return self._run_standard(prompt)
                
        except Exception as e:
            error_msg = f"Error in {self.role}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"ERROR: {error_msg}"
    
    def _run_huggingface(self, prompt: str) -> str:
        """
        Run analysis using Hugging Face Inference API.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Cleaned response content
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat_completion(
            messages=messages,
            max_tokens=HF_MAX_TOKENS,
            temperature=HF_TEMPERATURE
        )
        
        # Extract the response text
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content
        elif isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
        else:
            content = str(response)

        # Clean up repetitive content
        return self._clean_response(content)
    
    def _run_standard(self, prompt: str) -> str:
        """
        Run analysis using standard LangChain models (OpenAI/Ollama).
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Response content
        """
        response = self.model.invoke(prompt)
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    def _clean_response(self, content: str) -> str:
        """
        Clean response content by removing repetitive patterns.
        
        Args:
            content: Raw response content
            
        Returns:
            Cleaned content without excessive repetition
        """
        # Remove duplicate consecutive lines
        lines = content.split('\n')
        cleaned_lines = []
        prev_line = None
        repetition_count = 0

        for line in lines:
            stripped = line.strip()
            if stripped == prev_line:
                repetition_count += 1
                if repetition_count < MAX_REPETITION_COUNT:
                    cleaned_lines.append(line)
            else:
                repetition_count = 0
                cleaned_lines.append(line)
                prev_line = stripped

        final_content = '\n'.join(cleaned_lines)

        # Truncate if content is too long and repetitive
        if len(final_content) > MAX_CONTENT_LENGTH and final_content.count(REPETITION_PATTERN) > 2:
            parts = final_content.split(REPETITION_PATTERN)
            final_content = parts[0] + "\n\n(Analysis truncated to prevent repetition)"
            logger.warning(f"Response truncated for {self.role} due to repetition")

        return final_content


# Define specialized agent classes
class Cardiologist(Agent):
    """
    Cardiologist agent for cardiac assessment and analysis.
    
    Specializes in analyzing cardiac workups, ECGs, blood tests,
    Holter monitor results, and echocardiograms.
    """
    
    def __init__(
        self,
        medical_report: str,
        use_ollama: bool = False,
        ollama_model: str = DEFAULT_OLLAMA_MODEL,
        use_huggingface: bool = False,
        hf_model: str = DEFAULT_HF_MODEL
    ):
        """
        Initialize the Cardiologist agent.
        
        Args:
            medical_report: Patient's medical report
            use_ollama: Whether to use Ollama
            ollama_model: Ollama model name
            use_huggingface: Whether to use Hugging Face
            hf_model: Hugging Face model identifier
        """
        super().__init__(
            medical_report,
            AGENT_ROLES['CARDIOLOGIST'],
            use_ollama=use_ollama,
            ollama_model=ollama_model,
            use_huggingface=use_huggingface,
            hf_model=hf_model
        )


class Psychologist(Agent):
    """
    Psychologist agent for mental health assessment.
    
    Specializes in identifying mental health issues such as
    anxiety, depression, and trauma.
    """
    
    def __init__(
        self,
        medical_report: str,
        use_ollama: bool = False,
        ollama_model: str = DEFAULT_OLLAMA_MODEL,
        use_huggingface: bool = False,
        hf_model: str = DEFAULT_HF_MODEL
    ):
        """
        Initialize the Psychologist agent.
        
        Args:
            medical_report: Patient's medical report
            use_ollama: Whether to use Ollama
            ollama_model: Ollama model name
            use_huggingface: Whether to use Hugging Face
            hf_model: Hugging Face model identifier
        """
        super().__init__(
            medical_report,
            AGENT_ROLES['PSYCHOLOGIST'],
            use_ollama=use_ollama,
            ollama_model=ollama_model,
            use_huggingface=use_huggingface,
            hf_model=hf_model
        )


class Pulmonologist(Agent):
    """
    Pulmonologist agent for respiratory assessment.
    
    Specializes in identifying respiratory issues such as
    asthma, COPD, and lung infections.
    """
    
    def __init__(
        self,
        medical_report: str,
        use_ollama: bool = False,
        ollama_model: str = DEFAULT_OLLAMA_MODEL,
        use_huggingface: bool = False,
        hf_model: str = DEFAULT_HF_MODEL
    ):
        """
        Initialize the Pulmonologist agent.
        
        Args:
            medical_report: Patient's medical report
            use_ollama: Whether to use Ollama
            ollama_model: Ollama model name
            use_huggingface: Whether to use Hugging Face
            hf_model: Hugging Face model identifier
        """
        super().__init__(
            medical_report,
            AGENT_ROLES['PULMONOLOGIST'],
            use_ollama=use_ollama,
            ollama_model=ollama_model,
            use_huggingface=use_huggingface,
            hf_model=hf_model
        )


class MultidisciplinaryTeam(Agent):
    """
    Multidisciplinary team agent for final diagnosis synthesis.
    
    Combines reports from Cardiologist, Psychologist, and Pulmonologist
    to generate a comprehensive final diagnosis.
    """
    
    def __init__(
        self,
        cardiologist_report: str,
        psychologist_report: str,
        pulmonologist_report: str,
        use_ollama: bool = False,
        ollama_model: str = DEFAULT_OLLAMA_MODEL,
        use_huggingface: bool = False,
        hf_model: str = DEFAULT_HF_MODEL
    ):
        """
        Initialize the MultidisciplinaryTeam agent.
        
        Args:
            cardiologist_report: Report from Cardiologist agent
            psychologist_report: Report from Psychologist agent
            pulmonologist_report: Report from Pulmonologist agent
            use_ollama: Whether to use Ollama
            ollama_model: Ollama model name
            use_huggingface: Whether to use Hugging Face
            hf_model: Hugging Face model identifier
        """
        extra_info = {
            "cardiologist_report": cardiologist_report,
            "psychologist_report": psychologist_report,
            "pulmonologist_report": pulmonologist_report
        }
        super().__init__(
            role=AGENT_ROLES['MULTIDISCIPLINARY_TEAM'],
            extra_info=extra_info,
            use_ollama=use_ollama,
            ollama_model=ollama_model,
            use_huggingface=use_huggingface,
            hf_model=hf_model
        )