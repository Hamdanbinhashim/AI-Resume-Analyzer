import re

# Technical terms with special symbols that must be preserved before stripping punctuation
TOKEN_REPLACEMENTS = {
    r"\bc\+\+\b": " cplusplus ",
    r"\bc#\b": " csharp ",
    r"\b\.net\b": " dotnet ",
    r"\bnode\.js\b": " nodejs ",
    r"\breact\.js\b": " reactjs "
}

def clean_resume_text(text: str) -> str:
    """
    Cleans and normalizes resume text for skill extraction and NLP matching.
    
    Steps:
    1. Convert text to lowercase.
    2. Protect special tech terms (e.g. C++, .NET) from punctuation removal.
    3. Remove special characters and normalize whitespace.
    """
    if not text:
        return ""
    
    cleaned = text.lower()
    
    # Protect special technical terms
    for pattern, replacement in TOKEN_REPLACEMENTS.items():
        cleaned = re.sub(pattern, replacement, cleaned)
        
    # Remove non-alphanumeric characters except spaces
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    
    # Collapse multiple spaces into a single space
    return re.sub(r"\s+", " ", cleaned).strip()