import streamlit as st
import pandas as pd
import os
from PIL import Image

from db import get_connection, update_status, log_action

st.title("🛠 Complaint Management Panel")

st.write("Select a complaint below and update its status, assign officer, or upload proof photo.")

# Fetch complaints
def fetch_complaints():
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM complaints", conn)
        conn.close()
        return df
    return pd.DataFrame()

df = fetch_complaints()

# Show complaint list
st.subheader("All Complaints")
st.dataframe(df)

# Status choices
status_options = ["New", "Acknowledged", "Assigned", "In Progress", "Resolved", "Closed"]

# Select complaint ID
complaint_ids = df["complaint_id"].tolist()
selected_id = st.selectbox("Select Complaint ID to Update", complaint_ids)

if selected_id:
    selected_row = df[df["complaint_id"] == selected_id].iloc[0]

    st.write("### Complaint Details")
    st.write(f"**Name:** {selected_row['citizen_name']}")
    st.write(f"**Location:** {selected_row['location']}")
    st.write(f"**Category:** {selected_row['category']}")
    st.write(f"**Priority:** {selected_row['priority']}")
    st.write(f"**Current Status:** {selected_row['status']}")
    st.write(f"**Complaint Text:** {selected_row['complaint_text']}")

    # New status
    new_status = st.selectbox("Update Status", status_options)

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

    # Submit button
    if st.button("Submit Update"):
        update_status(selected_id, new_status, image_path)
        log_action(selected_id, officer_id, action_text)
        st.success("Complaint status updated successfully!")
