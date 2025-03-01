import streamlit as st
import random

st.title("Welcome to Rock, Paper, Scissors!")

choices = ["rock", "paper", "scissors"]

# Initialize session state variables
if "player_choice" not in st.session_state:
    st.session_state.player_choice = None
if "computer_choice" not in st.session_state:
    st.session_state.computer_choice = None
if "game_result" not in st.session_state:
    st.session_state.game_result = None

# Player choice
player_choice = st.selectbox("Enter your choice:", choices)

# Play button
if st.button("Play"):
    st.session_state.player_choice = player_choice
    st.session_state.computer_choice = random.choices(choices, weights=[0.4, 0.35, 0.25], k=1)[0]

    # Determine winner
    if st.session_state.player_choice == st.session_state.computer_choice:
        st.session_state.game_result = "🤝 It's a tie!"
    elif (st.session_state.player_choice == "rock" and st.session_state.computer_choice == "scissors") or \
         (st.session_state.player_choice == "paper" and st.session_state.computer_choice == "rock") or \
         (st.session_state.player_choice == "scissors" and st.session_state.computer_choice == "paper"):
        st.session_state.game_result = "🎉 You win!"
    else:
        st.session_state.game_result = "😞 The computer won!"

# Display results
if st.session_state.computer_choice:
    st.write(f"The computer chose **{st.session_state.computer_choice}**!")
    st.write(st.session_state.game_result)

# Play again button
if st.session_state.computer_choice:
    if st.button("Play Again"):
        st.session_state.player_choice = None
        st.session_state.computer_choice = None
        st.session_state.game_result = None
        st.experimental_rerun()
