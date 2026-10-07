import sys
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.resume_scorer import ResumeScorer
from modules.job_matcher import JobMatcher
from modules.recommendations import RecommendationEngine
from modules.database import init_db, save_analysis, get_history

# Initialize DB
init_db()

with open('assets/sample_resumes/sample_python_developer.pdf', 'rb') as f:
    pdf_bytes = f.read()

parser = ResumeParser()
parsed = parser.parse_all(pdf_bytes)
print("Candidate Name:", parsed["candidate_name"])
print("Email:", parsed["email"])

extractor = SkillExtractor()
skills = extractor.extract_skills(parsed["raw_text"])
print("Skill count:", skills["total_skills_count"])

scorer = ResumeScorer()
score = scorer.calculate_score(parsed, skills)
print("Score:", score["total_score"])

matcher = JobMatcher()
matches = matcher.match_resume(parsed["raw_text"], skills["all_skills"])
top = matches[0]
print(f"Top Role: {top['job_title']} ({top['match_percentage']}%)")
print(f"Matched: {top['matched_reason']}")
print(f"Missing: {top['missing_reason']}")

recommender = RecommendationEngine()
recs = recommender.generate_recommendations(matches, skills["all_skills"])
print("Dominant track:", recs["dominant_track"])

rec_id = save_analysis(
    candidate_name=parsed["candidate_name"],
    email=parsed["email"],
    phone=parsed["phone"],
    resume_score=score["total_score"],
    top_job_match=top["job_title"],
    top_match_percent=top["match_percentage"],
    skills_count=skills["total_skills_count"],
    skills_preview=", ".join(skills["all_skills"][:5]),
    file_name="sample_python_developer.pdf"
)
print("Saved record ID:", rec_id)

history = get_history()
print("History count:", len(history))
print("ALL TESTS PASSED!")
