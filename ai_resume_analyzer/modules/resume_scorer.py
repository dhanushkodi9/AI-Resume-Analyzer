"""
Resume Scorer Module
Calculates a comprehensive 0-100 ATS Resume Score across 7 critical dimensions:
Contact Completeness, Technical Skills, Soft Skills, Education, Projects,
Work Experience, and Certifications.
"""

from typing import Dict, Any, List


class ResumeScorer:
    """Intelligent scoring engine providing granular feedback and radar metrics."""

    def calculate_score(
        self,
        parsed_data: Dict[str, Any],
        skills_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates resume completeness and calculates an overall score (0-100)
        along with category breakdowns and actionable feedback.
        """
        breakdown = {}
        strengths: List[str] = []
        improvements: List[str] = []

        # ---------------------------------------------------------------------
        # 1. Contact & Identity Completeness (Max: 10 points)
        # ---------------------------------------------------------------------
        contact_pts = 0
        name = parsed_data.get("candidate_name")
        email = parsed_data.get("email")
        phone = parsed_data.get("phone")
        links = parsed_data.get("links", {})

        if name and name != "Candidate Name Not Found":
            contact_pts += 3
        else:
            improvements.append("Clearly position your full name at the very top of your resume.")

        if email:
            contact_pts += 4
        else:
            improvements.append("Missing contact email address. ATS requires a valid email.")

        if phone:
            contact_pts += 3
        else:
            improvements.append("Missing contact phone number for recruiter outreach.")

        if links.get("linkedin") or links.get("github"):
            contact_pts = min(10, contact_pts + 1)
            strengths.append("Professional profile links (LinkedIn/GitHub) present.")

        breakdown["Contact Information"] = {
            "score": contact_pts,
            "max_score": 10,
            "percentage": int((contact_pts / 10) * 100),
            "status": "Excellent" if contact_pts >= 9 else ("Good" if contact_pts >= 6 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 2. Technical Skills Depth & Diversity (Max: 25 points)
        # ---------------------------------------------------------------------
        tech_skills = skills_data.get("technical_skills", [])
        tech_count = len(tech_skills)
        cat_skills = skills_data.get("categorized_skills", {})

        tech_pts = 0
        if tech_count >= 12:
            tech_pts = 20
        elif tech_count >= 8:
            tech_pts = 16
        elif tech_count >= 5:
            tech_pts = 12
        elif tech_count >= 2:
            tech_pts = 7
        else:
            tech_pts = 3

        # Diversity bonus (up to 5 pts): covers languages, frameworks, and databases/cloud
        diverse_cats = sum(1 for c, sk in cat_skills.items() if len(sk) > 0 and c != "Soft Skills")
        diversity_bonus = min(5, diverse_cats)
        tech_pts = min(25, tech_pts + diversity_bonus)

        if tech_pts >= 20:
            strengths.append(f"Strong technical vocabulary: {tech_count} relevant technical skills detected.")
        else:
            improvements.append("Expand technical skill keywords with current frameworks, databases, and tools.")

        breakdown["Technical Skills"] = {
            "score": tech_pts,
            "max_score": 25,
            "percentage": int((tech_pts / 25) * 100),
            "status": "Excellent" if tech_pts >= 20 else ("Good" if tech_pts >= 14 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 3. Soft Skills (Max: 10 points)
        # ---------------------------------------------------------------------
        soft_skills = skills_data.get("soft_skills", [])
        soft_count = len(soft_skills)

        if soft_count >= 4:
            soft_pts = 10
            strengths.append(f"Demonstrates interpersonal competencies ({soft_count} soft skills highlighted).")
        elif soft_count >= 2:
            soft_pts = 7
        elif soft_count == 1:
            soft_pts = 4
            improvements.append("Highlight more soft skills like Problem Solving, Agile collaboration, or Leadership.")
        else:
            soft_pts = 1
            improvements.append("Add foundational soft skills (e.g. Communication, Teamwork, Critical Thinking).")

        breakdown["Soft Skills"] = {
            "score": soft_pts,
            "max_score": 10,
            "percentage": int((soft_pts / 10) * 100),
            "status": "Excellent" if soft_pts >= 8 else ("Good" if soft_pts >= 5 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 4. Education & Academics (Max: 15 points)
        # ---------------------------------------------------------------------
        education_records = parsed_data.get("education", [])
        edu_pts = 0

        if education_records:
            edu_pts += 8  # Degree found
            # Check if field and year were also recognized
            has_field = any(rec.get("field") != "Engineering / General" for rec in education_records)
            has_year = any(rec.get("year") != "Year not stated" for rec in education_records)
            if has_field:
                edu_pts += 4
            if has_year:
                edu_pts += 3
            strengths.append(f"Clear educational credentials: {education_records[0].get('degree')}.")
        else:
            edu_pts = 4
            improvements.append("Include clear academic degree headings (e.g., B.Tech, B.S., M.S.) and graduation year.")

        edu_pts = min(15, edu_pts)
        breakdown["Education"] = {
            "score": edu_pts,
            "max_score": 15,
            "percentage": int((edu_pts / 15) * 100),
            "status": "Excellent" if edu_pts >= 12 else ("Good" if edu_pts >= 8 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 5. Projects & Practical Work (Max: 15 points)
        # ---------------------------------------------------------------------
        projects_summary = parsed_data.get("projects", {})
        proj_pts = 0

        if projects_summary.get("has_projects_section"):
            proj_pts += 8
            count = projects_summary.get("estimated_project_count", 0)
            if count >= 3:
                proj_pts += 7
                strengths.append("Robust portfolio of hands-on technical projects featured.")
            elif count >= 1:
                proj_pts += 4
            else:
                proj_pts += 2
        else:
            proj_pts = 3
            improvements.append("Add a dedicated 'Projects' section detailing real-world applications and tech stacks.")

        proj_pts = min(15, proj_pts)
        breakdown["Projects"] = {
            "score": proj_pts,
            "max_score": 15,
            "percentage": int((proj_pts / 15) * 100),
            "status": "Excellent" if proj_pts >= 12 else ("Good" if proj_pts >= 8 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 6. Work Experience / Internships (Max: 15 points)
        # ---------------------------------------------------------------------
        exp_summary = parsed_data.get("experience", {})
        exp_pts = 0

        if exp_summary.get("has_experience_section"):
            exp_pts += 8
            if exp_summary.get("estimated_years", 0) > 0 or len(exp_summary.get("detected_titles", [])) > 0:
                exp_pts += 7
                strengths.append(f"Documented professional experience ({exp_summary.get('experience_level')}).")
            else:
                exp_pts += 4
        else:
            exp_pts = 4
            improvements.append("Include internship, freelance, or open-source contribution experience.")

        exp_pts = min(15, exp_pts)
        breakdown["Experience"] = {
            "score": exp_pts,
            "max_score": 15,
            "percentage": int((exp_pts / 15) * 100),
            "status": "Excellent" if exp_pts >= 12 else ("Good" if exp_pts >= 8 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # 7. Certifications & Badges (Max: 10 points)
        # ---------------------------------------------------------------------
        certs = parsed_data.get("certifications", [])
        cert_count = len(certs)
        cert_pts = 0

        if cert_count >= 2:
            cert_pts = 10
            strengths.append(f"Recognized industry certifications: {', '.join(certs[:2])}.")
        elif cert_count == 1:
            cert_pts = 6
            strengths.append(f"Industry certification recognized: {certs[0]}.")
        else:
            cert_pts = 2
            improvements.append("Add credible industry certifications (e.g. AWS Cloud, Azure, HackerRank badges).")

        breakdown["Certifications"] = {
            "score": cert_pts,
            "max_score": 10,
            "percentage": int((cert_pts / 10) * 100),
            "status": "Excellent" if cert_pts >= 8 else ("Good" if cert_pts >= 5 else "Needs Work")
        }

        # ---------------------------------------------------------------------
        # Overall Score Calculation
        # ---------------------------------------------------------------------
        total_score = sum(b["score"] for b in breakdown.values())
        total_score = max(0, min(100, total_score))

        # Grade & Tier Assignment
        if total_score >= 85:
            tier_badge = "🌟 Outstanding"
            tier_desc = "Top 10% ATS Ready. Excellent structure, breadth of skills, and quantifiable achievements."
            color = "#10B981"  # Emerald
        elif total_score >= 70:
            tier_badge = "🚀 Strong & Competitive"
            tier_desc = "Solid resume that passes most ATS filters. Minor optimizations will make it shine."
            color = "#3B82F6"  # Blue
        elif total_score >= 50:
            tier_badge = "⚡ Moderate Potential"
            tier_desc = "Good foundation, but missing critical skill keywords, projects, or clear section hierarchy."
            color = "#F59E0B"  # Amber
        else:
            tier_badge = "⚠️ Needs Major Optimization"
            tier_desc = "Requires restructuring: add missing contact info, projects, and high-demand skills."
            color = "#EF4444"  # Red

        return {
            "total_score": total_score,
            "tier_badge": tier_badge,
            "tier_description": tier_desc,
            "theme_color": color,
            "breakdown": breakdown,
            "strengths": strengths[:4],
            "improvements": improvements[:5]
        }
