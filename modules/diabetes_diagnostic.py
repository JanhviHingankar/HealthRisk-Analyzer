import streamlit as st
import pandas as pd
from datetime import datetime
from reports.report_generator import generate_pdf_report
from utils.helpers import load_html
from utils.helpers import draw_gauge_chart, draw_radar_chart, draw_symptoms_chart


def render(diabetes_model):
    load_html("templates/diabetes_header.html")
    col_input, col_result = st.columns([1.1, 1], gap="large")
    with col_input:
        with st.container(border=True):
            st.markdown("###  Patient Identification")
            pat_col1, pat_col2 = st.columns(2)
            with pat_col1:
                patient_name = st.text_input(
                    "Patient Name",
                    value="",
                    placeholder="Enter patient name",
                    key="diabetes_name",
                )
                patient_id = st.text_input(
                    "Patient ID / Record #",
                    value=st.session_state.gen_patient_id,
                    placeholder="Enter record number",
                    key="diabetes_id",
                )
            with pat_col2:
                report_date = st.date_input(
                    "Report Date", datetime.now(), key="diabetes_date"
                )
        with st.container(border=True):
            st.markdown("###  Patient Clinical Metrics")
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                age = st.number_input(
                    "Age",
                    min_value=0,
                    max_value=120,
                    value=None,
                    step=1,
                    format="%d",
                    placeholder="Enter value",
                )
                gender = st.selectbox(
                    "Gender",
                    ["Female", "Male"],
                    index=None,
                    placeholder="Select option",
                )
            with sub_col2:
                bmi = st.number_input(
                    "BMI (kg/m²)",
                    min_value=0.0,
                    max_value=80.0,
                    value=None,
                    step=0.1,
                    placeholder="Enter value",
                )
                smoking = st.selectbox(
                    "Smoking History",
                    ["Never", "Current", "Former", "Ever", "Not Current", "No Info"],
                    index=None,
                    placeholder="Select option",
                )
            st.markdown("##### Measurements & Background")
            sub_col3, sub_col4 = st.columns(2)
            with sub_col3:
                glucose = st.number_input(
                    "Blood Glucose Level (mg/dL)",
                    min_value=0.0,
                    max_value=500.0,
                    value=None,
                    step=1.0,
                    placeholder="Enter value",
                )
                hypertension = st.radio(
                    "Hypertension History?", ["No", "Yes"], index=None, horizontal=True
                )
            with sub_col4:
                hba1c = st.number_input(
                    "HbA1c Level (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=None,
                    step=0.1,
                    placeholder="Enter value",
                )
                heart_disease = st.radio(
                    "Heart Disease History?", ["No", "Yes"], index=None, horizontal=True
                )
        predict_btn = st.button("Analyze Diabetes Risk")
    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error(
                    " Patient Name and Patient ID are required to perform the analysis and generate the report."
                )
                st.stop()
            if None in [
                age,
                gender,
                bmi,
                smoking,
                glucose,
                hypertension,
                hba1c,
                heart_disease,
            ]:
                st.error(
                    " Please fill out all required clinical metrics before analyzing."
                )
                st.stop()
            hypertension_value = 1 if hypertension == "Yes" else 0
            heart_disease_value = 1 if heart_disease == "Yes" else 0
            smoking_map = {
                "Never": "never",
                "Current": "current",
                "Former": "former",
                "Ever": "ever",
                "Not Current": "not current",
                "No Info": "No Info",
            }
            smoking_value = smoking_map.get(smoking, "never")
            input_data = pd.DataFrame(
                [
                    {
                        "gender": gender,
                        "age": age,
                        "hypertension": hypertension_value,
                        "heart_disease": heart_disease_value,
                        "smoking_history": smoking_value,
                        "bmi": bmi,
                        "HbA1c_level": hba1c,
                        "blood_glucose_level": glucose,
                    }
                ]
            )
            diabetes_features = [
                "gender",
                "age",
                "hypertension",
                "heart_disease",
                "smoking_history",
                "bmi",
                "HbA1c_level",
                "blood_glucose_level",
            ]
            input_data = input_data[diabetes_features]
            probability = diabetes_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100
            with st.container(border=True):
                st.markdown("###  Risk Report Dashboard")
                fig_gauge = draw_gauge_chart(risk_percent, "Diabetes Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)
                if risk_percent < 35:
                    st.success(
                        f"**Low Risk ({risk_percent:.2f}%)** - Patient shows normal clinical levels. Encourage maintaining active lifestyle and balanced diet."
                    )
                elif risk_percent < 70:
                    st.warning(
                        f"**Moderate Risk ({risk_percent:.2f}%)** - Patient shows elevated risk parameters. Recommend monitoring diet and scheduling a routine check-up."
                    )
                else:
                    st.error(
                        f"**High Risk ({risk_percent:.2f}%)** - Patient exhibits clinical indicators strongly associated with diabetes. Clinical follow-up is recommended."
                    )
            with st.container(border=True):
                st.markdown("###  Health Profile Analysis")
                user_bmi_norm = min(100.0, (bmi / 24.9) * 50)
                user_hba1c_norm = min(100.0, (hba1c / 5.7) * 50)
                user_glucose_norm = min(100.0, (glucose / 100.0) * 50)
                fig_radar = draw_radar_chart(
                    ["BMI", "HbA1c", "Blood Glucose"],
                    [user_bmi_norm, user_hba1c_norm, user_glucose_norm],
                    [50, 50, 50],
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption(
                    "Note: Radar values are normalized. Values above the green dotted line (50%) exceed normal clinical thresholds."
                )
            with st.container(border=True):
                st.markdown("###  Patient Clinical Report")
                metrics_list = [
                    {
                        "name": "Age",
                        "value": f"{age} years",
                        "ref_range": "N/A",
                        "status": "Normal",
                    },
                    {
                        "name": "Gender",
                        "value": gender,
                        "ref_range": "N/A",
                        "status": "Normal",
                    },
                    {
                        "name": "BMI",
                        "value": f"{bmi:.1f} kg/m²",
                        "ref_range": "18.5 - 24.9",
                        "status": (
                            "Normal"
                            if bmi < 25.0
                            else ("Elevated" if bmi < 30.0 else "High")
                        ),
                    },
                    {
                        "name": "Blood Glucose Level",
                        "value": f"{glucose:.1f} mg/dL",
                        "ref_range": "< 100 mg/dL",
                        "status": (
                            "Normal"
                            if glucose < 100
                            else ("Elevated" if glucose < 126 else "High")
                        ),
                    },
                    {
                        "name": "HbA1c Level",
                        "value": f"{hba1c:.1f}%",
                        "ref_range": "< 5.7%",
                        "status": (
                            "Normal"
                            if hba1c < 5.7
                            else ("Elevated" if hba1c < 6.5 else "High")
                        ),
                    },
                    {
                        "name": "Hypertension History",
                        "value": hypertension,
                        "ref_range": "No",
                        "status": "Normal" if hypertension == "No" else "High",
                    },
                    {
                        "name": "Heart Disease History",
                        "value": heart_disease,
                        "ref_range": "No",
                        "status": "Normal" if heart_disease == "No" else "High",
                    },
                    {
                        "name": "Smoking History",
                        "value": smoking,
                        "ref_range": "Never / No Info",
                        "status": (
                            "Normal" if smoking in ["Never", "No Info"] else "Elevated"
                        ),
                    },
                ]
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d"),
                }
                prediction_info = {
                    "type": "Diabetes",
                    "risk_percent": risk_percent,
                    "risk_level": (
                        "High Risk"
                        if risk_percent >= 70
                        else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
                    ),
                }
                inputs = {
                    "bmi": bmi,
                    "glucose": glucose,
                    "hba1c": hba1c,
                    "hypertension": hypertension_value,
                    "heart_disease": heart_disease_value,
                    "smoking_history": smoking_value,
                }
                pdf_data = generate_pdf_report(
                    patient_info, prediction_info, inputs, metrics_list
                )
                st.download_button(
                    label=" Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Diabetes_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="diabetes_download",
                )
        else:
            with st.container(border=True):
                load_html("templates/diabetes_awaiting.html")
