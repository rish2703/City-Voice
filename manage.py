import streamlit as st
import pandas as pd
import os
from PIL import Image
import logging

from db import get_connection, update_status, log_action

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Zone authority mapping - maps zones to authorized users
ZONE_AUTHORITIES = {
    "North": {"password": "north_auth_123", "officer_name": "North Zone Authority"},
    "South": {"password": "south_auth_123", "officer_name": "South Zone Authority"},
    "East": {"password": "east_auth_123", "officer_name": "East Zone Authority"},
    "West": {"password": "west_auth_123", "officer_name": "West Zone Authority"},
    "Admin": {"password": "admin_123", "officer_name": "System Admin"}
}

st.set_page_config(page_title="Complaint Management Panel", page_icon="🛠", layout="wide")
st.title("🛠 Complaint Management Panel")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.assigned_zone = None
    st.session_state.officer_name = None

# Authentication Section
if not st.session_state.authenticated:
    st.warning("🔐 Please authenticate to access the dashboard")
    
    with st.form("login_form"):
        st.subheader("Authority Login")
        selected_zone = st.selectbox("Select Your Zone", ["North", "South", "East", "West", "Admin"])
        password = st.text_input("Enter Password", type="password")
        login_button = st.form_submit_button("Login")
        
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

# Main Dashboard (only shown if authenticated)
else:
    st.success(f"✅ Logged in as: {st.session_state.officer_name} ({st.session_state.assigned_zone})")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.assigned_zone = None
            st.session_state.officer_name = None
            logger.info(f"Authority logged out from zone: {st.session_state.assigned_zone}")
            st.rerun()
    
    st.write(f"Select complaints from **{st.session_state.assigned_zone}** zone and update their status.")
    
    # Fetch complaints based on zone
    def fetch_complaints_by_zone(zone):
        conn = get_connection()
        if conn:
            if zone == "Admin":
                # Admin sees all complaints from all zones
                query = "SELECT * FROM complaints ORDER BY priority DESC, created_at DESC"
                logger.info("Admin fetching all complaints")
            else:
                # Zone authority only sees complaints from their zone
                query = f"SELECT * FROM complaints WHERE zone = '{zone}' ORDER BY priority DESC, created_at DESC"
                logger.info(f"Fetching complaints for zone: {zone}")
            
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        return pd.DataFrame()
    
    df = fetch_complaints_by_zone(st.session_state.assigned_zone)
    
    # Show statistics
    st.subheader(f"📊 {st.session_state.assigned_zone} Zone - Complaint Statistics")
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(df)
            st.metric("Total Complaints", total)
        
        with col2:
            high_priority = len(df[df["priority"] == "High"])
            st.metric("🔴 High Priority", high_priority)
        
        with col3:
            pending = len(df[df["status"] != "Resolved"])
            st.metric("⏳ Pending", pending)
        
        with col4:
            resolved = len(df[df["status"] == "Resolved"])
            st.metric("✅ Resolved", resolved)
    
    # Show complaint list
    st.subheader(f"All Complaints - {st.session_state.assigned_zone} Zone")
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info(f"No complaints found for {st.session_state.assigned_zone} zone.")
    
    # Status choices
    status_options = ["New", "Acknowledged", "Assigned", "In Progress", "Resolved", "Closed"]
    
    # Select complaint ID
    if not df.empty:
        complaint_ids = df["complaint_id"].tolist()
        selected_id = st.selectbox("Select Complaint ID to Update", complaint_ids)
        
        if selected_id:
            selected_row = df[df["complaint_id"] == selected_id].iloc[0]
        
            st.write("### Complaint Details")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Complaint ID:** {selected_row['complaint_id']}")
                st.write(f"**Name:** {selected_row['citizen_name']}")
                st.write(f"**Location:** {selected_row['location']}")
                st.write(f"**Zone:** {selected_row['zone']}")
            
            with col2:
                st.write(f"**Category:** {selected_row['category']}")
                st.write(f"**Priority:** {selected_row['priority']}")
                st.write(f"**Current Status:** {selected_row['status']}")
            
            st.write(f"**Complaint Text:** {selected_row['complaint_text']}")
        
            # New status
            new_status = st.selectbox("Update Status", status_options, index=status_options.index(selected_row['status']))
        
            # Officer
            officer_id = st.number_input("Officer ID", min_value=1, value=1)
        
            # Action description
            action_text = st.text_input("Action Description")
        
            # ⭐ FILE UPLOADER HERE ⭐
            uploaded_image = st.file_uploader("Upload Proof Photo (optional)", type=["jpg", "jpeg", "png"])
        
            image_path = None
        
            # Create uploads folder if not present
            UPLOAD_FOLDER = "uploads"
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
        
            # Save the image if uploaded
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                image_path = os.path.join(UPLOAD_FOLDER, uploaded_image.name)
                image.save(image_path)
                st.image(image, caption="Uploaded Image Preview", use_column_width=True)
                logger.info(f"Image uploaded for complaint {selected_id}: {image_path}")
        
            # Submit button
            if st.button("Submit Update"):
                try:
                    update_status(selected_id, new_status, image_path)
                    log_action(selected_id, officer_id, action_text)
                    st.success("✅ Complaint status updated successfully!")
                    logger.info(f"Complaint {selected_id} updated to status: {new_status} by {st.session_state.officer_name}")
                except Exception as e:
                    st.error(f"❌ Error updating complaint: {str(e)}")
                    logger.error(f"Error updating complaint {selected_id}: {str(e)}")

