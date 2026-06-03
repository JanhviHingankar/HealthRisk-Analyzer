import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line

def draw_risk_bar(score):
    """
    Draws a custom horizontal progress bar indicating the risk score.
    """
    d = Drawing(450, 30)
    # Background bar
    d.add(Rect(0, 12, 450, 10, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None, rx=5, ry=5))
    
    # Determine color based on risk score
    if score < 35:
        bar_color = colors.HexColor("#10B981") # Green (Low)
    elif score < 70:
        bar_color = colors.HexColor("#F59E0B") # Amber (Moderate)
    else:
        bar_color = colors.HexColor("#EF4444") # Red (High)
        
    # Fill bar (minimum width of 10 to be visible if score is very low)
    fill_width = max(10, (score / 100.0) * 450)
    d.add(Rect(0, 12, fill_width, 10, fillColor=bar_color, strokeColor=None, rx=5, ry=5))
    
    # Custom ticks/lines for reference
    d.add(Line(157.5, 10, 157.5, 24, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=1))
    d.add(Line(315, 10, 315, 24, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=1))
    
    # Labels below progress bar
    d.add(String(0, 0, "0%", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#64748B")))
    d.add(String(140, 0, "35% (Elevated)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#64748B")))
    d.add(String(295, 0, "70% (High)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#64748B")))
    d.add(String(430, 0, "100%", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#64748B")))
    return d

def get_recommendations(disease_type, risk_percent, inputs):
    """
    Compiles tailored clinical recommendations based on risk score and clinical inputs.
    """
    recs = []
    
    # Category advice
    if risk_percent < 35:
        recs.append("<b>General Assessment:</b> Low risk score detected. Patient parameters indicate normal ranges. Continue current lifestyle choices and undergo standard annual wellness screenings.")
    elif risk_percent < 70:
        recs.append("<b>General Assessment:</b> Moderate risk score detected. Patient exhibits mild anomalies. Clinical observation and proactive lifestyle adjustments are recommended to mitigate risk factors.")
    else:
        recs.append("<b>General Assessment:</b> High risk score detected. Patient displays significant risk parameters that correlate strongly with pathological indicators. A comprehensive physician checkup is advised as soon as possible.")

    # Tailored recommendations based on specific disease type
    if disease_type == "Diabetes":
        if risk_percent >= 35:
            recs.append("Monitor blood glucose levels and schedule an HbA1c test in 3 months to establish baseline tracking.")
            recs.append("Reduce intake of high glycemic index (GI) carbohydrates, saturated fats, and refined sugars.")
        if float(inputs.get('bmi', 0)) >= 25.0:
            recs.append(f"Current BMI ({inputs['bmi']} kg/m²) indicates overweight/obesity range. Aim for moderate weight management through structured exercise (minimum 150 mins per week).")
        if inputs.get('hypertension') == 1 or inputs.get('heart_disease') == 1:
            recs.append("Co-existing hypertension or cardiovascular disease increases metabolic risk factors. Coordinate care between cardiological and primary care professionals.")
        if inputs.get('smoking_history') in ['current', 'former', 'ever', 'not current']:
            recs.append("Maintain strong smoking cessation. Tobacco exposure negatively affects vascular health and insulin sensitivity.")

    elif disease_type == "Heart Disease":
        if risk_percent >= 35:
            recs.append("Schedule a comprehensive lipid panel to assess LDL, HDL, and triglyceride levels in detail.")
            recs.append("Adopt a heart-healthy diet such as the DASH or Mediterranean diet, limiting sodium intake to under 2,000 mg per day.")
        if float(inputs.get('systolic_bp', 0)) >= 130.0:
            recs.append(f"Systolic Blood Pressure ({inputs['systolic_bp']} mmHg) is in the elevated/hypertensive range. Monitor daily at home and record values for review.")
        if float(inputs.get('cholesterol', 0)) >= 200.0:
            recs.append(f"Total Cholesterol ({inputs['cholesterol']} mg/dL) exceeds normal levels. Focus on soluble dietary fiber and consult about therapeutic options if values remain elevated.")
        if float(inputs.get('bmi', 0)) >= 25.0:
            recs.append(f"Elevated BMI ({inputs['bmi']} kg/m²) places additional mechanical and metabolic stress on the heart. Consider active weight management.")
        if inputs.get('previous_heart_attack') == 1:
            recs.append("History of previous heart attack is a critical risk factor. Ensure adherence to prescribed beta-blockers, antiplatelet, or statin therapies under supervision.")

    elif disease_type == "Stroke":
        if risk_percent >= 35:
            recs.append("Monitor blood pressure daily; stroke risk is strongly correlated with poorly controlled hypertension.")
            recs.append("Screen for sleep apnea or sleep architecture issues, which are recognized independent contributors to stroke risk.")
        if inputs.get('high_blood_pressure') == 1:
            recs.append("Diagnosed hypertension needs aggressive control. Work with your physician to optimize medication management.")
        if inputs.get('chest_pain') == 1 or inputs.get('irregular_heartbeat') == 1:
            recs.append("Active cardiorespiratory symptoms (Chest Pain, Irregular Heartbeat) require urgent investigation (e.g. ECG) to rule out atrial fibrillation or coronary insufficiency.")
        if inputs.get('dizziness') == 1 or inputs.get('shortness_of_breath') == 1:
            recs.append("Reported dizziness and dyspnea may indicate transient cerebral hypoperfusion or circulatory strain. Rest and contact your healthcare provider if persistent.")

    return recs

def generate_pdf_report(patient_info, prediction_info, inputs, metrics_list):
    """
    Generates a PDF patient report in memory.
    
    patient_info: dict with 'name', 'patient_id', 'physician', 'date'
    prediction_info: dict with 'type', 'risk_percent', 'risk_level'
    inputs: dict of raw feature inputs
    metrics_list: list of dicts with 'name', 'value', 'ref_range', 'status'
    """
    buffer = io.BytesIO()
    
    # Document Setup
    # Margins: 0.75 inch = 54 pt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    normal_style = ParagraphStyle(
        'ReportNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    
    bold_style = ParagraphStyle(
        'ReportBold',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    title_style = ParagraphStyle(
        'ReportTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#FFFFFF"),
        alignment=1 # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#E2E8F0"),
        alignment=1 # Centered
    )
    
    h2_style = ParagraphStyle(
        'ReportH2',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=normal_style,
        fontSize=9,
        leading=12
    )
    
    table_header_style = ParagraphStyle(
        'TableHeaderText',
        parent=table_text_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    disclaimer_style = ParagraphStyle(
        'ReportDisclaimer',
        parent=normal_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        alignment=4 # Justify
    )
    
    risk_number_style = ParagraphStyle(
        'RiskNumberStyle',
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=32,
        textColor=colors.HexColor("#0F172A")
    )
    
    story = []
    
    # 1. Header Banner Table (Professional Look)
    banner_data = [
        [Paragraph("AI MULTI-DISEASE DIAGNOSTIC REPORT", title_style)],
        [Paragraph(f"PREDICTIVE ANALYSIS & HEALTH PROFILE &bull; {prediction_info['type'].upper()} SCREENING", subtitle_style)]
    ]
    banner_table = Table(banner_data, colWidths=[504])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,1), (-1,1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    # 2. Metadata / Demographics block
    meta_data = [
        [
            Paragraph("<b>Patient Name:</b>", normal_style), Paragraph(patient_info['name'], normal_style),
            Paragraph("<b>Date of Report:</b>", normal_style), Paragraph(patient_info['date'], normal_style)
        ],
        [
            Paragraph("<b>Patient ID:</b>", normal_style), Paragraph(patient_info['patient_id'], normal_style),
            Paragraph("<b>Assessment:</b>", normal_style), Paragraph(f"{prediction_info['type']} Risk", normal_style)
        ],
        [
            Paragraph("<b>Methodology:</b>", normal_style), Paragraph("Machine Learning Classification", normal_style),
            Paragraph("", normal_style), Paragraph("", normal_style)
        ]
    ]
    # Printable width is 504. Divide columns: 90, 162, 90, 162
    meta_table = Table(meta_data, colWidths=[90, 162, 90, 162])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,2), (-1,2), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # 3. Risk Summary Section
    story.append(Paragraph("Assessment Summary", h2_style))
    
    risk_score = prediction_info['risk_percent']
    risk_level = prediction_info['risk_level']
    
    # Color coding for Risk Level Badge
    if risk_level == "High Risk":
        level_color = "#DC2626"
    elif risk_level == "Moderate Risk":
        level_color = "#D97706"
    else:
        level_color = "#16A34A"
        
    badge_style = ParagraphStyle(
        'Badge',
        parent=bold_style,
        fontSize=12,
        textColor=colors.white,
        alignment=1
    )
    
    # Score Summary Table
    score_content = [
        [
            [
                Paragraph("Calculated Risk Score", normal_style),
                Spacer(1, 4),
                Paragraph(f"{risk_score:.2f}%", risk_number_style)
            ],
            Table([[Paragraph(risk_level.upper(), badge_style)]], colWidths=[140], style=[
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(level_color)),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ])
        ]
    ]
    
    score_table = Table(score_content, colWidths=[330, 174])
    score_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))
    
    # Risk progress indicator
    story.append(draw_risk_bar(risk_score))
    story.append(Spacer(1, 15))
    
    # 4. Clinical Metrics Table
    story.append(Paragraph("Clinical Measurements Checklist", h2_style))
    
    # Table headers
    metrics_data = [[
        Paragraph("Clinical Metric", table_header_style),
        Paragraph("Patient Value", table_header_style),
        Paragraph("Reference Standard", table_header_style),
        Paragraph("Interpretation", table_header_style)
    ]]
    
    for metric in metrics_list:
        # Determine interpreting color
        status = metric['status']
        if status.lower() == "normal":
            status_text = f"<font color='#16A34A'><b>{status}</b></font>"
        elif status.lower() in ["elevated", "borderline"]:
            status_text = f"<font color='#D97706'><b>{status}</b></font>"
        else: # High / Critical / Yes
            status_text = f"<font color='#DC2626'><b>{status}</b></font>"
            
        metrics_data.append([
            Paragraph(metric['name'], table_text_style),
            Paragraph(str(metric['value']), table_text_style),
            Paragraph(metric['ref_range'], table_text_style),
            Paragraph(status_text, table_text_style)
        ])
        
    metrics_table = Table(metrics_data, colWidths=[150, 110, 124, 120])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # 5. Clinical Recommendations
    story.append(Paragraph("Clinician Consultation & Guidance", h2_style))
    recs = get_recommendations(prediction_info['type'], risk_score, inputs)
    for rec in recs:
        bullet_text = f"&bull; {rec}"
        story.append(Paragraph(bullet_text, normal_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 15))
    
    # 6. Disclaimer
    story.append(Paragraph("<b>Disclaimer:</b>", bold_style))
    disclaimer_text = (
        "This diagnostic report is generated using an automated artificial intelligence predictive classification model. "
        "It is designed solely to assist medical personnel in screening and is for educational/informational use. It does "
        "not constitute medical advice, diagnostic confirmation, or treatment plans. Patient management decisions should "
        "be established by a qualified healthcare professional combining these metrics with physical examinations, clinical "
        "symptomatology, and laboratory investigations."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    # Signature area removed per user feedback
    
    # Footer function to run on canvas draw
    def add_page_decorations(canvas, doc_template):
        canvas.saveState()
        # Header line (subtle)
        canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
        canvas.setLineWidth(0.5)
        canvas.line(54, 738, 612 - 54, 738)
        
        # Footer text & page numbering
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(54, 30, "CONFIDENTIAL &bull; AI MULTI-DISEASE ANALYSIS CLINICAL REPORT")
        canvas.drawRightString(612 - 54, 30, f"Page {canvas._pageNumber}")
        canvas.line(54, 42, 612 - 54, 42)
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
