# HealthRisk Analyzer 🩺

A comprehensive, interactive web application built with **Streamlit** and **Machine Learning** that assists clinical professionals in predicting the risk of Diabetes, Heart Disease, and Stroke based on patient medical profiles.

The application boasts a premium glassmorphic UI, dynamic Plotly visualizations, and generates automated, heavily-formatted PDF clinical diagnostic reports via ReportLab.

---

## 🌟 Key Features

- **Multi-Disease Screening**: Contains three isolated models trained to predict clinical risk percentages for:
  - 🩸 **Diabetes** (Demographics, Glucose, HbA1c, etc.)
  - ❤️ **Heart Disease** (Cholesterol, Systolic BP, Fasting Sugar, etc.)
  - 🧠 **Stroke** (11+ Cardiorespiratory, Neurological, and Autonomic symptoms)
- **Automated Clinical Reports**: Generates downloadable, clinician-ready **PDF Diagnostics Reports** equipped with layout-adjusted tables, medical disclaimers, and dynamically assigned severity badges.
- **Dynamic Visualizations**: Utilizes Plotly to render radar charts, risk gauge meters, and symptom breakdown bars based solely on individualized patient input.
- **Robust UI Form Handling**: Auto-generates unique Patient IDs per session, implements rigorous form validations, and actively prohibits empty metrics arrays from causing server errors.
- **Premium Aesthetics**: Features custom-injected CSS targeting Streamlit components for a modern, glassmorphic layout, cohesive thematic styles per disease, and dynamic alerts.

## 🛠️ Technology Stack

- **Frontend**: Streamlit, Custom HTML/CSS
- **Data Visualizations**: Plotly (Graph Objects, Express)
- **PDF Generation**: ReportLab
- **Machine Learning**: Scikit-Learn (Pipelines, Classification)
- **Data Processing**: Pandas, NumPy

## 🚀 Quickstart Guide

### 1. Clone the repository
```bash
git clone https://github.com/JanhviHingankar/HealthRisk-Analyzer.git
cd HealthRisk-Analyzer
```

### 2. Install dependencies
Ensure you have Python 3.8+ installed. Install the necessary libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Run the application
Fire up the Streamlit server:
```bash
streamlit run app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*

## 📁 Repository Structure

```text
├── app.py                       # Main Streamlit application and UI routing
├── report_generator.py          # PDF generation engine leveraging ReportLab
├── requirements.txt             # Project dependencies
├── .gitignore                   # Git ignore rules
├── diabetes_pipeline.pkl        # Serialized ML model for Diabetes
├── heart_model.pkl              # Serialized ML model for Heart Disease
├── stroke_pipeline.pkl          # Serialized ML model for Stroke
└── features.pkl                 # Persisted feature lists for pre-processing
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to check out the [issues page](https://github.com/YOUR-USERNAME/multi-disease-prediction/issues).

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
