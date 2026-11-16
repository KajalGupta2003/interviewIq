import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", before="ner")

try:
    ruler.from_disk("./data/jz_skill_patterns.jsonl")
    print("Successfully loaded 2000+ skill patterns.")
except Exception as e:
    print(f"Warning: Could not load jsonl file. Error: {e}")

BLACKLIST_SKILLS = {
    "experience", "years", "team", "project", "knowledge", 
    "ability", "work", "responsibility", "candidate", "level"
}
# Universal list of headers to detect section boundaries
ALL_HEADINGS = [
    "experience", "work experience", "internship", "employment",
    "education", "academic background", "qualification",
    "skills", "technical skills", "technologies", "tools",
    "projects", "personal projects", "academic projects",
    "achievements", "awards", "honors", "certifications", 
    "summary", "objective", "languages", "publications"
]

def extract_section(text, section_keywords):
    lines = text.split("\n")
    capturing = False
    section_lines = []

   
    # all_headers = [
    #     "education", "technical skills", "skills", "projects", 
    #     "experience", "work experience", "achievements", 
    #     "extracurricular", "summary", "objective"
    # ]
    all_headers = ALL_HEADINGS

    for line in lines:
        clean_line = line.strip().lower()
        if not clean_line:
            continue

        
        if any(kw in clean_line for kw in section_keywords):
            capturing = True
            continue

       
        if capturing:
            
            if any(h == clean_line for h in all_headers):
               
                if not any(kw in clean_line for kw in section_keywords):
                    break
            
            section_lines.append(line.strip())

    return section_lines
# --- Wrapper Functions for your FastAPI routes ---

def extract_skills(text):
    raw_section = extract_section(text, ["skills", "technical skills", "technologies", "tools"])
    return refine_skills(raw_section)

def extract_experience(text):
    return extract_section(text, ["experience", "work experience", "internship"])

def extract_projects(text):
    return extract_section(text, ["projects", "personal projects", "academic projects"])

def extract_achievements(text):
    
    return extract_section(text, ["achievements", "awards", "honors"])

def refine_skills(skills_list):
   
    if not skills_list:
        return []
    text = " ".join(skills_list)
    text = text.replace("|", " ").replace(",", " ")
    doc = nlp(text)

    # From Jsonl
    official_skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    official_lower = {s.lower() for s in official_skills}

    potential_skills = []
    for token in doc:
        clean_token = token.text.strip()
        if token.pos_ in ["NOUN", "PROPN"] and len(clean_token) > 2:
            if token.is_stop:
                continue
            if not token.is_alpha:
                continue
            if clean_token.lower() in BLACKLIST_SKILLS:
                continue
            if clean_token.lower() not in official_lower:
                potential_skills.append(clean_token)

    final_skills = set()
    
    for skill in official_skills + potential_skills:
        final_skills.add(skill.lower())
    return sorted(final_skills)