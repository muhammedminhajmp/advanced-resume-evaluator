import os
import re
import spacy
import pandas as pd
import pdfplumber

# Define the keywords and criteria for Software Testers
REQUIRED_SKILLS = {
    "testing_types": ["manual testing", "automation testing", "api testing", "performance testing", "regression testing",
                      "functional testing"],
    "tools": ["selenium", "postman", "jmeter", "testng"],
    "bug_tracking_tools": ["jira"],
    "programming_languages": ["java"],
    "methodologies": ["agile"]
}

# Load spaCy's English model for NER
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def evaluate_resume(text, required_skills):
    """Evaluate the resume based on required skills."""
    matched_skills = {category: [] for category in required_skills}
    for category, keywords in required_skills.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                matched_skills[category].append(keyword)
    return matched_skills

# def score_resume(matched_skills):
#     """Calculate a simple score based on matched skills."""
#     total_keywords = sum(len(keywords) for keywords in REQUIRED_SKILLS.values())
#     matched_keywords = sum(len(skills) for skills in matched_skills.values())
#     return (matched_keywords / total_keywords) * 100

def score_resume(matched_skills):
    """Calculate a simple score based on matched skills."""
    total_keywords = sum(len(keywords) for keywords in REQUIRED_SKILLS.values())
    matched_keywords = sum(len(skills) for skills in matched_skills.values())
    score = (matched_keywords / total_keywords) * 100
    return round(score, 2)  # Round to 2 decimal places

def extract_name_from_filename(filename):
    """
    Extract the name from the resume filename by removing 'resume' or 'cv' keywords.
    """
    name_without_extension = os.path.splitext(filename)[0]
    cleaned_name = re.sub(r"[\s_/-]*(resume|cv|pdf)[\s_/-]*", "", name_without_extension, flags=re.IGNORECASE)
    return ' '.join(cleaned_name.split()).title()

def extract_entities(text, filename=None):
    """
    Extract names, places, phone numbers, and email addresses from text.
    Optionally, extract name from filename if provided.
    """
    names = []
    if filename:
        name_from_filename = extract_name_from_filename(filename)
        if name_from_filename:
            names.append(name_from_filename)

    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE" and len(ent.text.split()) < 3]
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_numbers = re.findall(r"(?:\+91[-.\s]?)?\d{10}", text)

    return {
        "names": list(set(names)),
        "locations": list(set(locations)),
        "emails": list(set(emails)),
        "phone_numbers": list(set(phone_numbers)),
    }

def save_to_spreadsheet(data, output_file):
    """Save extracted data to a spreadsheet."""
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

def process_resume(pdf_path):
    """
    Process a single resume file and return the extracted details, matched skills, and score.
    """
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    matched_skills = evaluate_resume(text, REQUIRED_SKILLS)
    score = score_resume(matched_skills)
    extracted_entities = extract_entities(text, os.path.basename(pdf_path))

    return {
        "file_name": os.path.basename(pdf_path),
        "entities": extracted_entities,
        "matched_skills": matched_skills,
        "score": score,
    }