"""
Job Matcher Module
Matches candidate resumes against job descriptions using TF-IDF NLP Cosine Similarity
combined with categorized skill overlap ratios, producing fully explainable match scores.
"""

import os
from typing import Dict, List, Any
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobMatcher:
    """Intelligent job matching engine with explainable AI reasoning."""

    def __init__(self, jobs_csv_path: str = None):
        if jobs_csv_path is None:
            # Default to data/jobs.csv relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            jobs_csv_path = os.path.join(base_dir, "data", "jobs.csv")

        self.jobs_csv_path = jobs_csv_path
        self.jobs_df = self._load_jobs()

    def _load_jobs(self) -> pd.DataFrame:
        """Loads and cleans job descriptions from CSV."""
        if not os.path.exists(self.jobs_csv_path):
            # Create a default dataframe if file missing
            return pd.DataFrame()
        df = pd.read_csv(self.jobs_csv_path)
        # Clean string columns
        for col in ["job_title", "category", "required_skills", "preferred_skills", "description"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
        return df

    def _split_skills(self, skill_str: str) -> List[str]:
        """Splits comma-separated skill string and cleans each skill token."""
        if not skill_str:
            return []
        tokens = [s.strip() for s in skill_str.split(",") if s.strip()]
        return tokens

    def match_resume(
        self,
        resume_text: str,
        candidate_skills: List[str],
        category_filter: str = "All Categories"
    ) -> List[Dict[str, Any]]:
        """
        Calculates cosine similarity and skill overlap between candidate resume
        and every job in the dataset, returning ranked results with explainable breakdowns.
        """
        if self.jobs_df.empty:
            return []

        # Filter jobs by category if requested
        df = self.jobs_df.copy()
        if category_filter and category_filter != "All Categories":
            df = df[df["category"] == category_filter]
            if df.empty:
                df = self.jobs_df.copy()

        # Build corpus for TF-IDF Vectorizer
        job_corpus = []
        for _, row in df.iterrows():
            combined = f"{row['job_title']} {row['required_skills']} {row['preferred_skills']} {row['description']}"
            job_corpus.append(combined)

        all_documents = [resume_text] + job_corpus

        # Compute TF-IDF Matrix and Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform(all_documents)
            # Row 0 is the resume; rows 1..N are jobs
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        except Exception:
            cosine_sims = [0.3] * len(df)

        candidate_skills_lower = {s.lower() for s in candidate_skills}

        results = []
        for idx, (_, row) in enumerate(df.iterrows()):
            required_list = self._split_skills(row.get("required_skills", ""))
            preferred_list = self._split_skills(row.get("preferred_skills", ""))

            # Identify matching & missing required skills
            matched_required = []
            missing_required = []
            for req in required_list:
                if req.lower() in candidate_skills_lower or any(cand in req.lower() for cand in candidate_skills_lower):
                    matched_required.append(req)
                else:
                    missing_required.append(req)

            # Identify matching & missing preferred skills
            matched_preferred = []
            missing_preferred = []
            for pref in preferred_list:
                if pref.lower() in candidate_skills_lower or any(cand in pref.lower() for cand in candidate_skills_lower):
                    matched_preferred.append(pref)
                else:
                    missing_preferred.append(pref)

            all_matched = sorted(list(set(matched_required + matched_preferred)))

            # Calculate Ratios
            req_ratio = len(matched_required) / max(len(required_list), 1)
            pref_ratio = len(matched_preferred) / max(len(preferred_list), 1)
            nlp_sim = float(cosine_sims[idx]) if idx < len(cosine_sims) else 0.0

            # Weighted Hybrid Score:
            # 55% Required Skills Match + 15% Preferred Skills Match + 30% NLP Context Sim
            raw_score = (req_ratio * 0.55) + (pref_ratio * 0.15) + (nlp_sim * 0.30)
            
            # Bonus boost if candidate has high skill coverage
            if req_ratio >= 0.8:
                raw_score += 0.10
            elif req_ratio >= 0.5:
                raw_score += 0.05

            match_pct = round(min(98.5, max(15.0, raw_score * 100)), 1)

            # Fit tier
            if match_pct >= 80:
                fit_level = "🔥 Exceptional Fit"
                fit_color = "#10B981"
            elif match_pct >= 65:
                fit_level = "✅ Strong Match"
                fit_color = "#3B82F6"
            elif match_pct >= 50:
                fit_level = "⚡ Moderate Fit"
                fit_color = "#F59E0B"
            else:
                fit_level = "🌱 Growth Opportunity"
                fit_color = "#6B7280"

            # Explainable AI Reasoning sentences
            if all_matched:
                matched_reason = f"Matched because you have: {', '.join(all_matched[:6])}"
            else:
                matched_reason = "Limited overlap with required core competencies."

            if missing_required:
                missing_reason = f"Missing core required skills: {', '.join(missing_required)}"
            else:
                missing_reason = "All primary required skills are satisfied! Great job."

            # Why Candidate matches summary
            job_title = row.get("job_title", "Job Role")
            if req_ratio >= 0.6:
                why_text = (
                    f"Your background aligns well with {job_title}. You demonstrate strong foundational "
                    f"competencies in {', '.join(matched_required[:3])}, meeting {int(req_ratio*100)}% "
                    f"of the core requirements."
                )
            else:
                why_text = (
                    f"You have transferable skills in {', '.join(all_matched[:3]) if all_matched else 'related tech'}, "
                    f"but developing {', '.join(missing_required[:3])} will significantly strengthen your candidacy."
                )

            results.append({
                "job_id": row.get("job_id", f"JOB_{idx}"),
                "job_title": job_title,
                "category": row.get("category", "General"),
                "experience_level": row.get("experience_level", "All Levels"),
                "min_experience_years": row.get("min_experience_years", 0),
                "salary_range": row.get("salary_range", "Competitive"),
                "description": row.get("description", ""),
                "required_skills": required_list,
                "preferred_skills": preferred_list,
                "match_percentage": match_pct,
                "fit_level": fit_level,
                "fit_color": fit_color,
                "matched_skills": all_matched,
                "missing_required": missing_required,
                "missing_preferred": missing_preferred,
                "matched_reason": matched_reason,
                "missing_reason": missing_reason,
                "why_text": why_text,
                "nlp_cosine_similarity": round(nlp_sim * 100, 1),
                "required_coverage_pct": int(req_ratio * 100)
            })

        # Sort descending by match percentage
        results.sort(key=lambda x: x["match_percentage"], reverse=True)
        return results

    def get_skill_gap_for_job(
        self,
        job_title: str,
        candidate_skills: List[str]
    ) -> Dict[str, Any]:
        """Provides a deep-dive skill gap breakdown for any selected job role."""
        job_matches = self.jobs_df[self.jobs_df["job_title"] == job_title]
        if job_matches.empty:
            return {}

        row = job_matches.iloc[0]
        required_list = self._split_skills(row.get("required_skills", ""))
        preferred_list = self._split_skills(row.get("preferred_skills", ""))
        candidate_set = {s.lower() for s in candidate_skills}

        matched_req = [s for s in required_list if s.lower() in candidate_set or any(c in s.lower() for c in candidate_set)]
        missing_req = [s for s in required_list if s not in matched_req]

        matched_pref = [s for s in preferred_list if s.lower() in candidate_set or any(c in s.lower() for c in candidate_set)]
        missing_pref = [s for s in preferred_list if s not in matched_pref]

        total_req = max(len(required_list), 1)
        coverage = round((len(matched_req) / total_req) * 100, 1)

        return {
            "job_title": job_title,
            "category": row.get("category"),
            "description": row.get("description"),
            "salary_range": row.get("salary_range"),
            "required_skills": required_list,
            "preferred_skills": preferred_list,
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "coverage_percentage": coverage
        }
