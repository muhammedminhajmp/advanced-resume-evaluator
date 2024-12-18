from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import zipfile
import io
import pdfplumber
import spacy
import re
import pandas as pd

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

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.secret_key = 'ce6bbc2c41b92c8944a2c5ac395a3dc1421663323122e68a'  # Replace with a secure key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension (pdf)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def process_resume(pdf_path, filename):
    """
    Process a single resume file and return the extracted details, matched skills, and score.
    """
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    matched_skills = evaluate_resume(text, REQUIRED_SKILLS)
    score = score_resume(matched_skills)
    extracted_entities = extract_entities(text, filename)

    return {
        "file_name": filename,
        "entities": extracted_entities,
        "matched_skills": matched_skills,
        "score": score,
    }

@app.route('/')
def index():
    """Render the index.html page."""
    return render_template('home.html')

# @app.route('/api/upload_resume', methods=['POST'])
# def upload_resume():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     files = request.files.getlist('file')

#     if not files:
#         return jsonify({'error': 'No files selected'}), 400

#     results = []

#     for file in files:
#         if file.filename.endswith('.zip'):
#             # Handle zip file containing multiple PDFs
#             zip_data = file.read()
#             with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
#                 for zip_name in zip_file.namelist():
#                     if zip_name.endswith('.pdf'):
#                         zip_file.extract(zip_name, app.config['UPLOAD_FOLDER'])
#                         file_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_name)
#                         result = process_resume(file_path, zip_name)
#                         if result:
#                             results.append(result)
#         elif allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             result = process_resume(file_path, filename)
#             if result:
#                 results.append(result)
#         else:
#             return jsonify({'error': f'File type {file.filename.split(".")[-1]} not allowed'}), 400
    
#     if not results:
#         return jsonify({'error': 'No valid resumes found'}), 400
    
#     return jsonify({'data': results})

import pandas as pd

from flask import send_from_directory

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('file')

    if not files:
        return jsonify({'error': 'No files selected'}), 400

    results = []

    for file in files:
        if file.filename.endswith('.zip'):
            # Handle zip file containing multiple PDFs
            zip_data = file.read()
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
                for zip_name in zip_file.namelist():
                    if zip_name.endswith('.pdf'):
                        zip_file.extract(zip_name, app.config['UPLOAD_FOLDER'])
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_name)
                        result = process_resume(file_path, zip_name)
                        if result:
                            results.append(result)
        elif allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = process_resume(file_path, filename)
            if result:
                results.append(result)
        else:
            return jsonify({'error': f'File type {file.filename.split(".")[-1]} not allowed'}), 400
    
    if not results:
        return jsonify({'error': 'No valid resumes found'}), 400
    
    # Save results to an Excel spreadsheet
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'resume_analysis.xlsx')
    
    # Prepare data for spreadsheet (convert results to a list of dictionaries)
    spreadsheet_data = []
    for result in results:
        spreadsheet_data.append({
            'File Name': result['file_name'],
            'Names': ', '.join(result['entities']['names']),
            'Locations': ', '.join(result['entities']['locations']),
            'Emails': ', '.join(result['entities']['emails']),
            'Phone Numbers': ', '.join(result['entities']['phone_numbers']),
            'Matched Skills': str(result['matched_skills']),
            'Relevance Score': result['score'],
        })
    
    # Save to Excel using pandas
    df = pd.DataFrame(spreadsheet_data)
    df.to_excel(output_file, index=False)
    
    return jsonify({
        'message': 'Resumes processed successfully',
        'data': results,
        'download_link': url_for('download_file', filename='resume_analysis.xlsx')
    })

@app.route('/uploads/<filename>')
def download_file(filename):
    """Route to download the saved Excel file."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
