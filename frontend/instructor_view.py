import streamlit as st
import pandas as pd
import plotly.express as px

from frontend.components import (
    fetch_class_analytics,
    fetch_students_summary,
    fetch_instructor_metrics
)

def render_instructor_view():
    st.markdown('<h1 class="main-title">Instructor Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Class-wide insights, key metrics, and targeted mapping of student learning obstacles.</p>', unsafe_allow_html=True)

    # 1. Fetch metrics and display them in cards
    metrics = fetch_instructor_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Submissions Logged", metrics["total_submissions"])
    with col2:
        st.metric("Active Enrolled Students", metrics["unique_students"])
    with col3:
        # Show top misconception
        st.metric("Top Weak Concept", metrics["top_misconception"])

    st.markdown("---")

    # 2. Main Analytics Charts
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.subheader("📊 Class-Wide Misconception Breakdown")
        analytics = fetch_class_analytics()
        
        if analytics:
            df = pd.DataFrame(list(analytics.items()), columns=["Misconception", "Count"])
            # Sort to get top 10
            df = df.sort_values(by="Count", ascending=True).tail(10)
            
            fig = px.bar(
                df,
                x="Count",
                y="Misconception",
                orientation="h",
                title="Top Misconceptions (by Occurrence Count)",
                labels={"Count": "Times Identified", "Misconception": ""},
                template="plotly_dark",
                color="Count",
                color_continuous_scale="Plasma"
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_family="'Outfit', sans-serif",
                font_family="'Outfit', sans-serif",
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickmode='linear', dtick=1),
                yaxis=dict(showgrid=False),
                coloraxis_showscale=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No submission records found to analyze.")

    with right_col:
        st.subheader("💡 Key Pedagogical Recommendations")
        st.markdown(
            f"""
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); padding: 20px; border-radius: 12px;">
                <h4 style="color: #818cf8; margin-top: 0; font-size: 1.15rem; font-weight: 600;">🎯 Action Item for This Week</h4>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                    Your class's primary hurdle is currently <strong>{metrics['top_misconception']}</strong>.
                    Consider dedicating the first 10 minutes of the next lecture to a live tracing session or mini-quiz targeted specifically at this conceptual blocker.
                </p>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 12px; margin-top: 15px;">
                <h4 style="color: #94a3b8; margin-top: 0; font-size: 1.15rem; font-weight: 600;">ℹ️ About These Insights</h4>
                <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin-bottom: 0;">
                    The analytics show aggregates of student mistakes computed via a dual NLP similarity mapping and static compiler check pipeline. This enables detecting *conceptual errors* (why the code is structured that way) rather than just syntax typos.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 3. Class Data Frame view
    st.subheader("👥 Student Misconception Tracking Ledger")
    st.write("Overview of all student profiles, total attempts, and their most frequently repeated coding misconception:")
    
    with st.spinner("Compiling student records..."):
        students_summary = fetch_students_summary()

    if students_summary:
        df_students = pd.DataFrame(students_summary)
        # Reorder and rename columns for display
        df_students = df_students[["student_id", "student_name", "submission_count", "most_common_misconception"]]
        df_students.columns = ["Student ID", "Student Name", "Submissions Count", "Most Frequent Misconception"]
        
        st.dataframe(
            df_students,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No registered students found in database.")
