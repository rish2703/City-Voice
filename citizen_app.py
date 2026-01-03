import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection, insert_complaint
from classifier import classify_complaint
from priority import assign_priority_with_reasoning
import os

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
                with st.spinner("🤖 Analyzing complaint with AI..."):
                    try:
                        # Call AI to auto-categorize and prioritize
                        category = classify_complaint(complaint_text)
                        priority_result = assign_priority_with_reasoning(complaint_text)
                        priority = priority_result["priority"]
                        priority_reasoning = priority_result["reasoning"]
                        
                        # Insert complaint into database
                        insert_complaint(
                            name=citizen_name,
                            location=location,
                            original_text=complaint_text,
                            clean_text=complaint_text,
                            category=category,
                            priority=priority,
                            ai_summary="Pending",
                            priority_reasoning=priority_reasoning,
                            is_ai_processed=False
                        )
                        
                        st.success(f"✅ Complaint submitted successfully! Thank you {citizen_name}.")
                        st.info(f"🏷️ **Auto-detected Category:** {category}\n\n⚡ **Priority Level:** {priority}\n\n💭 **Reasoning:** {priority_reasoning}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

with tab2:
    st.write("Track your complaints here")
    
    search_name = st.text_input("Enter your name to view complaints")
    
    if search_name:
        try:
            conn = get_connection()
            if conn:
                query = f"SELECT complaint_id, citizen_name, location, category, priority, status, submitted_at FROM complaints WHERE citizen_name LIKE '%{search_name}%' ORDER BY submitted_at DESC"
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
