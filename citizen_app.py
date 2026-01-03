import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection, insert_complaint
from classifier import classify_complaint
from priority import assign_priority_with_reasoning
import os
import logging

# Set up logging for zone assignment
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Zone Mapping for Bangalore Neighborhoods
ZONE_MAPPING = {
    "North": ["Hebbal", "Yelahanka", "RT Nagar", "Vidyaranyapura", "Sahakara Nagar", "Thanisandra"],
    "South": ["Jayanagar", "JP Nagar", "BTM Layout", "Banashankari", "HSR Layout", "Koramangala"],
    "East": ["Indiranagar", "Whitefield", "Marathahalli", "CV Raman Nagar", "Mahadevapura", "Varthur"],
    "West": ["Rajajinagar", "Malleshwaram", "Vijayanagar", "Basaveshwaranagar", "Kengeri", "Yeshwanthpur"]
}

def assign_zone(location):
    """
    Helper function to assign a zone to a given location/area.
    Searches through ZONE_MAPPING to find which zone the area belongs to.
    Case-insensitive matching with whitespace normalization.
    Returns the zone name (North/South/East/West) if found, otherwise returns 'Unknown'.
    Logs a warning if zone is 'Unknown' for tracking unmapped areas.
    """
    if not location or location.strip() == "":
        logger.warning("Empty location provided for zone assignment")
        return "Unknown"
    
    # Normalize input: strip whitespace and convert to lowercase for case-insensitive matching
    location_normalized = location.strip().lower()
    
    # Search through each zone's neighborhoods
    for zone, neighborhoods in ZONE_MAPPING.items():
        for neighborhood in neighborhoods:
            # Case-insensitive comparison
            if neighborhood.lower() == location_normalized:
                logger.info(f"Zone assigned: '{location.strip()}' -> {zone}")
                return zone
    
    # Log warning if area not found in mapping
    logger.warning(f"⚠️ Unknown area/neighborhood: '{location.strip()}' - Zone could not be determined. Please review mapping.")
    return "Unknown"

st.set_page_config(page_title="City Voice", page_icon="📝", layout="wide")
st.title("📝 City Voice - Submit a Complaint")

# Tabs for Submit, View, and Dashboard
tab1, tab2, tab3 = st.tabs(["📤 Submit Complaint", "📋 View My Complaints", "📊 Dashboard"])

with tab1:
    st.write("Help us improve the city by reporting issues!")
    
    with st.form("complaint_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            citizen_name = st.text_input("Your Name *")
            location = st.text_input("Location/Address *")
            email = st.text_input("Email (optional)")
        
        with col2:
            phone = st.text_input("Phone Number (optional)")
            st.write("**Note:** Category and Priority will be automatically detected using AI")
        
        complaint_text = st.text_area("Describe your complaint in detail *", height=150)
        
        submitted = st.form_submit_button("📤 Submit Complaint", use_container_width=True)
        
        if submitted:
            if not citizen_name or not location or not complaint_text:
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                st.info("🔄 Processing complaint through automated pipeline...")
                
                with st.spinner("⏳ Step 1/3: Analyzing complaint text..."):
                    try:
                        # ==========================================
                        # STEP 1: CATEGORIZATION
                        # ==========================================
                        logger.info(f"[STEP 1] Categorizing complaint from {citizen_name}")
                        category = classify_complaint(complaint_text)
                        logger.info(f"[STEP 1] ✅ Category assigned: {category}")
                        
                    except Exception as e:
                        logger.error(f"[STEP 1] ❌ Categorization failed: {str(e)}")
                        st.error(f"❌ Error during categorization: {str(e)}")
                        st.stop()
                
                with st.spinner("⏳ Step 2/3: Assessing priority level..."):
                    try:
                        # ==========================================
                        # STEP 2: PRIORITIZATION
                        # ==========================================
                        logger.info(f"[STEP 2] Prioritizing complaint from {citizen_name}")
                        priority_result = assign_priority_with_reasoning(complaint_text)
                        priority = priority_result["priority"]
                        priority_reasoning = priority_result["reasoning"]
                        logger.info(f"[STEP 2] ✅ Priority assigned: {priority}")
                        
                    except Exception as e:
                        logger.error(f"[STEP 2] ❌ Prioritization failed: {str(e)}")
                        st.error(f"❌ Error during prioritization: {str(e)}")
                        st.stop()
                
                with st.spinner("⏳ Step 3/3: Mapping to administrative zone..."):
                    try:
                        # ==========================================
                        # STEP 3: ZONE MAPPING
                        # ==========================================
                        logger.info(f"[STEP 3] Mapping zone for location: {location}")
                        zone = assign_zone(location)
                        logger.info(f"[STEP 3] ✅ Zone assigned: {zone}")
                        
                        # Log warning if zone is unknown
                        if zone == "Unknown":
                            logger.warning(f"⚠️ [STEP 3] Unknown area '{location}' - flagged for manual review")
                            st.warning(f"⚠️ Location '{location}' was not recognized in our system. It will be marked for manual review.")
                        
                    except Exception as e:
                        logger.error(f"[STEP 3] ❌ Zone mapping failed: {str(e)}")
                        st.error(f"❌ Error during zone mapping: {str(e)}")
                        st.stop()
                
                # ==========================================
                # SAVE TO DATABASE
                # ==========================================
                try:
                    logger.info(f"[SAVE] Storing complaint with all processed data...")
                    
                    complaint_id = insert_complaint(
                        name=citizen_name,
                        location=location,
                        original_text=complaint_text,
                        clean_text=complaint_text,
                        category=category,
                        priority=priority,
                        zone=zone,
                        ai_summary="Pending",
                        priority_reasoning=priority_reasoning,
                        is_ai_processed=False
                    )
                    
                    logger.info(f"[SAVE] ✅ Complaint #{complaint_id} successfully saved to database")
                    logger.info(f"[SAVE] Summary - Category: {category}, Priority: {priority}, Zone: {zone}")
                    
                except Exception as e:
                    logger.error(f"[SAVE] ❌ Database save failed: {str(e)}")
                    st.error(f"❌ Error saving complaint to database: {str(e)}")
                    st.stop()
                
                # ==========================================
                # CONFIRMATION PAGE
                # ==========================================
                st.success("✅ Complaint submitted successfully! Thank you {citizen_name}.")
                
                st.markdown("---")
                st.subheader("📋 Complaint Submission Summary")
                
                # Display in organized grid
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 👤 Your Details")
                    st.write(f"**Name:** {citizen_name}")
                    st.write(f"**Location:** {location}")
                    st.write(f"**Contact:** {email if email else phone if phone else 'Not provided'}")
                    st.write(f"**Complaint ID:** #{complaint_id}")
                
                with col2:
                    st.markdown("### 🤖 AI Analysis Results")
                    st.write(f"**Category:** 🏷️ {category}")
                    
                    # Color-code priority
                    if priority == "High":
                        st.write(f"**Priority:** :red[🔴 {priority}]")
                    elif priority == "Medium":
                        st.write(f"**Priority:** :orange[🟡 {priority}]")
                    else:
                        st.write(f"**Priority:** :green[🟢 {priority}]")
                    
                    st.write(f"**Zone:** 🗺️ {zone}")
                
                st.markdown("### 📝 Your Complaint")
                st.info(complaint_text)
                
                st.markdown("### 💭 AI Priority Assessment")
                st.write(priority_reasoning)
                
                st.markdown("---")
                st.success("📧 You will receive updates on your registered contact information.")
                st.info("💡 **Next Steps:** Our team in the **{zone}** zone will review your complaint and take necessary action. You can track your complaint status in the 'View My Complaints' tab.")
                
                st.balloons()

with tab2:
    st.write("Track your complaints here")
    
    search_name = st.text_input("Enter your name to view complaints")
    
    if search_name:
        try:
            conn = get_connection()
            if conn:
                query = f"SELECT complaint_id, citizen_name, location, category, priority, status, created_at FROM complaints WHERE citizen_name LIKE '%{search_name}%' ORDER BY created_at DESC"
                df = pd.read_sql(query, conn)
                conn.close()
                
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No complaints found for this name.")
            else:
                st.error("Database connection failed")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab3:
    st.write("View and analyze all citizen complaints submitted through the system.")
    
    # Fetch complaints from database
    def fetch_complaints():
        conn = get_connection()
        if conn:
            query = "SELECT complaint_id, citizen_name, location, category, priority, status, created_at FROM complaints"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        else:
            st.error("Failed to connect to the database.")
            return pd.DataFrame()
    
    df = fetch_complaints()
    # Replace missing values so dropdown works
    df['category'] = df['category'].fillna("Other")
    df['priority'] = df['priority'].fillna("Low")
    
    # Show raw table
    st.subheader("All Complaints")
    st.dataframe(df)
    
    # Filters
    st.subheader("Filter Complaints")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df["category"].unique()))
    
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(df["priority"].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]
    
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]
    
    st.write("### Filtered Results")
    st.dataframe(filtered_df)
    
    # Summary Metrics
    st.subheader("Complaint Summary")
    
    total_complaints = len(df)
    high_priority = len(df[df["priority"] == "High"])
    pending = len(df[df["status"] != "Resolved"])
    
    colA, colB, colC = st.columns(3)
    
    colA.metric("Total Complaints", total_complaints)
    colB.metric("High Priority Complaints", high_priority)
    colC.metric("Pending Complaints", pending)
    
    st.subheader("📊 Complaints by Category")
    
    if not df.empty:
        category_counts = df["category"].value_counts()
        
        fig, ax = plt.subplots()
        ax.bar(category_counts.index, category_counts.values)
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Complaints")
        ax.set_title("Complaints per Category")
        
        st.pyplot(fig)
    else:
        st.write("No data available.")
    
    st.subheader("🟡 Priority Distribution")
    
    if not df.empty:
        priority_counts = df["priority"].value_counts()
        
        fig2, ax2 = plt.subplots()
        ax2.pie(priority_counts.values, labels=priority_counts.index, autopct='%1.1f%%')
        ax2.set_title("Priority Breakdown")
        
        st.pyplot(fig2)
    else:
        st.write("No data available.")
    
    st.subheader("📈 Complaints Over Time")
    
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        timeline = df.groupby(df["created_at"].dt.date).size()
        
        fig3, ax3 = plt.subplots()
        ax3.plot(timeline.index, timeline.values, marker='o')
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Number of Complaints")
        ax3.set_title("Complaints Trend Over Time")
        
        st.pyplot(fig3)
    else:
        st.write("No data available.")

st.divider()
st.write("💡 **Tips:** Be specific about location, include details, and mention the impact on citizens.")
