"""
Authority Panel Interface Module
Handles statistics dashboard and status updates for officials
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from PIL import Image
from datetime import datetime
import logging
import io

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db import get_connection, update_status, log_action
from core.helpers import ZONE_AUTHORITIES, fetch_complaints_by_zone
from core.ui_theme import inject_global_styles, hero, badge, display_image_fixed

logger = logging.getLogger(__name__)

def optimize_image(image, max_width=1280, max_height=720, quality=85):
    """
    Optimize image by resizing and compressing while maintaining aspect ratio
    
    Args:
        image: PIL Image object
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100, default 85)
    
    Returns:
        Optimized PIL Image object
    """
    # Calculate aspect ratio
    aspect_ratio = image.width / image.height
    
    # Determine new dimensions while maintaining aspect ratio
    if image.width > max_width or image.height > max_height:
        if aspect_ratio > max_width / max_height:
            # Width is the limiting factor
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            # Height is the limiting factor
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image

def render_authority_interface():
    """Render the authority panel interface"""
    inject_global_styles()
    # Authentication check
    if not st.session_state.authenticated:
        render_authority_login()
    else:
        render_authority_dashboard()

def render_authority_login():
    """Render the authority login form"""
    hero("🔐 Authority Login", "Access the dashboard to manage complaints, view statistics, and update status.")
    
    st.markdown("<div class='cv-card' style='max-width:500px; margin:0 auto;'>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<div style='font-weight:700; font-size:1.1rem; margin-bottom:1rem;'>Enter Your Credentials</div>", unsafe_allow_html=True)
        selected_zone = st.selectbox("🗺️ Select Your Zone", ["North", "South", "East", "West", "Admin"])
        password = st.text_input("🔑 Enter Password", type="password", placeholder="Enter your zone password")
        login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
        
        if login_button:
            if password == ZONE_AUTHORITIES[selected_zone]["password"]:
                st.session_state.authenticated = True
                st.session_state.assigned_zone = selected_zone
                st.session_state.officer_name = ZONE_AUTHORITIES[selected_zone]["officer_name"]
                logger.info(f"Authority logged in for zone: {selected_zone}")
                st.success(f"✅ Welcome, {st.session_state.officer_name}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
                logger.warning(f"Failed login attempt for zone: {selected_zone}")
    st.markdown("</div>", unsafe_allow_html=True)

def render_authority_dashboard():
    """Render the authenticated authority dashboard"""
    # Enhanced header
    hero(f"🛠️ Authority Dashboard", f"Welcome, {st.session_state.officer_name} • {st.session_state.assigned_zone} Zone")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_mode = None
            st.session_state.authenticated = False
            st.session_state.assigned_zone = None
            st.session_state.officer_name = None
            st.rerun()
    
    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)
    
    # Create tabs for authority
    tab1, tab2 = st.tabs(["📊 Statistics Dashboard", "✏️ Update Status"])
    
    df = fetch_complaints_by_zone(st.session_state.assigned_zone)
    
    # TAB 1: STATISTICS
    with tab1:
        render_statistics_dashboard(df)
    
    # TAB 2: UPDATE STATUS
    with tab2:
        render_update_status(df)

def render_statistics_dashboard(df):
    """Render the statistics dashboard"""
    st.markdown(
        f"<div class='cv-title' style='font-size:1.2rem;'>📊 Statistics — {st.session_state.assigned_zone} Zone</div>",
        unsafe_allow_html=True,
    )
    
    if not df.empty:
        st.subheader("📈 Overall Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("High Priority", len(df[df["priority"] == "High"]))
        with col3:
            st.metric("Pending", len(df[df["status"] != "Resolved"]))
        with col4:
            st.metric("Resolved", len(df[df["status"] == "Resolved"]))
        with col5:
            st.metric("In Progress", len(df[df["status"] == "In Progress"]))
        
        st.markdown("---")
        st.subheader("📋 Statistics by Category")
        
        df['category'] = df['category'].fillna("Other")
        category_counts = df['category'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Complaints by Category**")
            if not category_counts.empty:
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                category_counts.plot(kind='bar', ax=ax1, color='steelblue')
                ax1.set_xlabel('Category', fontsize=12)
                ax1.set_ylabel('Number of Complaints', fontsize=12)
                ax1.set_title('Complaints Distribution by Category', fontsize=14, fontweight='bold')
                ax1.tick_params(axis='x', rotation=45)
                plt.tight_layout()
                st.pyplot(fig1)
        
        with col2:
            st.write("**Category Breakdown Table**")
            category_stats = pd.DataFrame({
                'Category': category_counts.index,
                'Count': category_counts.values,
                'Percentage': (category_counts.values / len(df) * 100).round(1)
            })
            category_stats['Percentage'] = category_stats['Percentage'].astype(str) + '%'
            st.dataframe(category_stats, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📊 Status Distribution")
        
        col1, col2 = st.columns(2)
        with col1:
            status_counts = df['status'].value_counts()
            st.write("**Complaints by Status**")
            if not status_counts.empty:
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                status_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=90)
                ax2.set_ylabel('')
                ax2.set_title('Status Distribution', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig2)
        
        with col2:
            st.write("**Priority Distribution**")
            priority_counts = df['priority'].value_counts()
            if not priority_counts.empty:
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                colors = {'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#27ae60'}
                priority_colors = [colors.get(p, '#95a5a6') for p in priority_counts.index]
                priority_counts.plot(kind='bar', ax=ax3, color=priority_colors)
                ax3.set_xlabel('Priority', fontsize=12)
                ax3.set_ylabel('Number of Complaints', fontsize=12)
                ax3.set_title('Priority Distribution', fontsize=14, fontweight='bold')
                ax3.tick_params(axis='x', rotation=0)
                plt.tight_layout()
                st.pyplot(fig3)
        
        st.markdown("---")
        st.subheader("🔍 Category vs Status Analysis")
        if 'category' in df.columns and 'status' in df.columns:
            pivot_table = pd.crosstab(df['category'], df['status'], margins=True)
            st.dataframe(pivot_table, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Recent Complaints")
        recent_df = df[['complaint_id', 'citizen_name', 'location', 'category', 'priority', 'status', 'created_at']].head(20)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"No complaints found for {st.session_state.assigned_zone} zone.")

def render_update_status(df):
    """Render the status update interface"""
    st.markdown("<div class='cv-title' style='font-size:1.2rem;'>✏️ Update Complaint Status</div>", unsafe_allow_html=True)
    st.caption(f"Select a complaint from the {st.session_state.assigned_zone} zone and log a clear action taken.")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
        with col2:
            priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df['priority'].unique()))
        
        filtered_df = df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
        
        if not filtered_df.empty:
            complaint_ids = filtered_df["complaint_id"].tolist()
            selected_id = st.selectbox(
                "Select Complaint ID to Update",
                complaint_ids,
                format_func=lambda x: f"#{x} - {filtered_df[filtered_df['complaint_id']==x].iloc[0]['category']} - {filtered_df[filtered_df['complaint_id']==x].iloc[0]['status']}"
            )
            
            if selected_id:
                selected_row = df[df["complaint_id"] == selected_id].iloc[0]
                
                st.markdown("---")
                status = str(selected_row.get("status", "New"))
                priority = str(selected_row.get("priority", "Medium"))
                status_variant = "success" if status == "Resolved" else "warning" if status in ["In Progress", "Assigned", "Acknowledged"] else "info"
                priority_variant = "danger" if priority == "High" else "warning" if priority == "Medium" else "success"

                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:flex-start; gap:0.75rem;'>"
                    f"<div class='cv-title' style='font-size:1.05rem;'>📋 Complaint #{selected_id}</div>"
                    f"<div style='display:flex; gap:0.4rem; flex-wrap:wrap;'>"
                    f"{badge(f'📝 {status}', status_variant)}"
                    f"{badge(f'⚡ {priority}', priority_variant)}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**👤 Citizen Name:** {selected_row['citizen_name']}")
                    st.write(f"**📍 Location:** {selected_row['location']}")
                    st.write(f"**🗺️ Zone:** {selected_row['zone']}")
                    st.write(f"**📅 Submitted:** {selected_row['created_at']}")
                with col2:
                    st.write(f"**🏷️ Category:** {selected_row['category']}")
                    st.write(f"**📝 Current Status:** {selected_row['status']}")
                
                st.markdown("---")
                st.write(f"**📝 Description:**")
                st.info(selected_row['complaint_text'])
                
                st.markdown("---")
                st.subheader("✏️ Update Status")
                
                with st.form("update_status_form"):
                    status_options = ["New", "Acknowledged", "Assigned", "In Progress", "Resolved", "Closed"]
                    current_status_index = status_options.index(selected_row['status']) if selected_row['status'] in status_options else 0
                    new_status = st.selectbox("Update Status *", status_options, index=current_status_index)
                    
                    # Auto-assign officer_id based on zone
                    zone_to_officer_id = {
                        "North": 1,
                        "South": 2,
                        "East": 3,
                        "West": 4,
                        "Admin": 5
                    }
                    officer_id = zone_to_officer_id.get(st.session_state.assigned_zone, 1)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📛 Officer ID: {officer_id} ({st.session_state.assigned_zone} Zone)")
                    with col2:
                        officer_name = st.text_input("Officer Name (Optional)", placeholder="Enter officer name")
                    
                    action_text = st.text_area("Action Description *", height=100, placeholder="Describe the action taken...")
                    uploaded_image = st.file_uploader("Upload Resolution Photo (Optional)", type=["jpg", "jpeg", "png"])
                    
                    image_path = None
                    UPLOAD_FOLDER = "uploads"
                    if not os.path.exists(UPLOAD_FOLDER):
                        os.makedirs(UPLOAD_FOLDER)
                    
                    if uploaded_image is not None:
                        image = Image.open(uploaded_image)
                        # Optimize image for display and storage
                        optimized_image = optimize_image(image)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"complaint_{selected_id}_{timestamp}.{uploaded_image.name.split('.')[-1]}"
                        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            display_image_fixed(optimized_image, caption="Uploaded Image Preview", size="small")
                        with col2:
                            st.write("**Image Details:**")
                            st.write(f"Original: {image.width}x{image.height}px")
                            st.write(f"Optimized: {optimized_image.width}x{optimized_image.height}px")
                            st.write(f"File: {uploaded_image.name}")
                            st.write(f"Original Size: {uploaded_image.size / 1024:.2f} KB")
                    
                    submitted = st.form_submit_button("✅ Submit Update", type="primary", use_container_width=True)
                    
                    if submitted:
                        if not action_text:
                            st.error("⚠️ Please provide an action description")
                        else:
                            try:
                                # Initialize image_path as None
                                image_path = None
                                UPLOAD_FOLDER = "uploads"
                                
                                # Save image if provided
                                if uploaded_image is not None:
                                    if not os.path.exists(UPLOAD_FOLDER):
                                        os.makedirs(UPLOAD_FOLDER)
                                    
                                    image = Image.open(uploaded_image)
                                    # Optimize image before saving
                                    optimized_image = optimize_image(image)
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    image_filename = f"complaint_{selected_id}_{timestamp}.{uploaded_image.name.split('.')[-1]}"
                                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                                    
                                    # Convert RGBA to RGB if necessary (for JPEG compatibility)
                                    if optimized_image.mode in ('RGBA', 'LA', 'P'):
                                        rgb_image = Image.new('RGB', optimized_image.size, (255, 255, 255))
                                        rgb_image.paste(optimized_image, mask=optimized_image.split()[-1] if optimized_image.mode == 'RGBA' else None)
                                        optimized_image = rgb_image
                                    
                                    # Save with compression
                                    optimized_image.save(image_path, quality=85, optimize=True)
                                
                                update_status(selected_id, new_status, image_path)
                                action_description = f"{action_text}"
                                if officer_name:
                                    action_description += f" (Officer: {officer_name})"
                                log_action(selected_id, officer_id, action_description, image_path)
                                st.success("✅ Complaint status updated successfully!")
                                st.balloons()
                                st.info(f"📝 Status updated to: **{new_status}** | 📸 Photo: {'Uploaded' if image_path else 'Not provided'}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error updating complaint: {str(e)}")
                
                if selected_row.get('photo_after') and os.path.exists(selected_row['photo_after']):
                    st.markdown("---")
                    st.subheader("📷 Existing Resolution Photo")
                    try:
                        existing_image = Image.open(selected_row['photo_after'])
                        display_image_fixed(existing_image, caption="Current resolution photo", size="medium")
                    except Exception as e:
                        st.warning(f"⚠️ Could not load image: {str(e)}")
        else:
            st.warning("No complaints match the selected filters.")
    else:
        st.info(f"No complaints found for {st.session_state.assigned_zone} zone.")

