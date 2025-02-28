# app.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image

# Define dictionaries for male and female terms
male_terms = {"male", "man", "boy", "gentleman", "baby boy"}
female_terms = {"female", "woman", "girl", "lady", "baby girl"}

# URLs of the online images
boy_image = "https://github.com/EliasAndEllis/shmy/blob/main/9ltija.jpg?raw=true"
girl_image = "https://github.com/EliasAndEllis/shmy/blob/main/download.jpg?raw=true"
failed_image = "https://github.com/EliasAndEllis/shmy/blob/main/9ltiog.jpg?raw=true"
infant_image = "https://raw.githubusercontent.com/EliasAndEllis/shmy/refs/heads/main/9ltjhq.jpg"

# Streamlit UI
st.title("Game of Thrones Greeting")

# Gender input
gender = st.text_input("Are you male or female?", key="gender").lower()

if gender:
    if gender in male_terms:
        name = st.text_input("What's thy name m'lord?", key="name")
    elif gender in female_terms:
        name = st.text_input("What's thy name m'lady?", key="name")
    elif gender == "infant":
        name = st.text_input("What's thy name infant?", key="name")
    else:
        name = st.text_input(f"{gender.title()} isn't human! What's thy name Earthling?", key="name")

    if name:
        real_got_fan = st.text_input("Valar Morghulis;", key="got").lower()

        if real_got_fan:
            if real_got_fan == "valar dohaeris" and gender in male_terms:
                st.write("A boy is truly no one!")
                response = requests.get(boy_image)
                img = Image.open(BytesIO(response.content))
                st.image(img)
            elif real_got_fan == "valar dohaeris" and gender in female_terms:
                st.write("A girl is truly no one!")
                response = requests.get(girl_image)
                img = Image.open(BytesIO(response.content))
                st.image(img)
            elif real_got_fan == "valar dohaeris" and gender == "infant":
                st.write("The infant is a bastard snow!")
                response = requests.get(infant_image)
                img = Image.open(BytesIO(response.content))
                st.image(img)
            else:
                st.write(f"You need to watch GAME OF THRONES {name.title()}!")
                response = requests.get(failed_image)
                img = Image.open(BytesIO(response.content))
                st.image(img)
