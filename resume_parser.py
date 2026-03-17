import docx
import re


def extract_text_from_docx(file):

    doc = docx.Document(file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def extract_skills(text):

    skills = [
        "python","sql","machine learning",
        "data analysis","power bi","tableau",
        "excel","statistics","deep learning"
    ]

    found = []

    for skill in skills:

        if skill in text.lower():
            found.append(skill)

    return found


def resume_match_score(skills):

    score = len(skills) * 10

    return min(score,100)