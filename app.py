import streamlit as st
import os
import base64
from io import BytesIO
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Lok Sewa Agri Paper II - Master Engine",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- CUSTOM READABILITY & UI STYLING ----------------- #
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 950px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        line-height: 1.75;
        font-size: 1.05rem;
    }
    h1, h2, h3, h4 {
        color: #1e3a8a;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .answer-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 22px;
        margin-top: 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }
    .model-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
    strong {
        color: #0f172a;
    }
    .stSidebar {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- COMPREHENSIVE LOK SEWA SYSTEM PROMPT ----------------- #
SYSTEM_PROMPT = """
You are an elite Public Service Commission (Lok Sewa Aayog) Chief Evaluator and Subject Specialist for the Nepal Agricultural Service (Gazetted Third Class, Technical Paper II).

Your mission is to formulate maximum-scoring (8.5+/10 or 4.5+/5) subjective answers strictly tailored to Lok Sewa Aayog's marking criteria.

========================================================================================
1. DYNAMIC & CONTENT-SPECIFIC DATA RULE (STRICT NO-PREFIX POLICY)
========================================================================================
- NEVER prefix, force, or dump unrelated macro-census statistics (such as total national holdings, population, or general land percentages) into technical answers where they are irrelevant.
- All numbers, empirical values, rates, and scientific metrics MUST BE DIRECTLY RELEVANT to the technical domain of the question:
  * Agronomy & Field Crops: Seed rates (kg/ha), planting geometry/spacing (cm x cm), fertilizer doses (N:P2O5:K2O kg/ha), critical stages of irrigation, plant population per unit area, seed replacement rates (SRR), and harvest yields (t/ha).
  * Horticulture: Spacing, pit dimensions, budding/grafting success rates, chilling hours requirements, storage temperature (°C) & relative humidity (RH %), TSS/Brix levels, and postharvest loss %.
  * Plant Protection (Entomology & Pathology): Economic Threshold Levels (ETL), pest scouting frequencies, spray concentrations (ppm or ml/L), active ingredient rates (g a.i./ha), Pre-Harvest Intervals (PHI days), and WHO hazard classifications.
  * Soil Science: Soil pH thresholds, C:N ratios, bulk density (g/cm³), Cation Exchange Capacity (cmol(+)/kg), organic matter %, and nutrient recommendation ranges.
  * Agricultural Economics & Extension: Benefit-Cost (B/C) ratios, internal rate of return (IRR), Net Present Value (NPV), price elasticity coefficients, marketing margins (%), and sample size parameters.
  * Macro Policy / National Planning / Land Questions: ONLY when the question explicitly deals with macro status, land governance, planning, or national trends, cite pertinent official data (e.g., 16th Periodic Plan targets, Agriculture Development Strategy milestones, or 7th National Agriculture Census indicators).

========================================================================================
2. STRUCTURAL BREAKDOWN ACCORDING TO MARKS
========================================================================================
A. FOR 5-MARK QUESTIONS (Target: 180-250 words, ~0.75 page, 7-8 min):
   1. Operational Definition & Core Concept: 2 lines with precise technical terminology.
   2. Core Technical Points: 5-6 structured, numbered points with bold keywords before colons.
   3. Single Compact Visual: A crisp Markdown comparison table, matrix, or micro-flowchart.
   4. Targeted Policy Reference: 1 active act/policy directly governing the topic.
   5. Direct Wrap-up: 1 concise takeaway line.

B. FOR 10-MARK QUESTIONS (Target: 450-650 words, ~1.5 to 2 pages, 15-16 min):
   1. Introduction & Conceptual Scope: 3-4 lines defining the subject with technical depth.
   2. Core Scientific / Technical Body: Grouped into logical categories using clear subheadings:
      - Theoretical / Physiological / Agronomic Principles
      - Technological, Operational, or Protection Practices
      - Institutional & Operational Governance
   3. Body Visual / Schematic (MANDATORY IN BODY):
      - For multi-tiered / hierarchical concepts (such as IPM, IPNS, Biosecurity, Extension Hierarchy), construct a multi-level Pyramidal / Hierarchical structure:
        * Base Tier: Foundational Prevention / Cultural & Agronomic practices
        * Middle Tier: Detection / Monitoring / Surveillance / Decision Support
        * Upper-Middle Tier: Physical, Mechanical, and Biological Control
        * Apex Tier: Targeted Chemical Intervention (Regulated Last Resort)
      - Render using valid ```mermaid ... ``` code blocks OR clean, aligned Markdown Tables/Matrices.
   4. Field Challenges & Ground Bottlenecks in Nepal: Paired factual critique with real field context.
   5. Mandatory Analytical Conclusion (DO NOT USE A PYRAMID IN THE CONCLUSION):
      The conclusion must be written in structured text following this 3-tier sequence:
      * STEP 1: Ground Problem Identification (Pinpoint the specific structural or field-level bottleneck in Nepal).
      * STEP 2: Dual Strategy Formulation (Articulate a clear dual approach, e.g., Supply-side enforcement vs. Demand-side empowerment; OR Short-term operational relief vs. Long-term institutional reform; OR Preventive community action vs. Regulatory compliance).
      * STEP 3: Statutory & Policy Target Alignment (Explicitly state how specific provisions and targets of relevant Acts, Regulations, and Policies directly solve the identified problem).

========================================================================================
3. EXHAUSTIVE STATUTORY & POLICY REPOSITORY
========================================================================================
Dynamically cross-reference the relevant laws and plans based on the subject matter:
- Food & Quality: Food Hygiene and Quality Act, 2081 (खाद्य स्वच्छता तथा गुणस्तर ऐन, २०८१), Right to Food & Food Sovereignty Act, 2075 & Regulation, 2081, Food Safety Policy, 2076.
- Master Strategies: 16th Periodic Plan (2081/82–2085/86), Agriculture Development Strategy (ADS, 2015–2035), Agriculture Investment Decade (2081–2091), National Agriculture Policy, 2061 / 2081 (Draft).
- Land & Farmers: Farmer Categorization and Listing System Management Directive, 2081, Land Related (20th Amendment) Rules, 2081, Land Use Act, 2076 & Rules, 2079, Local Government Operation Act (LGOA), 2074.
- Seeds & Biodiversity: Seeds Act, 2045 & Rules, 2069, National Seed Vision (2013–2025), Agro-biodiversity Promotion Policy, 2063 (Amended 2071).
- Plant Protection & Pesticides: Pesticide Management Act, 2076 & Pesticide Management Regulation, 2081 (जीवनाशक विषादी व्यवस्थापन नियमावली, २०८१), Plant Protection Act, 2064 & Rules, 2066, 24 Banned Pesticides List, RBPR & MRL guidelines.
- Soil, Forestry & Trade: Fertilizer Control Order, 2055 & Subsidy Directives, Agro-Forestry Policy, 2076, Agri-Business Promotion Policy, 2063, NTIS (2016/2023), WTO (AoA, SPS, TBT), SAFTA, Crop/Livestock Insurance Subsidy Directives.

========================================================================================
4. TECHNICAL CONVENTIONS
========================================================================================
- Use bold keywords before colons: **[Technical Keyword]:** Detailed technical statement.
- Write scientific botanical and zoological names strictly in italics (e.g., *Spodoptera frugiperda*, *Tuta absoluta*).
- Deliver dense, factual, and legally grounded answers with zero generic filler sentences.
"""

# ----------------- CREDENTIALS & DYNAMIC MODEL RESOLVER ----------------- #
def resolve_groq_api_key() -> str:
    """Auto-resolves Groq API key from Streamlit secrets, env variables, or session state."""
    if hasattr(st, "secrets"):
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
        elif "groq_api_key" in st.secrets:
            return st.secrets["groq_api_key"]
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key
    return st.session_state.get("manual_groq_api_key", "")

def get_groq_client(api_key: str):
    if not api_key:
        return None
    return Groq(api_key=api_key)

def get_available_models(client: Groq):
    """Dynamically queries the active model catalog on the user's specific Groq account."""
    try:
        models_data = client.models.list().data
        return [m.id for m in models_data]
    except Exception:
        return []

def select_best_models(available_models: list):
    """
    Selects the single highest quality and fastest active models with automatic fallbacks.
    """
    # Priority rank for reasoning & text generation (from highest reasoning to fast fallbacks)
    text_priority = [
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]
    
    # Priority rank for multimodal vision OCR
    vision_priority = [
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
    ]

    # Select best text model
    text_model = None
    for cand in text_priority:
        if cand in available_models:
            text_model = cand
            break
    if not text_model:
        # Filter out audio/moderation models to find the first usable LLM
        usable = [
            m for m in available_models 
            if not any(x in m for x in ["whisper", "guard", "embed", "safeguard", "orpheus"])
        ]
        text_model = usable[0] if usable else "llama-3.1-8b-instant"

    # Select best vision model
    vision_model = None
    for cand in vision_priority:
        if cand in available_models:
            vision_model = cand
            break
    if not vision_model:
        vision_candidates = [m for m in available_models if "vision" in m]
        vision_model = vision_candidates[0] if vision_candidates else "llama-3.2-11b-vision-preview"

    return text_model, vision_model

# ----------------- BACKEND FUNCTIONS ----------------- #
def encode_image(image: Image.Image) -> str:
    buffered = BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def extract_question_from_image(client: Groq, image: Image.Image, vision_model: str) -> str:
    """Uses Groq multimodal vision model to transcribe question from image."""
    base64_img = encode_image(image)
    response = client.chat.completions.create(
        model=vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Transcribe the subjective examination question(s) from this exam paper image verbatim. Do not answer it. Output only the extracted question text, including any marks indicated.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"},
                    },
                ],
            }
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()

def generate_model_answer(client: Groq, question: str, marks: int, diagram_type: str, text_model: str, fallback_models: list) -> tuple:
    """Generates maximum-scoring answer with automatic multi-model failover."""
    user_prompt = f"""
EXAMINATION QUESTION:
\"\"\"{question}\"\"\"

TARGET MARKS: {marks} Marks

RECOMMENDED DIAGRAM FORMAT (FOR THE BODY):
{diagram_type if diagram_type != "Auto-Detect Best Diagram" else "Select the most technically fitting visual (e.g., Pyramidal/Tiered Hierarchy for multi-tiered systems, Flowchart, Cycle, or Markdown Table) to place in the BODY of the answer."}

CRITICAL RULES:
1. DATA RELEVANCE: Do NOT dump generic census or land statistics unless the question explicitly asks for them. Use precise technical numbers that match the question's content (e.g., seed rates, NPK doses, ETL values, spacing, pH, B/C ratios).
2. BODY VISUAL: Include the diagram/pyramid/matrix directly in the BODY of the answer.
3. CONCLUSION FORMAT: Do NOT use a pyramid in the conclusion. Write the conclusion in structured text following the exact 3-step sequence:
   - Ground Problem Identification
   - Dual Strategy Formulation
   - Statutory & Policy Target Alignment (citing specific acts/rules up to 2081 BS).
"""
    # Candidate order: primary model followed by remaining available fallbacks
    candidates = [text_model] + [m for m in fallback_models if m != text_model]
    
    last_error = None
    for model_id in candidates:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.25,
                max_tokens=4096,
            )
            return response.choices[0].message.content, model_id
        except Exception as e:
            last_error = e
            continue

    raise last_error

# ----------------- USER INTERFACE ----------------- #
def main():
    st.title("🌾 Lok Sewa Agriculture Paper II: Master Engine")
    st.caption("Auto-Selecting Fastest High-Reasoning Model • 2081 BS Legal Baseline Embedded")

    # Resolve API Key
    active_api_key = resolve_groq_api_key()

    with st.sidebar:
        st.header("⚙️ Exam Controls")
        
        if active_api_key:
            st.success("🔒 API Key Connected")
        else:
            st.warning("⚠️ No API Key found.")
            input_key = st.text_input(
                "Enter Groq API Key:",
                type="password",
                help="Paste your key or add GROQ_API_KEY to your Streamlit secrets.",
            )
            if input_key:
                st.session_state["manual_groq_api_key"] = input_key
                active_api_key = input_key

        st.divider()

        marks = st.radio(
            "Target Question Marks",
            options=[10, 5],
            index=0,
            horizontal=True,
            help="10 Marks = Full body diagram & 3-step conclusion | 5 Marks = Compact technical answer",
        )

        diagram_options = [
            "Auto-Detect Best Diagram",
            "Pyramidal / Tiered Hierarchy (Mermaid)",
            "Flowchart (Mermaid)",
            "Cycle Diagram (Mermaid)",
            "Process Diagram (Mermaid)",
            "Tree / Hierarchical Diagram (Mermaid)",
            "Decision Tree (Mermaid)",
            "Timeline / Roadmap (Mermaid)",
            "Cause–Effect / Fishbone Diagram (Mermaid)",
            "Concept Map / Mind Map (Mermaid)",
            "Comparison Matrix / Table (Markdown)",
        ]
        selected_diagram = st.selectbox("Preferred Body Visual", options=diagram_options, index=0)

        st.divider()
        st.info("💡 **Active Policy Framework:** 2081 BS Acts (Food Hygiene, Pesticide Mgmt Reg, Agri Investment Decade, 16th Plan) are pre-loaded.")

    client = get_groq_client(active_api_key)

    tab_text, tab_scan = st.tabs(["✍️ Type Question", "📷 Scan Question from Picture"])
    target_question = ""

    with tab_text:
        typed_question = st.text_area(
            "Enter Subjective Agriculture Question:",
            height=130,
            placeholder="e.g., Define Integrated Pest Management (IPM). Illustrate its hierarchical components and analyze the regulatory and strategic measures required to minimize pesticide residue hazards in Nepal. [10]",
        )
        if st.button("Generate Master Answer", type="primary", key="btn_text"):
            if not typed_question.strip():
                st.warning("Please type a question before generating.")
            else:
                target_question = typed_question

    with tab_scan:
        uploaded_file = st.file_uploader(
            "Upload photo of exam question (Handwritten or Printed):",
            type=["png", "jpg", "jpeg", "webp"],
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Question", width=380)

            if st.button("Transcribe & Generate Answer", type="primary", key="btn_scan"):
                if not client:
                    st.error("Please supply a valid Groq API Key.")
                else:
                    with st.spinner("Connecting to vision engine..."):
                        try:
                            available_models = get_available_models(client)
                            _, vision_model = select_best_models(available_models)
                            extracted_q = extract_question_from_image(client, image, vision_model)
                            st.success(f"**Transcribed:** {extracted_q}")
                            target_question = extracted_q
                        except Exception as e:
                            st.error(f"Vision OCR Error: {e}")

    # Answer Execution Block
    if target_question:
        if not client:
            st.error("No active Groq API Key found. Please add GROQ_API_KEY to `.streamlit/secrets.toml`.")
            return

        with st.spinner("Auto-selecting optimal Groq model and architecting answer..."):
            try:
                available_models = get_available_models(client)
                text_model, _ = select_best_models(available_models)
                
                answer, executed_model = generate_model_answer(
                    client=client,
                    question=target_question,
                    marks=marks,
                    diagram_type=selected_diagram,
                    text_model=text_model,
                    fallback_models=available_models,
                )

                st.divider()
                st.markdown(f'<span class="model-badge">⚡ Engine: {executed_model}</span>', unsafe_allow_html=True)
                st.subheader(f"📝 Model Answer ({marks} Marks)")
                
                # Render inside readable container
                st.markdown(answer)

                st.download_button(
                    label="📥 Download Answer as Markdown",
                    data=answer,
                    file_name=f"loksewa_model_answer_{marks}marks.md",
                    mime="text/markdown",
                )

            except Exception as e:
                st.error(f"Generation Engine Error: {e}")

if __name__ == "__main__":
    main()
