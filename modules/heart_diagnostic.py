import streamlit as st
import pandas as pd
from datetime import datetime
from reports.report_generator import generate_pdf_report
from utils.helpers import load_html
from utils.helpers import draw_gauge_chart, draw_radar_chart, draw_symptoms_chart


def render(heart_model, heart_features):
    load_html("templates/heart_header.html")
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
                    key="heart_name",
                )
                patient_id = st.text_input(
                    "Patient ID / Record #",
                    value=st.session_state.gen_patient_id,
                    placeholder="Enter record number",
                    key="heart_id",
                )
            with pat_col2:
                report_date = st.date_input(
                    "Report Date", datetime.now(), key="heart_date"
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
                cholesterol = st.number_input(
                    "Total Cholesterol (mg/dL)",
                    min_value=0.0,
                    max_value=600.0,
                    value=None,
                    step=1.0,
                    placeholder="Enter value",
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
                previous_heart_attack = st.radio(
                    "Previous Heart Attack?", ["No", "Yes"], index=None, horizontal=True
                )
            st.markdown("##### Measurements & Background")
            sub_col3, sub_col4 = st.columns(2)
            with sub_col3:
                systolic_bp = st.number_input(
                    "Systolic BP (mmHg)",
                    min_value=0.0,
                    max_value=300.0,
                    value=None,
                    step=1.0,
                    placeholder="Enter value",
                )
                diabetes = st.radio(
                    "Diabetes?", ["No", "Yes"], index=None, horizontal=True
                )
            with sub_col4:
                fasting_sugar = st.number_input(
                    "Fasting Blood Sugar (mg/dL)",
                    min_value=0.0,
                    max_value=500.0,
                    value=None,
                    step=1.0,
                    placeholder="Enter value",
                )
                hypertension = st.radio(
                    "Hypertension?", ["No", "Yes"], index=None, horizontal=True
                )
        predict_btn = st.button("Analyze Heart Risk")
    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error(
                    " Patient Name and Patient ID are required to perform the analysis and generate the report."
                )
                st.stop()
            if None in [
                age,
                cholesterol,
                bmi,
                previous_heart_attack,
                systolic_bp,
                diabetes,
                fasting_sugar,
                hypertension,
            ]:
                st.error(
                    " Please fill out all required clinical metrics before analyzing."
                )
                st.stop()
            hypertension_value = 1 if hypertension == "Yes" else 0
            diabetes_value = 1 if diabetes == "Yes" else 0
            previous_heart_attack_value = 1 if previous_heart_attack == "Yes" else 0
            input_data = pd.DataFrame(
                [
                    {
                        "Age": age,
                        "Cholesterol_Total": cholesterol,
                        "Hypertension": hypertension_value,
                        "Diabetes": diabetes_value,
                        "Previous_Heart_Attack": previous_heart_attack_value,
                        "BMI": bmi,
                        "Blood_Sugar_Fasting": fasting_sugar,
                        "Systolic_BP": systolic_bp,
                    }
                ]
            )
            input_data = input_data[heart_features]
            probability = heart_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100
            with st.container(border=True):
                st.markdown("###  Risk Report Dashboard")
                fig_gauge = draw_gauge_chart(risk_percent, "Cardiac Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)
                if risk_percent < 35:
                    st.success(
                        f"**Low Risk ({risk_percent:.2f}%)** - Normal cardiovascular risk. Maintenance of current healthy lifestyle habits suggested."
                    )
                elif risk_percent < 70:
                    st.warning(
                        f"**Moderate Risk ({risk_percent:.2f}%)** - Mild anomalies detected. Advise routine clinical observation and BP monitoring."
                    )
                else:
                    st.error(
                        f"**High Risk ({risk_percent:.2f}%)** - Elevated parameters indicators present. Prompt consultation with a cardiologist is recommended."
                    )
            with st.container(border=True):
                st.markdown("###  Cardiovascular Profile")
                user_bmi_norm = min(100.0, (bmi / 24.9) * 50)
                user_chol_norm = min(100.0, (cholesterol / 200.0) * 50)
                user_bp_norm = min(100.0, (systolic_bp / 120.0) * 50)
                user_sugar_norm = min(100.0, (fasting_sugar / 100.0) * 50)
                fig_radar = draw_radar_chart(
                    ["BMI", "Cholesterol", "Systolic BP", "Fasting Sugar"],
                    [user_bmi_norm, user_chol_norm, user_bp_norm, user_sugar_norm],
                    [50, 50, 50, 50],
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption(
                    "Note: Radar values are normalized. Values exceeding the green boundary (50%) are in the clinical alert range."
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
                        "name": "Total Cholesterol",
                        "value": f"{cholesterol:.1f} mg/dL",
                        "ref_range": "< 200 mg/dL",
                        "status": (
                            "Normal"
                            if cholesterol < 200
                            else ("Elevated" if cholesterol < 240 else "High")
                        ),
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
                        "name": "Systolic Blood Pressure",
                        "value": f"{systolic_bp:.1f} mmHg",
                        "ref_range": "< 120 mmHg",
                        "status": (
                            "Normal"
                            if systolic_bp < 120
                            else ("Elevated" if systolic_bp < 140 else "High")
                        ),
                    },
                    {
                        "name": "Fasting Blood Sugar",
                        "value": f"{fasting_sugar:.1f} mg/dL",
                        "ref_range": "< 100 mg/dL",
                        "status": (
                            "Normal"
                            if fasting_sugar < 100
                            else ("Elevated" if fasting_sugar < 126 else "High")
                        ),
                    },
                    {
                        "name": "Previous Heart Attack",
                        "value": previous_heart_attack,
                        "ref_range": "No",
                        "status": "Normal" if previous_heart_attack == "No" else "High",
                    },
                    {
                        "name": "Diabetes History",
                        "value": diabetes,
                        "ref_range": "No",
                        "status": "Normal" if diabetes == "No" else "High",
                    },
                    {
                        "name": "Hypertension History",
                        "value": hypertension,
                        "ref_range": "No",
                        "status": "Normal" if hypertension == "No" else "High",
                    },
                ]
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d"),
                }
                prediction_info = {
                    "type": "Heart Disease",
                    "risk_percent": risk_percent,
                    "risk_level": (
                        "High Risk"
                        if risk_percent >= 70
                        else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
                    ),
                }
                inputs = {
                    "Age": age,
                    "cholesterol": cholesterol,
                    "bmi": bmi,
                    "systolic_bp": systolic_bp,
                    "fasting_sugar": fasting_sugar,
                    "previous_heart_attack": previous_heart_attack_value,
                    "diabetes": diabetes_value,
                    "hypertension": hypertension_value,
                }
                pdf_data = generate_pdf_report(
                    patient_info, prediction_info, inputs, metrics_list
                )
                st.download_button(
                    label=" Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Heart_Disease_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="heart_download",
                )
        else:
            with st.container(border=True):
                load_html("templates/heart_awaiting.html")
