"""
Recommendations Module
Generates personalized learning paths, portfolio project ideas, industry certifications,
ATS resume enhancements, and impactful action verbs tailored to candidate skill gaps.
"""

from typing import Dict, List, Any
from collections import Counter


class RecommendationEngine:
    """Actionable career roadmap and resume improvement advisor."""

    def __init__(self):
        # Curated portfolio project blueprints by domain
        self.project_blueprints = {
            "Data & AI": [
                {
                    "title": "End-to-End MLOps Pipeline & Model Serving",
                    "tech_stack": "Python, Scikit-Learn / PyTorch, Docker, FastAPI, MLflow",
                    "difficulty": "Intermediate",
                    "description": "Train a predictive classification or regression model, log experiments with MLflow, containerize an inference REST API in Docker, and deploy with automated health checks."
                },
                {
                    "title": "Retrieval-Augmented Generation (RAG) Document Q&A",
                    "tech_stack": "Python, LangChain, OpenAI / HuggingFace, ChromaDB, Streamlit",
                    "difficulty": "Advanced",
                    "description": "Build an interactive chatbot that ingests custom PDFs, chunks and vectorizes documents using embeddings, and retrieves contextual answers with grounded citations."
                },
                {
                    "title": "Executive Business Intelligence Dashboard",
                    "tech_stack": "SQL, Python, Pandas, Power BI / Tableau",
                    "difficulty": "Beginner to Intermediate",
                    "description": "Cleanse real-world sales and marketing datasets, engineer analytical metrics with DAX / SQL queries, and construct interactive multi-page KPI dashboards."
                }
            ],
            "Software & Backend": [
                {
                    "title": "High-Throughput Microservices REST API",
                    "tech_stack": "Python (FastAPI / Django), PostgreSQL, Redis, Docker",
                    "difficulty": "Intermediate",
                    "description": "Design a modular backend service featuring JWT authentication, asynchronous database queries with SQLAlchemy, and low-latency cache invalidation using Redis."
                },
                {
                    "title": "Real-Time Collaboration App with WebSockets",
                    "tech_stack": "Node.js / Python, React, WebSockets, MongoDB",
                    "difficulty": "Intermediate to Advanced",
                    "description": "Develop a multi-user collaborative workspace with live chat, presence indicators, real-time sync, and resilient document persistence."
                },
                {
                    "title": "Full-Stack SaaS Platform with Stripe Billing",
                    "tech_stack": "React, TypeScript, FastAPI, PostgreSQL, Tailwind CSS",
                    "difficulty": "Advanced",
                    "description": "Build an end-to-end cloud platform supporting multi-tenant user accounts, role-based access control, subscription tiers, and automated webhooks."
                }
            ],
            "Cloud & DevOps": [
                {
                    "title": "Automated Infrastructure as Code (IaC) Deployment",
                    "tech_stack": "Terraform, AWS (ECS, RDS, S3), GitHub Actions",
                    "difficulty": "Intermediate",
                    "description": "Provision automated cloud infrastructure using Terraform scripts and configure a zero-downtime CI/CD deployment pipeline with GitHub Actions."
                },
                {
                    "title": "Kubernetes Microservices Cluster with Monitoring",
                    "tech_stack": "Kubernetes, Docker, Prometheus, Grafana, Linux",
                    "difficulty": "Advanced",
                    "description": "Deploy a containerized distributed application onto a local minikube or cloud Kubernetes cluster with ingress controllers and Prometheus alerting."
                }
            ]
        }

        # Domain certifications roadmap
        self.certifications_catalog = {
            "Data & AI": [
                {"name": "AWS Certified Machine Learning - Specialty", "issuer": "Amazon Web Services", "level": "Advanced"},
                {"name": "Google Professional Data Engineer", "issuer": "Google Cloud", "level": "Advanced"},
                {"name": "DeepLearning.AI TensorFlow Developer Certificate", "issuer": "DeepLearning.AI / Coursera", "level": "Intermediate"},
                {"name": "Microsoft Certified: Azure Data Scientist Associate", "issuer": "Microsoft", "level": "Intermediate"}
            ],
            "Software & Backend": [
                {"name": "AWS Certified Solutions Architect - Associate", "issuer": "Amazon Web Services", "level": "Intermediate"},
                {"name": "Meta Back-End Developer Professional Certificate", "issuer": "Meta / Coursera", "level": "Beginner to Intermediate"},
                {"name": "Oracle Certified Professional: Java SE Developer", "issuer": "Oracle", "level": "Intermediate"},
                {"name": "PostgreSQL Professional Certification", "issuer": "PostgreSQL Foundation", "level": "Intermediate"}
            ],
            "Cloud & DevOps": [
                {"name": "Certified Kubernetes Administrator (CKA)", "issuer": "Cloud Native Computing Foundation", "level": "Advanced"},
                {"name": "AWS Certified Developer - Associate", "issuer": "Amazon Web Services", "level": "Intermediate"},
                {"name": "HashiCorp Certified: Terraform Associate", "issuer": "HashiCorp", "level": "Intermediate"},
                {"name": "Docker Certified Associate (DCA)", "issuer": "Docker", "level": "Intermediate"}
            ]
        }

        # Strong action verbs for ATS resumes
        self.action_verbs = [
            ("Architected & Built", "Architected, engineered, developed, spearheaded, designed, formulated"),
            ("Optimized & Accelerated", "Optimized, streamlined, refactored, automated, minimized, enhanced"),
            ("Led & Delivered", "Spearheaded, coordinated, mobilized, directed, delivered, executed"),
            ("Analyzed & Quantified", "Quantified, benchmarked, audited, evaluated, discovered, derived")
        ]

    def generate_recommendations(
        self,
        job_matches: List[Dict[str, Any]],
        candidate_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesizes top matched roles and skill gaps into targeted career guidance.
        """
        top_matches = job_matches[:5] if job_matches else []

        # 1. Identify most frequently missing skills across top matches
        missing_pool: List[str] = []
        target_categories: List[str] = []
        for job in top_matches:
            missing_pool.extend(job.get("missing_required", []))
            missing_pool.extend(job.get("missing_preferred", [])[:2])
            target_categories.append(job.get("category", "Software & Backend"))

        skill_counter = Counter(missing_pool)
        recommended_skills = [
            {"skill": skill, "occurrences": count, "priority": "High" if count >= 2 else "Medium"}
            for skill, count in skill_counter.most_common(8)
        ]

        # Determine dominant career track
        category_counts = Counter(target_categories)
        dominant_category = category_counts.most_common(1)[0][0] if category_counts else "Software & Backend"
        if "Data" in dominant_category or "AI" in dominant_category:
            blueprint_key = "Data & AI"
        elif "Cloud" in dominant_category or "Infrastructure" in dominant_category:
            blueprint_key = "Cloud & DevOps"
        else:
            blueprint_key = "Software & Backend"

        # Tailored projects & certifications
        suggested_projects = self.project_blueprints.get(blueprint_key, self.project_blueprints["Software & Backend"])
        suggested_certs = self.certifications_catalog.get(blueprint_key, self.certifications_catalog["Software & Backend"])

        # Resume formatting & ATS suggestions
        resume_enhancement_tips = [
            {
                "category": "Quantify Impact",
                "tip": "Transform task statements into achievements: 'Decreased API response latency by 35% through Redis caching' rather than 'Implemented Redis'."
            },
            {
                "category": "Keyword Optimization",
                "tip": f"Integrate high-frequency missing keywords ({', '.join([s['skill'] for s in recommended_skills[:4]])}) into project bullet points."
            },
            {
                "category": "ATS Standard Hierarchy",
                "tip": "Ensure clean headings: 'Summary', 'Technical Skills', 'Experience', 'Projects', 'Education', 'Certifications' without two-column tables."
            },
            {
                "category": "Active Technical Verbs",
                "tip": "Start every experience bullet with a commanding verb: 'Engineered', 'Optimized', 'Deployed', or 'Spearheaded'."
            }
        ]

        return {
            "dominant_track": blueprint_key,
            "recommended_skills": recommended_skills,
            "portfolio_projects": suggested_projects,
            "recommended_certifications": suggested_certs,
            "resume_enhancement_tips": resume_enhancement_tips,
            "action_verbs": self.action_verbs
        }
