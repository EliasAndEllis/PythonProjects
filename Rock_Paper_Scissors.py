import streamlit as st
import random

st.title("Welcome to Rock, Paper, Scissors!")

choices = ["rock", "paper", "scissors"]

# Game state
if "play_again" not in st.session_state:
    st.session_state.play_again = True

while st.session_state.play_again:
    player_choice = st.selectbox("Enter your choice:", choices)

    computer_choice = random.choices(choices, weights=[0.4, 0.35, 0.25], k=1)[0]
    st.write(f"The computer chose **{computer_choice}**!")

    if player_choice == computer_choice:
        st.write("🤝 It's a tie!")
    elif (player_choice == "rock" and computer_choice == "scissors") or \
         (player_choice == "paper" and computer_choice == "rock") or \
         (player_choice == "scissors" and computer_choice == "paper"):
        st.write("🎉 You win!")
    else:
        st.write("😞 The computer won!")

    # Play again option
    play_again = st.radio("Play again?", ["Yes", "No"])

    if play_again == "No":
        st.session_state.play_again = False
        st.write("Thanks for playing! 🎮")
    else:
        st.experimental_rerun()
