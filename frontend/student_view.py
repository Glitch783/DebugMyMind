import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_ace import st_ace

from frontend.components import (
    render_misconception_badge,
    render_explanation_box,
    render_exercise_box,
    submit_to_backend,
    fetch_student_history
)

def render_student_view():
    st.markdown('<h1 class="main-title">Coding Misconception Detector</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Submit Python code to detect programming misconceptions and receive instant learning guidance.</p>', unsafe_allow_html=True)

    # 1. Sidebar Inputs
    st.sidebar.subheader("👤 Student Profile")
    st.session_state["student_name"] = st.sidebar.text_input(
        "Your Name",
        value=st.session_state["student_name"],
        placeholder="Enter your name"
    )
    st.session_state["student_id"] = st.sidebar.text_input(
        "Student ID",
        value=st.session_state["student_id"],
        placeholder="Enter student ID (e.g. S1001)"
    )

    # 2. Main Code Editor Section
    st.subheader("💻 Submit Your Code")
    st.write("Write or paste your Python code inside the editor below, then click **Analyse My Code**:")

    # Initial template code in the editor
    default_code = 'def divide_numbers(a, b):\n    # Write Python code to divide numbers\n    return a // b'
    
    code = st_ace(
        value=default_code,
        language="python",
        theme="monokai",
        height=300,
        font_size=14,
        tab_size=4,
        wrap=True,
        key="student_ace_editor"
    )

    if st.button("Analyse My Code"):
        # Profile validation
        if not st.session_state["student_name"].strip() or not st.session_state["student_id"].strip():
            st.warning("⚠️ Please provide both your **Name** and **Student ID** in the sidebar to run the analysis.")
        elif not code.strip():
            st.error("⚠️ Code submission cannot be empty.")
        else:
            with st.spinner("Analyzing code patterns, executing safety check, and retrieving conceptual matches..."):
                try:
                    result = submit_to_backend(
                        student_id=st.session_state["student_id"].strip(),
                        student_name=st.session_state["student_name"].strip(),
                        code=code
                    )
                    
                    st.success("✅ Analysis Complete!")
                    
                    # Renders color pill badge based on confidence level
                    render_misconception_badge(
                        confidence=result["confidence"],
                        name=result["misconception_name"]
                    )
                    
                    # Explanations and targeted exercises
                    render_explanation_box(result["explanation"])
                    render_exercise_box(result["micro_exercise"])

                    # Technical details details inside expander
                    with st.expander("🛠️ View Execution Output & Statically Flagged Flaws"):
                        if result["error_trace"]:
                            st.subheader("Console Output / Error Log")
                            st.code(result["error_trace"], language="python")
                        else:
                            st.write("✅ Dynamic check completed: **No runtime error encountered.**")
                        
                        st.subheader("Static Flaws (AST Tokens)")
                        if result["ast_flags"]:
                            for flag in result["ast_flags"]:
                                st.markdown(f"- 🚩 Found AST Anti-Pattern: `{flag}`")
                        else:
                            st.write("✅ Static check completed: **No major syntactic anti-patterns caught.**")
                            
                except Exception as e:
                    st.error(f"❌ Could not complete submission: {str(e)}")

    st.markdown("---")

    # 3. Personal History Lookup Section
    st.subheader("📊 My Learning History")
    
    # Pre-fill lookup field with the current student profile ID for ease of use
    lookup_id = st.text_input(
        "Enter Student ID to retrieve history",
        value=st.session_state["student_id"],
        placeholder="e.g. S1001"
    )

    if lookup_id.strip():
        with st.spinner("Fetching historical submissions..."):
            history = fetch_student_history(lookup_id.strip())
            
        if history:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"#### Last {len(history)} Submissions")
                for index, sub in enumerate(history):
                    # Expander title formatting
                    time_str = sub["timestamp"]
                    if "T" in time_str:
                        time_str = time_str.split("T")[0] + " " + time_str.split("T")[1][:5]
                    else:
                        time_str = time_str[:16]
                        
                    title = f"🕒 {time_str} | {sub['misconception_name']} (Confidence: {sub['confidence']*100:.0f}%)"
                    with st.expander(title):
                        st.markdown("**Submitted Code:**")
                        st.code(sub["code"], language="python")
                        
                        if sub["error_trace"]:
                            st.markdown("**Error Trace:**")
                            st.code(sub["error_trace"], language="python")
                            
                        st.markdown(f"💡 **Explanation:** {sub['explanation']}")
                        st.markdown(f"🛠️ **Target Exercise:** {sub['exercise']}")
                        
            with col2:
                st.markdown("#### Progress Analytics")
                # Aggregate misconceptions
                valid_misconceptions = [s["misconception_name"] for s in history if s["misconception_name"]]
                if valid_misconceptions:
                    counts = pd.Series(valid_misconceptions).value_counts().reset_index()
                    counts.columns = ["Misconception", "Count"]
                    top_3 = counts.head(3)
                    
                    fig = px.bar(
                        top_3,
                        x="Count",
                        y="Misconception",
                        orientation="h",
                        title="Top 3 Recurring Misconceptions",
                        labels={"Count": "Occurrences", "Misconception": ""},
                        template="plotly_dark",
                        color="Count",
                        color_continuous_scale="Viridis"
                    )
                    
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        title_font_family="'Outfit', sans-serif",
                        font_family="'Outfit', sans-serif",
                        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickmode='linear', dtick=1),
                        yaxis=dict(showgrid=False),
                        coloraxis_showscale=False,
                        height=280
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    most_repeated = top_3.iloc[0]["Misconception"]
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin-top: 10px;">
                            🎯 <strong>Your most repeated mistake is:</strong> <code>{most_repeated}</code>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.info("No misconception patterns registered in history yet.")
        else:
            st.info("No submission records found for this Student ID.")
    else:
        st.info("Provide a Student ID to query historical records.")
