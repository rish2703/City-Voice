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

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db import get_connection, update_status, log_action
from core.helpers import ZONE_AUTHORITIES, fetch_complaints_by_zone

logger = logging.getLogger(__name__)

def render_authority_interface():
    """Render the authority panel interface"""
    # Authentication check
    if not st.session_state.authenticated:
        render_authority_login()
    else:
        render_authority_dashboard()

def render_authority_login():
    """Render the authority login form"""
    st.warning("🔐 Please authenticate to access the authority panel")
    
    with st.form("login_form"):
        st.subheader("Authority Login")
        selected_zone = st.selectbox("Select Your Zone", ["North", "South", "East", "West", "Admin"])
        password = st.text_input("Enter Password", type="password")
        login_button = st.form_submit_button("Login", type="primary")
        
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

def render_authority_dashboard():
    """Render the authenticated authority dashboard"""
    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🛠️ Authority Panel")
        st.success(f"✅ Logged in as: **{st.session_state.officer_name}** ({st.session_state.assigned_zone} Zone)")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_mode = None
            st.session_state.authenticated = False
            st.session_state.assigned_zone = None
            st.session_state.officer_name = None
            st.rerun()
    
    st.markdown("---")
    
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
    st.header(f"📊 Statistics Dashboard - {st.session_state.assigned_zone} Zone")
    
    if not df.empty:
        st.subheader("📈 Overall Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Complaints", len(df))
        with col2:
            st.metric("🔴 High Priority", len(df[df["priority"] == "High"]))
        with col3:
            st.metric("⏳ Pending", len(df[df["status"] != "Resolved"]))
        with col4:
            st.metric("✅ Resolved", len(df[df["status"] == "Resolved"]))
        with col5:
            st.metric("🔄 In Progress", len(df[df["status"] == "In Progress"]))
        
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
    st.header("✏️ Update Complaint Status")
    st.write(f"Select and update complaints from **{st.session_state.assigned_zone}** zone.")
    
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
                st.subheader(f"📋 Complaint Details - ID: #{selected_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**👤 Citizen Name:** {selected_row['citizen_name']}")
                    st.write(f"**📍 Location:** {selected_row['location']}")
                    st.write(f"**🗺️ Zone:** {selected_row['zone']}")
                    st.write(f"**📅 Submitted:** {selected_row['created_at']}")
                with col2:
                    st.write(f"**🏷️ Category:** {selected_row['category']}")
                    priority_emoji = "🔴" if selected_row['priority'] == "High" else "🟡" if selected_row['priority'] == "Medium" else "🟢"
                    st.write(f"**⚡ Priority:** {priority_emoji} {selected_row['priority']}")
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
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        officer_id = st.number_input("Officer ID *", min_value=1, value=1)
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
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"complaint_{selected_id}_{timestamp}.{uploaded_image.name.split('.')[-1]}"
                        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(image, caption="Uploaded Image Preview", use_container_width=True)
                        with col2:
                            st.write("**Image Details:**")
                            st.write(f"Filename: {uploaded_image.name}")
                            st.write(f"Size: {uploaded_image.size / 1024:.2f} KB")
                    
                    submitted = st.form_submit_button("✅ Submit Update", type="primary", use_container_width=True)
                    
                    if submitted:
                        if not action_text:
                            st.error("⚠️ Please provide an action description")
                        else:
                            try:
                                update_status(selected_id, new_status, image_path)
                                action_description = f"{action_text}"
                                if officer_name:
                                    action_description += f" (Officer: {officer_name})"
                                log_action(selected_id, officer_id, action_description)
                                st.success("✅ Complaint status updated successfully!")
                                st.balloons()
                                st.info(f"📝 Status updated to: **{new_status}** | 📸 Photo: {'Uploaded' if image_path else 'Not provided'}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error updating complaint: {str(e)}")
                
                if selected_row.get('photo_after') and os.path.exists(selected_row['photo_after']):
                    st.markdown("---")
                    st.subheader("📷 Existing Resolution Photo")
                    st.image(selected_row['photo_after'], caption="Current resolution photo", use_container_width=True)
        else:
            st.warning("No complaints match the selected filters.")
    else:
        st.info(f"No complaints found for {st.session_state.assigned_zone} zone.")

