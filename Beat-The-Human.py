import random
import streamlit as st

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

# Initialize session state variables
if 'user_history' not in st.session_state:
    st.session_state.user_history = []
if 'computer_history' not in st.session_state:
    st.session_state.computer_history = []
if 'games' not in st.session_state:
    st.session_state.games = 0
if 'wins' not in st.session_state:
    st.session_state.wins = {"user": 0, "computer": 0, "ties": 0}
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# Game setup
choices = ["rock", "paper", "scissors"]

# Streamlit UI
st.title("Adaptive Rock, Paper, Scissors")
st.write("I’ll learn your patterns and try to beat you!")

if not st.session_state.game_over:
    # User choice input
    player_choice = st.text_input("Enter your choice (rock, paper, scissors):", "").lower()

    if st.button("Play"):
        if player_choice not in choices:
            st.error("Invalid choice. Please enter 'rock', 'paper', or 'scissors'.")
        else:
            # Add to history
            st.session_state.user_history.append(player_choice)
            st.session_state.games += 1

            # Predict and counter
            predicted_choice = predict_user_choice(st.session_state.user_history)
            computer_choice = get_counter_move(predicted_choice)
            st.session_state.computer_history.append(computer_choice)

            # Display computer choice
            st.write(f"The computer chose {computer_choice}!")

            # Determine winner
            if player_choice == computer_choice:
                st.write("It's a tie!")
                st.session_state.wins["ties"] += 1
            elif (player_choice == "rock" and computer_choice == "scissors") or \
                 (player_choice == "paper" and computer_choice == "rock") or \
                 (player_choice == "scissors" and computer_choice == "paper"):
                st.write("You win!")
                st.session_state.wins["user"] += 1
            else:
                st.write("The computer wins!")
                st.session_state.wins["computer"] += 1

            # Show current stats
            st.write(f"Games: {st.session_state.games}, User wins: {st.session_state.wins['user']}, "
                    f"Computer wins: {st.session_state.wins['computer']}, Ties: {st.session_state.wins['ties']}")

    # Play again or end game
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Play Again"):
            st.session_state.game_over = False  # Reset to keep playing
    with col2:
        if st.button("End Game"):
            st.session_state.game_over = True

else:
    # Display final stats when game is over
    st.write("\nFinal Stats:")
    st.write(f"Games played: {st.session_state.games}")
    st.write(f"User wins: {st.session_state.wins['user']} "
            f"({(st.session_state.wins['user'] / st.session_state.games) * 100:.1f}%)")
    st.write(f"Computer wins: {st.session_state.wins['computer']} "
            f"({(st.session_state.wins['computer'] / st.session_state.games) * 100:.1f}%)")
    st.write(f"Ties: {st.session_state.wins['ties']} "
            f"({(st.session_state.wins['ties'] / st.session_state.games) * 100:.1f}%)")
    st.write("Your choices:", st.session_state.user_history)
    st.write("System's choices:", st.session_state.computer_history)

    # Reset game option
    if st.button("Start New Game"):
        # Reset all session state variables
        st.session_state.user_history = []
        st.session_state.computer_history = []
        st.session_state.games = 0
        st.session_state.wins = {"user": 0, "computer": 0, "ties": 0}
        st.session_state.game_over = False
