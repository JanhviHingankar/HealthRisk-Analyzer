import streamlit as st
import pandas as pd
from datetime import datetime
from reports.report_generator import generate_pdf_report
from utils.helpers import load_html
from utils.helpers import draw_gauge_chart, draw_radar_chart, draw_symptoms_chart


def render(stroke_model):
    load_html("templates/stroke_header.html")
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
                    key="stroke_name",
                )
                patient_id = st.text_input(
                    "Patient ID / Record #",
                    value=st.session_state.gen_patient_id,
                    placeholder="Enter record number",
                    key="stroke_id",
                )
            with pat_col2:
                report_date = st.date_input(
                    "Report Date", datetime.now(), key="stroke_date"
                )
        with st.container(border=True):
            st.markdown("###  Patient Profile & Symptoms")
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
            with sub_col2:
                high_blood_pressure = st.radio(
                    "High Blood Pressure?", ["No", "Yes"], index=None, horizontal=True
                )
            st.markdown("#####  Cardiorespiratory Symptoms")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                chest_pain = st.radio(
                    "Chest Pain", ["No", "Yes"], index=None, horizontal=True
                )
                irregular_heartbeat = st.radio(
                    "Irregular Heartbeat", ["No", "Yes"], index=None, horizontal=True
                )
            with c_col2:
                shortness_of_breath = st.radio(
                    "Shortness of Breath", ["No", "Yes"], index=None, horizontal=True
                )
                persistent_cough = st.radio(
                    "Persistent Cough", ["No", "Yes"], index=None, horizontal=True
                )
            st.markdown("#####  Neurological, General & Autonomic")
            n_col1, n_col2 = st.columns(2)
            with n_col1:
                dizziness = st.radio(
                    "Dizziness", ["No", "Yes"], index=None, horizontal=True
                )
                fatigue_weakness = st.radio(
                    "Fatigue & Weakness", ["No", "Yes"], index=None, horizontal=True
                )
                cold_hands_feet = st.radio(
                    "Cold Hands/Feet", ["No", "Yes"], index=None, horizontal=True
                )
            with n_col2:
                snoring_sleep_apnea = st.radio(
                    "Sleep Apnea", ["No", "Yes"], index=None, horizontal=True
                )
                swelling_edema = st.radio(
                    "Swelling or Edema", ["No", "Yes"], index=None, horizontal=True
                )
                excessive_sweating = st.radio(
                    "Excessive Sweating", ["No", "Yes"], index=None, horizontal=True
                )
        predict_btn = st.button("Analyze Stroke Risk")
    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error(
                    " Patient Name and Patient ID are required to perform the analysis and generate the report."
                )
                st.stop()
            if None in [
                age,
                high_blood_pressure,
                dizziness,
                fatigue_weakness,
                cold_hands_feet,
                snoring_sleep_apnea,
                swelling_edema,
                excessive_sweating,
                chest_pain,
                irregular_heartbeat,
                shortness_of_breath,
                persistent_cough,
            ]:
                st.error(
                    " Please fill out all required clinical metrics before analyzing."
                )
                st.stop()
            chest_pain_value = 1 if chest_pain == "Yes" else 0
            high_bp_value = 1 if high_blood_pressure == "Yes" else 0
            breath_value = 1 if shortness_of_breath == "Yes" else 0
            dizziness_value = 1 if dizziness == "Yes" else 0
            heartbeat_value = 1 if irregular_heartbeat == "Yes" else 0
            fatigue_value = 1 if fatigue_weakness == "Yes" else 0
            snoring_value = 1 if snoring_sleep_apnea == "Yes" else 0
            cold_hands_value = 1 if cold_hands_feet == "Yes" else 0
            sweating_value = 1 if excessive_sweating == "Yes" else 0
            cough_value = 1 if persistent_cough == "Yes" else 0
            edema_value = 1 if swelling_edema == "Yes" else 0
            input_data = pd.DataFrame(
                [
                    {
                        "age": age,
                        "chest_pain": chest_pain_value,
                        "high_blood_pressure": high_bp_value,
                        "shortness_of_breath": breath_value,
                        "dizziness": dizziness_value,
                        "irregular_heartbeat": heartbeat_value,
                        "fatigue_&_weakness": fatigue_value,
                        "snoringsleep_apnea": snoring_value,
                        "cold_handsfeet": cold_hands_value,
                        "excessive_sweating": sweating_value,
                        "persistent_cough": cough_value,
                        "swelling_edema": edema_value,
                    }
                ]
            )
            stroke_features = [
                "age",
                "chest_pain",
                "high_blood_pressure",
                "shortness_of_breath",
                "dizziness",
                "irregular_heartbeat",
                "fatigue_&_weakness",
                "snoringsleep_apnea",
                "cold_handsfeet",
                "excessive_sweating",
                "persistent_cough",
                "swelling_edema",
            ]
            input_data = input_data[stroke_features]
            probability = stroke_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100
            with st.container(border=True):
                st.markdown("###  Risk Report Dashboard")
                fig_gauge = draw_gauge_chart(risk_percent, "Stroke Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)
                if risk_percent < 35:
                    st.success(
                        f"**Low Risk ({risk_percent:.2f}%)** - Normal stroke risk assessment. Standard preventative checkups advised."
                    )
                elif risk_percent < 70:
                    st.warning(
                        f"**Moderate Risk ({risk_percent:.2f}%)** - Moderate risk indicators present. Keep watch on BP levels and consult a health practitioner."
                    )
                else:
                    st.error(
                        f"**High Risk ({risk_percent:.2f}%)** - Significant clinical indicators present. Immediate medical evaluation recommended."
                    )
            with st.container(border=True):
                st.markdown("###  Symptoms Breakdown")
                cardio_symptoms = sum(
                    [chest_pain_value, heartbeat_value, breath_value, cough_value]
                )
                neuro_symptoms = sum([dizziness_value, fatigue_value, snoring_value])
                auto_symptoms = sum([cold_hands_value, sweating_value, edema_value])
                fig_bar = draw_symptoms_chart(
                    cardio_symptoms, neuro_symptoms, auto_symptoms
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption(
                    "This chart displays reported vs. absent symptoms per physiological category."
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
                        "name": "High Blood Pressure Status",
                        "value": high_blood_pressure,
                        "ref_range": "No",
                        "status": "Normal" if high_blood_pressure == "No" else "High",
                    },
                    {
                        "name": "Chest Pain Symptom",
                        "value": chest_pain,
                        "ref_range": "No",
                        "status": "Normal" if chest_pain == "No" else "High",
                    },
                    {
                        "name": "Irregular Heartbeat",
                        "value": irregular_heartbeat,
                        "ref_range": "No",
                        "status": "Normal" if irregular_heartbeat == "No" else "High",
                    },
                    {
                        "name": "Shortness of Breath",
                        "value": shortness_of_breath,
                        "ref_range": "No",
                        "status": "Normal" if shortness_of_breath == "No" else "High",
                    },
                    {
                        "name": "Persistent Cough",
                        "value": persistent_cough,
                        "ref_range": "No",
                        "status": "Normal" if persistent_cough == "No" else "High",
                    },
                    {
                        "name": "Dizziness Symptom",
                        "value": dizziness,
                        "ref_range": "No",
                        "status": "Normal" if dizziness == "No" else "High",
                    },
                    {
                        "name": "Fatigue & Weakness",
                        "value": fatigue_weakness,
                        "ref_range": "No",
                        "status": "Normal" if fatigue_weakness == "No" else "High",
                    },
                    {
                        "name": "Sleep Apnea / Snoring",
                        "value": snoring_sleep_apnea,
                        "ref_range": "No",
                        "status": "Normal" if snoring_sleep_apnea == "No" else "High",
                    },
                    {
                        "name": "Cold Hands & Feet",
                        "value": cold_hands_feet,
                        "ref_range": "No",
                        "status": "Normal" if cold_hands_feet == "No" else "High",
                    },
                    {
                        "name": "Swelling or Edema",
                        "value": swelling_edema,
                        "ref_range": "No",
                        "status": "Normal" if swelling_edema == "No" else "High",
                    },
                    {
                        "name": "Excessive Sweating",
                        "value": excessive_sweating,
                        "ref_range": "No",
                        "status": "Normal" if excessive_sweating == "No" else "High",
                    },
                ]
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d"),
                }
                prediction_info = {
                    "type": "Stroke",
                    "risk_percent": risk_percent,
                    "risk_level": (
                        "High Risk"
                        if risk_percent >= 70
                        else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
                    ),
                }
                inputs = {
                    "age": age,
                    "high_blood_pressure": high_bp_value,
                    "chest_pain": chest_pain_value,
                    "irregular_heartbeat": heartbeat_value,
                    "shortness_of_breath": breath_value,
                    "persistent_cough": cough_value,
                    "dizziness": dizziness_value,
                    "fatigue_&_weakness": fatigue_value,
                    "snoringsleep_apnea": snoring_value,
                    "cold_handsfeet": cold_hands_value,
                    "swelling_edema": edema_value,
                    "excessive_sweating": sweating_value,
                }
                pdf_data = generate_pdf_report(
                    patient_info, prediction_info, inputs, metrics_list
                )
                st.download_button(
                    label=" Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Stroke_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="stroke_download",
                )
        else:
            with st.container(border=True):
                load_html("templates/stroke_awaiting.html")
