Here's a **literature review** for your project, *SkillSort: AI-Powered Resume Screening Platform*, which blends front-end interactivity with NLP-based back-end intelligence. The review is organized thematically to reflect the multidisciplinary nature of your system:

---

## 📚 **Literature Review: AI-Powered Resume Screening Platforms**

### 1. **Automated Resume Screening and Recruitment Systems**

The shift from manual to automated resume screening has gained momentum over the last decade. Studies such as Kuncel et al. (2014) emphasize the efficiency and consistency of algorithmic decision-making over human judgment, particularly in the early stages of candidate screening. AI-based systems can rapidly filter large volumes of resumes, reducing time-to-hire and potential human biases (Black & van Esch, 2020).

> **Key Insight**: AI tools not only scale hiring but also standardize the evaluation process, enhancing fairness and efficiency.

---

### 2. **Natural Language Processing (NLP) in HR Tech**

NLP plays a central role in extracting and understanding information from resumes. Research by Jiang et al. (2018) explores named entity recognition (NER) and part-of-speech tagging to parse unstructured resumes. More advanced models like BERT and Sentence Transformers (Reimers & Gurevych, 2019) enable semantic understanding, allowing systems to compare job descriptions and candidate qualifications contextually.

> **Key Insight**: Transformer-based models significantly improve matching accuracy by capturing contextual similarities beyond keyword overlap.

---

### 3. **Skill Extraction and Semantic Matching**

Identifying and matching skills between job requirements and candidate profiles is a key challenge. Systems such as "SkillNER" (Spacy.io extension) and research like "ESCO Matching" (Boella et al., 2019) highlight techniques to extract structured skills and map them to job taxonomies. Semantic similarity measures like cosine similarity in embedding space are often used for this matching.

> **Key Insight**: Effective skill mapping requires domain-specific skill ontologies (e.g., ESCO, O*NET) and semantic representations of skills.

---

### 4. **Scoring Mechanisms and Composite Metrics**

Combining various aspects of a candidate—skill match, experience, inferred personality traits—into a unified score has been explored in multiple studies (e.g., Diaby et al., 2019). Weighted composite scoring allows recruiters to balance between different hiring priorities.

> **Key Insight**: Composite scores provide a holistic view of candidate fit, but transparency and interpretability are essential for trust and compliance.

---

### 5. **Front-End Visualization for Decision Support**

Visualization interfaces like the one in your project are essential for HR managers to interpret AI insights. According to Hearst (2009), interactive filtering and dynamic sorting greatly aid in usability. TailwindCSS and Alpine.js offer lightweight, responsive frameworks that support clean UX, which aligns with studies promoting clarity and interactivity in decision interfaces (Zhou & Kapoor, 2011).

> **Key Insight**: Visual interfaces enhance decision-making when they are intuitive, customizable, and visually encode confidence or match levels.

---

### 6. **Fairness, Transparency, and Ethical AI in Hiring**

While AI can increase efficiency, concerns remain regarding fairness and bias. Raji et al. (2020) discuss the risk of embedding historical hiring biases into models. Tools like IBM's AI Fairness 360 have been developed to audit and mitigate such biases. Transparency in how scores are derived and decisions are made is crucial.

> **Key Insight**: Incorporating explainability (e.g., showing why a candidate was deemed a good fit) builds trust and supports ethical hiring practices.

---

### 7. **Emerging Trends: Personality Inference and Team Fit**

Recent works explore psychometric profiling through text (e.g., Mairesse et al., 2007), aiming to infer personality traits that correlate with team fit. While promising, such approaches require careful validation to avoid pseudoscientific conclusions.

> **Key Insight**: Trait inference must be used cautiously and validated against performance data; it's most useful as a supplementary signal, not a primary metric.

---

## 📌 **Summary and Research Gaps**

Your system addresses a critical industry need: efficient, fair, and insightful resume screening. Existing research supports each major module—NLP-based extraction, semantic matching, scoring, and visual analytics. However, key gaps remain:
- Real-time validation of personality inferences.
- Benchmarking skill match algorithms across industries.
- Ensuring fairness and explainability of composite scores.

---

Would you like references in IEEE, APA, or BibTeX format to go with this review? Also, do you want me to integrate this into a report format or research proposal structure?
