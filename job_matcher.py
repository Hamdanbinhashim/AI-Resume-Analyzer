import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_job_roles(filepath="data/job_roles.csv") -> pd.DataFrame:
    """
    Loads predefined job roles and required skills from CSV.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Job roles dataset file missing at {filepath}")
    return pd.read_csv(filepath)


def rank_job_roles(user_skills: list, jobs_df: pd.DataFrame) -> list:
    """
    Ranks job roles against candidate skills using TF-IDF vectorization 
    and Cosine Similarity scoring. Also identifies found and missing skills.
    
    Args:
        user_skills: List of extracted skill strings from candidate's resume.
        jobs_df: Dataframe containing job roles and required skills.
        
    Returns:
        list: Sorted dictionaries containing role details, match score, found and missing skills.
    """
    if not user_skills or jobs_df.empty:
        return []
    
    user_skills_str = " ".join(user_skills).lower()
    user_skill_set = set(user_skills)
    
    # Extract required skill lists and space-separated strings per role
    role_req_lists = [
        [s.strip().lower() for s in str(row['required_skills']).split(",") if s.strip()]
        for _, row in jobs_df.iterrows()
    ]
    role_req_strings = [" ".join(reqs) for reqs in role_req_lists]
    
    # Compute TF-IDF Matrix across candidate skills (row 0) and all job roles (rows 1..)
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([user_skills_str] + role_req_strings)
        # Compute Cosine Similarity between user vector (row 0) and role vectors (rows 1..)
        sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    except ValueError:
        # Fallback for empty vocabulary edge cases
        sim_scores = [0.0] * len(jobs_df)
        
    # Calculate exact found and missing skills per role
    results = []
    for i, (_, row) in enumerate(jobs_df.iterrows()):
        req_list = role_req_lists[i]
        found = [s for s in req_list if s in user_skill_set]
        missing = [s for s in req_list if s not in user_skill_set]
        
        results.append({
            "role_name": row['role_name'],
            "match_score": round(float(sim_scores[i] * 100), 1),
            "found_skills": found,
            "missing_skills": missing
        })
        
    # Sort roles from highest to lowest match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results