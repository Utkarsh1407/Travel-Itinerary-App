import streamlit as st
import requests

backend = "http://localhost:8000"  # Change for deployment

st.title("🌍 Travel Itinerary Planner")

country = st.text_input("Country:")
city = st.text_input("City:")
duration = st.number_input("Duration (days):", min_value=1)
budget = st.number_input("Budget (INR):", min_value=100)

if st.button("Get Popular Places"):
    r = requests.post(f"{backend}/top-places", json={
        "country": country,
        "city": city,
        "duration": duration,
        "budget": budget
    }).json()
    st.session_state.places = r["places"]
    st.write(r["places"])

if st.button("Generate Itinerary"):
    r = requests.post(f"{backend}/itinerary", json={
        "country": country,
        "city": city,
        "duration": duration,
        "budget": budget
    }).json()
    st.write(r["itinerary"])

query = st.text_input("Ask something:")
if query:
    r = requests.post(f"{backend}/ask", json={
        "country": country,
        "city": city,
        "duration": duration,
        "budget": budget,
        "question": query
    }).json()
    st.write(r["answer"])
