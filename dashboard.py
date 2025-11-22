import streamlit as st
import matplotlib.pyplot as plt

import pandas as pd
from db import get_connection

st.title("📊 CityVoice Dashboard")

st.write("View and analyze all citizen complaints submitted through the system.")

# 1. Fetch complaints from database
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

# 2. Filters
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


# 3. Summary Metrics
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
