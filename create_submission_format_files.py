import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx(filename="FINAL_PROJECT_SUBMISSION_FORMAT.docx"):
    doc = Document()
    
    # Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title & Header
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nACADEMIC PROJECT SUBMISSION REPORT")
    run_inst.font.name = 'Calibri'
    run_inst.font.size = Pt(14)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(30, 58, 138)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_proj = p_proj.add_run("Rainfall-Based Flood Early Warning System (FEWS)\nUsing HiveMQ Cloud MQTT, PyTorch LSTM, and Node-RED")
    run_proj.font.name = 'Calibri'
    run_proj.font.size = Pt(16)
    run_proj.font.bold = True
    run_proj.font.color.rgb = RGBColor(37, 99, 235)

    doc.add_paragraph() # Spacer

    # Student Details Table
    table_meta = doc.add_table(rows=6, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.autofit = False

    meta_rows = [
        ("Student Name", "Shivaya Mishra"),
        ("Roll Number / Student ID", "0184 (Section B)"),
        ("Branch & Specialization", "Computer Science & Engineering (Data Science)"),
        ("Subject / Lab Course", "Full Stack Development (FSD Lab) / Capstone Project"),
        ("Project Repository (GitHub)", "https://github.com/shivaya34mishra-coder/Rainfall-warning-system"),
        ("Technology Stack", "HiveMQ Cloud MQTT (TLS 8883), Python 3.13, PyTorch 2.15, Node-RED, Streamlit")
    ]

    for i, (k, v) in enumerate(meta_rows):
        row = table_meta.rows[i]
        cell_k, cell_v = row.cells[0], row.cells[1]
        cell_k.width = Inches(2.3)
        cell_v.width = Inches(4.5)
        
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.font.bold = True
        rk.font.size = Pt(9.5)
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)
        
        set_cell_background(cell_k, "F1F5F9")
        set_cell_background(cell_v, "F8FAFC" if i % 2 == 0 else "FFFFFF")

    doc.add_paragraph()

    # Section 1: Abstract
    h1 = doc.add_heading("1. Abstract & Executive Summary", level=1)
    h1.style.font.color.rgb = RGBColor(30, 58, 138)
    p_abs = doc.add_paragraph(
        "Flooding caused by intense localized precipitation represents one of the most destructive natural disasters worldwide. "
        "Traditional riverbank monitoring infrastructures are reactive—triggering warnings only after retention banks have physically breached. "
        "This project presents an Automated, End-to-End Predictive Flood Early Warning System (FEWS). "
        "The architecture integrates continuous precipitation and river gauge telemetry streamed over HiveMQ Cloud (MQTT with TLS 8883), "
        "a 2-layer Long Short-Term Memory (LSTM) deep learning forecasting engine in PyTorch (achieving R² = 99.73%), "
        "and interactive dual operational dashboards implemented in Node-RED and Streamlit with an interactive Geographical GIS flood map. "
        "By modeling non-linear catchment runoff delay dynamics, the system predicts water level crests 15–60 minutes in advance and "
        "automatically triggers multi-tiered early warning protocols (Safe, Watch, Warning, Critical) to empower proactive disaster management."
    )
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Section 2: Objectives
    h2 = doc.add_heading("2. Project Objectives", level=1)
    h2.style.font.color.rgb = RGBColor(30, 58, 138)
    objectives = [
        "Real-Time Telemetry Streaming: Establish secure MQTT pub/sub data streams of rainfall intensity (mm) and river water levels (m) using HiveMQ Cloud.",
        "Deep Learning Hydrograph Forecasting: Formulate and train a 2-layer PyTorch LSTM model capturing temporal catchment runoff delays with R² > 99%.",
        "Automated Risk Stratification: Continuously evaluate forecasted crests against safety limits (Safe <1.5m, Watch 1.5-2.0m, Warning 2.0-2.5m, Critical >2.5m).",
        "Automated Alert Dispatch: Disseminate real-time emergency alert payloads to topic 'flood/alert' during impending flood surges.",
        "Industrial SCADA & GIS Dashboards: Deploy an industrial SCADA dashboard on Node-RED and an interactive analytical GIS portal on Streamlit."
    ]
    for obj in objectives:
        doc.add_paragraph(obj, style='List Bullet')

    # Section 3: Technical Specifications
    h3 = doc.add_heading("3. Technical Specifications & Architecture", level=1)
    h3.style.font.color.rgb = RGBColor(30, 58, 138)
    
    table_tech = doc.add_table(rows=6, cols=3)
    table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_headers = ["Layer", "Technology", "Role & Specification"]
    for j, h in enumerate(tech_headers):
        cell = table_tech.rows[0].cells[j]
        set_cell_background(cell, "CBD5E1")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.5)

    tech_rows = [
        ("Message Transport", "HiveMQ Cloud (TLS 8883)", "MQTTS pub/sub broker; topics: rainfall/data, flood/prediction, flood/alert"),
        ("Backend AI Engine", "Python 3.13, PyTorch 2.15", "Sliding window sequence processing, 2-layer LSTM regression network"),
        ("Data Science & Maths", "NumPy, Pandas, Scikit-Learn", "Feature scaling, time-series hydrograph windowing, RMSE & MAE evaluations"),
        ("Industrial SCADA", "Node-RED v5.0 + Dashboard", "Real-time telemetry gauges, SVG trend hydrographs, automated pop-up toast alerts"),
        ("GIS Command Center", "Streamlit 1.64 + Plotly", "Operational command center, interactive GIS map with station color badges")
    ]
    for i, row_data in enumerate(tech_rows):
        row = table_tech.rows[i+1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            set_cell_background(cell, "F8FAFC" if i % 2 == 0 else "FFFFFF")

    doc.add_page_break()

    # Section 4: Mathematical Modeling
    h4 = doc.add_heading("4. Mathematical Formulation & Deep Learning Model", level=1)
    h4.style.font.color.rgb = RGBColor(30, 58, 138)
    doc.add_paragraph(
        "Catchment Runoff Dynamic Equation:\n"
        "h(t) = h_base + (h(t-1) - h_base) * k_recession + [0.35*R(t) + 0.45*R(t-1) + 0.20*R(t-2)] * C_runoff\n"
        "Where h(t) = river level (m), R(t) = rainfall (mm), k_recession = 0.92, C_runoff = 0.048."
    )
    doc.add_paragraph(
        "PyTorch LSTM Neural Network:\n"
        "Input Tensor: X in R^(batch x 5 x 2) representing 5 consecutive timesteps of [rainfall, water_level].\n"
        "Architecture: LSTM(2 -> 64, num_layers=2, dropout=0.2) -> Linear(64 -> 32) -> ReLU -> Linear(32 -> 1).\n"
        "Performance: R² Score = 99.73% | RMSE = 0.0476 meters | MAE = 0.0217 meters | Latency < 12 ms."
    )

    # Section 5: Early Warning Severity Matrix
    h5 = doc.add_heading("5. Early Warning Severity Thresholds", level=1)
    h5.style.font.color.rgb = RGBColor(30, 58, 138)
    
    table_thresh = doc.add_table(rows=5, cols=4)
    table_thresh.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Forecast Level", "Risk State", "Color", "Automated Operational Directive"]
    for j, h in enumerate(t_headers):
        cell = table_thresh.rows[0].cells[j]
        set_cell_background(cell, "CBD5E1")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.5)

    thresh_rows = [
        ("< 1.50 meters", "SAFE", "Green", "Baseline river conditions. Routine continuous hydrological monitoring."),
        ("1.50 m - 2.00 m", "WATCH", "Yellow", "Moderate catchment runoff detected. Alert drainage operators and inspect retention basins."),
        ("2.00 m - 2.50 m", "WARNING", "Orange", "Approaching crest levee limit. Open flood retention gates and mobilize sandbag teams."),
        ("> 2.50 meters", "CRITICAL", "Red", "Imminent severe overflow! Sound community sirens and trigger immediate evacuation.")
    ]
    for i, row_data in enumerate(thresh_rows):
        row = table_thresh.rows[i+1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if j == 1:
                r.font.bold = True
            set_cell_background(cell, "F8FAFC" if i % 2 == 0 else "FFFFFF")

    doc.add_page_break()

    # Section 6: Screenshots & Outputs
    h6 = doc.add_heading("6. System Screenshots & Output Results", level=1)
    h6.style.font.color.rgb = RGBColor(30, 58, 138)

    sc_files = [
        ("screenshots/01_live_command_center.png", "Figure 1: Live Command Center Dashboard — KPI tiles, rainfall & water gauges, operational threat banner, and dual-axis hydrograph."),
        ("screenshots/02_gis_flood_map.png", "Figure 2: Geographical GIS Flood Monitoring Map — 6 river checkpoints with color-coded water level risk indicators."),
        ("screenshots/03_river_cross_section.png", "Figure 3: River Channel Hydraulic Cross-Section — Water depth vs. levee crest walls and inundation thresholds."),
        ("screenshots/04_system_architecture.png", "Figure 4: Complete System Architecture — Telemetry ingestion, HiveMQ Cloud TLS, PyTorch LSTM, and UI Dashboards.")
    ]

    for img_path, caption in sc_files:
        if os.path.exists(img_path):
            doc.add_picture(img_path, width=Inches(6.2))
            p_cap = doc.add_paragraph(caption)
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.style.font.size = Pt(8.5)
            p_cap.style.font.italic = True
            doc.add_paragraph() # Spacer

    doc.add_page_break()

    # Section 7: Declaration Block
    h7 = doc.add_heading("7. Student Declaration & Verification", level=1)
    h7.style.font.color.rgb = RGBColor(30, 58, 138)
    doc.add_paragraph(
        "I hereby declare that this project titled 'Rainfall-Based Flood Early Warning System (FEWS)' is my original academic work. "
        "All sensor simulators, deep learning LSTM models, MQTT broker configurations, and dashboard interfaces have been developed, "
        "tested, and verified by me. The complete source code, trained neural network weights, and documentation are publicly available "
        "on my GitHub repository."
    )
    doc.add_paragraph()
    
    # Signature Table
    table_sig = doc.add_table(rows=2, cols=2)
    table_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sig.rows[0].cells[0].paragraphs[0].add_run("Student Signature:\n\n__________________________\nShivaya Mishra\nRoll No: 0184 (CSE-DS)")
    table_sig.rows[0].cells[1].paragraphs[0].add_run("Evaluator / Faculty Signature:\n\n__________________________\nDepartment of CSE (Data Science)\nDate: November 2026")
    
    doc.save(filename)
    print(f"[SUCCESS] Word submission format created at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    out_docx = sys.argv[1] if len(sys.argv) > 1 else "FINAL_PROJECT_SUBMISSION_FORMAT.docx"
    create_docx(out_docx)
