import streamlit as st
from save_complaint import process_and_save

st.title("CityVoice – Citizen Complaint Submission")

st.write("Please fill in the details below to submit your complaint.")

# Form UI
with st.form("complaint_form"):
    name = st.text_input("Your Name")
    location = st.text_input("Location / Area")
    complaint_text = st.text_area("Describe your complaint")

    submit_button = st.form_submit_button("Submit Complaint")

# When the button is clicked
if submit_button:
    if name and location and complaint_text:
        process_and_save(name, location, complaint_text)
        st.success("Your complaint has been submitted successfully!")
    else:
        st.error("Please fill all fields before submitting.")
