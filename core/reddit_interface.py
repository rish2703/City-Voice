"""
Reddit-like Public Interface
- User login/registration
- Feed of all complaints
- Upvote functionality
- Area filtering
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db import get_connection, insert_complaint
from database.user_auth import register_user, login_user, get_user_by_id
from database.upvotes import upvote_complaint, remove_upvote, get_upvote_count, has_user_upvoted, get_complaints_with_upvotes
from core.helpers import ALL_AREAS, CATEGORIES, assign_zone, get_complaint_timeline
from core.ui_theme import inject_global_styles, hero, badge, complaint_card_start, complaint_card_end, display_image_fixed

def render_reddit_interface():
    """Main Reddit-like interface renderer"""
    inject_global_styles()
    # Check if user is logged in
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        render_login_register()
    else:
        render_main_feed()

def render_login_register():
    """Render login/registration interface"""
    hero("🏛️ Community", "Login to upvote and track issues, or create an account to post new complaints.")
    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if login_button:
                if username and password:
                    # Strip whitespace
                    username = username.strip()
                    password = password.strip()
                    result = login_user(username, password)
                    if result["success"]:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = result["username"]
                        st.session_state.email = result["email"]
                        st.success(f"✅ Welcome back, {result['username']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("⚠️ Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_button = st.form_submit_button("Register", type="primary", use_container_width=True)
            
            if register_button:
                if username and email and password and confirm_password:
                    # Strip whitespace
                    username = username.strip()
                    email = email.strip()
                    password = password.strip()
                    confirm_password = confirm_password.strip()
                    
                    if password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        result = register_user(username, email, password)
                        if result["success"]:
                            st.success(f"✅ Account created! Please login.")
                            st.info("💡 Switch to Login tab to access your account")
                        else:
                            st.error(f"❌ {result['message']}")
                else:
                    st.error("⚠️ Please fill in all fields")

def render_main_feed():
    """Render the main Reddit-like feed"""
    # Enhanced header
    hero("🏛️ Community Feed", f"Welcome back, {st.session_state.username}! Browse issues, upvote what matters, and submit new complaints.")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.rerun()
    
    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📰 Community Feed", "➕ Submit Complaint"])
    
    with tab1:
        render_community_feed()
    
    with tab2:
        render_submit_complaint()

def render_community_feed():
    """Render the Reddit-like feed of complaints"""
    st.markdown("<div class='cv-title' style='font-size:1.35rem; margin-bottom:1rem;'>📰 All City Complaints</div>", unsafe_allow_html=True)
    
    # Filter options in a card
    st.markdown("<div class='cv-card' style='padding:1.25rem; margin-bottom:1.5rem;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; margin-bottom:0.75rem; font-size:0.95rem;'>🔍 Filter & Sort</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        area_filter = st.selectbox("📍 Filter by Area", ["All Areas"] + ALL_AREAS)
    with col2:
        category_filter = st.selectbox("🏷️ Filter by Category", ["All Categories"] + CATEGORIES)
    with col3:
        sort_by = st.selectbox("🔄 Sort by", ["Most Upvoted", "Newest", "Oldest"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Get complaints with upvotes
    complaints = get_complaints_with_upvotes(st.session_state.user_id)
    
    # Apply filters
    if area_filter != "All Areas":
        complaints = [c for c in complaints if c.get('location') == area_filter]
    if category_filter != "All Categories":
        complaints = [c for c in complaints if c.get('category') == category_filter]
    
    # Sort
    if sort_by == "Newest":
        complaints = sorted(complaints, key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == "Oldest":
        complaints = sorted(complaints, key=lambda x: x.get('created_at', ''))
    # Most Upvoted is already sorted by default
    
    # Display complaints
    if complaints:
        st.write(f"**Showing {len(complaints)} complaint(s)**")
        
        for complaint in complaints:
            render_complaint_card(complaint)
    else:
        st.info("No complaints found matching your filters.")

def render_complaint_card(complaint):
    """Render a single complaint card in Reddit style"""
    complaint_id = complaint['complaint_id']
    upvote_count = complaint.get('upvote_count', 0) or get_upvote_count(complaint_id)
    user_id = st.session_state.get('user_id')
    user_upvoted = complaint.get('user_upvoted', 0) == 1 or (has_user_upvoted(complaint_id, user_id) if user_id else False)

    status = complaint.get("status", "New")
    status_variant = "success" if status == "Resolved" else "warning" if status in ["In Progress", "Assigned", "Acknowledged"] else "info"
    priority = complaint.get("priority", "Medium")
    priority_variant = "danger" if priority == "High" else "warning" if priority == "Medium" else "success"
    
    # Card container
    complaint_card_start()
    col1, col2 = st.columns([1.2, 20])
    
    with col1:
        # Upvote section
        st.markdown("<div style='text-align:center; padding:0.5rem 0;'>", unsafe_allow_html=True)
        
        user_id = st.session_state.get('user_id')
        if user_id:
            upvote_emoji = "🔼" if user_upvoted else "⬆️"
            if st.button(upvote_emoji, key=f"upvote_{complaint_id}", help="Upvote this complaint", use_container_width=True):
                if user_upvoted:
                    result = remove_upvote(complaint_id, user_id)
                else:
                    result = upvote_complaint(complaint_id, user_id)
                
                if result["success"]:
                    st.rerun()
        else:
            st.button("⬆️", key=f"upvote_{complaint_id}", disabled=True, help="Login to upvote", use_container_width=True)
        
        # Upvote count with styling
        upvote_color = "#EF4444" if user_upvoted else "rgba(243,244,246,0.7)"
        st.markdown(
            f"<div style='text-align:center; margin-top:0.5rem;'>"
            f"<div style='font-weight:800; font-size:1.5rem; color:{upvote_color};'>{upvote_count}</div>"
            f"<div style='font-size:0.75rem; color:rgba(243,244,246,0.6); text-transform:uppercase; letter-spacing:0.05em;'>votes</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Title + badges row
        category = complaint.get('category', 'Other')
        location = complaint.get('location', 'Unknown')
        title_html = f"""
        <div style='display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; margin-bottom:0.75rem; flex-wrap:wrap;'>
            <div>
                <div style='font-weight:900; font-size:1.25rem; line-height:1.3; margin-bottom:0.25rem;'>
                    {category}
                </div>
                <div style='color:rgba(243,244,246,0.7); font-size:0.9rem;'>
                    📍 {location}
                </div>
            </div>
            <div style='display:flex; gap:0.5rem; flex-wrap:wrap; align-items:flex-start;'>
                {badge(f'📝 {status}', status_variant)}
                {badge(f'⚡ {priority}', priority_variant)}
            </div>
        </div>
        """
        st.markdown(title_html, unsafe_allow_html=True)
        
        # Metadata row
        col_meta1, col_meta2, col_meta3 = st.columns(3)
        with col_meta1:
            st.markdown(f"<div style='color:rgba(243,244,246,0.7); font-size:0.85rem;'>👤 <strong>{complaint.get('citizen_name', 'Anonymous')}</strong></div>", unsafe_allow_html=True)
        with col_meta2:
            created = complaint.get('created_at', '')
            if created:
                date_str = created[:10] if isinstance(created, str) else str(created)[:10]
                st.markdown(f"<div style='color:rgba(243,244,246,0.7); font-size:0.85rem;'>📅 {date_str}</div>", unsafe_allow_html=True)
        with col_meta3:
            zone = complaint.get('zone', 'Unknown')
            st.markdown(f"<div style='color:rgba(243,244,246,0.7); font-size:0.85rem;'>🗺️ {zone} Zone</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        
        # Complaint text
        complaint_text = complaint.get('complaint_text', '')
        st.markdown(f"<div style='color:rgba(243,244,246,0.9); line-height:1.7; font-size:0.95rem;'>{complaint_text}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        
        # View details button
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("📋 View Details", key=f"details_{complaint_id}", use_container_width=True):
                st.session_state[f"show_details_{complaint_id}"] = True
        
        # Show details if clicked
        if st.session_state.get(f"show_details_{complaint_id}", False):
            st.markdown("<div style='margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"**Zone:** {complaint.get('zone', 'Unknown')}")
                st.markdown(f"**Category:** {complaint.get('category', 'Other')}")
                if complaint.get('address'):
                    st.markdown(f"**Address:** {complaint.get('address')}")
            with col_d2:
                st.markdown(f"**Priority:** {complaint.get('priority', 'Medium')}")
                st.markdown(f"**Complaint ID:** #{complaint_id}")
                st.markdown(f"**Status:** {status}")
            
            # Timeline
            timeline = get_complaint_timeline(complaint_id)
            if timeline:
                st.markdown("---")
                st.markdown("**📅 Timeline:**")
                for event in timeline:
                    st.markdown(f"""
                    <div style='padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:8px; margin-bottom:0.5rem; border-left:3px solid var(--cv-primary);'>
                        <div style='font-weight:600; margin-bottom:0.25rem;'>{event['status']}</div>
                        <div style='color:rgba(243,244,246,0.8); font-size:0.9rem;'>{event['description']}</div>
                        <div style='color:rgba(243,244,246,0.6); font-size:0.85rem; margin-top:0.25rem;'>{event.get('details', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display image if available
                    if event.get('image_path') and os.path.exists(event['image_path']):
                        try:
                            from PIL import Image
                            img = Image.open(event['image_path'])
                            display_image_fixed(img, caption=f"📸 Update photo - {event['status']}", size="large")
                        except Exception as e:
                            st.warning(f"⚠️ Could not load image: {str(e)}")
            
            if st.button("✖️ Close Details", key=f"close_{complaint_id}", use_container_width=True):
                st.session_state[f"show_details_{complaint_id}"] = False
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    complaint_card_end()

def render_submit_complaint():
    """Render complaint submission form"""
    st.markdown("<div class='cv-title' style='font-size:1.35rem; margin-bottom:0.5rem;'>➕ Submit a New Complaint</div>", unsafe_allow_html=True)
    st.markdown("<p class='cv-subtitle' style='margin-bottom:1.5rem;'>Share your issue clearly — detailed descriptions help authorities resolve it faster.</p>", unsafe_allow_html=True)
    
    # Display success message if complaint was just submitted
    if st.session_state.get("last_complaint_id"):
        st.markdown("""
        <div class="cv-card" style="background:linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.1)); border-color:rgba(16,185,129,0.4);">
            <div style="text-align:center; padding:1rem;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">🎉</div>
                <div style="font-weight:800; font-size:1.25rem; margin-bottom:0.5rem;">Complaint Submitted Successfully!</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Complaint ID", f"#{st.session_state.last_complaint_id}")
        with col2:
            st.metric("Category", st.session_state.last_complaint_category)
        with col3:
            priority_color = "🔴" if st.session_state.last_complaint_is_urgent else "🟡"
            st.metric("Priority", f"{priority_color} {st.session_state.last_complaint_priority}")
        
        st.info(f"📍 Your complaint has been assigned to **{st.session_state.last_complaint_zone}** zone. View it in the Community Feed!")
        
        # Add delay button to clear message
        if st.button("➕ Submit Another Complaint", key="new_complaint_btn", use_container_width=True, type="primary"):
            st.session_state.last_complaint_id = None
            st.session_state.last_complaint_category = None
            st.session_state.last_complaint_priority = None
            st.session_state.last_complaint_is_urgent = None
            st.session_state.last_complaint_zone = None
            st.rerun()
    
    # Only show form if no recent submission
    if not st.session_state.get("last_complaint_id"):
        st.markdown("<div class='cv-card'>", unsafe_allow_html=True)
        with st.form("complaint_form", clear_on_submit=True):
            st.markdown("<div style='font-weight:700; font-size:1.1rem; margin-bottom:1rem;'>📋 Complaint Details</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                area = st.selectbox("📍 Select Area *", options=[""] + ALL_AREAS, help="Select the area where the issue is located")
            with col2:
                category = st.selectbox("🏷️ Select Category *", options=[""] + CATEGORIES, help="Select the category")
            
            address = st.text_input(
                "🏠 Enter Detailed Address *",
                placeholder="E.g., 123 Main Street, Apartment 4B, Near Park, Bangalore"
            )
            
            complaint_text = st.text_area(
                "📝 Describe your complaint *",
                height=150,
                placeholder="Provide a detailed description of the issue. Be specific about location, time, and impact..."
            )
            
            is_urgent = st.checkbox("🚨 Mark as Urgent", help="Check if this requires immediate attention")
            
            st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("📤 Submit Complaint", use_container_width=True, type="primary")
            
            if submitted:
                if not area or not category or not complaint_text or not address:
                    st.error("⚠️ Please fill in all required fields marked with (*)")
                else:
                    priority = "High" if is_urgent else "Medium"
                    zone = assign_zone(area)
                    
                    with st.spinner("🔄 Submitting your complaint..."):
                        try:
                            complaint_id = insert_complaint(
                                name=st.session_state.username,
                                location=area,
                                original_text=complaint_text,
                                clean_text=complaint_text,
                                category=category,
                                priority=priority,
                                zone=zone,
                                ai_summary=None,
                                priority_reasoning="Marked as urgent by user" if is_urgent else "Standard priority",
                                is_ai_processed=False,
                                address=address
                            )
                            
                            if complaint_id:
                                # Store in session state to persist message
                                st.session_state.last_complaint_id = complaint_id
                                st.session_state.last_complaint_category = category
                                st.session_state.last_complaint_priority = priority
                                st.session_state.last_complaint_is_urgent = is_urgent
                                st.session_state.last_complaint_zone = zone
                                st.rerun()
                            else:
                                st.error("❌ Failed to submit complaint. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error submitting complaint: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

