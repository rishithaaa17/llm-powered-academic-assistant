import streamlit as st
import requests
import pandas as pd
import json
import base64
import io
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from pages import (
    upload_study_material_page,
    generate_question_paper_page,
    evaluate_single_answer_page,
    evaluate_csv_page,
    score_summary_page,
    call_api
)

# Page configuration
st.set_page_config(
    page_title="📚 AI Question Paper Generator & Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: none;
    }
    
    .error-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
        border: none;
    }
    
    .info-box {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(78, 205, 196, 0.3);
        border: none;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        color: #2c3e50;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(254, 202, 87, 0.3);
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        color: #333;
    }
    
    .metric-container h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-container p {
        color: #666;
        margin: 0;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Status indicator */
    .status-connected {
        color: #00d4aa;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: rgba(0, 212, 170, 0.1);
        border: 2px solid #00d4aa;
    }
    
    .status-disconnected {
        color: #ff6b6b;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: rgba(255, 107, 107, 0.1);
        border: 2px solid #ff6b6b;
    }
    
    /* Feature card */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #667eea;
        transition: transform 0.3s ease;
        color: #333;
    }
    
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .feature-card p {
        color: #666;
        margin: 0;
        line-height: 1.5;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def show_toast(message: str, type: str = "success"):
    """Show a toast notification with enhanced styling"""
    if type == "success":
        st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
    elif type == "error":
        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
    elif type == "info":
        st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)
    elif type == "warning":
        st.markdown(f'<div class="warning-box">⚠️ {message}</div>', unsafe_allow_html=True)

def encode_file_to_base64(file_content: bytes) -> str:
    """Encode file content to base64"""
    return base64.b64encode(file_content).decode('utf-8')

def decode_base64_to_dataframe(base64_content: str) -> pd.DataFrame:
    """Decode base64 content to DataFrame"""
    decoded_content = base64.b64decode(base64_content)
    return pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))

def show_dashboard():
    """Show a dashboard with key metrics and quick actions"""
    st.markdown('<h2 class="main-header">📊 Dashboard</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3>📚 Study Material</h3>
            <p>Upload and process study content</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3>📝 Question Generation</h3>
            <p>AI-powered question paper creation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <h3>✅ Answer Evaluation</h3>
            <p>Intelligent answer assessment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-container">
            <h3>📈 Analytics</h3>
            <p>Performance insights and reports</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Upload Study Material", use_container_width=True):
            st.session_state['current_page'] = "📘 Upload Study Material"
            st.rerun()
    
    with col2:
        if st.button("📝 Generate Question Paper", use_container_width=True):
            st.session_state['current_page'] = "📝 Generate Question Paper"
            st.rerun()

def show_features():
    """Show features overview"""
    st.markdown('<h2 class="main-header">✨ Features Overview</h2>', unsafe_allow_html=True)
    
    features = [
        {
            "icon": "🤖",
            "title": "AI-Powered Generation",
            "description": "Generate comprehensive question papers using advanced LLM technology"
        },
        {
            "icon": "📊",
            "title": "Smart Evaluation",
            "description": "Evaluate student answers with detailed feedback and scoring"
        },
        {
            "icon": "📈",
            "title": "Analytics Dashboard",
            "description": "Visualize performance metrics and generate detailed reports"
        },
        {
            "icon": "🔄",
            "title": "Batch Processing",
            "description": "Process multiple evaluations efficiently with CSV support"
        }
    ]
    
    for feature in features:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{feature['icon']} {feature['title']}</h3>
            <p>{feature['description']}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application with enhanced UI"""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "🏠 Dashboard"
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>🎓 LLM System for Academic Question Generation & Evaluation</h2>
            <p style="color: #666;">Powered by DSPy & Llama3-70B</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📚 Navigation")
        pages = {
            "🏠 Dashboard": "dashboard",
            "📘 Upload Study Material": "upload",
            "📝 Generate Question Paper": "generate",
            "✅ Evaluate Single Answer": "evaluate",
            "📊 Evaluate from CSV": "csv_evaluate",
            "📈 Score Summary": "summary",
            "✨ Features": "features"
        }
        
        selected_page = st.selectbox(
            "Choose a page",
            list(pages.keys()),
            index=list(pages.keys()).index(st.session_state['current_page'])
        )
        
        # Update session state
        if selected_page != st.session_state['current_page']:
            st.session_state['current_page'] = selected_page
            st.rerun()
        
        st.markdown("---")
        
        # API Status with enhanced styling
        st.markdown("### 🔗 System Status")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                st.markdown('<div class="status-connected">🟢 Connected</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-disconnected">🔴 Disconnected</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="status-disconnected">🔴 Disconnected</div>', unsafe_allow_html=True)
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.markdown(f"**API URL:** {API_BASE_URL}")
        st.markdown("**Version:** 1.0.0")
        
        # Quick help
        with st.expander("❓ Quick Help"):
            st.markdown("""
            **Getting Started:**
            1. Upload study material
            2. Generate question paper
            3. Evaluate answers
            4. View analytics
            
            **Need Help?** Check the API docs at `/docs`
            """)
    
    # Main content area
    if st.session_state['current_page'] == "🏠 Dashboard":
        show_dashboard()
    elif st.session_state['current_page'] == "✨ Features":
        show_features()
    elif pages[st.session_state['current_page']] == "upload":
        upload_study_material_page()
    elif pages[st.session_state['current_page']] == "generate":
        generate_question_paper_page()
    elif pages[st.session_state['current_page']] == "evaluate":
        evaluate_single_answer_page()
    elif pages[st.session_state['current_page']] == "csv_evaluate":
        evaluate_csv_page()
    elif pages[st.session_state['current_page']] == "summary":
        score_summary_page()

if __name__ == "__main__":
    main() 