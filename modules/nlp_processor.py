import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re

# Load models only once
try:
    print("Loading NLP models...")
    nlp = spacy.load("en_core_web_sm")
    # Using a smaller, faster model suitable for semantic similarity
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("NLP models loaded successfully.")
except Exception as e:
    print(f"Error loading NLP models: {e}")
    # Handle model loading failure appropriately (e.g., exit or fallback)
    nlp = None
    model = None

def clean_text(text):
    """Basic text cleaning."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
    text = text.strip()
    return text

def get_embedding(text):
    """Generates sentence embedding for the given text."""
    if not model or not text:
        return None
    try:
        cleaned_text = clean_text(text)
        embedding = model.encode(cleaned_text, convert_to_tensor=True)
        return embedding.cpu().numpy() # Return as numpy array
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def calculate_similarity(embedding1, embedding2):
    """Calculates cosine similarity between two embeddings."""
    if embedding1 is None or embedding2 is None:
        return 0.0
    try:
        # Ensure embeddings are numpy arrays
        emb1 = np.asarray(embedding1)
        emb2 = np.asarray(embedding2)
        # Use sentence-transformers util for cosine similarity
        similarity_score = util.cos_sim(emb1, emb2).item() # Get scalar value
        # Ensure score is between 0 and 1 (or -1 and 1 depending on model, MiniLM is usually positive)
        # Clamp score to 0-1 range and convert to percentage * 100
        return max(0.0, min(1.0, similarity_score)) * 100
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

def extract_skills_and_traits(text):
    """Placeholder for extracting skills/traits using spaCy (can be expanded)."""
    if not nlp or not text:
        return {"skills": [], "traits": []}

    cleaned_text = clean_text(text)
    doc = nlp(cleaned_text[:nlp.max_length]) # Limit text length if very long

    # Example: Basic Noun Phrase extraction (potential skills)
    # More sophisticated extraction would use NER, Matcher rules, etc.
    skills = list(set([chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]))

    # Example: Simple keyword matching for traits (very basic)
    trait_keywords = {
        "team player": ["team", "collaboration", "collaborative", "teamwork"],
        "leader": ["lead", "leadership", "manage", "supervise", "direct"],
        "detail-oriented": ["detail", "precise", "meticulous", "accurate"],
        "creative": ["creative", "innovative", "design", "imagine"],
        "adaptable": ["adapt", "flexible", "versatile"],
        "independent": ["independent", "self-starter", "autonomous"],
        "analytical": ["analyze", "analytical", "data", "logic", "problem-solving"]
    }
    found_traits = []
    text_lower = cleaned_text.lower()
    for trait, keywords in trait_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_traits.append(trait.replace(" ", "-").capitalize()) # Format for display

    # Limit number of returned items for clarity
    return {
        "skills": skills[:15], # Return top 15 potential skills
        "traits": list(set(found_traits))[:5] # Return top 5 unique traits
    }

# --- Add Scoring Logic ---
def calculate_composite_score(skill_match_score, team_fit_score=None, skill_weight=0.7):
    """
    Calculates a weighted composite score.
    Args:
        skill_match_score (float): Score from 0-100.
        team_fit_score (float, optional): Score from 0-100. Defaults to None.
        skill_weight (float): Weight for the skill match score (0.0 to 1.0).
                               Team fit weight is (1.0 - skill_weight).
    Returns:
        float: Composite score (0-100).
    """
    if team_fit_score is not None:
        team_weight = 1.0 - skill_weight
        score = (skill_match_score * skill_weight) + (team_fit_score * team_weight)
    else:
        score = skill_match_score # Only skill match matters

    return max(0.0, min(100.0, score)) # Ensure score is within bounds

def calculate_team_fit(candidate_embedding, team_embeddings):
    """
    Calculates the average similarity between a candidate and team members.
    Args:
        candidate_embedding (np.array): Embedding of the candidate.
        team_embeddings (list[np.array]): List of embeddings for team members.
    Returns:
        float: Average team fit score (0-100), or 0.0 if no team embeddings.
    """
    if not team_embeddings or candidate_embedding is None:
        return 0.0

    total_similarity = 0
    valid_comparisons = 0
    for team_emb in team_embeddings:
        if team_emb is not None:
            similarity = calculate_similarity(candidate_embedding, team_emb)
            total_similarity += similarity
            valid_comparisons += 1

    if valid_comparisons == 0:
        return 0.0

    return total_similarity / valid_comparisons