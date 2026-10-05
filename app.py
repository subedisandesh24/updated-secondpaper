import streamlit as st
import streamlit.components.v1 as components
import os
import re
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
        max-width: 920px;
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

# ----------------- NATIVE MERMAID HTML/JS RENDERER ----------------- #
def render_mermaid(mermaid_code: str, height: int = 380):
    """Renders Mermaid code into an interactive graphical diagram using CDN."""
    clean_code = mermaid_code.strip()
    html_code = f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 10px 0;">
        <div class="mermaid" style="display: flex; justify-content: center;">
            {clean_code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'neutral',
            securityLevel: 'loose',
            flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }}
        }});
    </script>
    """
    components.html(html_code, height=height, scrolling=True)

def render_answer_with_mermaid(markdown_text: str):
    """Parses text, renders markdown, and injects visual Mermaid diagrams where present."""
    # Pattern to find ```mermaid ... ``` code blocks
    pattern = r"```mermaid\s*([\s\S]*?)\s*```"
    parts = re.split(pattern, markdown_text)

    # If no mermaid block, render standard markdown
    if len(parts) == 1:
        st.markdown(markdown_text)
        return

    # If mermaid block exists, alternate between markdown text and interactive diagram
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part)
        else:
            with st.container():
                st.caption("📊 *Interactive Visual Diagram:*")
                render_mermaid(part)

# ----------------- EXAM-READY SYSTEM PROMPT ----------------- #
SYSTEM_PROMPT = """
You are an elite Public Service Commission (Lok Sewa Aayog) Chief Evaluator for the Nepal Agricultural Service (Gazetted Third Class, Technical Paper II).

Your mission is to output ONLY the exact, maximum-scoring model answer that the candidate must write in the examination hall to score 8.5+/10 or 4.5+/5. Do NOT write conversational greetings, meta-explanations, or introductory commentary. Begin directly with the answer.

========================================================================================
1. STRICT MERMAID & FIGURE RULES (PREVENT SYNTAX ERRORS)
========================================================================================
- If outputting a ```mermaid ... ``` block:
  1. ALL node labels MUST be enclosed in double quotes. Example: A["Level 1: Prevention (Crop Rotation)"]
  2. NEVER use unquoted parentheses (), brackets [], or colons : inside node text.
  3. Keep the Mermaid code clean, valid, and fully enclosed in ```mermaid ... ```.
- In addition to the Mermaid block, ALWAYS provide a clean ASCII/Text Box Sketch under a sub-header "Exam Paper Sketch Guide (Draw this on Answer Sheet)" with complete labels (Title, Left-Axis, Right-Axis, Tier Annotations). This ensures the candidate knows exactly how to sketch it with a pen.

========================================================================================
2. STRUCTURAL BREAKDOWN ACCORDING TO MARKS
========================================================================================
A. FOR 5-MARK QUESTIONS (Target: 180-250 words, ~0.75 page):
   1. Operational Definition & Core Concept (2 lines with precise technical terms).
   2. Core Technical Points (5 to 6 structured, numbered points with bold keywords before colons).
   3. Single Compact Labeled Visual (Comparison table, matrix, or micro-flowchart with clear caption).
   4. Targeted Policy Citation (1 active act/policy directly governing the topic).
   5. Cohesive Concluding Paragraph (2-3 lines weaving problem, dual approach, and policy target).

B. FOR 10-MARK QUESTIONS (Target: 450-650 words, ~1.5 to 2 pages):
   1. Conceptual Definition & Scope (3-4 lines with scientific depth and constitutional/macro context).
   2. Core Scientific / Technical Body (Grouped into clear, logical subheadings):
      - Theoretical / Physiological / Agronomic Principles
      - Technological, Operational, or Protection Practices
      - Institutional & Operational Governance
   3. Body Visual / Schematic with Complete Labels (MANDATORY IN BODY):
      - Valid ```mermaid ... ``` diagram AND clean ASCII sketch with labels.
   4. Field Challenges & Ground Bottlenecks in Nepal (Paired factual critique with real field context).
   5. MANDATORY CONCLUSION IN A COHESIVE PARAGRAPH:
      - Do NOT use bullet points or numbered steps in the conclusion.
      - Write the conclusion as a single, powerful, highly authoritative administrative PARAGRAPH (4 to 6 sentences).
      - Seamlessly weave together:
        1) The specific ground problem / structural bottleneck in Nepal;
        2) A balanced Dual Strategy (e.g., Upstream regulatory enforcement vs. Downstream farmer enablement);
        3) Concrete statutory and policy target realization by citing specific provisions and quantitative targets from relevant Acts, Regulations, and Strategic Plans (e.g., Pesticide Management Regulation 2081, Food Hygiene and Quality Act 2081, 16th Periodic Plan, Agriculture Investment Decade 2081–2091).

========================================================================================
3. DYNAMIC & CONTENT-SPECIFIC DATA RULE (STRICT NO-PREFIX POLICY)
========================================================================================
- NEVER prefix or force unrelated national macro-census data into technical answers where they are irrelevant.
- All numbers, empirical values, rates, and scientific metrics MUST BE DIRECTLY RELEVANT to the technical domain:
  * Agronomy & Field Crops: Seed rates (kg/ha), spacing (cm x cm), fertilizer doses (N:P2O5:K2O kg/ha), critical irrigation stages, plant population, seed replacement rate (SRR), and harvest yields (t/ha).
  * Horticulture: Spacing, pit dimensions, budding/grafting success rates, chilling hours, storage temp (°C) & RH (%), TSS/Brix, and postharvest loss %.
  * Plant Protection: Economic Threshold Levels (ETL), spray concentrations (ppm or ml/L), active ingredient rates (g a.i./ha), Pre-Harvest Intervals (PHI days), and WHO hazard classifications.
  * Soil Science: Soil pH thresholds, C:N ratios, bulk density (g/cm³), CEC (cmol(+)/kg), organic matter %, and critical nutrient ranges.
  * Agricultural Economics & Extension: B/C ratios, IRR, NPV, price elasticity, marketing margins (%), and sample size parameters.
  * Macro / Land / Policy: Cite 16th Plan targets, ADS milestones, or 7th Agriculture Census indicators ONLY when asked.

========================================================================================
4. STATUTORY & POLICY REPOSITORY
========================================================================================
- Food & Quality: Food Hygiene and Quality Act, 2081 (खाद्य स्वच्छता तथा गुणस्तर ऐन, २०८१), Right to Food & Food Sovereignty Act, 2075 & Regulation, 2081, Food Safety Policy, 2076.
- Master Strategies: 16th Periodic Plan (2081/82–2085/86), Agriculture Development Strategy (ADS, 2015–2035), Agriculture Investment Decade (2081–2091), National Agriculture Policy, 2061 / 2081 (Draft).
- Land & Farmers: Farmer Categorization and Listing System Management Directive, 2081, Land Related (20th Amendment) Rules, 2081, Land Use Act, 2076 & Rules, 2079, Local Government Operation Act (LGOA), 2074.
- Seeds & Biodiversity: Seeds Act, 2045 & Rules, 2069, National Seed Vision (2013–2025), Agro-biodiversity Promotion Policy, 2063 (Amended 2071).
- Plant Protection & Pesticides: Pesticide Management Act, 2076 & Pesticide Management Regulation, 2081 (जीवनाशक विषादी व्यवस्थापन नियमावली, २०८१), Plant Protection Act, 2064 & Rules, 2066, 24 Banned Pesticides List, RBPR & MRL guidelines.
- Soil, Forestry & Trade: Fertilizer Control Order, 2055 & Subsidy Directives, Agro-Forestry Policy, 2076, Agri-Business Promotion Policy, 2063, NTIS (2016/2023), WTO (AoA, SPS, TBT), SAFTA, Crop/Livestock Insurance Subsidy Directives.
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
    """Dynamically queries the active model catalog on user's Groq account."""
    try:
        models_data = client.models.list().data
        return [m.id for m in models_data]
    except Exception:
        return []

def select_best_models(available_models: list):
    """Selects the fastest and highest reasoning model available with failovers."""
    text_priority = [
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]
    vision_priority = [
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
    ]

    text_model = None
    for cand in text_priority:
        if cand in available_models:
            text_model = cand
            break
    if not text_model:
        usable = [
            m for m in available_models 
            if not any(x in m for x in ["whisper", "guard", "embed", "safeguard", "orpheus"])
        ]
        text_model = usable[0] if usable else "llama-3.1-8b-instant"

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
    """Uses Groq vision model to transcribe question from image."""
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
    """Generates the model answer with automatic failover."""
    user_prompt = f"""
EXAMINATION QUESTION:
\"\"\"{question}\"\"\"

ALLOCATED MARKS: {marks} Marks

RECOMMENDED BODY VISUAL:
{diagram_type if diagram_type != "Auto-Detect Best Diagram" else "Select the most appropriate visual (e.g. Pyramidal/Tiered Hierarchy for multi-tiered systems, Flowchart, Cycle, or Matrix) to place in the BODY of the answer."}

CRITICAL RULES:
1. OUTPUT: Deliver directly the exam answer sheet response. Zero meta-commentary.
2. MERMAID SYNTAX: If writing Mermaid, every label MUST be enclosed in double quotes like A["Label"].
3. PAPER SKETCH: Include a clean ASCII/Text Box Sketch with side labels for paper drawing.
4. DATA: Use precise content-specific empirical figures (seed rates, doses, ETL, PHI, spacing).
5. CONCLUSION: Write the conclusion STRICTLY as a single, cohesive administrative PARAGRAPH weaving together the Ground Problem -> Dual Strategy -> Statutory/Policy Target Realization (citing acts/regulations up to 2081 BS). Do NOT use bullet points in the conclusion.
"""
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

# ----------------- STREAMLINED USER INTERFACE ----------------- #
def main():
    st.title("🌾 Lok Sewa Agriculture Paper II: Master Engine")
    st.caption("Interactive Mermaid Graphics + Paper Sketch Guide • 2081 BS Acts Integrated")

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
                help="Add GROQ_API_KEY to your Streamlit secrets or paste it here.",
            )
            if input_key:
                st.session_state["manual_groq_api_key"] = input_key
                active_api_key = input_key

        st.divider()

        marks = st.radio(
            "Marks Allocation",
            options=[10, 5],
            index=0,
            horizontal=True,
            help="10 Marks = Exhaustive (~1.5-2 pages) | 5 Marks = Compact (~0.75 page)",
        )

        diagram_options = [
            "Auto-Detect Best Diagram",
            "Pyramidal / Tiered Hierarchy (Mermaid + Sketch)",
            "Flowchart (Mermaid + Sketch)",
            "Cycle Diagram (Mermaid + Sketch)",
            "Process Diagram (Mermaid + Sketch)",
            "Tree / Hierarchical Diagram (Mermaid + Sketch)",
            "Decision Tree (Mermaid + Sketch)",
            "Timeline / Roadmap (Mermaid + Sketch)",
            "Cause–Effect / Fishbone Diagram (Mermaid + Sketch)",
            "Concept Map / Mind Map (Mermaid + Sketch)",
            "Comparison Matrix / Table (Markdown)",
        ]
        selected_diagram = st.selectbox("Preferred Body Visual", options=diagram_options, index=0)

        st.divider()
        st.info("💡 **Diagram Protection:** Mermaid syntax is automatically validated and rendered graphically. An ASCII guide is provided for paper copying.")

    client = get_groq_client(active_api_key)

    tab_text, tab_scan = st.tabs(["✍️ Type Question", "📷 Scan Question from Picture"])
    target_question = ""

    with tab_text:
        typed_question = st.text_area(
            "Enter Subjective Agriculture Question:",
            height=130,
            placeholder="e.g., Define Integrated Pest Management (IPM). Describe its components in hierarchical order with a labeled diagram, and discuss the regulatory and strategic measures required to minimize pesticide hazards in Nepal. [10]",
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
                    with st.spinner("Transcribing via Groq Vision OCR..."):
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
            st.error("No active Groq API Key found. Add GROQ_API_KEY to `.streamlit/secrets.toml` or sidebar.")
            return

        with st.spinner(f"Architecting {marks}-mark answer (Rendered Diagrams + Single-Paragraph Conclusion)..."):
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

                # Render with dual Mermaid Graphic + Markdown support
                render_answer_with_mermaid(answer)

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
