"""
Unified City Voice Application - Main Entry Point
Single website with 2 authentication modes:
  1. Public User Mode (for citizens)
  2. Authority Mode (for officials)
"""

import streamlit as st
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.reddit_interface import render_reddit_interface
from core.authority_interface import render_authority_interface

# Page configuration
st.set_page_config(page_title="City Voice", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
if "user_mode" not in st.session_state:
    st.session_state.user_mode = None  # None, "public", or "authority"
    st.session_state.authenticated = False
    st.session_state.assigned_zone = None
    st.session_state.officer_name = None

def render_landing_page():
    """Render the landing page with mode selection"""
    st.title("🏛️ City Voice")
    st.markdown("### Your Voice Matters - Complaint Management System")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='padding: 30px; border: 2px solid #1f77b4; border-radius: 10px; text-align: center; height: 100%;'>
            <h2>👤 Public User</h2>
            <p>Submit complaints and track their status</p>
            <ul style='text-align: left;'>
                <li>Login/Register as individual user</li>
                <li>View all city complaints in feed</li>
                <li>Upvote complaints you agree with</li>
                <li>Filter by area and category</li>
                <li>Submit your own complaints</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter as Public User", key="public_btn", use_container_width=True, type="primary"):
            st.session_state.user_mode = "public"
            st.session_state.authenticated = True
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style='padding: 30px; border: 2px solid #e74c3c; border-radius: 10px; text-align: center; height: 100%;'>
            <h2>🛠️ Authority</h2>
            <p>Manage complaints and view statistics</p>
            <ul style='text-align: left;'>
                <li>Update complaint status</li>
                <li>Upload resolution photos</li>
                <li>View statistics dashboard</li>
                <li>Category-wise analysis</li>
                <li>Zone-based management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enter as Authority", key="authority_btn", use_container_width=True, type="primary"):
            st.session_state.user_mode = "authority"
            st.rerun()
    
    st.markdown("---")
    st.info("💡 **Select your mode above to continue**")

# ==========================================
# LANDING PAGE / MODE SELECTION
# ==========================================
if st.session_state.user_mode is None:
    render_landing_page()

# ==========================================
# PUBLIC USER MODE (Reddit-like Interface)
# ==========================================
elif st.session_state.user_mode == "public":
    render_reddit_interface()

# ==========================================
# AUTHORITY MODE
# ==========================================
elif st.session_state.user_mode == "authority":
    render_authority_interface()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🏛️ City Voice - Your Voice Matters</p>
    <p>For support, contact: support@cityvoice.gov.in</p>
</div>
""", unsafe_allow_html=True)
