"""
AI Resume Analyzer & Job Matcher
Build & Automated Validation Suite
Verifies all components, datasets, modules, databases, and dependencies.
"""

import sys
import os
import py_compile
import pandas as pd
import sqlite3

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_build():
    print("=" * 60)
    print("🚀 STARTING AI RESUME ANALYZER PROJECT BUILD & AUDIT")
    print("=" * 60)

    # 1. Python Environment Check
    print(f"\n[1/7] Python Runtime: {sys.version.split()[0]} on {sys.platform}")

    # 2. Syntax Compilation Check
    print("\n[2/7] Compiling all Python source files...")
    py_files = [
        "app.py",
        "modules/resume_parser.py",
        "modules/skill_extractor.py",
        "modules/resume_scorer.py",
        "modules/job_matcher.py",
        "modules/recommendations.py",
        "modules/database.py",
        "assets/sample_resumes/create_samples.py"
    ]
    for pf in py_files:
        try:
            py_compile.compile(pf, doraise=True)
            print(f"  ✓ Compiled: {pf}")
        except Exception as e:
            print(f"  ✗ Compilation Error in {pf}: {e}")
            sys.exit(1)

    # 3. Import Check
    print("\n[3/7] Verifying dependencies and libraries...")
    try:
        import streamlit
        import pypdf
        import pdfplumber
        import sklearn
        import pandas
        import plotly
        import nltk
        import reportlab
        print("  ✓ All required libraries imported successfully.")
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        sys.exit(1)

    # 4. Jobs Dataset Verification
    print("\n[4/7] Verifying data/jobs.csv...")
    jobs_path = os.path.join("data", "jobs.csv")
    if not os.path.exists(jobs_path):
        print("  ✗ data/jobs.csv not found!")
        sys.exit(1)
    df = pd.read_csv(jobs_path)
    print(f"  ✓ jobs.csv found with {len(df)} job roles and columns: {list(df.columns)}")
    assert len(df) >= 10, "Job dataset should have at least 10 roles"

    # 5. SQLite Database Verification
    print("\n[5/7] Verifying SQLite database initialization...")
    from modules.database import init_db, save_analysis, get_history
    init_db()
    db_path = os.path.join("data", "resume_history.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_history'")
        table = cur.fetchone()
        conn.close()
        if table:
            print(f"  ✓ Database verified: {db_path} (table: analysis_history)")
        else:
            print("  ✗ Database table missing!")
            sys.exit(1)

    # 6. Sample Resumes Verification
    print("\n[6/7] Verifying sample PDF resumes...")
    samples = [
        "sample_python_developer.pdf",
        "sample_data_scientist.pdf",
        "sample_fresher_webdev.pdf"
    ]
    for s in samples:
        sp = os.path.join("assets", "sample_resumes", s)
        if os.path.exists(sp) and os.path.getsize(sp) > 500:
            print(f"  ✓ Verified sample PDF: {s} ({os.path.getsize(sp)} bytes)")
        else:
            print(f"  ✗ Missing or corrupt sample PDF: {s}")
            sys.exit(1)

    # 7. End-to-End Pipeline Stress Test on all 3 sample profiles
    print("\n[7/7] Testing end-to-end NLP & AI pipeline across all 3 profiles...")
    from modules.resume_parser import ResumeParser
    from modules.skill_extractor import SkillExtractor
    from modules.resume_scorer import ResumeScorer
    from modules.job_matcher import JobMatcher
    from modules.recommendations import RecommendationEngine

    parser = ResumeParser()
    extractor = SkillExtractor()
    scorer = ResumeScorer()
    matcher = JobMatcher()
    recommender = RecommendationEngine()

    for s in samples:
        sp = os.path.join("assets", "sample_resumes", s)
        with open(sp, "rb") as f:
            pdf_bytes = f.read()

        parsed = parser.parse_all(pdf_bytes)
        assert parsed["success"], f"Failed to parse {s}"

        skills = extractor.extract_skills(parsed["raw_text"])
        assert skills["total_skills_count"] > 5, f"Too few skills extracted from {s}"

        score = scorer.calculate_score(parsed, skills)
        assert 0 <= score["total_score"] <= 100, f"Invalid score for {s}"

        matches = matcher.match_resume(parsed["raw_text"], skills["all_skills"])
        assert len(matches) > 0, f"No job matches for {s}"

        recs = recommender.generate_recommendations(matches, skills["all_skills"])
        assert len(recs["portfolio_projects"]) > 0, f"No recommendations for {s}"

        top_match = matches[0]
        print(f"  ✓ [{s}] -> {parsed['candidate_name']} | Skills: {skills['total_skills_count']} | Score: {score['total_score']}/100 | Top Fit: {top_match['job_title']} ({top_match['match_percentage']}%)")

    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL! All modules and data verified.")
    print("=" * 60)

if __name__ == "__main__":
    run_build()
