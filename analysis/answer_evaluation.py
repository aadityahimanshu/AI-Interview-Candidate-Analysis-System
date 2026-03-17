from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def evaluate_answer(candidate_answer, ideal_answer):

    emb1 = model.encode(candidate_answer, convert_to_tensor=True)
    emb2 = model.encode(ideal_answer, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2)

    return float(score[0][0])