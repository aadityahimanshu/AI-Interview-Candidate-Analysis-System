import streamlit as st
import json
import os
import tempfile
import matplotlib.pyplot as plt

from main import run_analysis,record_live_interview,get_candidate_ranking,generate_report


USER_DB="users.json"


if not os.path.exists(USER_DB):

    with open(USER_DB,"w") as f:
        json.dump({},f)


if "logged_in" not in st.session_state:
    st.session_state.logged_in=False


def load_users():

    with open(USER_DB,"r") as f:
        return json.load(f)


def save_users(users):

    with open(USER_DB,"w") as f:
        json.dump(users,f)


def signup(username,password):

    users=load_users()

    if username in users:
        return False

    users[username]=password

    save_users(users)

    return True


def login(username,password):

    users=load_users()

    if username in users and users[username]==password:
        return True

    return False


st.title("AI Interview Candidate Analysis System")


# =========================
# LOGIN SYSTEM
# =========================

if not st.session_state.logged_in:

    menu=["Login","Signup"]

    choice=st.sidebar.selectbox("Menu",menu)

    username=st.text_input("Username")

    password=st.text_input("Password",type="password")

    if choice=="Signup":

        if st.button("Signup"):

            if signup(username,password):

                st.success("Account created")

            else:

                st.error("User already exists")


    if choice=="Login":

        if st.button("Login"):

            if login(username,password):

                st.session_state.logged_in=True

                st.rerun()

            else:

                st.error("Invalid credentials")


# =========================
# DASHBOARD
# =========================

else:

    st.sidebar.success("Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    page = st.sidebar.selectbox("Dashboard",[
        "Upload Interview Video",
        "Live Interview",
        "AI Interview",
        "Candidate Ranking",
        "Performance Report"
    ])

    # ======================
    # Upload Interview
    # ======================

    if page == "Upload Interview Video":

        video = st.file_uploader("Upload Interview Video", type=["mp4","avi","mov"])

        if video:

            st.video(video)

            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(video.read())
                video_path = tmp.name

            if st.button("Run AI Analysis"):

                results = run_analysis(video_path)

                st.json(results)


    # ======================
    # Live Interview
    # ======================

    elif page == "Live Interview":

        if st.button("Start Recording"):

            video_path = record_live_interview()

            results = run_analysis(video_path)

            st.json(results)


    # ======================
    # AI Interview
    # ======================

    elif page == "AI Interview":

        from ai_interviewer import generate_question, evaluate_answer

        st.header("AI Interview Mode")

        if "question" not in st.session_state:
            st.session_state.question = generate_question()

        st.write(st.session_state.question)

        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):

            score = evaluate_answer(answer)

            st.success(f"Answer Score: {score}/100")

            st.session_state.question = generate_question()


    # ======================
    # Candidate Ranking
    # ======================

    elif page == "Candidate Ranking":

        df = get_candidate_ranking()

        if df.empty:
            st.warning("No candidates yet")
        else:
            st.dataframe(df)


    # ======================
    # Performance Report
    # ======================

    elif page == "Performance Report":

        report = generate_report()

        if report == {}:
            st.warning("No data")
        else:

            c1,c2,c3 = st.columns(3)

            c1.metric("Average Score", report["Average Score"])
            c2.metric("Top Score", report["Top Score"])
            c3.metric("Total Candidates", report["Total Candidates"])
# import streamlit as st
# import json
# import os
# import tempfile
# import pandas as pd
# import matplotlib.pyplot as plt

# from main import (
#     run_analysis,
#     record_live_interview,
#     get_candidate_ranking,
#     generate_report
# )

# # -----------------------------
# # User Database
# # -----------------------------
# USER_DB = "users.json"

# if not os.path.exists(USER_DB):
#     with open(USER_DB, "w") as f:
#         json.dump({}, f)


# def load_users():
#     with open(USER_DB, "r") as f:
#         return json.load(f)


# def save_users(users):
#     with open(USER_DB, "w") as f:
#         json.dump(users, f)


# # -----------------------------
# # Authentication
# # -----------------------------
# def signup(username, password):

#     users = load_users()

#     if username in users:
#         return False

#     users[username] = password
#     save_users(users)

#     return True


# def login(username, password):

#     users = load_users()

#     if username in users and users[username] == password:
#         return True

#     return False


# # -----------------------------
# # Streamlit UI
# # -----------------------------
# st.title("🎥 AI Interview Candidate Analysis System")

# menu = ["Login", "Signup"]

# choice = st.sidebar.selectbox("Menu", menu)

# # -----------------------------
# # Signup
# # -----------------------------
# if choice == "Signup":

#     st.subheader("Create Account")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Signup"):

#         if signup(username, password):
#             st.success("Account created. Please login.")

#         else:
#             st.error("User already exists")


# # -----------------------------
# # Login
# # -----------------------------
# if choice == "Login":

#     st.subheader("Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):

#         if login(username, password):

#             st.success("Login Successful")

#             dashboard = st.sidebar.selectbox(
#                 "Dashboard",
#                 [
#                     "Upload Interview Video",
#                     "Live Interview",
#                     "Candidate Ranking",
#                     "Performance Report"
#                 ]
#             )

#             # -----------------------------
#             # Upload Interview Video
#             # -----------------------------
#             if dashboard == "Upload Interview Video":

#                 st.subheader("Upload Interview Video")

#                 video = st.file_uploader(
#                     "Upload Video",
#                     type=["mp4", "mov", "avi"]
#                 )

#                 if video:

#                     with tempfile.NamedTemporaryFile(delete=False) as tmp:
#                         tmp.write(video.read())
#                         video_path = tmp.name

#                     st.video(video)

#                     if st.button("Run AI Analysis"):

#                         with st.spinner("Analyzing Interview..."):

#                             results = run_analysis(video_path)

#                         st.success("Analysis Complete")

#                         st.json(results)

#                         # Chart
#                         labels = [
#                             "Emotion",
#                             "Eye Contact",
#                             "Sentiment",
#                             "Voice",
#                             "Speech",
#                             "Competency",
#                             "Resume",
#                             "Answer"
#                         ]

#                         values = [
#                             results["Emotion Score"],
#                             results["Eye Contact"],
#                             results["Sentiment Score"],
#                             results["Voice Clarity"],
#                             results["Speech Clarity"],
#                             results["Competency"],
#                             results["Resume Match"],
#                             results["Answer Score"]
#                         ]

#                         fig, ax = plt.subplots()
#                         ax.bar(labels, values)
#                         plt.xticks(rotation=45)

#                         st.pyplot(fig)

#             # -----------------------------
#             # Live Interview
#             # -----------------------------
#             if dashboard == "Live Interview":

#                 st.subheader("Start Live Interview")

#                 if st.button("Start Recording"):

#                     with st.spinner("Recording Interview..."):

#                         video_path = record_live_interview()

#                     st.success("Recording Complete")

#                     results = run_analysis(video_path)

#                     st.json(results)

#             # -----------------------------
#             # Candidate Ranking
#             # -----------------------------
#             if dashboard == "Candidate Ranking":

#                 st.subheader("Candidate Ranking Dashboard")

#                 df = get_candidate_ranking()

#                 if df.empty:
#                     st.warning("No candidates analyzed yet")

#                 else:
#                     st.dataframe(df)

#             # -----------------------------
#             # Performance Report
#             # -----------------------------
#             if dashboard == "Performance Report":

#                 st.subheader("Recruiter Performance Report")

#                 report = generate_report()

#                 if report == {}:
#                     st.warning("No data available")

#                 else:

#                     st.metric("Average Score", report["Average Score"])
#                     st.metric("Top Score", report["Top Score"])
#                     st.metric("Total Candidates", report["Total Candidates"])

#         else:
#             st.error("Invalid Credentials")