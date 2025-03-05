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

# Initialize session state variables (necessary for Streamlit)
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
if 'play_submitted' not in st.session_state:
    st.session_state.play_submitted = False

# Game setup
choices = ["rock", "paper", "scissors"]

# Streamlit UI
st.title("Adaptive Rock, Paper, Scissors")  # Replacing initial print
st.write("I’ll learn your patterns and try to beat you!")  # Replacing initial print

if not st.session_state.game_over:
    # Get user input (replacing input with st.text_input)
    player_choice = st.text_input("Enter your choice (rock, paper, scissors):", "").lower()

    if st.button("Submit Choice"):  # Button to submit choice
        st.session_state.play_submitted = True
        if player_choice not in choices:
            st.error("Invalid choice. Please select one of the 3 options.")  # Replacing print
        else:
            # Add to history
            st.session_state.user_history.append(player_choice)
            st.session_state.games += 1

            # Predict user's next choice based on history and counter it
            predicted_choice = predict_user_choice(st.session_state.user_history)
            computer_choice = get_counter_move(predicted_choice)
            st.session_state.computer_history.append(computer_choice)
            st.write("The computer chose " + computer_choice + " !")  # Replacing print

            # Determine winner
            if player_choice == computer_choice:
                st.write("It's a tie!")  # Replacing print
                st.session_state.wins["ties"] += 1
            elif (player_choice == "rock" and computer_choice == "scissors") or \
                    (player_choice == "paper" and computer_choice == "rock") or \
                    (player_choice == "scissors" and computer_choice == "paper"):
                st.write("You win!")  # Replacing print
                st.session_state.wins["user"] += 1
            else:
                st.write("The computer wins!")  # Replacing print
                st.session_state.wins["computer"] += 1

            # Show stats
            st.write(f"Games: {st.session_state.games}, User wins: {st.session_state.wins['user']}, "
                    f"Computer wins: {st.session_state.wins['computer']}, Ties: {st.session_state.wins['ties']}")

    # Ask to play again with validation (only after first play)
    if st.session_state.play_submitted and st.session_state.games > 0:
        play_again = st.text_input("Play again? (yes/no):", "").lower()
        if st.button("Submit Play Again"):
            if play_again == "yes":
                st.session_state.play_submitted = False  # Reset for next round
            elif play_again == "no":
                st.session_state.game_over = True  # Replace exit() with flag
            else:
                st.error("Invalid choice, please enter 'yes' or 'no': ")  # Replacing print

if st.session_state.game_over:
    st.write("\nFinal Stats:")  # Replacing print
    st.write(f"Games played: {st.session_state.games}")
    st.write(f"User wins: {st.session_state.wins['user']} "
            f"({(st.session_state.wins['user'] / st.session_state.games) * 100:.1f}%)")
    st.write(f"Computer wins: {st.session_state.wins['computer']} "
            f"({(st.session_state.wins['computer'] / st.session_state.games) * 100:.1f}%)")
    st.write(f"Ties: {st.session_state.wins['ties']} "
            f"({(st.session_state.wins['ties'] / st.session_state.games) * 100:.1f}%)")
    st.write("Your choices:", st.session_state.user_history)
    st.write("System's choices:", st.session_state.computer_history)

    # Add reset option (Streamlit-specific addition)
    if st.button("Start New Game"):
        st.session_state.user_history = []
        st.session_state.computer_history = []
        st.session_state.games = 0
        st.session_state.wins = {"user": 0, "computer": 0, "ties": 0}
        st.session_state.game_over = False
        st.session_state.play_submitted = False
