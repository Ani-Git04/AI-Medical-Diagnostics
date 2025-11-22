"""
Streamlit web application for AI Medical Diagnostics System.

Provides a user-friendly interface for analyzing medical reports
using specialized AI agents.
"""

import streamlit as st
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import warnings
from pathlib import Path

# Suppress secrets file warning
warnings.filterwarnings('ignore', message='.*secrets.*')

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from Utils.Agents import Cardiologist, Psychologist, Pulmonologist, MultidisciplinaryTeam
    from Utils.constants import (
        DEFAULT_HF_MODEL,
        OPENAI_MODELS,
        MIN_REPORT_LENGTH,
        MIN_REPORT_LENGTH_WARNING,
        MEDICAL_KEYWORDS,
        MEDICAL_REPORTS_DIR
    )
    from config import Config
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all dependencies are installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Medical Diagnostics System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.4rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        line-height: 1.6;
    }
    .final-diagnosis {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-top: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #78350f;
    }
    .warning-box strong {
        color: #92400e;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #065f46;
    }
    .success-box strong {
        color: #047857;
        font-size: 1.1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    .stButton>button {
        font-weight: 600;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'final_diagnosis' not in st.session_state:
    st.session_state.final_diagnosis = ""

# Header
st.markdown('<div class="main-header"> AI Medical Diagnostics System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Advanced Multi-Agent AI for Comprehensive Medical Case Analysis<br><small style="color: #94a3b8;">Get insights from Cardiology, Psychology, and Pulmonology specialists</small></div>',
    unsafe_allow_html=True)

# Warning disclaimer
st.markdown("""
<div class="warning-box">
    <strong>⚠️ DISCLAIMER:</strong> This system is for research and educational purposes only. 
    It is NOT intended for clinical use or medical decision-making. Always consult qualified healthcare professionals.
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    # st.header("⚙️ Configuration")

    # Check if API keys are in Streamlit secrets (for deployment)
    use_secrets = False
    try:
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            if "HUGGINGFACEHUB_API_TOKEN" in st.secrets or "huggingface_token" in st.secrets:
                use_secrets = True
                hf_token = st.secrets.get("HUGGINGFACEHUB_API_TOKEN") or st.secrets.get("huggingface_token")
                os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
    except (FileNotFoundError, AttributeError):
        use_secrets = False

    if use_secrets:
        # Deployed mode - no API key input needed
        st.markdown("""
        <div class="success-box">
            <strong>✅ System Ready!</strong><br>
            <span style="font-size: 0.95rem;">Powered by Llama 3.2 AI for medical analysis</span>
        </div>
        """, unsafe_allow_html=True)

        use_huggingface = True
        use_openai = False
        api_key_valid = True
        hf_model = DEFAULT_HF_MODEL
        model_name = None

    else:
        # Local development mode - show API key inputs
        llm_provider = st.radio(
            "Select LLM Provider",
            ["🤗 Hugging Face (FREE API)", "🔵 OpenAI (API Key Required)"],
            help="Hugging Face provides free API access to many models. OpenAI requires payment after free credits."
        )

        use_huggingface = "Hugging Face" in llm_provider
        use_openai = "OpenAI" in llm_provider

        # Initialize variables
        api_key_valid = False
        hf_model = None
        model_name = None

        if use_huggingface:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Using Hugging Face (Free API!)</strong><br>
                Llama 3.2 model - works great for medical analysis.
            </div>
            """, unsafe_allow_html=True)

            hf_token = st.text_input(
                "Hugging Face API Token",
                type="password",
                help="Get your FREE token at https://huggingface.co/settings/tokens"
            )

            if hf_token:
                os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
                st.success("✅ HF Token loaded")
                api_key_valid = True
            else:
                st.warning("⚠️ Please enter your Hugging Face token")
                api_key_valid = False

            hf_model = DEFAULT_HF_MODEL

            with st.expander("📖 How to Get Your HF Token (30 seconds)"):
                st.markdown("""
                **Step 1:** Go to https://huggingface.co/settings/tokens

                **Step 2:** Click "New token"

                **Step 3:** Give it a name (e.g., "medical-app")

                **Step 4:** Select "Read" permission

                **Step 5:** Click "Generate" and copy the token

                **Step 6:** Paste it above!

                ✅ It's completely **FREE** with no credit card required!
                """)

        else:  # OpenAI
            # API Key input for OpenAI
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
            )

            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                st.success("✅ API Key loaded")
                api_key_valid = True
            else:
                st.warning("⚠️ Please enter your OpenAI API key")
                api_key_valid = False

            # Model selection
            model_name = st.selectbox(
                "Select Model",
                OPENAI_MODELS,
                help="Select which OpenAI model to use. Try gpt-3.5-turbo first (cheapest and fastest)."
            )

    st.divider()

    # About section
    st.header("ℹ️ About")
    st.markdown("""
    This system uses three specialized AI agents:

    - **🫀 Cardiologist**: Cardiac assessment
    - **🧠 Psychologist**: Mental health evaluation  
    - **🫁 Pulmonologist**: Respiratory analysis

    All agents run in parallel for faster results.
    """)

    # if use_huggingface:
        # st.info("💡 **Tip**: Hugging Face is completely free and works on any macOS version!")

# Main content area
tab1, tab2, tab3 = st.tabs(["📝 Input Medical Report", "🔬 Analysis", "📊 Sample Reports"])

with tab1:
    st.subheader("Enter Patient Medical Report")

    # Info box about good medical reports
    with st.expander("ℹ️ What makes a good medical report for AI analysis?"):
        st.markdown("""
        **A comprehensive medical report should include:**

        ✅ **Patient Information**: Age, gender, ID  
        ✅ **Chief Complaint**: Main symptoms and concerns  
        ✅ **Medical History**: Past conditions, medications, family history  
        ✅ **Vital Signs**: Blood pressure, heart rate, temperature, etc.  
        ✅ **Test Results**: Lab work, imaging, diagnostic tests  
        ✅ **Physical Examination**: Doctor's observations and findings  

        **Note:** This system is designed for complete medical case reports, not simple questions or symptoms lists.
        """)

    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Type/Paste Report", "Upload File"],
        horizontal=True
    )

    medical_report = ""

    if input_method == "Type/Paste Report":
        medical_report = st.text_area(
            "Medical Report",
            height=300,
            placeholder="Paste the patient's medical report here...",
            help="Include all relevant medical history, symptoms, test results, and observations."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Medical Report",
            type=['txt'],
            help="Upload a text file containing the medical report"
        )
        if uploaded_file:
            medical_report = uploaded_file.read().decode('utf-8')
            st.text_area("Preview:", medical_report, height=200)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Medical Report",
            type="primary",
            use_container_width=True,
            disabled=not medical_report or not api_key_valid
        )

    # Basic validation for medical content
    if medical_report and len(medical_report) < MIN_REPORT_LENGTH:
        st.warning(f"⚠️ The report seems too short. Please provide a detailed medical report (at least {MIN_REPORT_LENGTH} characters).")

    # Check for medical keywords
    if medical_report:
        text_lower = medical_report.lower()
        has_medical_content = any(keyword in text_lower for keyword in MEDICAL_KEYWORDS)

        if not has_medical_content and len(medical_report) > MIN_REPORT_LENGTH_WARNING:
            st.error(
                "⚠️ This doesn't appear to be a medical report. Please provide a valid medical case report with patient information, symptoms, and clinical findings.")
            analyze_button = False  # Disable analysis

with tab2:
    if analyze_button and medical_report and api_key_valid:
        st.session_state.analysis_complete = False
        st.session_state.responses = {}

        st.subheader("🔄 Analysis in Progress")

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Create containers for each agent
        st.markdown("### Specialist Consultations")
        card_col, psych_col, pulm_col = st.columns(3)

        with card_col:
            card_status = st.empty()
            card_expander = st.expander("🫀 Cardiologist", expanded=False)

        with psych_col:
            psych_status = st.empty()
            psych_expander = st.expander("🧠 Psychologist", expanded=False)

        with pulm_col:
            pulm_status = st.empty()
            pulm_expander = st.expander("🫁 Pulmonologist", expanded=False)

        # Initialize agents based on provider
        try:
            if use_huggingface:
                agents = {
                    "Cardiologist": Cardiologist(medical_report, use_huggingface=True, hf_model=hf_model),
                    "Psychologist": Psychologist(medical_report, use_huggingface=True, hf_model=hf_model),
                    "Pulmonologist": Pulmonologist(medical_report, use_huggingface=True, hf_model=hf_model)
                }
            else:  # OpenAI
                agents = {
                    "Cardiologist": Cardiologist(medical_report, use_huggingface=False),
                    "Psychologist": Psychologist(medical_report, use_huggingface=False),
                    "Pulmonologist": Pulmonologist(medical_report, use_huggingface=False)
                }
                # Update model for OpenAI agents
                for agent in agents.values():
                    agent.model.model_name = model_name


            # Function to run each agent
            def get_response(agent_name, agent):
                response = agent.run()
                return agent_name, response


            # Run agents in parallel
            responses = {}
            total_agents = len(agents)
            completed = 0

            status_text.text("⏳ Running specialist consultations in parallel...")

            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(get_response, name, agent): name for name, agent in agents.items()}

                for future in as_completed(futures):
                    try:
                        agent_name, response = future.result()

                        # Check if response is None or an error
                        if response is None:
                            response = f"❌ {agent_name} returned no response. Check your API configuration."
                        elif "ERROR:" in str(response):
                            st.error(f"Error in {agent_name}: {response}")

                        responses[agent_name] = response
                        completed += 1

                        # Update progress
                        progress_bar.progress(completed / (total_agents + 1))

                        # Update specific agent status
                        if agent_name == "Cardiologist":
                            if "ERROR:" in str(response):
                                card_status.error("❌ Error")
                            else:
                                card_status.success("✅ Complete")
                            with card_expander:
                                st.markdown(response)
                        elif agent_name == "Psychologist":
                            if "ERROR:" in str(response):
                                psych_status.error("❌ Error")
                            else:
                                psych_status.success("✅ Complete")
                            with psych_expander:
                                st.markdown(response)
                        elif agent_name == "Pulmonologist":
                            if "ERROR:" in str(response):
                                pulm_status.error("❌ Error")
                            else:
                                pulm_status.success("✅ Complete")
                            with pulm_expander:
                                st.markdown(response)
                    except Exception as e:
                        st.error(f"Error processing {futures[future]}: {str(e)}")
                        responses[futures[future]] = f"ERROR: {str(e)}"

            # Run MultidisciplinaryTeam agent
            status_text.text("🔄 Generating final diagnosis from multidisciplinary team...")

            if use_huggingface:
                team_agent = MultidisciplinaryTeam(
                    cardiologist_report=responses.get("Cardiologist", "No report"),
                    psychologist_report=responses.get("Psychologist", "No report"),
                    pulmonologist_report=responses.get("Pulmonologist", "No report"),
                    use_huggingface=True,
                    hf_model=hf_model
                )
            else:  # OpenAI
                team_agent = MultidisciplinaryTeam(
                    cardiologist_report=responses.get("Cardiologist", "No report"),
                    psychologist_report=responses.get("Psychologist", "No report"),
                    pulmonologist_report=responses.get("Pulmonologist", "No report"),
                    use_huggingface=False
                )
                team_agent.model.model_name = model_name

            final_diagnosis = team_agent.run()
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")

            # Store in session state
            st.session_state.responses = responses
            st.session_state.final_diagnosis = final_diagnosis if final_diagnosis else "No diagnosis generated"
            st.session_state.analysis_complete = True

            st.balloons()

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            if use_huggingface:
                st.warning("""
                **Possible issues:**
                - Invalid Hugging Face token
                - Model may be loading (try again in 30 seconds)
                - Rate limit reached (wait a few minutes)

                Get your FREE token at: https://huggingface.co/settings/tokens
                """)
            else:
                st.warning("""
                **Possible issues:**
                - Invalid API key
                - Insufficient credits/quota
                - Internet connection issue

                Check your account at: https://platform.openai.com/account/billing
                """)

    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.final_diagnosis:
        st.markdown("---")
        st.markdown('<div class="final-diagnosis">', unsafe_allow_html=True)
        st.markdown("### 🎯 Final Diagnosis & Recommendations")
        st.markdown(st.session_state.final_diagnosis)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download options
        st.markdown("---")
        st.subheader("💾 Download Results")

        col1, col2 = st.columns(2)

        with col1:
            # Prepare text file
            full_report = f"""
AI MEDICAL DIAGNOSTICS SYSTEM
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

CARDIOLOGIST CONSULTATION
{'=' * 60}
{st.session_state.responses.get('Cardiologist', 'N/A')}

PSYCHOLOGIST CONSULTATION
{'=' * 60}
{st.session_state.responses.get('Psychologist', 'N/A')}

PULMONOLOGIST CONSULTATION
{'=' * 60}
{st.session_state.responses.get('Pulmonologist', 'N/A')}

FINAL DIAGNOSIS & RECOMMENDATIONS
{'=' * 60}
{st.session_state.final_diagnosis}
"""
            if full_report and st.session_state.final_diagnosis:
                st.download_button(
                    label="📄 Download Full Report",
                    data=full_report,
                    file_name=f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_full"
                )

        with col2:
            if st.session_state.final_diagnosis:
                st.download_button(
                    label="📋 Download Final Diagnosis Only",
                    data=st.session_state.final_diagnosis,
                    file_name=f"final_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_diagnosis"
                )

with tab3:
    st.subheader("📚 Sample Medical Reports")
    st.info("You can load sample reports from the 'Medical Reports' folder to test the system.")

    # Check if Medical Reports folder exists
    reports_dir = Path(MEDICAL_REPORTS_DIR)
    if reports_dir.exists():
        report_files = [f.name for f in reports_dir.glob("*.txt")]

        if report_files:
            selected_report = st.selectbox("Select a sample report:", report_files)

            if st.button("📂 Load Sample Report"):
                report_path = reports_dir / selected_report
                with open(report_path, 'r', encoding='utf-8') as f:
                    sample_content = f.read()
                st.success(f"✅ Loaded: {selected_report}")
                st.text_area("Report Content:", sample_content, height=300)
                st.info("💡 Switch to the 'Input Medical Report' tab, then paste this content to analyze it.")
        else:
            st.warning("No sample reports found in the Medical Reports folder.")
    else:
        st.warning("Medical Reports folder not found. Please create sample reports in a 'Medical Reports' folder.")

# Footer
provider_text = "🤗 Hugging Face (Free API)" if use_huggingface else "🔵 OpenAI API"

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    <p>🔬 AI Medical Diagnostics System v2.0 | Built with Streamlit & LangChain</p>
    <p>Using: {provider_text}</p>
    <p>⚠️ For Research & Educational Purposes Only - Not for Clinical Use</p>
</div>
""", unsafe_allow_html=True)