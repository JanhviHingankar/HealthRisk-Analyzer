import streamlit as st
import pickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import uuid
from report_generator import generate_pdf_report

# PAGE SETTINGS
st.set_page_config(
    page_title="AI Multi-Disease Risk Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS FOR SLICK DESIGN
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global resets and font styling */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #0A0E1A !important;
    color: #E2E8F0 !important;
}

/* Sidebar design */
section[data-testid="stSidebar"] {
    background-color: #050811 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-title {
    text-align: center;
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 30px;
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* Main Container spacing */
.main .block-container {
    max-width: 95%;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Custom card container styling targeting native Streamlit containers with borders */
div[data-testid="stVerticalBlockBorder"] {
    background: rgba(17, 24, 39, 0.7) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
}

/* Remove default background and border from columns to prevent duplicate/empty cards */
[data-testid="column"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Style headers inside glass cards */
div[data-testid="stVerticalBlockBorder"] h3 {
    margin-top: 0 !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding-bottom: 12px !important;
    margin-bottom: 20px !important;
}

div[data-testid="stVerticalBlockBorder"] h5 {
    color: #818CF8 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    margin-top: 20px !important;
    margin-bottom: 10px !important;
    border-bottom: none !important;
    padding-bottom: 0 !important;
}

/* Input Fields overrides */
div[data-baseweb="input"], div[data-baseweb="select"] {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Radio button text */
.stRadio label {
    font-size: 14px !important;
    color: #94A3B8 !important;
}

/* Interactive elements headers */
p {
    font-size: 15px !important;
    font-weight: 500;
    color: #E2E8F0;
    margin-bottom: 6px !important;
}

/* Buttons style */
.stButton button {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    width: 100%;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    background: linear-gradient(135deg, #5A52E6 0%, #8B4CFA 100%) !important;
}

.stButton button:active {
    transform: translateY(0) !important;
}

/* Custom styled Alert alerts */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background-color: rgba(30, 41, 59, 0.4) !important;
}

</style>
""", unsafe_allow_html=True)

if 'gen_patient_id' not in st.session_state:
    st.session_state.gen_patient_id = f"PID-{uuid.uuid4().hex[:6].upper()}"

# LOAD MODELS
diabetes_model = pickle.load(open("diabetes_pipeline.pkl", "rb"))
heart_model = pickle.load(open("heart_model.pkl", "rb"))
stroke_model = pickle.load(open("stroke_pipeline.pkl", "rb"))
heart_features = pickle.load(open("features.pkl", "rb"))

# CHART HELPER FUNCTIONS
def draw_gauge_chart(risk_percent, title_text):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_percent,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title_text, 'font': {'size': 18, 'color': "#94A3B8", 'family': "Outfit"}},
        number={'suffix': "%", 'font': {'size': 38, 'color': "#F8FAFC", 'family': "Outfit"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#6366F1"},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
            'steps': [
                {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.15)'},
                {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.15)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ],
            'threshold': {
                'line': {'color': "#818CF8", 'width': 3},
                'thickness': 0.75,
                'value': risk_percent
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#F8FAFC", 'family': "Outfit"},
        height=220,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def draw_radar_chart(categories, user_vals, target_vals):
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=user_vals + [user_vals[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Patient Metrics',
        fillcolor='rgba(99, 102, 241, 0.25)',
        line=dict(color='#6366F1', width=2)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=target_vals + [target_vals[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Healthy Limit',
        fillcolor='rgba(16, 185, 129, 0.05)',
        line=dict(color='#10B981', width=2, dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                ticks='',
                gridcolor="rgba(255, 255, 255, 0.08)"
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                linecolor="rgba(255, 255, 255, 0.08)",
                tickfont=dict(size=11, color="#94A3B8")
            ),
            bgcolor='rgba(15, 23, 42, 0.4)'
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=30, b=30),
        height=240,
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0.5,
            xanchor="center",
            font=dict(color="#94A3B8", size=10)
        )
    )
    return fig

def draw_symptoms_chart(cardio, neuro, auto):
    categories = ['Cardiorespiratory', 'Neurological', 'Autonomic']
    active = [cardio, neuro, auto]
    total = [4, 3, 3]
    
    fig = go.Figure(data=[
        go.Bar(name='Reported Symptoms', x=categories, y=active, marker_color='#818CF8', opacity=0.9, width=0.4),
        go.Bar(name='Absent Symptoms', x=categories, y=[t-a for t, a in zip(total, active)], marker_color='rgba(255, 255, 255, 0.05)', opacity=0.5, width=0.4)
    ])
    
    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94A3B8", family="Outfit"),
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", font=dict(size=10)),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(size=10),
            dtick=1,
            range=[0, 4]
        ),
        xaxis=dict(
            tickfont=dict(size=11)
        )
    )
    return fig

# SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-title">
            🩺 AI Diagnostics
        </div>
        """,
        unsafe_allow_html=True
    )

    selected = st.radio(
        "Select Risk Calculator",
        [
            "Diabetes Prediction",
            "Heart Disease Prediction",
            "Stroke Prediction"
        ]
    )

# DIABETES PAGE
def diabetes_page():
    # Page Header Banner
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%); padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 25px; display: flex; align-items: center; gap: 20px;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px;">
                <span style="font-size: 32px;">🩺</span>
            </div>
            <div>
                <h2 style="color: #F8FAFC; margin: 0; font-size: 24px; font-weight: 800;">Diabetes Risk Assessment</h2>
                <p style="color: #94A3B8; margin: 5px 0 0 0; font-size: 14px;">Evaluates demographic profile, glucose, HbA1c levels, and cardiovascular history.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_input, col_result = st.columns([1.1, 1], gap="large")

    with col_input:
        with st.container(border=True):
            st.markdown("### 👤 Patient Identification")
            pat_col1, pat_col2 = st.columns(2)
            with pat_col1:
                patient_name = st.text_input("Patient Name", value="", placeholder="Enter patient name", key="diabetes_name")
                patient_id = st.text_input("Patient ID / Record #", value=st.session_state.gen_patient_id, placeholder="Enter record number", key="diabetes_id")
            with pat_col2:
                report_date = st.date_input("Report Date", datetime.now(), key="diabetes_date")

        with st.container(border=True):
            st.markdown("### 📋 Patient Clinical Metrics")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                age = st.number_input("Age", min_value=0, max_value=120, value=None, step=1, format="%d", placeholder="Enter value")
                gender = st.selectbox("Gender", ["Female", "Male"], index=None, placeholder="Select option")
            with sub_col2:
                bmi = st.number_input("BMI (kg/m²)", min_value=0.0, max_value=80.0, value=None, step=0.1, placeholder="Enter value")
                smoking = st.selectbox("Smoking History", ["Never", "Current", "Former", "Ever", "Not Current", "No Info"], index=None, placeholder="Select option")
                
            st.markdown("##### Measurements & Background")
            
            sub_col3, sub_col4 = st.columns(2)
            with sub_col3:
                glucose = st.number_input("Blood Glucose Level (mg/dL)", min_value=0.0, max_value=500.0, value=None, step=1.0, placeholder="Enter value")
                hypertension = st.radio("Hypertension History?", ["No", "Yes"], index=None, horizontal=True)
            with sub_col4:
                hba1c = st.number_input("HbA1c Level (%)", min_value=0.0, max_value=20.0, value=None, step=0.1, placeholder="Enter value")
                heart_disease = st.radio("Heart Disease History?", ["No", "Yes"], index=None, horizontal=True)
            
        predict_btn = st.button("Analyze Diabetes Risk")

    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error("⚠️ Patient Name and Patient ID are required to perform the analysis and generate the report.")
                st.stop()
            if None in [age, gender, bmi, smoking, glucose, hypertension, hba1c, heart_disease]:
                st.error("⚠️ Please fill out all required clinical metrics before analyzing.")
                st.stop()

            hypertension_value = 1 if hypertension == "Yes" else 0

            heart_disease_value = 1 if heart_disease == "Yes" else 0
            
            smoking_map = {
                "Never": "never",
                "Current": "current",
                "Former": "former",
                "Ever": "ever",
                "Not Current": "not current",
                "No Info": "No Info"
            }
            smoking_value = smoking_map.get(smoking, "never")

            input_data = pd.DataFrame([{
                'gender': gender,
                'age': age,
                'hypertension': hypertension_value,
                'heart_disease': heart_disease_value,
                'smoking_history': smoking_value,
                'bmi': bmi,
                'HbA1c_level': hba1c,
                'blood_glucose_level': glucose
            }])

            diabetes_features = [
                'gender', 'age', 'hypertension', 'heart_disease', 'smoking_history',
                'bmi', 'HbA1c_level', 'blood_glucose_level'
            ]
            input_data = input_data[diabetes_features]

            probability = diabetes_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100

            with st.container(border=True):
                st.markdown("### 📊 Risk Report Dashboard")
                
                # Gauge chart
                fig_gauge = draw_gauge_chart(risk_percent, "Diabetes Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)

                # Advice alerts
                if risk_percent < 35:
                    st.success(f"**Low Risk ({risk_percent:.2f}%)** - Patient shows normal clinical levels. Encourage maintaining active lifestyle and balanced diet.")
                elif risk_percent < 70:
                    st.warning(f"**Moderate Risk ({risk_percent:.2f}%)** - Patient shows elevated risk parameters. Recommend monitoring diet and scheduling a routine check-up.")
                else:
                    st.error(f"**High Risk ({risk_percent:.2f}%)** - Patient exhibits clinical indicators strongly associated with diabetes. Clinical follow-up is recommended.")

            with st.container(border=True):
                st.markdown("### 📈 Health Profile Analysis")
                
                user_bmi_norm = min(100.0, (bmi / 24.9) * 50)
                user_hba1c_norm = min(100.0, (hba1c / 5.7) * 50)
                user_glucose_norm = min(100.0, (glucose / 100.0) * 50)
                
                fig_radar = draw_radar_chart(
                    ["BMI", "HbA1c", "Blood Glucose"],
                    [user_bmi_norm, user_hba1c_norm, user_glucose_norm],
                    [50, 50, 50]
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption("Note: Radar values are normalized. Values above the green dotted line (50%) exceed normal clinical thresholds.")

            # PDF Report Download Card
            with st.container(border=True):
                st.markdown("### 📄 Patient Clinical Report")
                
                metrics_list = [
                    {"name": "Age", "value": f"{age} years", "ref_range": "N/A", "status": "Normal"},
                    {"name": "Gender", "value": gender, "ref_range": "N/A", "status": "Normal"},
                    {"name": "BMI", "value": f"{bmi:.1f} kg/m²", "ref_range": "18.5 - 24.9", "status": "Normal" if bmi < 25.0 else ("Elevated" if bmi < 30.0 else "High")},
                    {"name": "Blood Glucose Level", "value": f"{glucose:.1f} mg/dL", "ref_range": "< 100 mg/dL", "status": "Normal" if glucose < 100 else ("Elevated" if glucose < 126 else "High")},
                    {"name": "HbA1c Level", "value": f"{hba1c:.1f}%", "ref_range": "< 5.7%", "status": "Normal" if hba1c < 5.7 else ("Elevated" if hba1c < 6.5 else "High")},
                    {"name": "Hypertension History", "value": hypertension, "ref_range": "No", "status": "Normal" if hypertension == "No" else "High"},
                    {"name": "Heart Disease History", "value": heart_disease, "ref_range": "No", "status": "Normal" if heart_disease == "No" else "High"},
                    {"name": "Smoking History", "value": smoking, "ref_range": "Never / No Info", "status": "Normal" if smoking in ["Never", "No Info"] else "Elevated"},
                ]
                
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d")
                }
                
                prediction_info = {
                    "type": "Diabetes",
                    "risk_percent": risk_percent,
                    "risk_level": "High Risk" if risk_percent >= 70 else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
                }
                
                inputs = {
                    "bmi": bmi,
                    "glucose": glucose,
                    "hba1c": hba1c,
                    "hypertension": hypertension_value,
                    "heart_disease": heart_disease_value,
                    "smoking_history": smoking_value
                }
                
                pdf_data = generate_pdf_report(patient_info, prediction_info, inputs, metrics_list)
                
                st.download_button(
                    label="📥 Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Diabetes_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="diabetes_download"
                )
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="text-align: center; padding: 40px 10px; color: #64748B;">
                        <span style="font-size: 50px;">🩺</span>
                        <h3 style="margin-top: 15px; color: #94A3B8; border-bottom: none; padding-bottom: 0; margin-bottom: 10px;">Awaiting Diagnostics</h3>
                        <p style="color: #64748B; font-size: 14px;">Fill out the clinical parameters on the left and click <b>Analyze Diabetes Risk</b> to generate a clinical breakdown and health charts.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# HEART PAGE
def heart_page():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #451A03 0%, #701A75 100%); padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 25px; display: flex; align-items: center; gap: 20px;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px;">
                <span style="font-size: 32px;">❤️</span>
            </div>
            <div>
                <h2 style="color: #F8FAFC; margin: 0; font-size: 24px; font-weight: 800;">Heart Disease Prediction</h2>
                <p style="color: #94A3B8; margin: 5px 0 0 0; font-size: 14px;">Analyzes systolic pressure, cholesterol levels, fasting sugar, and history of cardiac episodes.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_input, col_result = st.columns([1.1, 1], gap="large")

    with col_input:
        with st.container(border=True):
            st.markdown("### 👤 Patient Identification")
            pat_col1, pat_col2 = st.columns(2)
            with pat_col1:
                patient_name = st.text_input("Patient Name", value="", placeholder="Enter patient name", key="heart_name")
                patient_id = st.text_input("Patient ID / Record #", value=st.session_state.gen_patient_id, placeholder="Enter record number", key="heart_id")
            with pat_col2:
                report_date = st.date_input("Report Date", datetime.now(), key="heart_date")

        with st.container(border=True):
            st.markdown("### 📋 Patient Clinical Metrics")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                age = st.number_input("Age", min_value=0, max_value=120, value=None, step=1, format="%d", placeholder="Enter value")
                cholesterol = st.number_input("Total Cholesterol (mg/dL)", min_value=0.0, max_value=600.0, value=None, step=1.0, placeholder="Enter value")
            with sub_col2:
                bmi = st.number_input("BMI (kg/m²)", min_value=0.0, max_value=80.0, value=None, step=0.1, placeholder="Enter value")
                previous_heart_attack = st.radio("Previous Heart Attack?", ["No", "Yes"], index=None, horizontal=True)
                
            st.markdown("##### Measurements & Background")
            
            sub_col3, sub_col4 = st.columns(2)
            with sub_col3:
                systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=0.0, max_value=300.0, value=None, step=1.0, placeholder="Enter value")
                diabetes = st.radio("Diabetes?", ["No", "Yes"], index=None, horizontal=True)
            with sub_col4:
                fasting_sugar = st.number_input("Fasting Blood Sugar (mg/dL)", min_value=0.0, max_value=500.0, value=None, step=1.0, placeholder="Enter value")
                hypertension = st.radio("Hypertension?", ["No", "Yes"], index=None, horizontal=True)
            
        predict_btn = st.button("Analyze Heart Risk")

    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error("⚠️ Patient Name and Patient ID are required to perform the analysis and generate the report.")
                st.stop()
            if None in [age, cholesterol, bmi, previous_heart_attack, systolic_bp, diabetes, fasting_sugar, hypertension]:
                st.error("⚠️ Please fill out all required clinical metrics before analyzing.")
                st.stop()

            hypertension_value = 1 if hypertension == "Yes" else 0

            diabetes_value = 1 if diabetes == "Yes" else 0
            previous_heart_attack_value = 1 if previous_heart_attack == "Yes" else 0

            input_data = pd.DataFrame([{
                'Age': age,
                'Cholesterol_Total': cholesterol,
                'Hypertension': hypertension_value,
                'Diabetes': diabetes_value,
                'Previous_Heart_Attack': previous_heart_attack_value,
                'BMI': bmi,
                'Blood_Sugar_Fasting': fasting_sugar,
                'Systolic_BP': systolic_bp
            }])

            input_data = input_data[heart_features]

            probability = heart_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100

            with st.container(border=True):
                st.markdown("### 📊 Risk Report Dashboard")
                
                # Gauge chart
                fig_gauge = draw_gauge_chart(risk_percent, "Cardiac Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)

                # Advice alerts
                if risk_percent < 35:
                    st.success(f"**Low Risk ({risk_percent:.2f}%)** - Normal cardiovascular risk. Maintenance of current healthy lifestyle habits suggested.")
                elif risk_percent < 70:
                    st.warning(f"**Moderate Risk ({risk_percent:.2f}%)** - Mild anomalies detected. Advise routine clinical observation and BP monitoring.")
                else:
                    st.error(f"**High Risk ({risk_percent:.2f}%)** - Elevated parameters indicators present. Prompt consultation with a cardiologist is recommended.")

            with st.container(border=True):
                st.markdown("### 📈 Cardiovascular Profile")
                
                user_bmi_norm = min(100.0, (bmi / 24.9) * 50)
                user_chol_norm = min(100.0, (cholesterol / 200.0) * 50)
                user_bp_norm = min(100.0, (systolic_bp / 120.0) * 50)
                user_sugar_norm = min(100.0, (fasting_sugar / 100.0) * 50)
                
                fig_radar = draw_radar_chart(
                    ["BMI", "Cholesterol", "Systolic BP", "Fasting Sugar"],
                    [user_bmi_norm, user_chol_norm, user_bp_norm, user_sugar_norm],
                    [50, 50, 50, 50]
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                st.caption("Note: Radar values are normalized. Values exceeding the green boundary (50%) are in the clinical alert range.")

            # PDF Report Download Card
            with st.container(border=True):
                st.markdown("### 📄 Patient Clinical Report")
                
                metrics_list = [
                    {"name": "Age", "value": f"{age} years", "ref_range": "N/A", "status": "Normal"},
                    {"name": "Total Cholesterol", "value": f"{cholesterol:.1f} mg/dL", "ref_range": "< 200 mg/dL", "status": "Normal" if cholesterol < 200 else ("Elevated" if cholesterol < 240 else "High")},
                    {"name": "BMI", "value": f"{bmi:.1f} kg/m²", "ref_range": "18.5 - 24.9", "status": "Normal" if bmi < 25.0 else ("Elevated" if bmi < 30.0 else "High")},
                    {"name": "Systolic Blood Pressure", "value": f"{systolic_bp:.1f} mmHg", "ref_range": "< 120 mmHg", "status": "Normal" if systolic_bp < 120 else ("Elevated" if systolic_bp < 140 else "High")},
                    {"name": "Fasting Blood Sugar", "value": f"{fasting_sugar:.1f} mg/dL", "ref_range": "< 100 mg/dL", "status": "Normal" if fasting_sugar < 100 else ("Elevated" if fasting_sugar < 126 else "High")},
                    {"name": "Previous Heart Attack", "value": previous_heart_attack, "ref_range": "No", "status": "Normal" if previous_heart_attack == "No" else "High"},
                    {"name": "Diabetes History", "value": diabetes, "ref_range": "No", "status": "Normal" if diabetes == "No" else "High"},
                    {"name": "Hypertension History", "value": hypertension, "ref_range": "No", "status": "Normal" if hypertension == "No" else "High"},
                ]
                
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d")
                }
                
                prediction_info = {
                    "type": "Heart Disease",
                    "risk_percent": risk_percent,
                    "risk_level": "High Risk" if risk_percent >= 70 else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
                }
                
                inputs = {
                    "Age": age,
                    "cholesterol": cholesterol,
                    "bmi": bmi,
                    "systolic_bp": systolic_bp,
                    "fasting_sugar": fasting_sugar,
                    "previous_heart_attack": previous_heart_attack_value,
                    "diabetes": diabetes_value,
                    "hypertension": hypertension_value
                }
                
                pdf_data = generate_pdf_report(patient_info, prediction_info, inputs, metrics_list)
                
                st.download_button(
                    label="📥 Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Heart_Disease_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="heart_download"
                )
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="text-align: center; padding: 40px 10px; color: #64748B;">
                        <span style="font-size: 50px;">❤️</span>
                        <h3 style="margin-top: 15px; color: #94A3B8; border-bottom: none; padding-bottom: 0; margin-bottom: 10px;">Awaiting Diagnostics</h3>
                        <p style="color: #64748B; font-size: 14px;">Fill out the cardiovascular parameters on the left and click <b>Analyze Heart Risk</b> to generate a clinical breakdown and health charts.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# STROKE PAGE
def stroke_page():
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #064E3B 0%, #1E3A8A 100%); padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 25px; display: flex; align-items: center; gap: 20px;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px;">
                <span style="font-size: 32px;">🧠</span>
            </div>
            <div>
                <h2 style="color: #F8FAFC; margin: 0; font-size: 24px; font-weight: 800;">Stroke Risk Assessment</h2>
                <p style="color: #94A3B8; margin: 5px 0 0 0; font-size: 14px;">Correlates age and blood pressure with 11 distinct physiological symptoms to estimate risk.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_input, col_result = st.columns([1.1, 1], gap="large")

    with col_input:
        with st.container(border=True):
            st.markdown("### 👤 Patient Identification")
            pat_col1, pat_col2 = st.columns(2)
            with pat_col1:
                patient_name = st.text_input("Patient Name", value="", placeholder="Enter patient name", key="stroke_name")
                patient_id = st.text_input("Patient ID / Record #", value=st.session_state.gen_patient_id, placeholder="Enter record number", key="stroke_id")
            with pat_col2:
                report_date = st.date_input("Report Date", datetime.now(), key="stroke_date")

        with st.container(border=True):
            st.markdown("### 📋 Patient Profile & Symptoms")
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                age = st.number_input("Age", min_value=0, max_value=120, value=None, step=1, format="%d", placeholder="Enter value")
            with sub_col2:
                high_blood_pressure = st.radio("High Blood Pressure?", ["No", "Yes"], index=None, horizontal=True)
                
            st.markdown("##### 🫁 Cardiorespiratory Symptoms")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                chest_pain = st.radio("Chest Pain", ["No", "Yes"], index=None, horizontal=True)
                irregular_heartbeat = st.radio("Irregular Heartbeat", ["No", "Yes"], index=None, horizontal=True)
            with c_col2:
                shortness_of_breath = st.radio("Shortness of Breath", ["No", "Yes"], index=None, horizontal=True)
                persistent_cough = st.radio("Persistent Cough", ["No", "Yes"], index=None, horizontal=True)
                
            st.markdown("##### 🧠 Neurological, General & Autonomic")
            n_col1, n_col2 = st.columns(2)
            with n_col1:
                dizziness = st.radio("Dizziness", ["No", "Yes"], index=None, horizontal=True)
                fatigue_weakness = st.radio("Fatigue & Weakness", ["No", "Yes"], index=None, horizontal=True)
                cold_hands_feet = st.radio("Cold Hands/Feet", ["No", "Yes"], index=None, horizontal=True)
            with n_col2:
                snoring_sleep_apnea = st.radio("Sleep Apnea", ["No", "Yes"], index=None, horizontal=True)
                swelling_edema = st.radio("Swelling or Edema", ["No", "Yes"], index=None, horizontal=True)
                excessive_sweating = st.radio("Excessive Sweating", ["No", "Yes"], index=None, horizontal=True)
            
        predict_btn = st.button("Analyze Stroke Risk")

    with col_result:
        if predict_btn:
            if not patient_name.strip() or not patient_id.strip():
                st.error("⚠️ Patient Name and Patient ID are required to perform the analysis and generate the report.")
                st.stop()
            if None in [age, high_blood_pressure, dizziness, fatigue_weakness, cold_hands_feet, snoring_sleep_apnea, swelling_edema, excessive_sweating, chest_pain, irregular_heartbeat, shortness_of_breath, persistent_cough]:
                st.error("⚠️ Please fill out all required clinical metrics before analyzing.")
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

            input_data = pd.DataFrame([{
                'age': age,
                'chest_pain': chest_pain_value,
                'high_blood_pressure': high_bp_value,
                'shortness_of_breath': breath_value,
                'dizziness': dizziness_value,
                'irregular_heartbeat': heartbeat_value,
                'fatigue_&_weakness': fatigue_value,
                'snoringsleep_apnea': snoring_value,
                'cold_handsfeet': cold_hands_value,
                'excessive_sweating': sweating_value,
                'persistent_cough': cough_value,
                'swelling_edema': edema_value
            }])

            stroke_features = [
                'age', 'chest_pain', 'high_blood_pressure', 'shortness_of_breath',
                'dizziness', 'irregular_heartbeat', 'fatigue_&_weakness',
                'snoringsleep_apnea', 'cold_handsfeet', 'excessive_sweating',
                'persistent_cough', 'swelling_edema'
            ]
            input_data = input_data[stroke_features]

            probability = stroke_model.predict_proba(input_data)[0][1]
            risk_percent = probability * 100

            with st.container(border=True):
                st.markdown("### 📊 Risk Report Dashboard")
                
                # Gauge chart
                fig_gauge = draw_gauge_chart(risk_percent, "Stroke Risk Score")
                st.plotly_chart(fig_gauge, use_container_width=True)

                # Advice alerts
                if risk_percent < 35:
                    st.success(f"**Low Risk ({risk_percent:.2f}%)** - Normal stroke risk assessment. Standard preventative checkups advised.")
                elif risk_percent < 70:
                    st.warning(f"**Moderate Risk ({risk_percent:.2f}%)** - Moderate risk indicators present. Keep watch on BP levels and consult a health practitioner.")
                else:
                    st.error(f"**High Risk ({risk_percent:.2f}%)** - Significant clinical indicators present. Immediate medical evaluation recommended.")

            with st.container(border=True):
                st.markdown("### 📈 Symptoms Breakdown")
                
                cardio_symptoms = sum([chest_pain_value, heartbeat_value, breath_value, cough_value])
                neuro_symptoms = sum([dizziness_value, fatigue_value, snoring_value])
                auto_symptoms = sum([cold_hands_value, sweating_value, edema_value])
                
                fig_bar = draw_symptoms_chart(cardio_symptoms, neuro_symptoms, auto_symptoms)
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption("This chart displays reported vs. absent symptoms per physiological category.")

            # PDF Report Download Card
            with st.container(border=True):
                st.markdown("### 📄 Patient Clinical Report")
                
                metrics_list = [
                    {"name": "Age", "value": f"{age} years", "ref_range": "N/A", "status": "Normal"},
                    {"name": "High Blood Pressure Status", "value": high_blood_pressure, "ref_range": "No", "status": "Normal" if high_blood_pressure == "No" else "High"},
                    {"name": "Chest Pain Symptom", "value": chest_pain, "ref_range": "No", "status": "Normal" if chest_pain == "No" else "High"},
                    {"name": "Irregular Heartbeat", "value": irregular_heartbeat, "ref_range": "No", "status": "Normal" if irregular_heartbeat == "No" else "High"},
                    {"name": "Shortness of Breath", "value": shortness_of_breath, "ref_range": "No", "status": "Normal" if shortness_of_breath == "No" else "High"},
                    {"name": "Persistent Cough", "value": persistent_cough, "ref_range": "No", "status": "Normal" if persistent_cough == "No" else "High"},
                    {"name": "Dizziness Symptom", "value": dizziness, "ref_range": "No", "status": "Normal" if dizziness == "No" else "High"},
                    {"name": "Fatigue & Weakness", "value": fatigue_weakness, "ref_range": "No", "status": "Normal" if fatigue_weakness == "No" else "High"},
                    {"name": "Sleep Apnea / Snoring", "value": snoring_sleep_apnea, "ref_range": "No", "status": "Normal" if snoring_sleep_apnea == "No" else "High"},
                    {"name": "Cold Hands & Feet", "value": cold_hands_feet, "ref_range": "No", "status": "Normal" if cold_hands_feet == "No" else "High"},
                    {"name": "Swelling or Edema", "value": swelling_edema, "ref_range": "No", "status": "Normal" if swelling_edema == "No" else "High"},
                    {"name": "Excessive Sweating", "value": excessive_sweating, "ref_range": "No", "status": "Normal" if excessive_sweating == "No" else "High"},
                ]
                
                patient_info = {
                    "name": patient_name,
                    "patient_id": patient_id,
                    "physician": "",
                    "date": report_date.strftime("%Y-%m-%d")
                }
                
                prediction_info = {
                    "type": "Stroke",
                    "risk_percent": risk_percent,
                    "risk_level": "High Risk" if risk_percent >= 70 else ("Moderate Risk" if risk_percent >= 35 else "Low Risk")
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
                    "excessive_sweating": sweating_value
                }
                
                pdf_data = generate_pdf_report(patient_info, prediction_info, inputs, metrics_list)
                
                st.download_button(
                    label="📥 Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name=f"Stroke_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="stroke_download"
                )
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="text-align: center; padding: 40px 10px; color: #64748B;">
                        <span style="font-size: 50px;">🧠</span>
                        <h3 style="margin-top: 15px; color: #94A3B8; border-bottom: none; padding-bottom: 0; margin-bottom: 10px;">Awaiting Diagnostics</h3>
                        <p style="color: #64748B; font-size: 14px;">Fill out the profile and symptoms on the left and click <b>Analyze Stroke Risk</b> to generate a clinical breakdown and health charts.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# PAGE NAVIGATOR CALLS
if selected == "Diabetes Prediction":
    diabetes_page()
elif selected == "Heart Disease Prediction":
    heart_page()
elif selected == "Stroke Prediction":
    stroke_page()