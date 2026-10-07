"""
Skill Extractor Module
Identifies technical and soft skills from resume text using categorized skill ontologies,
synonym normalization, and regex word boundary matching.
"""

import re
from typing import Dict, List, Set, Any


class SkillExtractor:
    """Categorized NLP skill extraction engine."""

    def __init__(self):
        # Master categorized skill ontology
        self.skill_taxonomy = {
            "Programming Languages": [
                "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript",
                "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R", "SQL",
                "Bash", "Shell", "Scala", "Dart", "HTML", "CSS"
            ],
            "Frameworks & Web Tech": [
                "Django", "Flask", "FastAPI", "React", "Node.js", "Express",
                "Next.js", "Angular", "Vue.js", "Spring Boot", "ASP.NET",
                "Tailwind CSS", "Bootstrap", "REST API", "GraphQL", "WebSockets",
                "Redux", "HTML5", "CSS3"
            ],
            "AI, Machine Learning & Data": [
                "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
                "Computer Vision", "TensorFlow", "PyTorch", "Scikit-Learn", "Keras",
                "Pandas", "NumPy", "Matplotlib", "Seaborn", "Hugging Face", "LLMs",
                "LangChain", "OpenCV", "Generative AI", "RAG", "Prompt Engineering",
                "NLTK", "spaCy", "Statistics", "Data Visualization", "ETL", "A/B Testing"
            ],
            "Cloud, DevOps & Infrastructure": [
                "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
                "CI/CD", "Git", "GitHub", "GitLab", "Linux", "Terraform",
                "Ansible", "Jenkins", "Microservices", "Serverless"
            ],
            "Databases & Big Data": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
                "Cassandra", "Snowflake", "Databricks", "Apache Spark", "PySpark",
                "Hadoop", "Kafka", "Airflow"
            ],
            "BI, Analytics & Tools": [
                "Power BI", "Tableau", "Excel", "Looker", "Postman", "JIRA",
                "VS Code", "Figma", "Wireshark", "Data Warehousing"
            ],
            "Soft Skills": [
                "Communication", "Leadership", "Problem Solving", "Critical Thinking",
                "Teamwork", "Collaboration", "Adaptability", "Time Management",
                "Agile", "Scrum", "Mentorship", "Presentation", "Analytical Thinking"
            ]
        }

        # Skill synonyms / aliases mapping to standardized name
        self.synonyms = {
            "js": "JavaScript",
            "ts": "TypeScript",
            "golang": "Go",
            "py": "Python",
            "postgres": "PostgreSQL",
            "k8s": "Kubernetes",
            "tf": "TensorFlow",
            "ml": "Machine Learning",
            "dl": "Deep Learning",
            "genai": "Generative AI",
            "llm": "LLMs",
            "scikit learn": "Scikit-Learn",
            "sklearn": "Scikit-Learn",
            "node": "Node.js",
            "nodejs": "Node.js",
            "reactjs": "React",
            "vue": "Vue.js",
            "vuejs": "Vue.js",
            "amazon web services": "AWS",
            "ms azure": "Azure",
            "google cloud platform": "GCP",
            "rest": "REST API",
            "restful": "REST API",
            "restful api": "REST API",
            "ci cd": "CI/CD",
            "ci/cd pipeline": "CI/CD",
            "ms excel": "Excel",
            "pbi": "Power BI"
        }

        # Build patterns for special token skills (e.g., C, C++, C#, R, Go, .NET)
        self.special_tokens = {
            "c++": re.compile(r'\bc\+\+\b', re.IGNORECASE),
            "c#": re.compile(r'\bc#\b', re.IGNORECASE),
            "c": re.compile(r'\b(?<![a-zA-Z0-9])C(?![a-zA-Z0-9+#])\b'),
            "r": re.compile(r'\b(?<![a-zA-Z0-9])R(?![a-zA-Z0-9])\b'),
            "go": re.compile(r'\b(?:golang|go language|go programming)\b|\b(?<![a-zA-Z])Go(?![a-zA-Z])\b'),
            ".net": re.compile(r'\b\.net\b', re.IGNORECASE)
        }

    def _normalize_skill_query(self, skill: str) -> str:
        """Translates known synonyms into canonical names."""
        clean = skill.strip().lower()
        return self.synonyms.get(clean, skill)

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Parses resume text and extracts all categorized technical and soft skills.
        """
        detected_by_category: Dict[str, List[str]] = {}
        all_detected: Set[str] = set()

        text_lower = text.lower()

        # Step 1: Detect synonym occurrences
        for synonym, canonical in self.synonyms.items():
            pattern = r'\b' + re.escape(synonym) + r'\b'
            if re.search(pattern, text_lower):
                all_detected.add(canonical)

        # Step 2: Detect taxonomy skills
        for category, skills in self.skill_taxonomy.items():
            cat_detected = set()

            for skill in skills:
                # If already detected via synonym
                if skill in all_detected:
                    cat_detected.add(skill)
                    continue

                # Check special single-letter or symbol skills
                s_lower = skill.lower()
                if s_lower in self.special_tokens:
                    if self.special_tokens[s_lower].search(text):
                        cat_detected.add(skill)
                        all_detected.add(skill)
                    continue

                # Standard multi-character skill matching with word boundaries
                escaped = re.escape(skill)
                # Allow hyphens or spaces interchangeably (e.g. Node-js or Node.js)
                escaped = escaped.replace(r'\.', r'[\.\s]?').replace(r'\-', r'[\-\s]?')
                pattern = r'\b' + escaped + r'\b'

                if re.search(pattern, text, re.IGNORECASE):
                    cat_detected.add(skill)
                    all_detected.add(skill)

            detected_by_category[category] = sorted(list(cat_detected))

        # Flatten technical skills vs soft skills
        tech_skills = set()
        soft_skills = set()

        for category, skill_list in detected_by_category.items():
            if category == "Soft Skills":
                soft_skills.update(skill_list)
            else:
                tech_skills.update(skill_list)

        return {
            "categorized_skills": detected_by_category,
            "all_skills": sorted(list(all_detected)),
            "technical_skills": sorted(list(tech_skills)),
            "soft_skills": sorted(list(soft_skills)),
            "total_skills_count": len(all_detected),
            "tech_skills_count": len(tech_skills),
            "soft_skills_count": len(soft_skills)
        }
