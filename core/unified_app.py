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

from core.ui_theme import inject_global_styles, hero, feature_card
from core.reddit_interface import render_reddit_interface
from core.authority_interface import render_authority_interface

# Page configuration
st.set_page_config(page_title="City Voice", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# Global presentation theme
inject_global_styles()

# Initialize session state
if "user_mode" not in st.session_state:
    st.session_state.user_mode = None  # None, "public", or "authority"
    st.session_state.authenticated = False
    st.session_state.assigned_zone = None
    st.session_state.officer_name = None

def render_landing_page():
    """Render the landing page with mode selection"""
    hero("🏛️ City Voice", "A modern, citizen-first platform to report issues and track resolution — built for transparency and efficiency.")
    
    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    
    # Stats row
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <div style="font-size:2rem; font-weight:800; color:#3B82F6;">🏛️</div>
            <div style="color:rgba(243,244,246,0.7); font-size:0.9rem; margin-top:0.5rem;">Citizen Platform</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <div style="font-size:2rem; font-weight:800; color:#10B981;">📊</div>
            <div style="color:rgba(243,244,246,0.7); font-size:0.9rem; margin-top:0.5rem;">Real-time Tracking</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <div style="font-size:2rem; font-weight:800; color:#F59E0B;">⚡</div>
            <div style="color:rgba(243,244,246,0.7); font-size:0.9rem; margin-top:0.5rem;">Fast Resolution</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat4:
        st.markdown("""
        <div style="text-align:center; padding:1rem;">
            <div style="font-size:2rem; font-weight:800; color:#8B5CF6;">🔒</div>
            <div style="color:rgba(243,244,246,0.7); font-size:0.9rem; margin-top:0.5rem;">Secure & Transparent</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        feature_card(
            "👤",
            "Public User",
            "Submit complaints, follow progress, and support issues via upvotes.",
            [
                "✨ Quick login/register in seconds",
                "📰 Browse a clean community feed",
                "👍 Upvote & filter by area/category",
                "📝 Submit new complaints with detailed address",
                "📸 View timeline updates & resolution photos"
            ]
        )
        
        if st.button("🚀 Enter as Public User", key="public_btn", use_container_width=True, type="primary"):
            st.session_state.user_mode = "public"
            st.session_state.authenticated = True
            st.rerun()
    
    with col2:
        feature_card(
            "🛠️",
            "Authority",
            "Review, prioritize, and resolve issues with traceable updates.",
            [
                "🗺️ Zone-based access (North/South/East/West/Admin)",
                "📊 Dashboard with metrics & distributions",
                "🔍 Filter, open complaints, update status",
                "📷 Upload resolution photos",
                "📋 Complete action logging for auditability"
            ]
        )
        
        if st.button("🔐 Enter as Authority", key="authority_btn", use_container_width=True, type="primary"):
            st.session_state.user_mode = "authority"
            st.rerun()

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
<div style='text-align: center; color: rgba(229,231,235,0.65); padding: 20px;'>
    <p style="margin:0;">🏛️ City Voice</p>
    <p style="margin:0.35rem 0 0 0; font-size: 0.95rem;">Your voice matters • support@cityvoice.gov.in</p>
</div>
""", unsafe_allow_html=True)
