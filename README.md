# AI Resume Analyzer and Job Recommendation System

An NLP-powered application that evaluates technical resumes against industry job roles, calculates TF-IDF cosine match scores, identifies skill gaps, generates a personalized 4-week learning roadmap, exports downloadable PDF reports, and provides an interactive **AI Resume Coach Chatbot** using **LangChain**.

---

## 📌 Features

- **Document Extraction**: Parses PDF (`pypdf`) and DOCX (`python-docx`) resumes into raw text.
- **Text Normalization**: Cleans punctuation while preserving special technical terms like `C++`, `C#`, `.NET`, `Node.js`, and `React.js`.
- **Taxonomy Skill Extraction**: Scans text against a controlled dictionary of 80+ technical skills grouped into 7 categories using exact word-boundary regex (`\b`).
- **TF-IDF & Cosine Match Scoring**: Ranks candidate suitability against industry job roles using `scikit-learn` vectorization and matrix cosine similarity.
- **Skill Gap Deep Dive**: Displays exact matched strengths and missing skill gaps per target role.
- **AI 4-Week Learning Roadmap**: Generates a tailored week-by-week learning plan via Google Gemini AI (`gemini-3.5-flash-lite`).
- **PDF Analysis Export**: Renders a formatted PDF analysis report including matched scores, skill gaps, and roadmap using `fpdf`.
- **LangChain AI Resume Coach Chatbot**: Multi-turn conversational chatbot with full context awareness (resume text, role match, skill gaps, and generated roadmap) using LangChain's LCEL pipeline (`ChatPromptTemplate | ChatGoogleGenerativeAI | StrOutputParser`).

---

## 🏗️ Architecture & Data Flow

```
                [Upload Resume PDF / DOCX]
                           |
                           V
          [Extract Raw Text - resume_parser.py]
                           |
                           V
        [Clean & Normalize Text - text_cleaner.py]
                           |
                           V
      [Extract Technical Skills - skill_extractor.py]
                           |
                           V   
[Match Job Roles via TF-IDF & Cosine Similarity - job_matcher.py]
                           |
                           V
     [Display Matches & Skill Gaps - app.py Dashboard]
                           |
                           V
    [Generate AI 4-Week Roadmap - roadmap_generator.py]
                           |
                           V
   [Export Downloadable PDF Report - report_generator.py]
                           |
                           V 
         [AI Resume Coach Chatbot - resume_coach.py]
```

---

## 📁 Repository Structure

```text
Resume Analyzer/
│── app.py                       # Streamlit dashboard & tab navigation
│── resume_parser.py             # PDF & DOCX text extraction
│── text_cleaner.py              # Regex normalization & token protection
│── skill_extractor.py           # Controlled skill dictionary extraction
│── job_matcher.py               # TF-IDF vectorization & cosine similarity scoring
│── roadmap_generator.py         # Google Gemini 4-week learning roadmap engine
│── report_generator.py          # FPDF styled PDF report generator
│── resume_coach.py              # LangChain conversational coach assistant
│── requirements.txt             # Python dependencies
│── Dockerfile                   # Containerized deployment script
│── .env                         # Environment variables (API Key)
│── .gitignore                   # Excluded git tracking files
│
├── data/
│   ├── job_roles.csv            # Predefined industry job roles & required skills
│   └── skill_dictionary.csv     # Controlled technical skills taxonomy
│
├── sample_resumes/
│   └── sample_data_analyst.txt  # Sample test resume
│
└── tests/
    └── test_cases.csv           # Testing & evaluation verification sheet
```

---

## ⚙️ Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer
```

### 2. Create Virtual Environment & Install Dependencies
**On Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**On Linux/Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 🐳 Docker Deployment

To build and run the application using Docker:

```bash
# 1. Build Docker image
docker build -t resume-analyzer .

# 2. Run Docker container
docker run -d -p 8501:8501 --env-file .env resume-analyzer
```
Access the application at `http://localhost:8501`.

---