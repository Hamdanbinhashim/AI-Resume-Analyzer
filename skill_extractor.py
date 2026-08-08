import os
import re
import pandas as pd

def load_skill_dictionary(filepath="data/skill_dictionary.csv") -> pd.DataFrame:
    """
    Loads the controlled technical skill taxonomy from a CSV file.
    Normalizes column headers to lowercase.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Skill dictionary file missing at {filepath}")
    
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df


def extract_skills(text: str, skill_dict_df: pd.DataFrame) -> dict:
    """
    Scans normalized resume text for technical skills using word-boundary regex matching.
    
    Args:
        text: Normalized text string.
        skill_dict_df: Dataframe with 'category' and 'skill_name' columns.
        
    Returns:
        dict: Grouped skills by category, e.g. {'Programming': ['python', 'cplusplus']}
    """
    if 'category' not in skill_dict_df.columns or 'skill_name' not in skill_dict_df.columns:
        raise ValueError("Skill dataset must contain 'category' and 'skill_name' columns.")
        
    extracted_skills = {}
    
    # Iterate through skill taxonomy and perform regex matching
    for _, row in skill_dict_df.iterrows():
        category = str(row['category']).strip()
        skill = str(row['skill_name']).lower().strip()
        
        # \b ensures exact word boundary matching (prevents 'c' from matching inside 'cat')
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            cat_list = extracted_skills.setdefault(category, [])
            if skill not in cat_list:
                cat_list.append(skill)
                
    return extracted_skills
