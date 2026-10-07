# 💼 AI Resume Analyzer & Job Matcher

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![NLP](https://img.shields.io/badge/NLP-TF--IDF%20%2B%20NLTK-green.svg)](https://www.nltk.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Cosine%20Similarity-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An intelligent, full-stack **AI Resume Analyzer & Job Matcher** web application built with **Python, NLP, and Streamlit**. It parses PDF resumes, categorizes candidate skills, computes an explainable **0–100 ATS Resume Score**, pinpoints skill gaps, and matches resumes against real-world tech job roles using **TF-IDF Vectorization** and **Cosine Similarity**.

---

## 🌟 Key Features

1. **📄 Automated PDF Resume Parsing**
   - Extracts clean text using `pdfplumber` and `pypdf`.
   - Identifies candidate name, email, phone number, LinkedIn, GitHub, and portfolio links.
   - Parses degree credentials, graduation years, work experience, projects, and certifications.
   - Built-in preloaded demo resumes (Python Developer, Data Scientist, Fresher Web Dev) for immediate testing without external uploads.

2. **🧠 Categorized NLP Skill Extraction**
   - Multi-tier skill taxonomy covering:
     - **Programming Languages:** Python, Java, C++, TypeScript, SQL, Go, Rust, etc.
     - **Frameworks & Web:** Django, FastAPI, React, Node.js, Spring Boot, etc.
     - **AI / ML & Data:** Machine Learning, Deep Learning, NLP, PyTorch, TensorFlow, LangChain, etc.
     - **Cloud & DevOps:** AWS, Azure, Docker, Kubernetes, CI/CD, Git, Linux, Terraform.
     - **Databases & Big Data:** PostgreSQL, MongoDB, Redis, Snowflake, Apache Spark.
     - **Soft Skills:** Communication, Leadership, Problem Solving, Agile, Scrum.
   - Normalizes tech synonyms (e.g. `k8s` → `Kubernetes`, `postgres` → `PostgreSQL`).

3. **🏆 0–100 ATS Resume Scorecard**
   - Transparent, explainable 7-dimensional scoring formula:
     - **Contact Completeness (10 pts)**
     - **Technical Skills Depth & Diversity (25 pts)**
     - **Soft Skills (10 pts)**
     - **Education & Academics (15 pts)**
     - **Projects & Portfolio (15 pts)**
     - **Work Experience & Internships (15 pts)**
     - **Certifications & Badges (10 pts)**
   - Interactive **Plotly Radar Chart** and **Donut Gauge**.

4. **🎯 Explainable AI Job Matching (Cosine Similarity)**
   - Curated dataset of 12 distinct tech roles in `data/jobs.csv`.
   - Combines **TF-IDF Vectorizer + Cosine Similarity** with **Required & Preferred Skill Overlap Ratios**.
   - Clear explainable reasoning:
     - *"Matched because you have: Python, SQL, Django, Docker"*
     - *"Missing critical skills: Kubernetes, AWS"*
     - *"Why candidate matches: Strong alignment with backend data handling..."*

5. **🔍 Interactive Skill Gap Deep-Dive**
   - Select any target tech role to inspect required vs. missing competencies.
   - Visual coverage percentage progress and categorized skill badges.

6. **💡 Actionable Career & Resume Recommendations**
   - Prioritized missing skills ranked by industry frequency.
   - Curated portfolio project blueprints with tech stacks and architecture descriptions.
   - Recommended industry certifications (AWS, Google Cloud, DeepLearning.AI).
   - ATS resume tips and high-impact action verbs cheatsheet.

7. **🕒 SQLite Database History & Report Export**
   - Automatically logs analysis runs to a local SQLite database (`data/resume_history.db`).
   - Download complete analysis reports in **JSON** or **Plaintext (.txt)**.

---

## 🏗️ Project Architecture

```
ai_resume_analyzer/
│
├── app.py                     # Main Streamlit web application & UI
├── requirements.txt           # Python dependencies
├── README.md                  # Complete documentation
│
├── data/
│   ├── jobs.csv               # Dataset of 12 tech jobs with skill requirements
│   └── resume_history.db      # Local SQLite database (auto-generated)
│
├── modules/
│   ├── __init__.py            # Python package initialization
│   ├── resume_parser.py       # PDF text extraction & profile metadata parser
│   ├── skill_extractor.py     # Categorized skill taxonomy & regex extractor
│   ├── resume_scorer.py       # 0–100 ATS scoring engine & radar breakdown
│   ├── job_matcher.py         # TF-IDF Cosine Similarity & explainable matcher
│   ├── recommendations.py     # Learning roadmap, project blueprints & tips
│   └── database.py            # SQLite database persistence layer
│
└── assets/
    └── sample_resumes/        # Pre-loaded professional PDF resumes
        ├── create_samples.py  # Script that generates sample PDFs
        ├── sample_python_developer.pdf
        ├── sample_data_scientist.pdf
        └── sample_fresher_webdev.pdf
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Programming Language** | Python 3.10+ |
| **Web Interface** | Streamlit |
| **NLP & Similarity** | NLTK, Scikit-Learn (TF-IDF Vectorizer, Cosine Similarity) |
| **PDF Extraction** | `pdfplumber`, `pypdf` |
| **Data Processing** | Pandas |
| **Data Visualizations** | Plotly (Radar, Donut Gauge, Horizontal Bar Charts) |
| **Database** | SQLite3 |
| **PDF Generation (Demos)**| ReportLab |

---

## ⚡ Installation & Setup Instructions

### 1. Clone or Navigate to the Project Directory

```bash
cd C:\Users\ELCOT\.gemini\antigravity-ide\scratch\ai_resume_analyzer
```

### 2. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Download NLTK Corpora

The application automatically utilizes NLTK tokenizers. You can pre-download them with:

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"
```

---

## 🚀 How to Run the Application

Launch the Streamlit web application with:

```bash
streamlit run app.py
```

Streamlit will launch locally in your default web browser (typically at `http://localhost:8501`).

---

## 💻 How to Use the Application

1. **Upload or Select a Resume:**
   - In the sidebar, select **"Use Pre-loaded Demo Resume"** for instant 1-click testing with realistic profiles (Python Developer, Data Scientist, or Fresher Web Dev).
   - Or toggle **"Upload PDF Resume"** to upload any standard `.pdf` document.
2. **Review ATS Score:**
   - Navigate to the **"📊 Resume Score & Radar"** tab to view your score out of 100, radar breakdown, strengths, and areas for improvement.
3. **Inspect Job Matches:**
   - Go to the **"🎯 Top Job Matches"** tab to see your top 5 recommended tech positions, matching percentages, and explainable reasons.
4. **Deep-Dive into Skill Gaps:**
   - Go to **"🔍 Skill Gap Deep Dive"** and pick any specific job title to see exactly which skills you have vs. which skills you need to acquire.
5. **Get Recommendations:**
   - Open **"💡 Action Recommendations"** for recommended portfolio projects, certifications, and ATS formatting guidelines.
6. **Export & View History:**
   - Go to **"🕒 Analysis History"** to download your report as JSON or plain text.

---

## 🔬 Explainable AI Matching Formula

The matching engine avoids naive keyword counts by using a **hybrid weighted matching model**:

$$\text{Match Score} = (0.55 \times \text{Required Ratio}) + (0.15 \times \text{Preferred Ratio}) + (0.30 \times \text{TF-IDF Cosine Similarity})$$

- **Required Skills Coverage (55%):** Direct overlap with essential prerequisites.
- **Preferred Skills Coverage (15%):** Bonus points for nice-to-have technologies.
- **Contextual NLP Similarity (30%):** Cosine distance between the TF-IDF representation of the candidate's resume and the job's full narrative description.

---

## 🔮 Future Enhancements

- 🌐 **Live Web Scraping:** Real-time job ingestion from LinkedIn / Indeed RSS feeds.
- 🤖 **Local LLM Integration:** Deep semantic feedback using Ollama or Gemini API for personalized cover letter drafting.
- 📑 **Docx Support:** Text extraction from `.docx` resumes via `python-docx`.
- 🔐 **User Authentication:** Multi-user accounts with secure cloud history.

---

## 👨‍💻 Project Information

- **Designed for:** Final Year College Capstone Project, AI/NLP Demonstration, and Fresher Portfolio.
- **Author:** Antigravity AI Engineering
- **Status:** Complete, Tested, and Fully Functional
