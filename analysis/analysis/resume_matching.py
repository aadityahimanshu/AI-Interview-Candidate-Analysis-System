from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def resume_match(resume_text, interview_text):

    r = model.encode(resume_text, convert_to_tensor=True)
    i = model.encode(interview_text, convert_to_tensor=True)

    score = util.cos_sim(r, i)

    return float(score[0][0])