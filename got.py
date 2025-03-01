from PIL import Image
import requests  # To fetch the image from a URL
from io import BytesIO  # To handle the image data in memory

# Define dictionaries for male and female terms
male_terms = {"male", "man", "boy", "gentleman", "baby boy"}
female_terms = {"female", "woman", "girl", "lady", "baby girl"}

# Ask user for gender
gender = input("Are you male or female? ").lower()
if gender in male_terms:
    name = input("What's thy name m'lord? ")
elif gender in female_terms:
    name = input("What's thy name m'lady? ")
# Infant is neither male nor female
elif gender == "infant":
    name = input("What's thy name infant? ")
# If user input is something else
else:
    name = input(gender.title() + " isn't human! What's thy name Earthling? ")

# Check if user is a GOT fan and respond based on name and gender
real_got_fan = input("Valar Morghulis; ").lower()

# URL of the online image (example: a Game of Thrones-related image)
boy_image = "https://github.com/EliasAndEllis/shmy/blob/main/9ltija.jpg?raw=true"  # Replace with a real U
girl_image = "https://github.com/EliasAndEllis/shmy/blob/main/download.jpg?raw=true"  # Replace with a real U
failed_image = "https://github.com/EliasAndEllis/shmy/blob/main/9ltiog.jpg?raw=true"  # Replace with a real U
infant_image = "https://raw.githubusercontent.com/EliasAndEllis/shmy/refs/heads/main/9ltjhq.jpg"  # Replace with a real U

if real_got_fan == "valar dohaeris" and gender in male_terms:
    print("A boy is truly no one!")
    # Fetch the image from the URL
    response = requests.get(boy_image)
    img = Image.open(BytesIO(response.content))  # Open image from memory
    img.show()  # Display the image
    exit()
elif real_got_fan == "valar dohaeris" and gender in female_terms:
    print("A girl is truly no one!")
    # Fetch the image from the URL
    response = requests.get(girl_image)
    img = Image.open(BytesIO(response.content))  # Open image from memory
    img.show()  # Display the image
    exit()
elif real_got_fan == "valar dohaeris" and gender == "infant":
    print("The infant is a bastard snow!")
    # Fetch the image from the URL
    response = requests.get(infant_image)
    img = Image.open(BytesIO(response.content))  # Open image from memory
    img.show()  # Display the image
    exit()
else:
    print("You need to watch GAME OF THRONES " + name.title() + "!")
    # Fetch the image from the URL
    response = requests.get(failed_image)
    img = Image.open(BytesIO(response.content))  # Open image from memory
    img.show()  # Display the image
    exit()
