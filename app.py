import os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

# Modular helper imports
from job_matcher import load_job_roles, rank_job_roles
from report_generator import create_pdf_report
from resume_coach import get_langchain_coach_response
from resume_parser import extract_text
from roadmap_generator import generate_learning_roadmap
from skill_extractor import extract_skills, load_skill_dictionary
from text_cleaner import clean_resume_text

# Load environment variables
load_dotenv()

# --- Page Configuration & Custom Theme ---
st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 500; }
    .stTabs [data-baseweb="tab-list"] { gap: 32px; border-bottom: 1px solid rgba(128, 128, 128, 0.2); }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 0px; font-size: 15px; border: none; }
    .stTabs [aria-selected="true"] { background-color: transparent; font-weight: 600; color: #3b82f6 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: 600; color: #3b82f6; }
    </style>
""", unsafe_allow_html=True)

st.title("AI Resume Analyzer")
st.markdown("Evaluate your technical skills against industry roles, identify gaps, and get a personalized learning roadmap.")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    
    st.divider()
    st.header("Optional: Custom Job")
    custom_jd = st.text_area("Paste a specific job description here:")
    
    st.divider()
    st.info("""
    **Responsible AI Notice**
    - Educational guidance & match metrics only, not hiring decisions.
    - Protected attributes (age, gender, etc.) are ignored.
    - Resumes are processed in memory and not permanently stored.
    """)

# --- Main Application Logic ---
if uploaded_file:
    with st.spinner("Analyzing your resume..."):
        # 1. Parse and clean resume text
        raw_text = extract_text(uploaded_file)
        cleaned_text = clean_resume_text(raw_text)
        
        # 2. Load dataset resources
        try:
            skill_dict = load_skill_dictionary()
            jobs_df = load_job_roles()
        except Exception as e:
            st.error(f"Error loading data files: {e}. Please ensure data files exist in the data/ directory.")
            st.stop()
            
        # 3. Process optional custom job description
        if custom_jd.strip():
            jd_found = extract_skills(clean_resume_text(custom_jd), skill_dict)
            jd_flat_skills = sorted(set(skill for skills in jd_found.values() for skill in skills))
            if jd_flat_skills:
                custom_row = pd.DataFrame([{"role_name": "Custom Job (Pasted)", "required_skills": ", ".join(jd_flat_skills)}])
                jobs_df = pd.concat([custom_row, jobs_df], ignore_index=True)
            else:
                st.sidebar.warning("No technical skills detected in the pasted job description.")
        
        # 4. Extract candidate skills and rank matched job roles
        categorized_skills = extract_skills(cleaned_text, skill_dict)
        flat_skills = sorted(set(skill for skills in categorized_skills.values() for skill in skills))
        ranked_roles = rank_job_roles(flat_skills, jobs_df)
        
    if not flat_skills:
        st.warning("We couldn't detect any technical skills in this document. Please ensure it is a valid technical resume.")
    else:
        st.success(f"Successfully extracted {len(flat_skills)} technical skills.")
        
        # --- Dashboard Navigation Tabs ---
        tab1, tab2, tab3, tab4 = st.tabs(["Role Recommendations", "Skill Gap Analysis", "Learning Roadmap", "AI Resume Coach"])
        top_3 = ranked_roles[:3]
        
        # --- TAB 1: Role Recommendations ---
        with tab1:
            st.subheader("Top Role Matches")
            chart_df = pd.DataFrame({
                "Role": [r["role_name"] for r in top_3],
                "Match Score (%)": [r["match_score"] for r in top_3]
            })
            
            fig = px.bar(
                chart_df, 
                x="Match Score (%)", 
                y="Role", 
                orientation='h',
                color="Match Score (%)",
                color_continuous_scale="Blues",
                range_x=[0, 100],
                text_auto='.1f'
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'}, 
                margin=dict(l=0, r=0, t=30, b=0), 
                height=300,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display Extracted Skills grouped by Category
            st.subheader("Extracted Skills")
            for cat, skills in categorized_skills.items():
                st.markdown(f"**{cat}:** " + ", ".join(f"`{s}`" for s in skills))

        # --- TAB 2: Skill Gap Analysis ---
        with tab2:
            st.subheader("Deep Dive: Skill Analysis")
            role_map = {r["role_name"]: r for r in top_3}
            selected_role_name = st.selectbox("Select a target role to analyze:", list(role_map.keys()))
            selected_role = role_map[selected_role_name]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Match Score", f"{selected_role['match_score']:.1f}%")
            col2.metric("Skills Found", len(selected_role['found_skills']))
            col3.metric("Skills Missing", len(selected_role['missing_skills']))
            
            st.divider()
            colA, colB = st.columns(2)
            with colA:
                st.markdown("### Strengths (Found)")
                if selected_role['found_skills']:
                    for skill in selected_role['found_skills']:
                        st.markdown(f"- {skill.title()}")
                else:
                    st.write("None of the core skills for this role were found.")
                    
            with colB:
                st.markdown("### Gaps (Missing)")
                if selected_role['missing_skills']:
                    for skill in selected_role['missing_skills']:
                        st.markdown(f"- {skill.title()}")
                else:
                    st.write("No missing skills. Perfect match.")

        # --- TAB 3: Learning Roadmap ---
        with tab3:
            st.subheader(f"Action Plan: {selected_role['role_name']}")
            if st.button("Generate AI Roadmap"):
                with st.spinner("Crafting your personalized 4-week roadmap..."):
                    api_key = os.getenv("GEMINI_API_KEY")
                    roadmap_text = generate_learning_roadmap(
                        selected_role["role_name"], 
                        selected_role["missing_skills"], 
                        api_key
                    )
                    st.session_state["generated_roadmap"] = roadmap_text
                    
            if st.session_state.get("generated_roadmap"):
                roadmap_text = st.session_state["generated_roadmap"]
                st.markdown(roadmap_text)
                
                # Downloadable PDF Report Option
                pdf_bytes = create_pdf_report(
                    selected_role['role_name'],
                    selected_role['match_score'],
                    selected_role['found_skills'],
                    selected_role['missing_skills'],
                    roadmap_text
                )
                st.download_button(
                    label="Download PDF Analysis Report",
                    data=pdf_bytes,
                    file_name=f"resume_report_{selected_role['role_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

        # --- TAB 4: AI Resume Coach (LangChain Assistant) ---
        with tab4:
            st.subheader("AI Resume Coach & Content Assistant")
            st.markdown("Ask natural language questions to refine bullet points, improve ATS keywords, or get tailored career advice.")

            # Initialize chat message history
            if "coach_chat_history" not in st.session_state:
                st.session_state["coach_chat_history"] = [
                    {
                        "role": "assistant", 
                        "content": f"Hello! I am your AI Resume Coach powered by LangChain. I have loaded your full resume text and target role context (**{selected_role['role_name']}**). How can I assist you in optimizing your resume today?"
                    }
                ]

            # 1. Render all conversation messages FIRST
            for msg in st.session_state["coach_chat_history"]:
                st.chat_message(msg["role"]).write(msg["content"])

            # 2. Capture Chat Input
            if user_query := st.chat_input("Ask how to rewrite bullet points, add metrics, or improve skills..."):
                st.session_state["coach_chat_history"].append({"role": "user", "content": user_query})
                
                current_roadmap = st.session_state.get("generated_roadmap", "")
                api_key = os.getenv("GEMINI_API_KEY")
                
                coach_reply = get_langchain_coach_response(
                    messages_history=st.session_state["coach_chat_history"][:-1],
                    user_query=user_query,
                    raw_resume_text=raw_text,
                    categorized_skills=categorized_skills,
                    target_role=selected_role,
                    job_roles_df=jobs_df,
                    skill_dict_df=skill_dict,
                    generated_roadmap=current_roadmap,
                    api_key=api_key
                )
                
                st.session_state["coach_chat_history"].append({"role": "assistant", "content": coach_reply})
                st.rerun()

else:
    st.info("Please upload your resume (PDF or DOCX) in the sidebar to begin the analysis.")
