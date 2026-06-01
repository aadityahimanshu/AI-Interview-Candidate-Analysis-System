import random
# import spacy
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# nlp = spacy.load("en_core_web_sm")

# Interview Questions
questions = [
    "Tell me about yourself.",
    "Explain a challenging project you worked on.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?",
    "Describe a time you solved a difficult problem.",
    "Explain your experience with Python.",
    "How do you handle pressure at work?"
]


def generate_question():
    return random.choice(questions)


def evaluate_answer(answer):

    if len(answer.split()) < 20:
        return 40

    if len(answer.split()) < 50:
        return 60

    if len(answer.split()) < 100:
        return 80

    return 90