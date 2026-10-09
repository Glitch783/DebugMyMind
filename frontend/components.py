import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def inject_custom_css():
    """Injects high-end, premium custom CSS to style the Streamlit interface."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap');
        
        /* Font overrides */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        code, pre, .stCodeBlock {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Glassmorphism sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Metric cards */
        div[data-testid="metric-container"] {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 15px 20px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        /* Premium headers */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.02em !important;
        }
        
        .main-title {
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .main-subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 2rem;
        }

        /* Customize submit button */
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100%;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.4) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_misconception_badge(confidence: float, name: str):
    """Renders a colorful, glassmorphic pill badge showing confidence percentage."""
    if confidence > 0.8:
        # High confidence (red-orange)
        bg = "rgba(239, 68, 68, 0.15)"
        border = "#ef4444"
        text = "#fca5a5"
    elif confidence >= 0.6:
        # Medium confidence (orange)
        bg = "rgba(249, 115, 22, 0.15)"
        border = "#f97316"
        text = "#fdbb2d"
    else:
        # Low confidence (yellow)
        bg = "rgba(234, 179, 8, 0.15)"
        border = "#eab308"
        text = "#fef08a"

    badge_html = f"""
    <div style="
        display: inline-flex;
        align-items: center;
        background: {bg};
        border: 1px solid {border};
        color: {text};
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    ">
        <span style="display:inline-block; width: 8px; height: 8px; border-radius:50%; background: {border}; margin-right: 8px;"></span>
        {name} &nbsp;|&nbsp; Confidence: {confidence*100:.1f}%
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def render_explanation_box(explanation: str):
    """Renders plain-English explanation card using modern styling."""
    html = f"""
    <div style="
        background: rgba(14, 165, 233, 0.08);
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    ">
        <h4 style="margin: 0 0 8px 0; color: #38bdf8; font-weight: 600; font-size: 1.1rem; display: flex; align-items: center;">
            💡 Conceptual Explanation
        </h4>
        <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
            {explanation}
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_exercise_box(exercise: str):
    """Renders targeted micro-exercise card using modern styling."""
    html = f"""
    <div style="
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    ">
        <h4 style="margin: 0 0 8px 0; color: #34d399; font-weight: 600; font-size: 1.1rem; display: flex; align-items: center;">
            🛠️ Target Micro-Exercise
        </h4>
        <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">
            {exercise}
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Helper API functions
def submit_to_backend(student_id: str, student_name: str, code: str) -> dict:
    url = f"{BACKEND_URL}/submit"
    payload = {
        "student_id": student_id,
        "student_name": student_name,
        "code": code
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Backend submission failed: {response.text}")

def fetch_student_history(student_id: str) -> list:
    url = f"{BACKEND_URL}/history/{student_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_class_analytics() -> dict:
    url = f"{BACKEND_URL}/analytics"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def fetch_top_misconceptions() -> list:
    url = f"{BACKEND_URL}/top-misconceptions"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_students_summary() -> list:
    url = f"{BACKEND_URL}/students-summary"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_instructor_metrics() -> dict:
    url = f"{BACKEND_URL}/instructor-metrics"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"total_submissions": 0, "unique_students": 0, "top_misconception": "None"}
