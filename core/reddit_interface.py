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

def render_reddit_interface():
    """Main Reddit-like interface renderer"""
    # Check if user is logged in
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        render_login_register()
    else:
        render_main_feed()

def render_login_register():
    """Render login/registration interface"""
    st.title("🏛️ City Voice - Community Platform")
    st.markdown("### Join the community to report and track city issues")
    st.markdown("---")
    
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
    # Header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏛️ City Voice - Community Feed")
    with col2:
        st.write(f"👤 **{st.session_state.username}**")
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.rerun()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📰 Community Feed", "➕ Submit Complaint"])
    
    with tab1:
        render_community_feed()
    
    with tab2:
        render_submit_complaint()

def render_community_feed():
    """Render the Reddit-like feed of complaints"""
    st.header("📰 All City Complaints")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        area_filter = st.selectbox("Filter by Area", ["All Areas"] + ALL_AREAS)
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All Categories"] + CATEGORIES)
    with col3:
        sort_by = st.selectbox("Sort by", ["Most Upvoted", "Newest", "Oldest"])
    
    st.markdown("---")
    
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
    
    # Card container
    with st.container():
        col1, col2 = st.columns([1, 20])
        
        with col1:
            # Upvote button
            upvote_emoji = "🔼" if user_upvoted else "⬆️"
            upvote_color = "red" if user_upvoted else "gray"
            
            user_id = st.session_state.get('user_id')
            if user_id:
                if st.button(upvote_emoji, key=f"upvote_{complaint_id}", help="Upvote this complaint"):
                    if user_upvoted:
                        result = remove_upvote(complaint_id, user_id)
                    else:
                        result = upvote_complaint(complaint_id, user_id)
                    
                    if result["success"]:
                        st.rerun()
            else:
                st.button("⬆️", key=f"upvote_{complaint_id}", disabled=True, help="Login to upvote")
            
            # Upvote count
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: {upvote_color};'>{upvote_count}</div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; font-size: 0.8em;'>votes</div>", unsafe_allow_html=True)
        
        with col2:
            # Complaint content
            st.markdown(f"### {complaint.get('category', 'Other')} - {complaint.get('location', 'Unknown')}")
            
            # Metadata
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.caption(f"👤 {complaint.get('citizen_name', 'Anonymous')}")
            with col_meta2:
                priority_emoji = "🔴" if complaint.get('priority') == "High" else "🟡" if complaint.get('priority') == "Medium" else "🟢"
                st.caption(f"{priority_emoji} {complaint.get('priority', 'Medium')}")
            with col_meta3:
                created = complaint.get('created_at', '')
                if created:
                    if isinstance(created, str):
                        st.caption(f"📅 {created[:10]}")
                    else:
                        st.caption(f"📅 {created}")
            
            # Complaint text
            st.markdown(f"**{complaint.get('complaint_text', '')}**")
            
            # Status badge
            status = complaint.get('status', 'New')
            if status == "Resolved":
                st.success(f"✅ Status: {status}")
            elif status in ["In Progress", "Assigned"]:
                st.warning(f"⏳ Status: {status}")
            else:
                st.info(f"📝 Status: {status}")
            
            # View details button
            if st.button("View Details", key=f"details_{complaint_id}"):
                st.session_state[f"show_details_{complaint_id}"] = True
            
            # Show details if clicked
            if st.session_state.get(f"show_details_{complaint_id}", False):
                with st.expander("📋 Full Details", expanded=True):
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.write(f"**Zone:** {complaint.get('zone', 'Unknown')}")
                        st.write(f"**Category:** {complaint.get('category', 'Other')}")
                    with col_d2:
                        st.write(f"**Priority:** {complaint.get('priority', 'Medium')}")
                        st.write(f"**Complaint ID:** #{complaint_id}")
                    
                    # Timeline
                    timeline = get_complaint_timeline(complaint_id)
                    if timeline:
                        st.markdown("**Timeline:**")
                        for event in timeline:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.caption(f"• {event['status']}: {event['description']}")
                                st.caption(f"  {event['details']}")
                            with col2:
                                if event.get('date'):
                                    date_str = str(event['date'])[:10] if isinstance(event['date'], str) else str(event['date'])[:10]
                                    st.caption(f"📅 {date_str}")
                            
                            # Display image if available
                            if event.get('image_path') and os.path.exists(event['image_path']):
                                try:
                                    from PIL import Image
                                    img = Image.open(event['image_path'])
                                    st.image(img, caption=f"📸 Update photo - {event['status']}", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"⚠️ Could not load image: {str(e)}")
                    
                    if st.button("Close Details", key=f"close_{complaint_id}"):
                        st.session_state[f"show_details_{complaint_id}"] = False
                        st.rerun()
        
        st.markdown("---")

def render_submit_complaint():
    """Render complaint submission form"""
    st.header("➕ Submit a New Complaint")
    st.write("Share your city issue with the community")
    
    # Display success message if complaint was just submitted
    if st.session_state.get("last_complaint_id"):
        st.success(f"✅ Complaint submitted successfully!")
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
        if st.button("Submit Another Complaint", key="new_complaint_btn"):
            st.session_state.last_complaint_id = None
            st.session_state.last_complaint_category = None
            st.session_state.last_complaint_priority = None
            st.session_state.last_complaint_is_urgent = None
            st.session_state.last_complaint_zone = None
            st.rerun()
    
    # Only show form if no recent submission
    if not st.session_state.get("last_complaint_id"):
        with st.form("complaint_form", clear_on_submit=True):
            st.subheader("📋 Complaint Details")
            
            col1, col2 = st.columns(2)
            with col1:
                area = st.selectbox("Select Area *", options=[""] + ALL_AREAS, help="Select the area where the issue is located")
            with col2:
                category = st.selectbox("Select Category *", options=[""] + CATEGORIES, help="Select the category")
            
            address = st.text_input(
                "Enter Detailed Address *",
                placeholder="E.g., 123 Main Street, Apartment 4B, Near Park, Bangalore"
            )
            
            complaint_text = st.text_area(
                "Describe your complaint *",
                height=150,
                placeholder="Provide a detailed description of the issue. Be specific about location, time, and impact..."
            )
            
            is_urgent = st.checkbox("🚨 Mark as Urgent", help="Check if this requires immediate attention")
            
            st.markdown("---")
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

