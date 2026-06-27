import streamlit as st
import pickle
import uuid
from utils.helpers import load_css, load_html
from modules import diabetes_diagnostic, heart_diagnostic, stroke_diagnostic

st.set_page_config(
    page_title="Health Risk Predictor",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css("templates/style.css")

if "gen_patient_id" not in st.session_state:
    st.session_state.gen_patient_id = f"PID-{uuid.uuid4().hex[:6].upper()}"

diabetes_model = pickle.load(open("models/diabetes_pipeline.pkl", "rb"))
heart_model = pickle.load(open("models/heart_model.pkl", "rb"))
stroke_model = pickle.load(open("models/stroke_pipeline.pkl", "rb"))
heart_features = pickle.load(open("models/features.pkl", "rb"))

with st.sidebar:
    load_html("templates/sidebar.html")
    selected = st.radio(
        "Select Risk Calculator",
        ["Diabetes Prediction", "Heart Disease Prediction", "Stroke Prediction"],
    )

if selected == "Diabetes Prediction":
    diabetes_diagnostic.render(diabetes_model)
elif selected == "Heart Disease Prediction":
    heart_diagnostic.render(heart_model, heart_features)
elif selected == "Stroke Prediction":
    stroke_diagnostic.render(stroke_model)

