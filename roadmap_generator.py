from google import genai

def generate_learning_roadmap(target_role: str, missing_skills: list, api_key: str) -> str:
    """
    Generates a structured 4-week learning roadmap for missing skills using Google Gemini AI.
    
    Args:
        target_role: Target job role title string.
        missing_skills: List of missing skill strings.
        api_key: Gemini API key from environment variables.
        
    Returns:
        str: Generated markdown roadmap string or status message.
    """
    if not missing_skills:
        return "You already possess all baseline required skills for this role!"
        
    if not api_key:
        return "API Key missing. Please add your Gemini API Key to the .env file."
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert technical career mentor.
        Target Job Role: {target_role}
        Missing Technical Skills: {', '.join(missing_skills)}
        
        Task:
        Create a concise, practical week-by-week learning roadmap (up to 4 weeks) to help a student learn these missing skills.
        For each week, provide:
        1. Focus Topic
        2. Core practical task or mini-project to build
        Keep the tone encouraging, professional, and directly focused on the listed missing skills.
        """
        
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        return f"An error occurred while communicating with Google Gemini: {e}"
