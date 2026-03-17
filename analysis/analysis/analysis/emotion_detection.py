from deepface import DeepFace
import cv2


def detect_emotion_timeline(video_path):

    cap = cv2.VideoCapture(video_path)

    timeline = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = result[0]["dominant_emotion"]
            timeline.append(emotion)
        except:
            pass

    cap.release()

    return timeline