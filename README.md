# SkillSort AI - Visual Resume Screening Platform ✨

**Find the perfect fit — faster, smarter.**

SkillSort AI is an intelligent platform designed to streamline the initial resume screening process. It helps recruiters and hiring managers quickly identify the most relevant candidates by analyzing semantic similarity between resumes and job descriptions using NLP techniques.

## Overview 📝

Manually screening hundreds of resumes is time-consuming and prone to bias. SkillSort AI automates this by:

1.  Allowing users to upload multiple candidate resumes and a job description.
2.  Extracting text content from PDF and DOCX files.
3.  Using advanced Sentence Transformer models to understand the *meaning* behind the text, not just keywords.
4.  Calculating a semantic match score between each candidate and the job description.
5.  (Optionally) Calculating a team fit score if team member resumes are provided.
6.  Displaying a ranked list of candidates with clear scoring and verdict indicators.

This allows users to focus their time on the most promising candidates first.

## Core Features (Implemented) 🚀

*   **Multi-File Upload:** Upload multiple candidate resumes (`.pdf`, `.docx`) simultaneously.
*   **Job Description Upload:** Upload a single job description file (`.pdf`, `.docx`).
*   **(Experimental) Team Upload:** Interface to upload team member resumes with names/occupations (team fit calculation requires further validation).
*   **Text Extraction:** Automatically extracts text content using `pdfplumber` and `python-docx`.
*   **Semantic Analysis:** Employs the `all-MiniLM-L6-v2` Sentence Transformer model to generate text embeddings.
*   **Scoring:**
    *   Calculates **Skill Match** score based on cosine similarity between candidate embedding and JD embedding.
    *   Calculates (optional) **Team Fit** score based on average similarity to provided team members.
    *   Computes a weighted **Composite Score**.
*   **Database Storage:** Stores file metadata, extracted text, embeddings (serialized), and scores in an SQLite database.
*   **Ranked Results View:** Displays candidates sorted by score, showing:
    *   Candidate Name & Original Filename
    *   Skill Match, Team Fit (if applicable), and Overall Scores with progress bars.
    *   Inferred basic traits (keyword-based).
    *   A simple verdict badge (e.g., "Excellent Fit", "Consider").
*   **Web Interface:** Built with Flask, TailwindCSS (CDN), and Alpine.js (CDN).

## Tech Stack ⚙️

*   **Backend:**
    *   Python 3.x
    *   Flask (Web Framework)
    *   Flask-CORS
    *   SQLite3 (Database)
*   **NLP & AI:**
    *   `sentence-transformers` (specifically `all-MiniLM-L6-v2`)
    *   `spacy` (`en_core_web_sm` model for basic trait extraction)
    *   `numpy`
    *   `torch` (dependency for sentence-transformers)
*   **File Parsing:**
    *   `pdfplumber`
    *   `python-docx`
*   **Frontend:**
    *   HTML5
    *   TailwindCSS (via CDN)
    *   Alpine.js (via CDN for dropdown interactivity)


## Setup and Installation 🛠️

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd skill-sort-ai
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `sentence-transformers` often requires PyTorch. Installation might take some time.*

4.  **Download spaCy language model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Run the Flask application:**
    ```bash
    python app.py
    ```

6.  **Access the application:** Open your web browser and navigate to `http://127.0.0.1:5500` (or the address shown in the terminal).

## Usage Guide 📖

1.  Navigate to the **Upload Page** (`/`).
2.  **Upload Candidate Resumes:** Click "Choose Files" under "Upload Candidate Resumes" and select one or more `.pdf` or `.docx` files. Optionally provide candidate names in the generated fields.
3.  **Upload Job Description:** Click "Choose File" under "Upload Job Description" and select a single `.pdf` or `.docx` file.
4.  **(Optional) Upload Team Resumes:** Click "Show" under "Upload Team Resumes", upload team member `.pdf` or `.docx` files, and fill in their names and occupations. *Note: Team fit calculation is basic.*
5.  Click the **"Analyze Resumes"** button. Processing might take some time depending on the number and size of resumes and your machine's performance.
6.  You will be redirected to the **Results Page** (`/results`).
7.  View the ranked list of candidates. Use the **Sort By** dropdown to reorder the results.

## Project Structure 📁
Use code with caution.
Markdown
skill-sort-ai/
├── app.py # Main Flask application logic and routes
├── modules/
│ ├── init.py
│ ├── db_manager.py # Database interactions (SQLite)
│ ├── file_parser.py # PDF/DOCX text extraction
│ └── nlp_processor.py # NLP tasks (spaCy, SentenceTransformers, scoring)
├── static/
│ └── css/
│ └── styles.css # Optional custom CSS
│ └── js/ # Optional custom JS (not used in current version)
├── templates/
│ ├── index.html # Upload interface template
│ └── results.html # Results display template (table view)
├── uploads/ # Stores uploaded files (auto-created)
│ ├── candidates/
│ ├── jd/
│ └── team/
├── requirements.txt # Python dependencies
├── database.db # SQLite database file (auto-created)
└── README.md # This file
## Future Improvements / Roadmap (Based on Prompt) 💡

*   **Interactive Analytics:** Add charts/visualizations (e.g., score distribution, trait comparisons) back using Chart.js or Plotly.
*   **Advanced Trait/Personality Profiling:** Implement more sophisticated trait extraction (e.g., Big Five) using NLP techniques or keyword mapping.
*   **Natural Language Feedback:** Generate basic feedback or skill gap summaries for candidates.
*   **Resume Quality Scoring:** Add metrics for formatting, clarity, keyword density, etc.
*   **Skill Gap Heatmap:** Visually compare skills extracted from resumes against JD requirements.
*   **Improved Team Fit:** Enhance team compatibility scoring and potentially add a team fit matrix visualization.
*   **Asynchronous Processing:** Implement background tasks (e.g., using Celery) for handling large uploads without blocking the UI.
*   **UI/UX Enhancements:** Improve visual design, responsiveness, and user feedback.
*   **Error Handling:** Add more robust error handling throughout the application.
*   **Export Functionality:** Implement the "Export PDF" feature.

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License ⚖️

*(MIT License)*
