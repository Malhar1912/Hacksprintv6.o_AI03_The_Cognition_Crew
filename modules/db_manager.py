import sqlite3
import json
import datetime
import numpy as np
import os

DATABASE_PATH = 'database.db'
UPLOAD_FOLDER = 'uploads' # Base upload folder

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing tables for a fresh start each time (optional, for demo purposes)
    # In production, you might want migrations instead.
    # cursor.execute("DROP TABLE IF EXISTS candidates")
    # cursor.execute("DROP TABLE IF EXISTS job_description")
    # cursor.execute("DROP TABLE IF EXISTS team_members")

    # Candidate Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_content TEXT,
            embedding BLOB, -- Store embedding as BLOB (requires serialization)
            skill_match_score REAL,
            team_fit_score REAL,
            composite_score REAL,
            extracted_skills TEXT, -- Store as JSON string
            extracted_traits TEXT  -- Store as JSON string
        )
    ''')

    # Job Description Table (assuming only one active JD at a time for simplicity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_description (
            id INTEGER PRIMARY KEY CHECK (id = 1), -- Enforce only one row
            title TEXT DEFAULT 'Job Description',
            original_filename TEXT,
            file_path TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_content TEXT,
            embedding BLOB
        )
    ''')

    # Team Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            occupation TEXT,
            original_filename TEXT,
            file_path TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_content TEXT,
            embedding BLOB
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")

def clear_all_data():
    """Clears all data from the tables for a fresh analysis run."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM candidates")
        cursor.execute("DELETE FROM job_description")
        cursor.execute("DELETE FROM team_members")
        conn.commit()
        print("Previous analysis data cleared.")

        # Also clear uploaded files
        for folder in ['candidates', 'jd', 'team']:
            folder_path = os.path.join(UPLOAD_FOLDER, folder)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")

    except sqlite3.Error as e:
        print(f"Database error during clearing: {e}")
    finally:
        conn.close()


# --- Job Description Functions ---
def save_job_description(filename, file_path, text, embedding):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_description") # Ensure only one JD
    embedding_blob = sqlite3.Binary(json.dumps(embedding.tolist()).encode('utf-8')) if embedding is not None else None
    cursor.execute('''
        INSERT INTO job_description (id, original_filename, file_path, text_content, embedding)
        VALUES (1, ?, ?, ?, ?)
    ''', (filename, file_path, text, embedding_blob))
    conn.commit()
    jd_id = cursor.lastrowid
    conn.close()
    return jd_id

def get_job_description():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_description WHERE id = 1")
    jd = cursor.fetchone()
    conn.close()
    if jd:
        jd_dict = dict(jd)
        if jd_dict.get('embedding'):
            try:
                jd_dict['embedding'] = json.loads(jd_dict['embedding'].decode('utf-8'))
            except (json.JSONDecodeError, AttributeError):
                 jd_dict['embedding'] = None # Handle cases where blob is invalid
        return jd_dict
    return None


# --- Candidate Functions ---
def save_candidate(name, filename, file_path, text, embedding, skills, traits):
    conn = get_db_connection()
    cursor = conn.cursor()
    embedding_blob = sqlite3.Binary(json.dumps(embedding.tolist()).encode('utf-8')) if embedding is not None else None
    skills_json = json.dumps(skills) if skills else '[]'
    traits_json = json.dumps(traits) if traits else '[]'
    cursor.execute('''
        INSERT INTO candidates (name, original_filename, file_path, text_content, embedding, extracted_skills, extracted_traits)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, filename, file_path, text, embedding_blob, skills_json, traits_json))
    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()
    return candidate_id

def update_candidate_scores(candidate_id, skill_score, team_score, composite_score):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE candidates
        SET skill_match_score = ?, team_fit_score = ?, composite_score = ?
        WHERE id = ?
    ''', (skill_score, team_score, composite_score, candidate_id))
    conn.commit()
    conn.close()

def get_ranked_candidates(sort_by='composite_score', order='DESC'):
    """Retrieves candidates, ranked by the specified score."""
    conn = get_db_connection()
    # Basic validation to prevent SQL injection on column name/order
    valid_sort_columns = ['composite_score', 'skill_match_score', 'team_fit_score', 'name', 'upload_time']
    valid_orders = ['ASC', 'DESC']
    if sort_by not in valid_sort_columns:
        sort_by = 'composite_score'
    if order.upper() not in valid_orders:
        order = 'DESC'

    query = f"SELECT * FROM candidates ORDER BY {sort_by} {order.upper()}"
    cursor = conn.cursor()
    cursor.execute(query)
    candidates = cursor.fetchall()
    conn.close()

    results = []
    for row in candidates:
        candidate_dict = dict(row)
         # Deserialize embedding (optional, might not be needed for results page directly)
        # if candidate_dict.get('embedding'):
        #     try:
        #         candidate_dict['embedding'] = json.loads(candidate_dict['embedding'].decode('utf-8'))
        #     except:
        #         candidate_dict['embedding'] = None
        # else:
        #      candidate_dict['embedding'] = None
        candidate_dict.pop('embedding', None) # Remove embedding blob from results sent to frontend

        # Deserialize skills/traits
        try:
            candidate_dict['extracted_skills'] = json.loads(candidate_dict.get('extracted_skills', '[]'))
        except (json.JSONDecodeError, TypeError):
            candidate_dict['extracted_skills'] = []
        try:
            candidate_dict['extracted_traits'] = json.loads(candidate_dict.get('extracted_traits', '[]'))
        except (json.JSONDecodeError, TypeError):
            candidate_dict['extracted_traits'] = []

        # Format timestamp
        try:
            # Assuming timestamp is stored like 'YYYY-MM-DD HH:MM:SS'
             dt_obj = datetime.datetime.strptime(candidate_dict['upload_time'], '%Y-%m-%d %H:%M:%S')
             candidate_dict['upload_time_formatted'] = dt_obj.strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            candidate_dict['upload_time_formatted'] = 'N/A' # Handle potential parsing errors or NULL

        results.append(candidate_dict)

    return results

# --- Team Member Functions ---
def save_team_member(name, occupation, filename, file_path, text, embedding):
    conn = get_db_connection()
    cursor = conn.cursor()
    embedding_blob = sqlite3.Binary(json.dumps(embedding.tolist()).encode('utf-8')) if embedding is not None else None
    cursor.execute('''
        INSERT INTO team_members (name, occupation, original_filename, file_path, text_content, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, occupation, filename, file_path, text, embedding_blob))
    conn.commit()
    member_id = cursor.lastrowid
    conn.close()
    return member_id

def get_team_member_embeddings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT embedding FROM team_members")
    rows = cursor.fetchall()
    conn.close()
    embeddings = []
    for row in rows:
        if row['embedding']:
            try:
                # Deserialize BLOB back to list, then convert to numpy array
                emb_list = json.loads(row['embedding'].decode('utf-8'))
                embeddings.append(np.array(emb_list))
            except (json.JSONDecodeError, AttributeError, ValueError):
                print("Warning: Could not deserialize team member embedding.")
                continue # Skip invalid embeddings
    return embeddings