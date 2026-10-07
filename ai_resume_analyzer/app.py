"""
AI Resume Analyzer & Job Matcher
Streamlit Application
Main entry point for intelligent resume parsing, scoring, job matching,
skill gap analysis, and personalized career recommendations.
"""

import os
import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import internal modules
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.resume_scorer import ResumeScorer
from modules.job_matcher import JobMatcher
from modules.recommendations import RecommendationEngine
from modules.database import init_db, save_analysis, get_history, clear_history


# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer & Job Matcher",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize local SQLite DB
init_db()

# -----------------------------------------------------------------------------
# Custom CSS for Premium Design & Modern Typography
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        border-radius: 16px;
        padding: 32px 36px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #FFFFFF, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #C7D2FE;
        max-width: 850px;
        line-height: 1.5;
    }
    
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
    }
    
    .metric-sub {
        font-size: 0.85rem;
        color: #475569;
        margin-top: 4px;
    }
    
    .skill-badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4338CA;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px 4px;
        border: 1px solid #C7D2FE;
    }
    
    .skill-badge-green {
        display: inline-block;
        background: #ECFDF5;
        color: #065F46;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px 4px;
        border: 1px solid #A7F3D0;
    }
    
    .skill-badge-red {
        display: inline-block;
        background: #FEF2F2;
        color: #991B1B;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px 4px;
        border: 1px solid #FECACA;
    }
    
    .skill-badge-amber {
        display: inline-block;
        background: #FFFBEB;
        color: #92400E;
        font-weight: 600;
        font-size: 0.8rem;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 3px 4px;
        border: 1px solid #FDE68A;
    }
    
    .job-card {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .job-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
    }
    
    .job-meta {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 12px;
    }
    
    .explain-box {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 0.9rem;
        color: #334155;
    }
    
    .explain-missing {
        background: #FFF1F2;
        border-left: 4px solid #E11D48;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 0.9rem;
        color: #881337;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Module Instances Cache
# -----------------------------------------------------------------------------
@st.cache_resource
def get_services():
    parser = ResumeParser()
    extractor = SkillExtractor()
    scorer = ResumeScorer()
    matcher = JobMatcher()
    recommender = RecommendationEngine()
    return parser, extractor, scorer, matcher, recommender


parser, extractor, scorer, matcher, recommender = get_services()


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def load_sample_resume_bytes(filename: str) -> bytes:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(base_dir, "assets", "sample_resumes", filename)
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            return f.read()
    return b""


# -----------------------------------------------------------------------------
# Sidebar Configuration & Resume Upload / Sample Selector
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💼 AI Resume Analyzer")
    st.markdown("Automated Resume Intelligence & Job Matching")
    st.markdown("---")

    st.subheader("1. Resume Source")
    source_mode = st.radio(
        "Choose Upload Mode:",
        ["Upload PDF Resume", "Use Pre-loaded Demo Resume"],
        help="Upload your own PDF resume or select a verified test resume."
    )

    resume_bytes = None
    resume_name = None

    if source_mode == "Upload PDF Resume":
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF format)",
            type=["pdf"],
            help="Select a standard PDF document (max 10MB)"
        )
        if uploaded_file is not None:
            resume_bytes = uploaded_file.read()
            resume_name = uploaded_file.name
    else:
        sample_choice = st.selectbox(
            "Select a Sample Portfolio Resume:",
            [
                "sample_python_developer.pdf (Alex Morgan - Python Backend)",
                "sample_data_scientist.pdf (Sophia Chen - Data & AI Scientist)",
                "sample_fresher_webdev.pdf (Rahul Sharma - Fresher Software Eng)"
            ]
        )
        sample_filename = sample_choice.split(" ")[0]
        resume_bytes = load_sample_resume_bytes(sample_filename)
        resume_name = sample_filename
        st.info(f"Loaded demo resume: **{resume_name}**")

    st.markdown("---")
    st.subheader("2. Job Matching Preferences")

    # Category filter
    all_categories = ["All Categories"]
    if not matcher.jobs_df.empty and "category" in matcher.jobs_df.columns:
        all_categories.extend(sorted(matcher.jobs_df["category"].unique().tolist()))

    selected_category = st.selectbox(
        "Target Job Domain:",
        all_categories,
        index=0
    )

    top_n_jobs = st.slider("Number of Top Recommendations:", min_value=3, max_value=10, value=5)

    st.markdown("---")
    st.markdown("### 📊 Database & History")
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        history_records = get_history(limit=50)
        st.caption(f"Saved Analyses: **{len(history_records)}**")
    with col_hist2:
        if st.button("Clear DB", help="Reset local SQLite history"):
            clear_history()
            st.rerun()

    st.markdown("---")
    st.markdown("<small style='color: #64748B;'>Antigravity IDE • Python NLP Project</small>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Panel View
# -----------------------------------------------------------------------------
# Header Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">AI Resume Analyzer & Job Matcher</div>
    <div class="hero-subtitle">
        Leverage Natural Language Processing, TF-IDF Cosine Similarity, and ATS heuristics 
        to evaluate resume completeness, identify skill gaps, and match with ideal tech job roles with explainable reasoning.
    </div>
</div>
""", unsafe_allow_html=True)


# If no resume loaded
if not resume_bytes:
    st.info("👈 Please upload a PDF resume or pick a pre-loaded sample resume from the sidebar to begin analysis.")

    # Demonstration of System Features
    st.markdown("### 🚀 Core Platform Capabilities")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">NLP Profile Parser</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B; margin: 8px 0;">Automated Extraction</div>
            <p style="color: #64748B; font-size: 0.88rem;">
                Accurately extracts candidate contact info, educational qualifications, projects, experience, and categorized technical & soft skills.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f_col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">0–100 ATS Scorer</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B; margin: 8px 0;">Transparent Scoring</div>
            <p style="color: #64748B; font-size: 0.88rem;">
                7-dimensional evaluation formula checking contact completeness, technical depth, soft skills, projects, experience, and certifications.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Explainable Matcher</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #1E293B; margin: 8px 0;">Why You Match</div>
            <p style="color: #64748B; font-size: 0.88rem;">
                TF-IDF Cosine Similarity + skill overlap ratio showing exact matching skills, missing core competencies, and targeted upskilling advice.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# -----------------------------------------------------------------------------
# Resume Processing Pipeline
# -----------------------------------------------------------------------------
with st.spinner("🤖 Analyzing resume with NLP engine..."):
    # 1. Parse text & profile
    parsed = parser.parse_all(resume_bytes)

    if not parsed.get("success"):
        st.error(f"❌ Resume Extraction Error: {parsed.get('error', 'Unknown parsing error')}")
        st.stop()

    # 2. Extract Skills
    skills = extractor.extract_skills(parsed["raw_text"])

    # 3. Calculate Resume Score
    score_result = scorer.calculate_score(parsed, skills)

    # 4. Job Matching
    job_matches = matcher.match_resume(
        resume_text=parsed["raw_text"],
        candidate_skills=skills["all_skills"],
        category_filter=selected_category
    )

    top_matches = job_matches[:top_n_jobs]
    best_job = top_matches[0] if top_matches else {}

    # 5. Career & Learning Recommendations
    recommendations = recommender.generate_recommendations(top_matches, skills["all_skills"])

    # Save to SQLite History (avoid repeating on immediate re-renders by tracking in session_state)
    last_saved_key = f"{resume_name}_{parsed['char_count']}"
    if st.session_state.get("last_saved") != last_saved_key:
        save_analysis(
            candidate_name=parsed.get("candidate_name", "Anonymous"),
            email=parsed.get("email", "N/A"),
            phone=parsed.get("phone", "N/A"),
            resume_score=score_result["total_score"],
            top_job_match=best_job.get("job_title", "General"),
            top_match_percent=best_job.get("match_percentage", 0.0),
            skills_count=skills["total_skills_count"],
            skills_preview=", ".join(skills["all_skills"][:6]),
            file_name=resume_name
        )
        st.session_state["last_saved"] = last_saved_key


# -----------------------------------------------------------------------------
# Top Metric Highlights Card
# -----------------------------------------------------------------------------
h_col1, h_col2, h_col3, h_col4 = st.columns(4)

with h_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Candidate Profile</div>
        <div class="metric-value" style="font-size: 1.3rem;">{parsed.get('candidate_name', 'Not Found')}</div>
        <div class="metric-sub">{parsed.get('email', 'No email detected')}</div>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    total_score = score_result["total_score"]
    badge = score_result["tier_badge"]
    color = score_result["theme_color"]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">ATS Resume Score</div>
        <div class="metric-value" style="color: {color};">{total_score} <span style="font-size: 1rem; color: #64748B;">/ 100</span></div>
        <div class="metric-sub" style="font-weight: 600; color: {color};">{badge}</div>
    </div>
    """, unsafe_allow_html=True)

with h_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Skills Detected</div>
        <div class="metric-value">{skills['total_skills_count']}</div>
        <div class="metric-sub">{skills['tech_skills_count']} Tech • {skills['soft_skills_count']} Soft Skills</div>
    </div>
    """, unsafe_allow_html=True)

with h_col4:
    best_title = best_job.get("job_title", "N/A")
    best_pct = best_job.get("match_percentage", 0.0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Top Job Match</div>
        <div class="metric-value" style="font-size: 1.3rem; color: #2563EB;">{best_title}</div>
        <div class="metric-sub" style="font-weight: 700; color: #10B981;">{best_pct}% Match Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Resume Overview",
    "📊 Resume Score & Radar",
    "🎯 Top Job Matches",
    "🔍 Skill Gap Deep Dive",
    "💡 Action Recommendations",
    "🕒 Analysis History"
])


# =============================================================================
# TAB 1: RESUME OVERVIEW
# =============================================================================
with tab1:
    st.subheader("Candidate Overview & Extracted Data")
    
    ov_col1, ov_col2 = st.columns([1, 1])

    with ov_col1:
        st.markdown("#### 👤 Contact & Identification")
        st.write(f"**Full Name:** {parsed.get('candidate_name', 'Not Found')}")
        st.write(f"**Email Address:** {parsed.get('email') or '⚠️ Not Found in Resume'}")
        st.write(f"**Phone Number:** {parsed.get('phone') or '⚠️ Not Found in Resume'}")
        
        links = parsed.get("links", {})
        if links.get("linkedin"):
            st.write(f"**LinkedIn:** [{links['linkedin']}](https://{links['linkedin'].replace('https://', '')})")
        if links.get("github"):
            st.write(f"**GitHub:** [{links['github']}](https://{links['github'].replace('https://', '')})")
        if links.get("portfolio"):
            st.write(f"**Portfolio:** [{links['portfolio']}](https://{links['portfolio'].replace('https://', '')})")

        st.markdown("#### 🎓 Education History")
        edu_list = parsed.get("education", [])
        if edu_list:
            for edu in edu_list:
                st.markdown(f"- **{edu.get('degree')}** in *{edu.get('field')}* ({edu.get('year')})")
        else:
            st.warning("No explicit degree found. Consider adding degree titles like B.Tech, B.S., M.S., or BCA.")

    with ov_col2:
        st.markdown("#### 💼 Professional Experience Summary")
        exp_info = parsed.get("experience", {})
        st.write(f"**Estimated Seniority Level:** {exp_info.get('experience_level', 'Fresher')}")
        if exp_info.get("estimated_years", 0) > 0:
            st.write(f"**Documented Experience:** ~{exp_info.get('estimated_years')} Years")
        
        titles = exp_info.get("detected_titles", [])
        if titles:
            st.write(f"**Recognized Titles:** {', '.join(titles)}")

        st.markdown("#### 🚀 Projects & Portfolio")
        proj_info = parsed.get("projects", {})
        if proj_info.get("has_projects_section"):
            st.success(f"Projects section detected (~{proj_info.get('estimated_project_count')} major project items)")
        else:
            st.warning("No dedicated Projects section identified.")

        st.markdown("#### 📜 Certifications & Credentials")
        cert_list = parsed.get("certifications", [])
        if cert_list:
            for c in cert_list:
                st.markdown(f"- 🏅 {c}")
        else:
            st.info("No recognized vendor certifications found.")

    st.markdown("---")
    with st.expander("📄 View Full Cleaned Resume Text"):
        st.text_area("Extracted Resume Text", parsed.get("raw_text", ""), height=280)


# =============================================================================
# TAB 2: RESUME SCORE & RADAR
# =============================================================================
with tab2:
    st.subheader("ATS Resume Score Breakdown (0–100)")
    
    score_col1, score_col2 = st.columns([1, 1])

    with score_col1:
        # Donut Chart for Score
        fig_donut = go.Figure(go.Pie(
            values=[score_result["total_score"], 100 - score_result["total_score"]],
            labels=["Achieved", "Room for Growth"],
            hole=0.75,
            marker_colors=[score_result["theme_color"], "#E2E8F0"],
            hoverinfo="label+value",
            textinfo="none"
        ))
        fig_donut.update_layout(
            annotations=[dict(
                text=f"<b>{score_result['total_score']}</b><br><span style='font-size:14px;color:#64748B;'>/ 100</span>",
                x=0.5, y=0.5, font_size=28, showarrow=False
            )],
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=260
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown(f"""
        <div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
            <span style="font-size: 1.15rem; font-weight: 700; color: {score_result['theme_color']};">
                {score_result['tier_badge']}
            </span>
            <p style="color: #475569; font-size: 0.9rem; margin-top: 6px;">
                {score_result['tier_description']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with score_col2:
        # Radar Chart of 7 Dimensions
        dimensions = list(score_result["breakdown"].keys())
        pct_values = [score_result["breakdown"][k]["percentage"] for k in dimensions]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=pct_values + [pct_values[0]],
            theta=dimensions + [dimensions[0]],
            fill='toself',
            fillcolor='rgba(79, 70, 229, 0.25)',
            line=dict(color='#4F46E5', width=2),
            name="Resume Score"
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False,
            margin=dict(t=25, b=25, l=35, r=35),
            height=280
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Detailed Dimension Breakdown Bars
    st.markdown("#### 📊 Evaluation Dimension Points")
    b_cols = st.columns(3)
    for idx, (cat_name, cat_data) in enumerate(score_result["breakdown"].items()):
        col_idx = idx % 3
        with b_cols[col_idx]:
            st.markdown(f"**{cat_name}** ({cat_data['score']}/{cat_data['max_score']} pts)")
            st.progress(cat_data['score'] / cat_data['max_score'])
            st.caption(f"Status: **{cat_data['status']}** ({cat_data['percentage']}%)")

    st.markdown("---")
    str_col, imp_col = st.columns(2)
    with str_col:
        st.markdown("#### ✅ Detected Key Strengths")
        for s in score_result.get("strengths", []):
            st.markdown(f"- 🟢 {s}")
    with imp_col:
        st.markdown("#### ⚡ Priority Improvement Areas")
        for imp in score_result.get("improvements", []):
            st.markdown(f"- 🟠 {imp}")


# =============================================================================
# TAB 3: TOP JOB MATCHES & EXPLAINABLE REASONING
# =============================================================================
with tab3:
    st.subheader(f"Top {len(top_matches)} Matched Job Roles")
    st.caption("Matched using NLP Cosine Similarity on job descriptions + Categorized required & preferred skill overlap.")

    # Match percentage comparison chart
    job_titles = [j["job_title"] for j in top_matches]
    job_pcts = [j["match_percentage"] for j in top_matches]
    fit_colors = [j["fit_color"] for j in top_matches]

    fig_bar = px.bar(
        x=job_pcts,
        y=job_titles,
        orientation='h',
        color=job_pcts,
        color_continuous_scale="Blues",
        labels={"x": "Match Percentage (%)", "y": "Job Role"},
        title="Job Fit Comparison"
    )
    fig_bar.update_layout(height=260, margin=dict(t=35, b=10, l=10, r=10))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Render each job as an explainable card
    for rank, job in enumerate(top_matches, start=1):
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="job-title">#{rank} {job['job_title']}</span>
                        <span style="margin-left: 10px; font-weight: 700; color: {job['fit_color']};">{job['fit_level']}</span>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #2563EB;">
                        {job['match_percentage']}%
                    </div>
                </div>
                <div class="job-meta">
                    Category: <b>{job['category']}</b> | Level: <b>{job['experience_level']}</b> | Estimated Salary: <b>{job['salary_range']}</b>
                </div>
                <div class="explain-box">
                    <b>💡 Explainable AI Match:</b><br/>
                    {job['matched_reason']}
                </div>
                <div class="explain-missing">
                    <b>⚠️ Missing Competencies:</b><br/>
                    {job['missing_reason']}
                </div>
                <p style="color: #475569; font-size: 0.9rem; margin-top: 10px;">
                    <i>{job['why_text']}</i>
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Inspect Skills Breakdown for {job['job_title']}"):
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    st.markdown("**✅ Matching Skills in Resume:**")
                    if job["matched_skills"]:
                        badges_html = " ".join([f"<span class='skill-badge-green'>{s}</span>" for s in job["matched_skills"]])
                        st.markdown(badges_html, unsafe_allow_html=True)
                    else:
                        st.write("No direct overlap found.")
                with m_c2:
                    st.markdown("**❌ Missing Required Skills:**")
                    if job["missing_required"]:
                        badges_html = " ".join([f"<span class='skill-badge-red'>{s}</span>" for s in job["missing_required"]])
                        st.markdown(badges_html, unsafe_allow_html=True)
                    else:
                        st.success("You possess 100% of the core required skills!")

                    if job["missing_preferred"]:
                        st.markdown("<br/>**🌟 Missing Preferred/Bonus Skills:**", unsafe_allow_html=True)
                        badges_html = " ".join([f"<span class='skill-badge-amber'>{s}</span>" for s in job["missing_preferred"]])
                        st.markdown(badges_html, unsafe_allow_html=True)


# =============================================================================
# TAB 4: SKILL GAP DEEP DIVE
# =============================================================================
with tab4:
    st.subheader("Interactive Skill Gap Analysis")
    st.caption("Select any target job position to compare your current skill repertoire against industry job expectations.")

    all_job_titles = matcher.jobs_df["job_title"].tolist() if not matcher.jobs_df.empty else []
    
    selected_gap_job = st.selectbox(
        "Choose Target Job Title to Inspect:",
        all_job_titles,
        index=0 if all_job_titles else None
    )

    if selected_gap_job:
        gap_info = matcher.get_skill_gap_for_job(selected_gap_job, skills["all_skills"])

        cov_pct = gap_info.get("coverage_percentage", 0.0)
        
        # Coverage metric row
        g_col1, g_col2, g_col3 = st.columns(3)
        with g_col1:
            st.metric("Required Skills Coverage", f"{cov_pct}%")
        with g_col2:
            st.metric("Matched Core Skills", len(gap_info.get("matched_required", [])))
        with g_col3:
            st.metric("Missing Core Skills", len(gap_info.get("missing_required", [])))

        st.progress(cov_pct / 100.0)

        st.markdown("---")
        gap_c1, gap_c2 = st.columns(2)

        with gap_c1:
            st.markdown("#### ✅ Skills You Have")
            st.caption("Skills detected in your resume that fulfill requirements:")
            all_acquired = gap_info.get("matched_required", []) + gap_info.get("matched_preferred", [])
            if all_acquired:
                badges = " ".join([f"<span class='skill-badge-green'>{s}</span>" for s in all_acquired])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.write("None of the specific required skills were detected.")

        with gap_c2:
            st.markdown("#### ❌ Critical Skills to Acquire")
            st.caption("Essential skills for this role missing from your resume:")
            missing_core = gap_info.get("missing_required", [])
            if missing_core:
                badges = " ".join([f"<span class='skill-badge-red'>{s}</span>" for s in missing_core])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.success("All core required skills are present in your resume!")

            missing_bonus = gap_info.get("missing_preferred", [])
            if missing_bonus:
                st.markdown("<br/>**⭐ Bonus Skills that Set You Apart:**", unsafe_allow_html=True)
                badges_b = " ".join([f"<span class='skill-badge-amber'>{s}</span>" for s in missing_bonus])
                st.markdown(badges_b, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📋 Role Description & Responsibilities")
        st.info(gap_info.get("description", "No description available."))


# =============================================================================
# TAB 5: ACTION RECOMMENDATIONS & PORTFOLIO PROJECTS
# =============================================================================
with tab5:
    st.subheader("Personalized Career & Resume Roadmap")
    st.caption("Tailored learning steps, portfolio project ideas, and ATS optimizations to qualify for top roles.")

    # 1. High Demand Skills to Learn
    st.markdown("#### 1. 🎯 Priority Skills to Learn")
    rec_skills = recommendations.get("recommended_skills", [])
    if rec_skills:
        df_skills = pd.DataFrame(rec_skills)
        df_skills.rename(columns={"skill": "Skill to Learn", "occurrences": "Demand Across Matches", "priority": "Priority Level"}, inplace=True)
        st.dataframe(df_skills, use_container_width=True, hide_index=True)
    else:
        st.write("No major skill gaps identified across top matched roles!")

    st.markdown("---")

    # 2. Portfolio Project Ideas
    st.markdown("#### 2. 🛠️ Recommended Portfolio Projects to Build")
    st.caption(f"Curated for the **{recommendations.get('dominant_track', 'Software')}** career track:")
    
    proj_cols = st.columns(len(recommendations.get("portfolio_projects", [])))
    for p_idx, project in enumerate(recommendations.get("portfolio_projects", [])):
        with proj_cols[p_idx]:
            st.markdown(f"""
            <div class="metric-card" style="height: 100%;">
                <div class="metric-title">{project['difficulty']} Level</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #1E293B; margin: 6px 0;">{project['title']}</div>
                <p style="font-size: 0.85rem; color: #64748B;"><b>Tech Stack:</b> {project['tech_stack']}</p>
                <p style="font-size: 0.82rem; color: #334155;">{project['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Recommended Industry Certifications
    st.markdown("#### 3. 🏅 Targeted Industry Certifications")
    cert_cols = st.columns(2)
    for c_idx, cert in enumerate(recommendations.get("recommended_certifications", [])):
        c_target = cert_cols[c_idx % 2]
        with c_target:
            st.markdown(f"- **{cert['name']}** (*{cert['issuer']}*) — Level: `{cert['level']}`")

    st.markdown("---")

    # 4. Resume Formatting & ATS Optimization Tips
    st.markdown("#### 4. 📝 ATS Resume Enhancement Guidelines")
    for tip in recommendations.get("resume_enhancement_tips", []):
        st.markdown(f"**{tip['category']}:** {tip['tip']}")

    # 5. Action Verbs Cheatsheet
    st.markdown("#### 5. ⚡ Power Action Verbs for Bullet Points")
    for category, verbs in recommendations.get("action_verbs", []):
        st.markdown(f"- **{category}:** `{verbs}`")


# =============================================================================
# TAB 6: ANALYSIS HISTORY & EXPORT
# =============================================================================
with tab6:
    st.subheader("Analysis History & Export Report")
    st.caption("Locally persisted records in SQLite database.")

    history_records = get_history(limit=50)

    if history_records:
        df_hist = pd.DataFrame(history_records)
        df_display = df_hist[[
            "id", "timestamp", "candidate_name", "resume_score",
            "top_job_match", "top_match_percent", "skills_count", "file_name"
        ]].copy()
        df_display.rename(columns={
            "id": "ID",
            "timestamp": "Analyzed At",
            "candidate_name": "Candidate",
            "resume_score": "Score",
            "top_job_match": "Top Match",
            "top_match_percent": "Match %",
            "skills_count": "Skills #",
            "file_name": "File"
        }, inplace=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No saved analysis history yet.")

    st.markdown("---")
    st.markdown("#### 📥 Export Current Analysis Report")

    # Prepare export JSON
    export_payload = {
        "candidate_name": parsed.get("candidate_name"),
        "email": parsed.get("email"),
        "phone": parsed.get("phone"),
        "resume_score": score_result["total_score"],
        "score_tier": score_result["tier_badge"],
        "top_matches": [
            {
                "title": j["job_title"],
                "match_percentage": j["match_percentage"],
                "matched_skills": j["matched_skills"],
                "missing_skills": j["missing_required"]
            }
            for j in top_matches
        ],
        "extracted_skills": skills["all_skills"],
        "priority_skills_to_learn": [s["skill"] for s in recommendations.get("recommended_skills", [])]
    }

    export_json_str = json.dumps(export_payload, indent=2)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            label="Download Analysis Summary (JSON)",
            data=export_json_str,
            file_name=f"{parsed.get('candidate_name', 'resume')}_analysis.json",
            mime="application/json"
        )
    with col_exp2:
        text_summary = f"""AI RESUME ANALYZER & JOB MATCHER REPORT
==================================================
Candidate: {parsed.get('candidate_name')}
Email: {parsed.get('email')}
Phone: {parsed.get('phone')}
Resume Score: {score_result['total_score']} / 100 ({score_result['tier_badge']})

TOP JOB MATCHES:
--------------------------------------------------
"""
        for rank, j in enumerate(top_matches, start=1):
            text_summary += f"{rank}. {j['job_title']} - {j['match_percentage']}%\n"
            text_summary += f"   Matched Skills: {', '.join(j['matched_skills'])}\n"
            text_summary += f"   Missing Skills: {', '.join(j['missing_required'])}\n\n"

        st.download_button(
            label="Download Plaintext Summary (.txt)",
            data=text_summary,
            file_name=f"{parsed.get('candidate_name', 'resume')}_summary.txt",
            mime="text/plain"
        )
