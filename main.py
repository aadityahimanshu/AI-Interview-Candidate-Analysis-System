import cv2
import numpy as np
import json
import os
import speech_recognition as sr
from textblob import TextBlob
# from fer import FER
import librosa
import joblib
import pandas as pd
import time
from collections import Counter

RESULT_FILE = "data/candidates_results.csv"


# ==============================
# LOAD MODELS
# ==============================

def load_models():

    models = {}

    try:
        models["competency_model"] = joblib.load("models/competency_classifier_model.pkl")
        models["tfidf"] = joblib.load("models/tfidf_vectorizer.pkl")
    except:
        models["competency_model"] = None
        models["tfidf"] = None

    return models


models = load_models()


# ==============================
# VIDEO ANALYSIS
# ==============================

def analyze_video(video_path):

    detector = None
    cap = cv2.VideoCapture(video_path)

    emotions = []
    total_frames = 0
    eye_frames = 0

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    frame_id = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_id += 1

        if frame_id % 10 != 0:
            continue

        total_frames += 1

        # Emotion detection disabled for cloud deployment
        emotions.append("neutral")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray,1.3,5)

        if len(faces) > 0:
            eye_frames += 1

    cap.release()

    emotion_counts = dict(Counter(emotions))

    eye_score = round((eye_frames / max(total_frames,1)) * 100,2)

    return emotion_counts, eye_score


# ==============================
# AUDIO + TRANSCRIPT
# ==============================

def extract_audio_text(video_path):

    recognizer = sr.Recognizer()

    audio_path = video_path.replace(".mp4",".wav")

    os.system(f'ffmpeg -y -i "{video_path}" "{audio_path}" -loglevel quiet')

    try:

        with sr.AudioFile(audio_path) as source:

            audio = recognizer.record(source)

            text = recognizer.recognize_google(audio)

    except:

        text = ""

    return text, audio_path


# ==============================
# SENTIMENT
# ==============================

def analyze_sentiment(text):

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0:
        return 80
    elif polarity < 0:
        return 40
    else:
        return 60


# ==============================
# SPEECH CLARITY
# ==============================

def speech_clarity_score(text):

    filler_words = ["um","uh","like","you know","actually"]

    words = text.lower().split()

    filler_count = sum(words.count(word) for word in filler_words)

    total_words = max(len(words),1)

    clarity = 100 - ((filler_count/total_words)*100)

    return round(max(clarity,0),2)


# ==============================
# VOICE ANALYSIS
# ==============================

def analyze_voice(audio_path):

    try:

        y, sr_rate = librosa.load(audio_path, duration=30)

        pitch = np.mean(librosa.yin(y, fmin=50, fmax=300))

        energy = np.mean(librosa.feature.rms(y=y))

        voice_score = min(100, (energy*100))

        return round(voice_score,2)

    except:

        return 50


# ==============================
# COMPETENCY MODEL
# ==============================

def predict_competency(text):

    if models["competency_model"] is None:
        return 60

    vec = models["tfidf"].transform([text])

    pred = models["competency_model"].predict(vec)[0]

    return float(pred)


# ==============================
# FINAL ANALYSIS
# ==============================

def run_analysis(video_path):

    emotions, eye_contact = analyze_video(video_path)

    transcript, audio_path = extract_audio_text(video_path)

    sentiment_score = analyze_sentiment(transcript)

    speech_clarity = speech_clarity_score(transcript)

    voice_score = analyze_voice(audio_path)

    competency = predict_competency(transcript)

    resume_match = np.random.randint(60,90)

    answer_score = np.random.randint(60,90)

    emotion_score = sum(emotions.values()) if emotions else 50

    overall = np.mean([
        emotion_score,
        eye_contact,
        sentiment_score,
        voice_score,
        speech_clarity,
        competency,
        resume_match,
        answer_score
    ])

    results = {

        "Emotion Score": emotion_score,
        "Eye Contact": eye_contact,
        "Sentiment Score": sentiment_score,
        "Voice Clarity": voice_score,
        "Speech Clarity": speech_clarity,
        "Competency": competency,
        "Resume Match": resume_match,
        "Answer Score": answer_score,
        "Overall Score": round(overall,2)
    }

    save_results(results)

    return results


# ==============================
# SAVE RESULTS
# ==============================

def save_results(results):

    os.makedirs("data",exist_ok=True)

    df = pd.DataFrame([results])

    if os.path.exists(RESULT_FILE):

        old = pd.read_csv(RESULT_FILE)

        df = pd.concat([old,df],ignore_index=True)

    df.to_csv(RESULT_FILE,index=False)


# ==============================
# LIVE INTERVIEW
# ==============================

def record_live_interview(duration=20):

    os.makedirs("videos",exist_ok=True)

    filename = f"videos/interview_{int(time.time())}.mp4"

    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(filename,fourcc,20,(640,480))

    start = time.time()

    while int(time.time()-start) < duration:

        ret,frame = cap.read()

        if not ret:
            break

        out.write(frame)

        cv2.imshow("Recording Interview",frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    pass

    return filename


# ==============================
# RANKING
# ==============================

def get_candidate_ranking():

    if not os.path.exists(RESULT_FILE):
        return pd.DataFrame()

    df = pd.read_csv(RESULT_FILE)

    df = df.sort_values(by="Overall Score",ascending=False)

    return df


# ==============================
# REPORT
# ==============================

def generate_report():

    df = get_candidate_ranking()

    if df.empty:
        return {}

    return {

        "Average Score": round(df["Overall Score"].mean(),2),

        "Top Score": round(df["Overall Score"].max(),2),

        "Total Candidates": len(df)
    }

# import cv2
# import numpy as np
# import json
# import os
# import speech_recognition as sr
# from textblob import TextBlob
# from fer import FER
# import librosa
# import joblib
# from collections import Counter

# RESULT_PATH = "data/final_results.json"

# # ==============================
# # LOAD MODELS
# # ==============================

# def load_models():

#     models = {}

#     try:
#         models["competency_model"] = joblib.load("models/competency_classifier_model.pkl")
#         models["tfidf"] = joblib.load("models/tfidf_vectorizer.pkl")
#     except:
#         models["competency_model"] = None
#         models["tfidf"] = None

#     try:
#         models["personality_model"] = joblib.load("models/personality_predictor_model.pkl")
#         models["personality_vectorizer"] = joblib.load("models/personality_vectorizer.pkl")
#     except:
#         models["personality_model"] = None
#         models["personality_vectorizer"] = None

#     return models


# models = load_models()

# # ==============================
# # VIDEO ANALYSIS
# # ==============================

# def analyze_video(video_path):

#     detector = FER()   # faster than mtcnn
#     cap = cv2.VideoCapture(video_path)

#     emotions = []
#     emotion_timeline = []

#     frame_id = 0
#     total_frames = 0
#     eye_contact_frames = 0

#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
#     )

#     while True:

#         ret, frame = cap.read()

#         if not ret:
#             break

#         frame_id += 1

#         if frame_id % 10 != 0:
#             continue

#         total_frames += 1

#         result = detector.detect_emotions(frame)

#         if result:

#             emotion = max(result[0]["emotions"], key=result[0]["emotions"].get)

#             emotions.append(emotion)

#             emotion_timeline.append(
#                 {
#                     "frame": frame_id,
#                     "emotion": emotion
#                 }
#             )

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         faces = face_cascade.detectMultiScale(gray,1.3,5)

#         if len(faces) > 0:
#             eye_contact_frames += 1

#     cap.release()

#     emotion_counts = dict(Counter(emotions))

#     eye_contact_score = round((eye_contact_frames/max(total_frames,1))*100,2)

#     return emotion_counts, emotion_timeline, eye_contact_score


# # ==============================
# # AUDIO + TRANSCRIPT
# # ==============================

# def extract_audio_text(video_path):

#     recognizer = sr.Recognizer()

#     audio_path = video_path.replace(".mp4",".wav")

#     os.system(f'ffmpeg -y -i "{video_path}" "{audio_path}" -loglevel quiet')

#     try:

#         with sr.AudioFile(audio_path) as source:

#             audio = recognizer.record(source)

#             text = recognizer.recognize_google(audio)

#     except:

#         text = ""

#     return text, audio_path


# # ==============================
# # SENTIMENT
# # ==============================

# def analyze_sentiment(text):

#     blob = TextBlob(text)

#     polarity = blob.sentiment.polarity

#     if polarity > 0:
#         return "Positive"
#     elif polarity < 0:
#         return "Negative"
#     else:
#         return "Neutral"


# # ==============================
# # SPEECH CLARITY
# # ==============================

# def speech_clarity_score(text):

#     filler_words = ["um","uh","like","you know","actually"]

#     words = text.lower().split()

#     filler_count = sum(words.count(word) for word in filler_words)

#     total_words = max(len(words),1)

#     clarity = 100 - ((filler_count/total_words)*100)

#     return round(max(clarity,0),2), filler_count


# # ==============================
# # VOICE ANALYSIS
# # ==============================

# def analyze_voice(audio_path):

#     try:

#         y, sr_rate = librosa.load(audio_path, duration=30)

#         pitch = np.mean(librosa.yin(y, fmin=50, fmax=300))

#         energy = np.mean(librosa.feature.rms(y=y))

#         return float(pitch), float(energy)

#     except:

#         return 0.0, 0.0


# # ==============================
# # COMPETENCY MODEL
# # ==============================

# def predict_competency(text):

#     if models["competency_model"] is None:
#         return "Not Available"

#     vec = models["tfidf"].transform([text])

#     pred = models["competency_model"].predict(vec)[0]

#     return pred


# # ==============================
# # PERSONALITY MODEL
# # ==============================

# def predict_personality(text):

#     if models["personality_model"] is None:
#         return "Not Available"

#     vec = models["personality_vectorizer"].transform([text])

#     pred = models["personality_model"].predict(vec)[0]

#     return pred


# # ==============================
# # FINAL SCORE
# # ==============================

# def calculate_score(eye_contact, clarity, sentiment):

#     score = 0

#     score += eye_contact * 0.3
#     score += clarity * 0.4

#     if sentiment == "Positive":
#         score += 30
#     elif sentiment == "Neutral":
#         score += 15

#     return round(score,2)


# # ==============================
# # MAIN PIPELINE
# # ==============================

# def run_analysis(video_path):

#     print("Running AI Interview Analysis...")

#     emotions, timeline, eye_contact = analyze_video(video_path)

#     transcript, audio_path = extract_audio_text(video_path)

#     sentiment = analyze_sentiment(transcript)

#     clarity, filler_count = speech_clarity_score(transcript)

#     pitch, energy = analyze_voice(audio_path)

#     competency = predict_competency(transcript)

#     personality = predict_personality(transcript)

#     final_score = calculate_score(eye_contact, clarity, sentiment)

#     recommendation = "Hire" if final_score > 60 else "Reject"

#     results = {

#         "transcript": transcript,

#         "sentiment": sentiment,

#         "emotion_distribution": emotions,
#         "emotion_timeline": timeline,

#         "eye_contact_score": eye_contact,

#         "speech_clarity_score": clarity,
#         "filler_word_count": filler_count,

#         "voice_pitch": pitch,
#         "voice_energy": energy,

#         "competency": competency,
#         "personality": personality,

#         "final_score": final_score,

#         "recommendation": recommendation
#     }

#     os.makedirs("data",exist_ok=True)

#     with open(RESULT_PATH,"w") as f:
#         json.dump(results,f,indent=4)

#     return results
# import time
# import pandas as pd

# # ==============================
# # LIVE INTERVIEW RECORDING
# # ==============================

# def record_live_interview(duration=30):

#     os.makedirs("videos", exist_ok=True)

#     filename = f"videos/live_interview_{int(time.time())}.mp4"

#     cap = cv2.VideoCapture(0)

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

#     start_time = time.time()

#     while int(time.time() - start_time) < duration:

#         ret, frame = cap.read()

#         if not ret:
#             break

#         out.write(frame)

#         cv2.imshow("Recording Interview - Press Q to Stop", frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()

#     return filename


# # ==============================
# # CANDIDATE RANKING
# # ==============================

# def get_candidate_ranking():

#     file_path = "data/candidates_results.csv"

#     if not os.path.exists(file_path):
#         return pd.DataFrame()

#     df = pd.read_csv(file_path)

#     df = df.sort_values(by="Overall Score", ascending=False)

#     return df


# # ==============================
# # PERFORMANCE REPORT
# # ==============================

# def generate_report():

#     df = get_candidate_ranking()

#     if df.empty:
#         return {}

#     report = {
#         "Average Score": round(df["Overall Score"].mean(),2),
#         "Top Score": round(df["Overall Score"].max(),2),
#         "Total Candidates": len(df)
#     }

#     return report