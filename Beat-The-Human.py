import random
import streamlit as st  # Essential for Streamlit

# Initialize session state for persistent variables
if 'user_history' not in st.session_state:
    st.session_state.user_history = []
if 'games' not in st.session_state:
    st.session_state.games = 0
if 'wins' not in st.session_state:
    st.session_state.wins = {"user": 0, "computer": 0, "ties": 0}
if 'play_again' not in st.session_state:
    st.session_state.play_again = True

def get_counter_move(predicted_choice):
    """Return the move that beats the predicted choice."""
    if predicted_choice == "rock":
        return "paper"
    elif predicted_choice == "paper":
        return "scissors"
    elif predicted_choice == "scissors":
        return "rock"

def predict_user_choice(history):
    """Predict the user's next choice based on frequency."""
    if not history:  # No history yet
        return random.choice(["rock", "paper", "scissors"])
    
    # Count frequency of each choice
    frequency = {"rock": 0, "paper": 0, "scissors": 0}
    for choice in history:
        frequency[choice] += 1
    
    # Find the most frequent choice
    max_count = max(frequency.values())
    most_frequent = [choice for choice, count in frequency.items() if count == max_count]
    
    # If multiple choices tie for most frequent, pick one randomly
    return random.choice(most_frequent)

# Game setup
choices = ["rock", "paper", "scissors"]
user_history = st.session_state.user_history
games = st.session_state.games
wins = st.session_state.wins

st.write("Welcome to Adaptive Rock, Paper, Scissors!")  # Replace print
st.write("I’ll learn your patterns and try to beat you!")  # Replace print

# Only run game logic if user wants to play
if st.session_state.play_again:
    # Get user input (replaces input())
    player_choice = st.text_input("Enter your choice (rock, paper, scissors)", key=f"game_{games}").lower()
    
    if player_choice:  # Only proceed if user enters something
        while player_choice not in choices:
            st.write("Invalid choice. Please select one of the 3 options.")  # Replace print
            player_choice = st.text_input("Enter your choice (rock, paper, scissors)", key=f"retry_{games}").lower()
            if player_choice in choices:
                break  # Exit retry loop once valid

        # Add to history
        user_history.append(player_choice)
        games += 1

        # Predict user's next choice based on history and counter it
        predicted_choice = predict_user_choice(user_history)
        computer_choice = get_counter_move(predicted_choice)
        st.write("The computer chose " + computer_choice + " !")  # Replace print

        # Determine winner
        if player_choice == computer_choice:
            st.write("It's a tie!")  # Replace print
            wins["ties"] += 1
        elif (player_choice == "rock" and computer_choice == "scissors") or \
                (player_choice == "paper" and computer_choice == "rock") or \
                (player_choice == "scissors" and computer_choice == "paper"):
            st.write("You win!")  # Replace print
            wins["user"] += 1
        else:
            st.write("The computer wins!")  # Replace print
            wins["computer"] += 1

        # Show stats
        st.write(f"Games: {games}, User wins: {wins['user']}, Computer wins: {wins['computer']}, Ties: {wins['ties']}")  # Replace print

        # Update session state
        st.session_state.user_history = user_history
        st.session_state.games = games
        st.session_state.wins = wins

        # Ask to play again (replaces input())
        play_again = st.text_input("Play again? (y/n)", key=f"play_again_{games}").lower()
        if play_again == "n":
            st.session_state.play_again = False

# Final stats when game ends
if not st.session_state.play_again:
    st.write("\nFinal Stats:")  # Replace print
    st.write(f"Games played: {games}")  # Replace print
    st.write(f"User wins: {wins['user']} ({(wins['user'] / games) * 100:.1f}%)")  # Replace print
    st.write(f"Computer wins: {wins['computer']} ({(wins['computer'] / games) * 100:.1f}%)")  # Replace print
    st.write(f"Ties: {wins['ties']} ({(wins['ties'] / games) * 100:.1f}%)")  # Replace print
    st.write("Your choices:", user_history)  # Replace print
