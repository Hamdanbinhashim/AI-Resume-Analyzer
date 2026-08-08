from pypdf import PdfReader
from docx import Document

def extract_text(uploaded_file) -> str:
    """
    Extracts raw text content from uploaded PDF or DOCX file objects.
    
    Args:
        uploaded_file: Streamlit UploadedFile object containing file data.
        
    Returns:
        str: Combined text string from all pages/paragraphs.
    """
    file_name = uploaded_file.name.lower()
    text_chunks = []
    
    try:
        # Extract text page-by-page from PDF files
        if file_name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            text_chunks = [page.extract_text() for page in pdf.pages if page.extract_text()]
            
        # Extract text paragraph-by-paragraph from Word DOCX files
        elif file_name.endswith(".docx"):
            doc = Document(uploaded_file)
            text_chunks = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
            
    except Exception as e:
        print(f"Error parsing file {file_name}: {e}")
        return ""
        
    return " ".join(text_chunks).strip()