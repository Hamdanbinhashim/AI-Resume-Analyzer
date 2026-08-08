import os
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

def build_full_context_system_prompt(
    raw_resume_text: str,
    categorized_skills: dict,
    target_role: dict,
    job_roles_df: pd.DataFrame,
    skill_dict_df: pd.DataFrame,
    generated_roadmap: str = ""
) -> str:
    """
    Constructs a full-context system prompt for the AI Resume Coach:
    - Entire parsed candidate resume text
    - Extracted technical skills grouped by category
    - Target job role, match percentage score, found & missing skills
    - Candidate's generated learning roadmap (if available)
    - Full industry job roles dataset
    - Complete skill dictionary taxonomy
    """
    found_skills_str = ", ".join(target_role.get("found_skills", [])) if target_role.get("found_skills") else "None"
    missing_skills_str = ", ".join(target_role.get("missing_skills", [])) if target_role.get("missing_skills") else "None"
    
    categorized_str = "\n".join(f"- {cat}: {', '.join(skills)}" for cat, skills in categorized_skills.items()) if categorized_skills else "None detected"
    roles_context = "\n".join(f"- {row['role_name']}: Required Skills -> {row['required_skills']}" for _, row in job_roles_df.iterrows())
    skills_context = ", ".join(sorted(skill_dict_df['category'].unique()))
    roadmap_context = f"\"\"\"\n{generated_roadmap[:2500]}\n\"\"\"" if generated_roadmap and generated_roadmap.strip() else "None generated yet."
    
    system_prompt = f"""You are an elite ATS Resume Coach and Technical Career Mentor.
You are helping a candidate optimize their resume for technical job applications.

FULL CANDIDATE CONTEXT:
Target Role: {target_role.get('role_name', 'Technical Role')}
Match Score: {target_role.get('match_score', 0.0):.1f}%
Skills Found: {found_skills_str}
Missing Skills (Gaps): {missing_skills_str}

CANDIDATE'S GENERATED LEARNING ROADMAP:
{roadmap_context}

EXTRACTED SKILLS TAXONOMY:
{categorized_str}

ENTIRE CANDIDATE RESUME TEXT:
\"\"\"
{raw_resume_text[:4000]}
\"\"\"

AVAILABLE INDUSTRY JOB ROLES TAXONOMY:
{roles_context}

SKILL DICTIONARY CATEGORIES:
{skills_context}

YOUR GUIDELINES:
1. Provide professional, direct, and actionable resume optimization advice.
2. When asked to rewrite bullet points, provide high-impact STAR-method (Situation, Task, Action, Result) versions with quantifiable metrics and active verbs.
3. Reference the candidate's actual resume text, missing skills, and generated learning roadmap to customize your answers.
4. Maintain a clean, professional, and encouraging tone without using informal emojis.
"""
    return system_prompt


def get_langchain_coach_response(
    messages_history: list,
    user_query: str,
    raw_resume_text: str,
    categorized_skills: dict,
    target_role: dict,
    job_roles_df: pd.DataFrame,
    skill_dict_df: pd.DataFrame,
    generated_roadmap: str = "",
    api_key: str = ""
) -> str:
    """
    Executes a LangChain LCEL pipeline (ChatPromptTemplate | ChatGoogleGenerativeAI | StrOutputParser)
    to return a clean markdown string response.
    """
    if not api_key:
        return "API Key missing. Please add your Gemini API Key to the .env file."
        
    try:
        # Initialize LangChain Chat Model for Google Gemini
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            google_api_key=api_key,
            temperature=0.4
        )
        
        # Build System Prompt Context
        system_text = build_full_context_system_prompt(
            raw_resume_text,
            categorized_skills,
            target_role,
            job_roles_df,
            skill_dict_df,
            generated_roadmap
        )
        
        # 1. Define LangChain Chat Prompt Template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_text),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}")
        ])
        
        # 2. Reconstruct Conversation History into LangChain Message Objects
        history_messages = []
        for msg in messages_history:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=str(msg["content"])))
            elif msg["role"] == "assistant":
                content_text = msg["content"]
                if isinstance(content_text, list):
                    content_text = " ".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in content_text])
                history_messages.append(AIMessage(content=str(content_text)))
                
        # 3. Create LCEL Chain (Prompt | LLM | StrOutputParser)
        output_parser = StrOutputParser()
        chain = prompt_template | llm | output_parser
        
        # 4. Invoke LangChain Chain
        response_text = chain.invoke({
            "chat_history": history_messages,
            "user_input": user_query
        })
        
        return str(response_text)
        
    except Exception as e:
        return f"An error occurred while communicating with the AI Resume Coach: {e}"
