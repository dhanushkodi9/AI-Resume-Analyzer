"""
Resume Parser Module
Extracts clean text and key profile information (Name, Email, Phone, Education,
Experience, Projects, Certifications) from PDF resumes using pdfplumber and pypdf.
"""

import re
import io
from typing import Dict, Any, List, Optional
import pypdf
import pdfplumber


class ResumeParser:
    """Robust PDF resume extractor and structural text analyzer."""

    def __init__(self):
        # Email regular expression
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            re.IGNORECASE
        )

        # Phone number pattern supporting international (+1, +91) and formats
        self.phone_pattern = re.compile(
            r'(?:(?:\+|0{0,2})[1-9]\d{0,2}[-.\s]?)?'
            r'(?:\(?\d{2,5}\)?[-.\s]?)?'
            r'\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{1,4})?'
        )

        # Common education keywords and degree patterns
        self.degree_patterns = [
            r"\b(?:b\.?tech|b\.?e|bachelor\s+of\s+technology|bachelor\s+of\s+engineering)\b",
            r"\b(?:b\.?s|b\.?sc|bachelor\s+of\s+science)\b",
            r"\b(?:m\.?tech|m\.?e|master\s+of\s+technology|master\s+of\s+engineering)\b",
            r"\b(?:m\.?s|m\.?sc|master\s+of\s+science)\b",
            r"\b(?:bca|bachelor\s+of\s+computer\s+applications)\b",
            r"\b(?:mca|master\s+of\s+computer\s+applications)\b",
            r"\b(?:bba|mba|master\s+of\s+business\s+administration)\b",
            r"\b(?:ph\.?d|doctor\s+of\s+philosophy)\b",
            r"\b(?:diploma\s+in\s+[a-zA-Z\s]+)\b",
            r"\b(?:high\s+school|higher\s+secondary|cbse|icse)\b"
        ]

        # Major fields of study
        self.major_patterns = [
            r"computer\s+science(?:\s+and\s+engineering)?",
            r"information\s+technology",
            r"data\s+science",
            r"artificial\s+intelligence(?:\s+and\s+machine\s+learning)?",
            r"software\s+engineering",
            r"electrical\s+engineering",
            r"electronics\s+and\s+communication",
            r"mechanical\s+engineering",
            r"mathematics(?:\s+and\s+computing)?"
        ]

        # Common words that shouldn't be parsed as candidate names
        self.name_stop_words = {
            "resume", "curriculum", "vitae", "cv", "page", "email", "phone",
            "contact", "summary", "profile", "objective", "experience", "education",
            "skills", "projects", "certifications", "interests", "hobbies", "declaration",
            "developer", "engineer", "analyst", "scientist", "fresher", "senior", "junior"
        }

    def extract_text(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts raw and formatted text from uploaded PDF resume bytes.
        Uses pdfplumber first, falling back to pypdf.
        """
        raw_text = ""
        page_count = 0
        method_used = "pdfplumber"

        # Attempt 1: pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                page_count = len(pdf.pages)
                pages_text = []
                for p in pdf.pages:
                    txt = p.extract_text() or ""
                    pages_text.append(txt)
                raw_text = "\n\n".join(pages_text).strip()
        except Exception:
            raw_text = ""

        # Attempt 2: pypdf fallback if empty or failed
        if not raw_text.strip():
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                page_count = len(reader.pages)
                pages_text = []
                for p in reader.pages:
                    txt = p.extract_text() or ""
                    pages_text.append(txt)
                raw_text = "\n\n".join(pages_text).strip()
                method_used = "pypdf"
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to read PDF document: {str(e)}",
                    "raw_text": "",
                    "page_count": 0,
                    "word_count": 0,
                    "char_count": 0
                }

        cleaned_text = self._clean_text(raw_text)
        word_count = len(cleaned_text.split())
        char_count = len(cleaned_text)

        if word_count < 15:
            return {
                "success": False,
                "error": "Resume text is too short or appears to be a scanned image without OCR text.",
                "raw_text": cleaned_text,
                "page_count": page_count,
                "word_count": word_count,
                "char_count": char_count
            }

        return {
            "success": True,
            "error": None,
            "raw_text": cleaned_text,
            "page_count": max(page_count, 1),
            "word_count": word_count,
            "char_count": char_count,
            "method": method_used
        }

    def _clean_text(self, text: str) -> str:
        """Cleans and standardizes extracted resume text."""
        if not text:
            return ""
        # Normalize non-breaking spaces and unusual whitespace
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        # Replace non-standard bullet characters with standard dash
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219▪■●◆•]', '\n- ', text)
        # Collapse multiple empty lines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        # Remove repeated horizontal spaces
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def parse_candidate_name(self, text: str) -> str:
        """
        Identifies candidate's name typically located in the top 6 lines of resume.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:8]:
            # Skip lines with contact info, URLs or obvious headers
            if any(char in line for char in ['@', 'http', 'www.', '.com', '|', '/', '\\']):
                continue
            if any(term in line.lower() for term in self.name_stop_words):
                continue
            
            # Remove bullets or extra symbols
            clean_line = re.sub(r'[^a-zA-Z\s\.]', '', line).strip()
            tokens = clean_line.split()

            # Typically candidate names are 2 to 4 capitalized words
            if 2 <= len(tokens) <= 4:
                if all(t[0].isupper() for t in tokens if len(t) > 1 and t.isalpha()):
                    return clean_line.title()
                # If typed in ALL CAPS
                if all(t.isupper() for t in tokens if t.isalpha()):
                    return clean_line.title()

        return "Candidate Name Not Found"

    def parse_email(self, text: str) -> Optional[str]:
        """Extracts first valid email address from resume text."""
        matches = self.email_pattern.findall(text)
        if matches:
            # Filter out sample/dummy domains if real ones exist
            return matches[0].strip().lower()
        return None

    def parse_phone(self, text: str) -> Optional[str]:
        """Extracts candidate phone number."""
        matches = self.phone_pattern.findall(text)
        for match in matches:
            clean_digits = re.sub(r'\D', '', match)
            # Valid phone numbers usually have 10 to 13 digits
            if 10 <= len(clean_digits) <= 13:
                return match.strip()
        return None

    def parse_links(self, text: str) -> Dict[str, Optional[str]]:
        """Extracts LinkedIn, GitHub, and Portfolio URLs."""
        linkedin = None
        github = None
        portfolio = None

        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+', text, re.I)
        if linkedin_match:
            linkedin = linkedin_match.group(0)

        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-]+', text, re.I)
        if github_match:
            github = github_match.group(0)

        web_match = re.search(r'(?:https?://)?[a-zA-Z0-9_\-]+\.(?:vercel\.app|github\.io|netlify\.app|dev|me)', text, re.I)
        if web_match:
            portfolio = web_match.group(0)

        return {
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio
        }

    def parse_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts educational qualifications, degrees, majors, and graduation years.
        """
        education_records = []
        lower_text = text.lower()

        # Find degrees
        for deg_pat in self.degree_patterns:
            matches = list(re.finditer(deg_pat, lower_text, re.IGNORECASE))
            for m in matches:
                degree_name = m.group(0).upper().replace(".", "")
                start_pos = max(0, m.start() - 50)
                end_pos = min(len(text), m.end() + 150)
                context_window = text[start_pos:end_pos]

                # Look for graduation year (e.g., 2018 - 2024)
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', context_window)
                year_str = year_match.group(0) if year_match else "Year not stated"

                # Look for major/field
                major_str = "Engineering / General"
                for maj_pat in self.major_patterns:
                    maj_match = re.search(maj_pat, context_window, re.IGNORECASE)
                    if maj_match:
                        major_str = maj_match.group(0).title()
                        break

                education_records.append({
                    "degree": degree_name,
                    "field": major_str,
                    "year": year_str
                })

        # Remove duplicate degree names
        unique_records = []
        seen = set()
        for rec in education_records:
            key = f"{rec['degree']}_{rec['field']}"
            if key not in seen:
                seen.add(key)
                unique_records.append(rec)

        return unique_records

    def parse_experience_summary(self, text: str) -> Dict[str, Any]:
        """
        Analyzes work history, internships, job titles, and estimates years of experience.
        """
        lower_text = text.lower()
        
        # Check experience section presence
        has_experience_section = bool(re.search(r'\b(experience|work history|employment|internships?)\b', lower_text))

        # Look for explicit years mentioned: "3 years of experience", "2+ yrs"
        years_exp = 0.0
        exp_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', lower_text)
        if exp_matches:
            try:
                years_exp = max(float(x) for x in exp_matches)
            except Exception:
                years_exp = 1.0

        # Look for common job titles
        common_titles = [
            "software engineer", "software developer", "full stack developer", "frontend developer",
            "backend developer", "data scientist", "data analyst", "machine learning engineer",
            "ai engineer", "intern", "research intern", "cloud engineer", "devops engineer",
            "system engineer", "junior developer", "associate consultant"
        ]
        detected_titles = []
        for title in common_titles:
            if re.search(r'\b' + re.escape(title) + r'\b', lower_text):
                detected_titles.append(title.title())

        # Determine experience level
        if years_exp >= 5.0:
            level = "Senior Professional (5+ Years)"
        elif years_exp >= 2.0:
            level = "Mid-Level Professional (2-5 Years)"
        elif years_exp >= 0.5 or (has_experience_section and detected_titles):
            level = "Early Career / Junior (1-2 Years)"
        else:
            level = "Fresher / College Graduate (0-1 Years)"

        return {
            "has_experience_section": has_experience_section,
            "estimated_years": years_exp,
            "experience_level": level,
            "detected_titles": list(set(detected_titles))[:5]
        }

    def parse_projects_summary(self, text: str) -> Dict[str, Any]:
        """Detects project sections and bullet project items."""
        lower_text = text.lower()
        has_projects_section = bool(re.search(r'\b(projects|academic projects|personal projects|key projects)\b', lower_text))
        
        # Count project bullet indicators or titles
        project_count = 0
        if has_projects_section:
            # Look for lines starting with bullets or common project verbs
            project_markers = re.findall(r'(?:\n-\s|\n\*\s|\n•\s|\n[A-Z][a-zA-Z\s]{3,35}\s*\(?(?:using|with|in|tech stack)?)', text)
            project_count = max(len(project_markers) // 3, 1)
            project_count = min(project_count, 6)
        
        return {
            "has_projects_section": has_projects_section,
            "estimated_project_count": project_count
        }

    def parse_certifications(self, text: str) -> List[str]:
        """Extracts recognized certifications and credentials from resume text."""
        recognized_certs = [
            "AWS Certified Solutions Architect", "AWS Certified Cloud Practitioner",
            "AWS Certified Developer", "Microsoft Certified: Azure Fundamentals",
            "Azure Solutions Architect", "Google Cloud Associate Cloud Engineer",
            "Google Professional Data Engineer", "TensorFlow Developer Certificate",
            "Certified Kubernetes Administrator (CKA)", "CompTIA Security+",
            "Certified Ethical Hacker (CEH)", "Cisco Certified Network Associate (CCNA)",
            "PMP (Project Management Professional)", "Scrum Master (CSM)",
            "Deep Learning Specialization", "Machine Learning Specialization",
            "Coursera Verified Certificate", "HackerRank Gold Badge", "LeetCode Knight"
        ]
        
        found_certs = []
        lower_text = text.lower()
        for cert in recognized_certs:
            if cert.lower() in lower_text:
                found_certs.append(cert)
                
        # Also check general certification keywords
        custom_cert_pattern = re.findall(r'(?:certified|certification in|certificate in)\s+([a-zA-Z0-9\s]{3,30})', text, re.IGNORECASE)
        for c in custom_cert_pattern:
            clean_c = c.strip().title()
            if len(clean_c) > 3 and clean_c not in found_certs and len(found_certs) < 8:
                found_certs.append(f"Certified: {clean_c}")

        return list(set(found_certs))

    def parse_all(self, file_bytes: bytes) -> Dict[str, Any]:
        """Performs full extraction and returns structured resume data."""
        text_result = self.extract_text(file_bytes)
        if not text_result["success"]:
            return text_result

        text = text_result["raw_text"]
        
        name = self.parse_candidate_name(text)
        email = self.parse_email(text)
        phone = self.parse_phone(text)
        links = self.parse_links(text)
        education = self.parse_education(text)
        experience = self.parse_experience_summary(text)
        projects = self.parse_projects_summary(text)
        certifications = self.parse_certifications(text)

        return {
            "success": True,
            "error": None,
            "raw_text": text,
            "page_count": text_result["page_count"],
            "word_count": text_result["word_count"],
            "char_count": text_result["char_count"],
            "candidate_name": name,
            "email": email,
            "phone": phone,
            "links": links,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications
        }
