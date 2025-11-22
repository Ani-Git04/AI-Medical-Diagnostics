from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from huggingface_hub import InferenceClient
import os


class Agent:
    def __init__(self, medical_report=None, role=None, extra_info=None, use_ollama=False, ollama_model="llama3.2",
                 use_huggingface=False, hf_model="meta-llama/Llama-3.2-3B-Instruct"):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info
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
            self.model = InferenceClient(model=hf_model, token=hf_token)
            self.is_hf = True
        elif use_ollama:
            self.model = ChatOllama(
                model=ollama_model,
                temperature=0
            )
            self.is_hf = False
        else:
            self.model = ChatOpenAI(temperature=0, model="gpt-4-turbo")
            self.is_hf = False

    def create_prompt_template(self):
        if self.role == "MultidisciplinaryTeam":
            templates = f"""
                Act like a multidisciplinary team of healthcare professionals.
                You will receive a medical report of a patient visited by a Cardiologist, Psychologist, and Pulmonologist.
                Task: Review the patient's medical report from the Cardiologist, Psychologist, and Pulmonologist, analyze them and come up with a list of 3 possible health issues of the patient.
                Just return a list of bullet points of 3 possible health issues of the patient and for each issue provide the reason.

                Cardiologist Report: {self.extra_info.get('cardiologist_report', '')}
                Psychologist Report: {self.extra_info.get('psychologist_report', '')}
                Pulmonologist Report: {self.extra_info.get('pulmonologist_report', '')}
            """
        else:
            templates = {
                "Cardiologist": """
                    Act like a cardiologist. You will receive a medical report of a patient.
                    Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
                    Focus: Determine if there are any subtle signs of cardiac issues that could explain the patient's symptoms. Rule out any underlying heart conditions, such as arrhythmias or structural abnormalities, that might be missed on routine testing.
                    Recommendation: Provide guidance on any further cardiac testing or monitoring needed to ensure there are no hidden heart-related concerns. Suggest potential management strategies if a cardiac issue is identified.
                    Please only return the possible causes of the patient's symptoms and the recommended next steps.
                    Medical Report: {medical_report}
                """,
                "Psychologist": """
                    Act like a psychologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a psychological assessment.
                    Focus: Identify any potential mental health issues, such as anxiety, depression, or trauma, that may be affecting the patient's well-being.
                    Recommendation: Offer guidance on how to address these mental health concerns, including therapy, counseling, or other interventions.
                    Please only return the possible mental health issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """,
                "Pulmonologist": """
                    Act like a pulmonologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a pulmonary assessment.
                    Focus: Identify any potential respiratory issues, such as asthma, COPD, or lung infections, that may be affecting the patient's breathing.
                    Recommendation: Offer guidance on how to address these respiratory concerns, including pulmonary function tests, imaging studies, or other interventions.
                    Please only return the possible respiratory issues and the recommended next steps.
                    Patient's Report: {medical_report}
                """
            }
            templates = templates[self.role]
        return PromptTemplate.from_template(templates)

    def run(self):
        print(f"{self.role} is running...")
        prompt = self.prompt_template.format(medical_report=self.medical_report)
        try:
            if self.use_huggingface:
                # Use HuggingFace InferenceClient's chat_completion method for conversational models
                messages = [
                    {"role": "user", "content": prompt}
                ]
                response = self.model.chat_completion(
                    messages=messages,
                    max_tokens=600,  # Reduced to prevent repetition
                    temperature=0.7  # Increased for more varied output
                )
                # Extract the response text
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    content = response.choices[0].message.content
                elif isinstance(response, dict) and 'choices' in response:
                    content = response['choices'][0]['message']['content']
                else:
                    content = str(response)

                # Clean up repetitive content - remove duplicate consecutive lines
                lines = content.split('\n')
                cleaned_lines = []
                prev_line = None
                repetition_count = 0

                for line in lines:
                    stripped = line.strip()
                    # If same line repeats more than 2 times, stop adding
                    if stripped == prev_line:
                        repetition_count += 1
                        if repetition_count < 2:  # Allow max 2 repetitions
                            cleaned_lines.append(line)
                    else:
                        repetition_count = 0
                        cleaned_lines.append(line)
                        prev_line = stripped

                # Truncate if we detect repetitive patterns
                final_content = '\n'.join(cleaned_lines)

                # If content is too long and looks repetitive, cut it short
                if len(final_content) > 2000 and final_content.count("However, given") > 2:
                    # Find the first major repetition and cut there
                    parts = final_content.split("However, given")
                    final_content = parts[0] + "\n\n(Analysis truncated to prevent repetition)"

                return final_content
            else:
                response = self.model.invoke(prompt)
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
        except Exception as e:
            error_msg = f"Error in {self.role}: {str(e)}"
            print(error_msg)
            return f"ERROR: {error_msg}"


# Define specialized agent classes
class Cardiologist(Agent):
    def __init__(self, medical_report, use_ollama=False, ollama_model="llama3.2", use_huggingface=False,
                 hf_model="meta-llama/Llama-3.2-3B-Instruct"):
        super().__init__(medical_report, "Cardiologist", use_ollama=use_ollama, ollama_model=ollama_model,
                         use_huggingface=use_huggingface, hf_model=hf_model)


class Psychologist(Agent):
    def __init__(self, medical_report, use_ollama=False, ollama_model="llama3.2", use_huggingface=False,
                 hf_model="meta-llama/Llama-3.2-3B-Instruct"):
        super().__init__(medical_report, "Psychologist", use_ollama=use_ollama, ollama_model=ollama_model,
                         use_huggingface=use_huggingface, hf_model=hf_model)


class Pulmonologist(Agent):
    def __init__(self, medical_report, use_ollama=False, ollama_model="llama3.2", use_huggingface=False,
                 hf_model="meta-llama/Llama-3.2-3B-Instruct"):
        super().__init__(medical_report, "Pulmonologist", use_ollama=use_ollama, ollama_model=ollama_model,
                         use_huggingface=use_huggingface, hf_model=hf_model)


class MultidisciplinaryTeam(Agent):
    def __init__(self, cardiologist_report, psychologist_report, pulmonologist_report, use_ollama=False,
                 ollama_model="llama3.2", use_huggingface=False, hf_model="meta-llama/Llama-3.2-3B-Instruct"):
        extra_info = {
            "cardiologist_report": cardiologist_report,
            "psychologist_report": psychologist_report,
            "pulmonologist_report": pulmonologist_report
        }
        super().__init__(role="MultidisciplinaryTeam", extra_info=extra_info, use_ollama=use_ollama,
                         ollama_model=ollama_model, use_huggingface=use_huggingface, hf_model=hf_model)