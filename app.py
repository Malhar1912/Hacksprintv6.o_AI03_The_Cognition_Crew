import os
import json
import datetime
from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np

# Import custom modules
from modules.db_manager import init_db, clear_all_data, save_job_description, get_job_description, \
                               save_candidate, update_candidate_scores, get_ranked_candidates, \
                               save_team_member, get_team_member_embeddings
from modules.file_parser import extract_text
from modules.nlp_processor import get_embedding, calculate_similarity, calculate_team_fit, \
                                  calculate_composite_score, extract_skills_and_traits, nlp, model

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
CANDIDATE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'candidates')
JD_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'jd')
TEAM_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'team')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload size
app.secret_key = 'your_very_secret_key' # Change this for production
CORS(app) # Enable Cross-Origin Resource Sharing

# --- Ensure upload directories exist ---
os.makedirs(CANDIDATE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JD_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True)

# --- Initialize Database ---
init_db()

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_verdict(score):
    if score >= 80: return "Excellent Fit", "bg-green-100 text-green-800"
    if score >= 65: return "Consider", "bg-yellow-100 text-yellow-800"
    if score >= 50: return "Upskill Needed", "bg-orange-100 text-orange-800"
    return "Not Ideal", "bg-red-100 text-red-800"

# --- Routes ---
@app.route('/', methods=['GET'])
def index():
    """Renders the main upload page."""
    # Optionally, fetch some summary data if needed
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handles file uploads, processing, and scoring."""
    # 1. Clear previous data for a new analysis run
    clear_all_data()
    print("Cleared previous data.")

    # 2. Get form data
    candidate_files = request.files.getlist('candidate_resumes')
    jd_file = request.files.get('job_description')
    team_files = request.files.getlist('team_resumes')
    team_member_names = request.form.getlist('team_member_name')
    team_member_occupations = request.form.getlist('team_member_occupation')

    # Basic validation
    if not candidate_files or not candidate_files[0].filename:
        flash('No candidate resumes selected!', 'error')
        return redirect(url_for('index'))
    if not jd_file or jd_file.filename == '':
        flash('No job description file selected!', 'error')
        return redirect(url_for('index'))
    if not allowed_file(jd_file.filename):
         flash('Invalid job description file type (only .pdf, .docx allowed)', 'error')
         return redirect(url_for('index'))

    print(f"Received {len(candidate_files)} candidate files.")
    print(f"Received JD: {jd_file.filename}")
    print(f"Received {len(team_files)} team files.")

    # 3. Process Job Description
    jd_filename = secure_filename(jd_file.filename)
    jd_path = os.path.join(JD_UPLOAD_FOLDER, jd_filename)
    jd_file.save(jd_path)
    print(f"Saved JD to {jd_path}")

    jd_text = extract_text(jd_path)
    if not jd_text:
        flash(f'Could not extract text from job description: {jd_filename}', 'error')
        return redirect(url_for('index'))
    jd_embedding = get_embedding(jd_text)
    if jd_embedding is None:
         flash(f'Could not generate embedding for job description: {jd_filename}', 'error')
         return redirect(url_for('index'))

    save_job_description(jd_filename, jd_path, jd_text, jd_embedding)
    print("Processed and saved JD.")

    # 4. Process Team Resumes (if provided)
    team_embeddings = []
    use_team_fit = bool(team_files and team_files[0].filename and len(team_files) == len(team_member_names) == len(team_member_occupations))

    if use_team_fit:
        print("Processing team members...")
        for i, file in enumerate(team_files):
            if file and allowed_file(file.filename):
                member_name = team_member_names[i].strip() if i < len(team_member_names) else f"Team Member {i+1}"
                occupation = team_member_occupations[i].strip() if i < len(team_member_occupations) else "N/A"
                filename = secure_filename(file.filename)
                file_path = os.path.join(TEAM_UPLOAD_FOLDER, filename)
                file.save(file_path)

                text = extract_text(file_path)
                embedding = get_embedding(text) if text else None
                save_team_member(member_name, occupation, filename, file_path, text, embedding)
                if embedding is not None:
                    team_embeddings.append(embedding)
                print(f"Processed team member: {member_name}")
            else:
                 print(f"Skipping invalid team file or missing name/occupation at index {i}")
        print(f"Collected {len(team_embeddings)} valid team embeddings.")
    else:
        print("No valid team data provided or data mismatch, skipping team fit calculation.")


    # 5. Process Candidate Resumes and Score
    candidate_ids = [] # Store IDs for later updates if needed
    for i, file in enumerate(candidate_files):
        if file and allowed_file(file.filename):
            # Try to get name from form first, fallback to filename
            candidate_name = request.form.get(f'candidate_name_{i}', '').strip() # Assuming frontend sends names like candidate_name_0, candidate_name_1 etc.
            filename = secure_filename(file.filename)
            if not candidate_name: # Fallback if name wasn't provided or pattern mismatch
                 candidate_name = os.path.splitext(filename)[0].replace('_', ' ').title()

            file_path = os.path.join(CANDIDATE_UPLOAD_FOLDER, filename)
            file.save(file_path)
            print(f"Processing candidate: {candidate_name} ({filename})")

            text = extract_text(file_path)
            if not text:
                print(f"Warning: Could not extract text from {filename}. Skipping scoring.")
                # Optionally save candidate with error status or skip entirely
                save_candidate(candidate_name, filename, file_path, None, None, [], [])
                continue # Skip scoring for this candidate

            embedding = get_embedding(text)
            skills_traits = extract_skills_and_traits(text)

            candidate_id = save_candidate(
                candidate_name,
                filename,
                file_path,
                text,
                embedding,
                skills_traits['skills'],
                skills_traits['traits']
            )
            candidate_ids.append(candidate_id)

            # --- Scoring ---
            skill_match_score = 0.0
            team_fit_score = None
            composite_score = 0.0

            if embedding is not None and jd_embedding is not None:
                skill_match_score = calculate_similarity(embedding, jd_embedding)
                print(f"  Skill Match Score: {skill_match_score:.2f}")

                if use_team_fit and team_embeddings:
                    team_fit_score = calculate_team_fit(embedding, team_embeddings)
                    print(f"  Team Fit Score: {team_fit_score:.2f}")
                else:
                     team_fit_score = None # Explicitly None if not calculated

                composite_score = calculate_composite_score(skill_match_score, team_fit_score)
                print(f"  Composite Score: {composite_score:.2f}")

            else:
                 print(f"Warning: Could not generate embedding for {filename}. Scores set to 0.")


            update_candidate_scores(candidate_id, skill_match_score, team_fit_score, composite_score)

        else:
            flash(f'Invalid file type or no file provided for one of the candidates.', 'warning')

    print("Processing complete.")
    # 6. Redirect to Results Page
    return redirect(url_for('results'))

@app.route('/results', methods=['GET'])
def results():
    """Displays the ranked results page (NO CHARTS)."""
    print("--- Rendering /results (No Charts) ---") # Debugging line
    try:
        # Fetch data from DB
        jd_info = get_job_description()
        sort_by = request.args.get('sort_by', 'composite_score')
        order = request.args.get('order', 'DESC')
        candidates = get_ranked_candidates(sort_by=sort_by, order=order)
        print(f"Fetched {len(candidates)} candidates from DB.") # Debugging line

        # Prepare data for the template table
        results_data = []
        for cand in candidates:
            cand_data = dict(cand) # Copy row to modify
            score = cand_data.get('composite_score', 0) or 0
            cand_data['composite_score_display'] = f"{score:.1f}"
            cand_data['skill_match_score_display'] = f"{cand_data.get('skill_match_score', 0) or 0:.1f}"
            cand_data['team_fit_score_display'] = f"{cand_data.get('team_fit_score', 0) or 0:.1f}" if cand_data.get('team_fit_score') is not None else "N/A"
            cand_data['verdict_text'], cand_data['verdict_style'] = get_verdict(score)
            # Ensure traits is a list
            cand_data['extracted_traits'] = cand_data.get('extracted_traits', [])
            if not isinstance(cand_data['extracted_traits'], list):
                 cand_data['extracted_traits'] = []
            results_data.append(cand_data)

        # --- CHART DATA REMOVED ---
        # No chart_data_for_template needed

        print("Rendering results template without chart data.")

        # Pass only necessary data to the template
        return render_template(
            'results.html',
            job_title=jd_info.get('title', 'Job Description') if jd_info else 'Job Description',
            candidates=results_data
            # chart_data argument removed
        )

    except Exception as e:
        # Log the general error if something else goes wrong in the route
        print(f"!!! ERROR in /results route: {e}")
        import traceback
        traceback.print_exc()
        # Render a fallback or error page if appropriate
        return render_template('results.html', job_title="Error", candidates=[])
    
@app.route('/api/results', methods=['GET'])
def api_results():
    jd_info = get_job_description()
    sort_by = request.args.get('sort_by', 'composite_score')
    order = request.args.get('order', 'DESC')
    candidates = get_ranked_candidates(sort_by=sort_by, order=order)
     # Prepare data like in the /results route
    results_data = []
    for cand in candidates:
        # ... (same data preparation as in results route) ...
        results_data.append(dict(cand)) # Just send raw dict for API

    return jsonify({
        "job_title": jd_info.get('title', 'Job Description') if jd_info else 'N/A',
        "candidates": results_data
    })


if __name__ == '__main__':
    # Make sure NLP models are loaded before starting server
    if not nlp or not model:
         print("CRITICAL ERROR: NLP models failed to load. Exiting.")
         exit(1)
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000) # Use port 5500 as in screenshot