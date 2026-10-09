import streamlit as st
from frontend.components import inject_custom_css
from frontend.student_view import render_student_view
from frontend.instructor_view import render_instructor_view

# Configure Streamlit page layout and title
st.set_page_config(
    page_title="Coding Misconception Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global premium design system styles
inject_custom_css()

# Initialize session state for persistence across navigation
if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""
if "student_id" not in st.session_state:
    st.session_state["student_id"] = ""

# Sidebar navigation
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #38bdf8; font-weight: 800; font-size: 1.4rem; margin: 0;">IEEE TechForGood</h2>
        <span style="color: #64748b; font-size: 0.85rem;">Internship Project 2026</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

view_selection = st.sidebar.radio(
    "Navigation Portal",
    ["Student Portal", "Instructor Dashboard"],
    index=0
)

st.sidebar.markdown("---")

# Render active portal view
if view_selection == "Student Portal":
    render_student_view()
else:
    render_instructor_view()
