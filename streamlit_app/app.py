import streamlit as st
import requests
from datetime import date

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Study Recommendation System", layout="wide")

st.title("Study Recommendation System")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Create Student", "Add Study Log", "View Logs", "Get Recommendation"]
)

# ---------- Create Student ----------

with tab1:
    st.subheader("Register Student")

    name = st.text_input("Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["student", "admin"])

    if st.button("Create Student"):
        payload = {
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "role": role,
        }
        try:
            res = requests.post(f"{BACKEND_URL}/students", json=payload)
            if res.status_code == 200:
                st.success(
                    f"Student created with ID: {res.json().get('student_id')}"
                )
                st.json(res.json())
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------- Add Study Log ----------

with tab2:
    st.subheader("Add Study Log")

    student_id = st.number_input("Student ID", min_value=1, step=1)
    log_date = st.date_input("Date", value=date.today())
    day_name = log_date.strftime("%A")

    study_hour = st.number_input(
        "Study hours (numeric)", min_value=0.0, step=0.5
    )
    subject = st.text_input("Subject")
    method_used = st.text_input("Method used (e.g., flashcards, video, notes)")
    distraction_time = st.number_input(
        "Distraction time (e.g., minutes)", min_value=0.0, step=5.0
    )
    quiz_score = st.number_input(
        "Quiz score", min_value=0.0, max_value=100.0, step=1.0
    )

    if st.button("Submit Log"):
        payload = {
            "student_id": int(student_id),
            "date": str(log_date),
            "study_hour": float(study_hour),
            "subject": subject,
            "method_used": method_used,
            "distraction_time": float(distraction_time),
            "quiz_score": float(quiz_score),
            "day_name": day_name,
        }

        try:
            res = requests.post(f"{BACKEND_URL}/study-logs", json=payload)
            if res.status_code == 200:
                st.success("Study log added!")
                st.json(res.json())
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------- View Logs ----------

with tab3:
    st.subheader("View Logs for a Student")
    view_student_id = st.number_input(
        "Student ID (view logs)", min_value=1, step=1, key="view_logs"
    )

    if st.button("Fetch Logs"):
        try:
            res = requests.get(
                f"{BACKEND_URL}/study-logs/{int(view_student_id)}"
            )
            if res.status_code == 200:
                data = res.json()
                if not data:
                    st.info("No logs found for this student.")
                else:
                    st.success(f"Found {len(data)} logs.")
                    st.json(data)
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------- Get Recommendation ----------

with tab4:
    st.subheader("Get Recommendation for a Student")

    reco_student_id = st.number_input(
        "Student ID (recommendation)", min_value=1, step=1, key="reco_student"
    )

    if st.button("Get Recommendation"):
        try:
            res = requests.get(
                f"{BACKEND_URL}/students/{int(reco_student_id)}/recommendation"
            )
            if res.status_code == 200:
                data = res.json()
                st.write(f"Cluster ID: {data['cluster_id']}")
                st.write(f"Cluster Profile: {data['cluster_profile']}")
                st.write("Recommendations:")
                for r in data["recommendations"]:
                    st.markdown(f"- {r}")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
