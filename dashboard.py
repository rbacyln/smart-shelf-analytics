"""
Smart Shelf Analytics Dashboard
-------------------------------
This application provides a real-time interface for monitoring retail shelf stock levels.
It utilizes YOLOv8 for object detection and Streamlit for data visualization.

Author: Rabia Ceylan
Date: 2026-01-14
"""

import streamlit as st
import sqlite3
import pandas as pd
import os
import glob
import time
import random
import cv2
import datetime
from ultralytics import YOLO
from fpdf import FPDF

# Page Config
st.set_page_config(
    page_title="ShelfGuard AI | Enterprise",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; color: #FF4B4B; text-align: center; font-weight: 800; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] p { color: #555 !important; font-weight: 600 !important; }
    div[data-testid="stMetricValue"] { color: #111 !important; font-weight: 800 !important; }
    div.stButton > button { width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def generate_report(log_data, image_path):
    """
    Generates a PDF inspection report with the analysis details and visual evidence.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    pdf.cell(200, 10, txt="ShelfGuard AI - Inspection Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date & Time: {log_data['timestamp']}", ln=True, align='L')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Operational Metrics:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"- Status: {log_data['status']}", ln=True)
    pdf.cell(200, 10, txt=f"- Products Detected: {log_data['product_count']}", ln=True)
    pdf.cell(200, 10, txt=f"- Empty Spots: {log_data['empty_count']}", ln=True)
    pdf.ln(10)
    
    if image_path and os.path.exists(image_path):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Visual Evidence:", ln=True, align='L')
        pdf.image(image_path, x=10, y=90, w=100)
    
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Generated automatically by ShelfGuard AI System", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

def trigger_alert(gaps):
    """
    Placeholder for external notification services (e.g., Telegram, Slack).
    """
    # Integration logic would go here
    return True

def run_analysis_pipeline():
    """
    Executes the full analysis pipeline: Load model -> Predict -> Log -> Save Artifacts.
    """
    model_path = 'runs/detect/shelf_model/weights/best.pt'
    try:
        model = YOLO(model_path)
    except:
        st.error("Model weights not found. Please ensure training is complete.")
        return None

    # Simulation: Pick random image from test set
    test_dir = 'datasets/Retail Shelf Detection.v4i.yolov8/test/images'
    image_files = glob.glob(os.path.join(test_dir, '*.jpg'))
    if not image_files: return None

    test_image_path = random.choice(image_files)
    image_name = os.path.basename(test_image_path)
    
    results = model.predict(test_image_path, conf=0.25, verbose=False)
    result = results[0]

    product_count = 0
    empty_count = 0
    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = result.names[class_id]
        if class_name == 'Empty': empty_count += 1
        else: product_count += 1
    
    status = "RESTOCK_NEEDED" if empty_count > 0 else "OK"

    # Database Operation
    conn = sqlite3.connect("shelf_analytics.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS analysis_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, image_name TEXT, 
                       product_count INTEGER, empty_count INTEGER, status TEXT)''')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO analysis_logs (timestamp, image_name, product_count, empty_count, status) VALUES (?, ?, ?, ?, ?)",
                   (timestamp, image_name, product_count, empty_count, status))
    conn.commit()
    conn.close()

    # Save Processed Image
    output_dir = "runs/analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    annotated_frame = result.plot()
    processed_path = os.path.join(output_dir, f"processed_{timestamp.replace(':','-').replace(' ','_')}.jpg")
    cv2.imwrite(processed_path, annotated_frame)
    
    if status == "RESTOCK_NEEDED":
        trigger_alert(empty_count)
        st.toast(f"⚠️ Critical Stock Level! Notification sent to Manager.", icon="📲")
    
    return True

def fetch_logs():
    try:
        conn = sqlite3.connect("shelf_analytics.db")
        df = pd.read_sql_query("SELECT * FROM analysis_logs ORDER BY id DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# --- Layout Implementation ---

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=80)
    st.title("ShelfGuard AI")
    st.caption("Enterprise Edition v2.1")
    st.markdown("---")
    
    st.subheader("System Controls")
    if st.button("🚀 START NEW SCAN", type="primary"):
        with st.spinner("Analyzing shelf feed..."):
            run_analysis_pipeline()
            time.sleep(0.5)
        st.rerun()

    st.markdown("---")
    st.markdown("**Developed by Rabia Ceylan**")

st.markdown('<div class="main-title">🛒 Smart Shelf Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-Time Inventory Intelligence System</div>', unsafe_allow_html=True)

df = fetch_logs()
if df.empty:
    st.info("System Ready. Initiate a scan from the sidebar to begin.")
    st.stop()

latest = df.iloc[0]
total_items = latest['product_count'] + latest['empty_count']
fill_rate = (latest['product_count'] / total_items * 100) if total_items > 0 else 0

# Metrics
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Shelf Fill Rate", f"{fill_rate:.1f}%", delta="Target: 95%")
with c2: st.metric("Total Scans", len(df))
with c3: st.metric("Products Detected", latest['product_count'])
with c4: st.metric("Action Required", latest['status'], delta="- Critical" if latest['status']!="OK" else "Normal", delta_color="inverse")

st.divider()

# Tabs
tab1, tab2 = st.tabs(["🔴 Live Operation Center", "📈 Business Intelligence"])

with tab1:
    col_vis, col_details = st.columns([3, 1])
    
    with col_vis:
        output_dir = "runs/analysis_results"
        list_files = sorted(glob.glob(os.path.join(output_dir, 'processed_*.jpg')), key=os.path.getctime, reverse=True)
        if list_files:
            latest_img_path = list_files[0]
            st.image(latest_img_path, caption=f"Live Feed - {latest['timestamp']}", use_container_width=True)
            
            with open(latest_img_path, "rb") as img_file:
                pdf_bytes = generate_report(latest, latest_img_path)
                st.download_button(
                    label="📄 Download Inspection Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"report_{latest['id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
    with col_details:
        st.subheader("Current Status")
        if latest['status'] == "OK": st.success("✅ FULLY STOCKED")
        else: st.error(f"🚨 {latest['empty_count']} GAPS FOUND")
            
        st.markdown("**Detection Summary:**")
        st.write(f"- 📦 Products: **{latest['product_count']}**")
        st.write(f"- 🕳️ Empty Spots: **{latest['empty_count']}**")
        
        if latest['status'] != "OK":
             st.info("📲 Alert Sent to: **Store Manager**")

with tab2:
    st.subheader("Historical Trends")
    df['total'] = df['product_count'] + df['empty_count']
    df['fill_rate'] = (df['product_count'] / df['total'] * 100).fillna(0)
    chart_data = df[['timestamp', 'fill_rate']].set_index('timestamp').sort_index()
    st.line_chart(chart_data)
    st.dataframe(df, use_container_width=True, height=200)
