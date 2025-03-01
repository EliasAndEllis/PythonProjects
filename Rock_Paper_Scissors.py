import streamlit as st
import random

# Title of the game
st.title("Rock, Paper, Scissors Game 🤖")

# Choices
choices = ["rock", "paper", "scissors"]

# Custom weights for computer choice
weights = [0.4, 0.35, 0.25]

# Player selection
player_choice = st.radio("Choose your move:", choices)

# Play button
if st.button("Play"):
    computer_choice = random.choices(choices, weights=weights, k=1)[0]
    st.write(f"🤖 The computer chose: **{computer_choice}**")

    # Determine winner
    if player_choice == computer_choice:
        st.success("It's a tie! 😐")
    elif (player_choice == "rock" and computer_choice == "scissors") or \
         (player_choice == "paper" and computer_choice == "rock") or \
         (player_choice == "scissors" and computer_choice == "paper"):
        st.success("🎉 You win!")
    else:
        st.error("😞 The computer won!")

# Play Again button (Optional)
st.button("Reset")
