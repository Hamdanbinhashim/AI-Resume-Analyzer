import re
from fpdf import FPDF

def render_roadmap_markdown(pdf: FPDF, roadmap_text: str):
    """
    Parses markdown formatted roadmap text into styled FPDF elements.
    Handles headers, bold bullet points, numbers, and paragraphs.
    """
    lines = roadmap_text.split('\n')
    
    for line in lines:
        # Encode string safely for FPDF latin-1 font support
        raw_line = line.encode('latin-1', 'replace').decode('latin-1').rstrip()
        stripped = raw_line.strip()
        
        if not stripped:
            pdf.ln(2)
            continue
            
        # 1. Section Headers (# , ## , ###)
        if stripped.startswith('#'):
            header_level = len(stripped) - len(stripped.lstrip('#'))
            header_text = stripped.lstrip('#').strip()
            header_text = re.sub(r'\*\*(.*?)\*\*', r'\1', header_text)
            
            pdf.ln(3)
            if header_level <= 2:
                pdf.set_font("Arial", 'B', 13)
                pdf.set_text_color(41, 128, 185)  # Accent Blue
            else:
                pdf.set_font("Arial", 'B', 11)
                pdf.set_text_color(44, 62, 80)   # Dark Navy
                
            pdf.cell(0, 7, txt=header_text, ln=1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)
            
        # 2. Bullet Points (- , * , • , 1. , 2. )
        elif stripped.startswith(('-', '*', '•')) or (stripped[0].isdigit() and stripped[1:3] in ('. ', ') ')):
            content = stripped[1:].strip() if stripped.startswith(('-', '*', '•')) else stripped
            bold_match = re.match(r'^\*\*(.*?)\*\*:?\s*(.*)', content)
            
            pdf.set_font("Arial", '', 10)
            if bold_match:
                key_part = bold_match.group(1).strip()
                val_part = bold_match.group(2).strip()
                
                pdf.set_font("Arial", 'B', 10)
                pdf.write(5, f"   - {key_part}: ")
                pdf.set_font("Arial", '', 10)
                pdf.write(5, val_part + "\n")
            else:
                clean_content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                pdf.multi_cell(0, 5, txt=f"   - {clean_content}")
                
        # 3. Standalone Bold Titles (**Week 1: ...**)
        elif stripped.startswith('**') and stripped.endswith('**'):
            title_text = stripped[2:-2].strip()
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(41, 128, 185)
            pdf.cell(0, 6, txt=title_text, ln=1)
            pdf.set_text_color(0, 0, 0)
            
        # 4. Standard Paragraphs
        else:
            bold_match = re.match(r'^\*\*(.*?)\*\*:?\s*(.*)', stripped)
            if bold_match:
                key_part = bold_match.group(1).strip()
                val_part = bold_match.group(2).strip()
                pdf.set_font("Arial", 'B', 10)
                pdf.write(5, f"{key_part}: ")
                pdf.set_font("Arial", '', 10)
                pdf.write(5, val_part + "\n")
            else:
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 5, txt=clean_line)


def create_pdf_report(role_name: str, match_score: float, found_skills: list, missing_skills: list, roadmap_text: str) -> bytes:
    """
    Generates a PDF analysis report summarizing target role match, skills found, 
    missing skill gaps, and AI learning roadmap.
    
    Returns:
        bytes: Encoded PDF binary data ready for file download.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, txt="AI Resume Analysis Report", ln=1, align='C')
    pdf.ln(10)

    # Role Match Overview
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"Target Role: {role_name}", ln=1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=f"Match Score: {match_score:.1f}%", ln=1)
    pdf.ln(5)

    # Strengths
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Strengths (Found Skills):", ln=1)
    pdf.set_font("Arial", '', 11)
    skills_found_str = ", ".join([s.title() for s in found_skills]) if found_skills else "None found."
    pdf.multi_cell(0, 6, txt=skills_found_str)
    pdf.ln(5)

    # Skill Gaps
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt="Gaps (Missing Skills):", ln=1)
    pdf.set_font("Arial", '', 11)
    skills_missing_str = ", ".join([s.title() for s in missing_skills]) if missing_skills else "No missing skills. Perfect match!"
    pdf.multi_cell(0, 6, txt=skills_missing_str)
    pdf.ln(10)

    # Learning Roadmap Appendix Page
    if roadmap_text:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt="Action Plan & Learning Roadmap", ln=1)
        pdf.ln(5)
        render_roadmap_markdown(pdf, roadmap_text)

    return pdf.output(dest='S').encode('latin-1')