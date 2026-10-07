"""
Script to generate sample PDF resumes for testing and demonstrations.
Uses reportlab to generate realistic, professional PDFs.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def build_pdf(filepath: str, name: str, title: str, contact_info: str, summary: str,
              skills: str, experience: list, projects: list, education: list, certs: list):
    """Generates a professional resume PDF."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B')
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563EB')
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748B')
    )

    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=12
    )

    story = []

    # Header
    story.append(Paragraph(name, name_style))
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(contact_info, contact_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 6))

    # Skills
    story.append(Paragraph("TECHNICAL & PROFESSIONAL SKILLS", section_style))
    story.append(Paragraph(skills, body_style))
    story.append(Spacer(1, 6))

    # Experience
    if experience:
        story.append(Paragraph("WORK EXPERIENCE", section_style))
        for exp in experience:
            story.append(Paragraph(f"<b>{exp['role']}</b> | {exp['company']} ({exp['period']})", body_style))
            for bullet in exp['bullets']:
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # Projects
    if projects:
        story.append(Paragraph("KEY PROJECTS", section_style))
        for proj in projects:
            story.append(Paragraph(f"<b>{proj['title']}</b> ({proj['tech']})", body_style))
            for bullet in proj['bullets']:
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 4))

    # Education
    if education:
        story.append(Paragraph("EDUCATION", section_style))
        for edu in education:
            story.append(Paragraph(f"<b>{edu['degree']} in {edu['major']}</b> - {edu['school']} ({edu['year']})", body_style))
        story.append(Spacer(1, 6))

    # Certifications
    if certs:
        story.append(Paragraph("CERTIFICATIONS & BADGES", section_style))
        for cert in certs:
            story.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(story)


def generate_all_samples():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    # Sample 1: Python Developer
    build_pdf(
        filepath=os.path.join(out_dir, "sample_python_developer.pdf"),
        name="Alex Morgan",
        title="Python Backend Developer",
        contact_info="Email: alex.morgan@example.com | Phone: +1 (555) 234-5678 | LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan",
        summary="Results-oriented Python Developer with 3 years of experience architecting high-throughput REST APIs and asynchronous microservices. Proficient in Django, FastAPI, PostgreSQL, Docker, and Redis caching.",
        skills="<b>Languages:</b> Python, SQL, JavaScript, Bash<br/>"
               "<b>Frameworks & Backend:</b> Django, Flask, FastAPI, REST API, Microservices<br/>"
               "<b>Databases & Caching:</b> PostgreSQL, Redis, SQLite<br/>"
               "<b>DevOps & Tools:</b> Docker, Git, GitHub, Linux, PyTest, Postman, AWS<br/>"
               "<b>Soft Skills:</b> Agile, Problem Solving, Teamwork, Communication",
        experience=[
            {
                "role": "Python Backend Engineer",
                "company": "Nexus Cloud Solutions",
                "period": "2023 - Present",
                "bullets": [
                    "Engineered resilient RESTful APIs in Django and FastAPI serving over 150,000 daily active requests.",
                    "Optimized complex PostgreSQL database queries and integrated Redis caching, reducing API latency by 42%.",
                    "Containerized applications using Docker and established CI/CD automated test pipelines with GitHub Actions."
                ]
            },
            {
                "role": "Junior Software Developer",
                "company": "ByteWave Tech",
                "period": "2021 - 2023",
                "bullets": [
                    "Developed backend logic in Flask for an enterprise billing portal.",
                    "Collaborated in a fast-paced Agile Scrum squad delivering bi-weekly feature sprints."
                ]
            }
        ],
        projects=[
            {
                "title": "Scalable E-Commerce Inventory Microservice",
                "tech": "FastAPI, PostgreSQL, Docker, Redis",
                "bullets": [
                    "Constructed an event-driven inventory management microservice handling concurrent stock updates.",
                    "Implemented JWT token-based authentication and comprehensive unit tests with PyTest."
                ]
            }
        ],
        education=[
            {
                "degree": "B.Tech",
                "major": "Computer Science and Engineering",
                "school": "State Institute of Technology",
                "year": "2021"
            }
        ],
        certs=[
            "AWS Certified Cloud Practitioner",
            "HackerRank Gold Badge (Python)"
        ]
    )

    # Sample 2: Data Scientist & AI Engineer
    build_pdf(
        filepath=os.path.join(out_dir, "sample_data_scientist.pdf"),
        name="Sophia Chen",
        title="Data Scientist & Machine Learning Engineer",
        contact_info="Email: sophia.chen@example.com | Phone: +1 (415) 890-1234 | LinkedIn: linkedin.com/in/sophiachen-ai | GitHub: github.com/sophiachen",
        summary="Innovative Data Scientist and Machine Learning practitioner specializing in predictive modeling, Natural Language Processing (NLP), and Generative AI applications. Experienced in developing production ML pipelines using PyTorch, Scikit-Learn, and Docker.",
        skills="<b>Languages:</b> Python, SQL, R<br/>"
               "<b>AI / ML & NLP:</b> Machine Learning, Deep Learning, NLP, Scikit-Learn, PyTorch, TensorFlow, Pandas, NumPy, Hugging Face, LLMs, LangChain, Generative AI<br/>"
               "<b>Data & Visualization:</b> Matplotlib, Seaborn, Power BI, Statistics, Data Visualization, ETL<br/>"
               "<b>Cloud & Deployment:</b> Docker, AWS, Git, MLflow, FastAPI<br/>"
               "<b>Soft Skills:</b> Critical Thinking, Analytical Thinking, Collaboration, Presentation",
        experience=[
            {
                "role": "Machine Learning Scientist",
                "company": "Apex Analytics Labs",
                "period": "2023 - Present",
                "bullets": [
                    "Formulated and deployed gradient-boosted and deep neural network models with Scikit-Learn and PyTorch, yielding 91% precision.",
                    "Engineered automated feature engineering and data preprocessing pipelines in Pandas handling 10M+ rows.",
                    "Architected a Retrieval-Augmented Generation (RAG) assistant using LangChain and Hugging Face embeddings."
                ]
            }
        ],
        projects=[
            {
                "title": "Clinical NLP Entity & Sentiment Extractor",
                "tech": "Python, PyTorch, Hugging Face, Scikit-Learn",
                "bullets": [
                    "Fine-tuned Transformer language models for domain-specific entity extraction achieving an F1-score of 0.89.",
                    "Created interactive analytical dashboards in Streamlit and Matplotlib for medical researchers."
                ]
            },
            {
                "title": "Customer Churn Prediction Engine",
                "tech": "Python, Pandas, Scikit-Learn, Docker",
                "bullets": [
                    "Built an end-to-end classification system identifying churn risk with 88% ROC-AUC."
                ]
            }
        ],
        education=[
            {
                "degree": "M.S.",
                "major": "Data Science and Artificial Intelligence",
                "school": "Metropolitan University",
                "year": "2023"
            },
            {
                "degree": "B.S.",
                "major": "Computer Science",
                "school": "Tech University",
                "year": "2021"
            }
        ],
        certs=[
            "TensorFlow Developer Certificate",
            "Deep Learning Specialization",
            "AWS Certified Solutions Architect"
        ]
    )

    # Sample 3: Fresher Software Engineer
    build_pdf(
        filepath=os.path.join(out_dir, "sample_fresher_webdev.pdf"),
        name="Rahul Sharma",
        title="Fresher Software Developer",
        contact_info="Email: rahul.sharma@example.com | Phone: +91 98765 43210 | LinkedIn: linkedin.com/in/rahulsharma-dev | GitHub: github.com/rahulsharma",
        summary="Motivated Computer Science graduate with strong foundations in Data Structures, Algorithms, object-oriented programming in Java and Python, and full-stack web development. Eager to contribute to collaborative engineering teams.",
        skills="<b>Languages:</b> Java, Python, C++, JavaScript, HTML, CSS, SQL<br/>"
               "<b>Web Technologies:</b> React, Node.js, Express, REST API, Bootstrap<br/>"
               "<b>Databases & Tools:</b> MySQL, MongoDB, Git, GitHub, VS Code<br/>"
               "<b>Core CS:</b> Data Structures, Algorithms, Object-Oriented Programming (OOP)<br/>"
               "<b>Soft Skills:</b> Problem Solving, Quick Learner, Teamwork, Adaptability",
        experience=[
            {
                "role": "Software Engineering Intern",
                "company": "Innovatech Solutions",
                "period": "Summer 2024 (3 Months)",
                "bullets": [
                    "Assisted in developing modular UI components in React and integrated backend REST endpoints in Node.js.",
                    "Wrote unit tests and documented internal API specifications using Postman."
                ]
            }
        ],
        projects=[
            {
                "title": "Campus Resource Sharing Portal",
                "tech": "React, Node.js, Express, MongoDB",
                "bullets": [
                    "Developed a full-stack student resource exchange platform with user authentication and search filters.",
                    "Implemented responsive layouts and state management with React Hooks."
                ]
            },
            {
                "title": "Algorithmic Pathfinding Visualizer",
                "tech": "Python, Pygame, Data Structures",
                "bullets": [
                    "Created an interactive visual simulation of Dijkstra and A* pathfinding algorithms."
                ]
            }
        ],
        education=[
            {
                "degree": "B.Tech",
                "major": "Computer Science and Engineering",
                "school": "National Institute of Technology",
                "year": "2024"
            }
        ],
        certs=[
            "HackerRank Gold Badge (Java)",
            "Coursera Verified Certificate in Full Stack Development"
        ]
    )

    print("Sample PDF resumes generated successfully in:", out_dir)


if __name__ == "__main__":
    generate_all_samples()
