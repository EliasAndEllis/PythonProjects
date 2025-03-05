import random
import streamlit as st
import time

# Initialize session state
if 'user_history' not in st.session_state:
    st.session_state.user_history = []
if 'games' not in st.session_state:
    st.session_state.games = 0
if 'wins' not in st.session_state:
    st.session_state.wins = {"user": 0, "computer": 0, "ties": 0}
if 'play_again' not in st.session_state:
    st.session_state.play_again = True
if 'player_choice' not in st.session_state:  # Fixed typo: 'not_in' → 'not in'
    st.session_state.player_choice = None

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
    if not history:
        return random.choice(["rock", "paper", "scissors"])
    frequency = {"rock": 0, "paper": 0, "scissors": 0}
    for choice in history:
        frequency[choice] += 1
    max_count = max(frequency.values())
    most_frequent = [choice for choice, count in frequency.items() if count == max_count]
    return random.choice(most_frequent)

# Game setup
choices = ["rock", "paper", "scissors"]
user_history = st.session_state.user_history
games = st.session_state.games
wins = st.session_state.wins

# Custom CSS with your requested styles
st.markdown("""
    <style>
    .title {
        font-size: 79.2px;  /* 120% larger than 36px (36 * 2.2) */
        color: #FF6347;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }
    .subtitle {
        font-size: 36px;  /* 80% larger than 20px (20 * 1.8) */
        color: #FFFFFF;   /* White */
        text-align: center;
        font-style: italic;
    }
    .result {
        font-size: 24px;
        color: #32CD32;   /* Original green */
        font-weight: bold;
    }
    .stats {
        font-size: 18px;
        color: #1DA1F2;   /* Twitter blue */
        font-weight: bold;
    }
    .choice-button {
        font-size: 18px;
        padding: 10px 20px;
        margin: 5px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        background-color: #4682B4;
        color: white;
        transition: background-color 0.3s ease;
    }
    .choice-button:hover {
        background-color: #FF4500;
    }
    </style>
""", unsafe_allow_html=True)

# HTML-styled content
st.markdown('<p class="title">Welcome to Adaptive Rock, Paper, Scissors!</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">I’ll learn your patterns and try to beat you!</p>', unsafe_allow_html=True)

if st.session_state.play_again:
    # Button selection for choices
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Rock", key=f"rock_{games}"):
            st.session_state.player_choice = "rock"
    with col2:
        if st.button("Paper", key=f"paper_{games}"):
            st.session_state.player_choice = "paper"
    with col3:
        if st.button("Scissors", key=f"scissors_{games}"):
            st.session_state.player_choice = "scissors"
    st.markdown("</div>", unsafe_allow_html=True)

    # Process choice with a seamless loading effect
    if st.session_state.player_choice:
        with st.spinner("Processing your move..."):
            time.sleep(1)
            player_choice = st.session_state.player_choice
            user_history.append(player_choice)
            games += 1
            predicted_choice = predict_user_choice(user_history)
            computer_choice = get_counter_move(predicted_choice)
            st.markdown(f'<p class="result">The computer chose {computer_choice}!</p>', unsafe_allow_html=True)

            if player_choice == computer_choice:
                st.markdown('<p class="result">It\'s a tie!</p>', unsafe_allow_html=True)
                wins["ties"] += 1
            elif (player_choice == "rock" and computer_choice == "scissors") or \
                    (player_choice == "paper" and computer_choice == "rock") or \
                    (player_choice == "scissors" and computer_choice == "paper"):
                st.markdown('<p class="result">You win!</p>', unsafe_allow_html=True)
                wins["user"] += 1
            else:
                st.markdown('<p class="result">The computer wins!</p>', unsafe_allow_html=True)
                wins["computer"] += 1

            st.markdown(f'<p class="stats">Games: {games}, User wins: {wins["user"]}, Computer wins: {wins["computer"]}, Ties: {wins["ties"]}</p>', unsafe_allow_html=True)

            st.session_state.user_history = user_history
            st.session_state.games = games
            st.session_state.wins = wins
            st.session_state.player_choice = None

            # Play again buttons
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("Play Again", key=f"play_again_{games}"):
                st.session_state.play_again = True
            if st.button("End Game", key=f"end_{games}"):
                st.session_state.play_again = False
            st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.play_again:
    st.markdown('<p class="title">Final Stats:</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stats">Games played: {games}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stats">User wins: {wins["user"]} ({(wins["user"] / games) * 100:.1f}%)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stats">Computer wins: {wins["computer"]} ({(wins["computer"] / games) * 100:.1f}%)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stats">Ties: {wins["ties"]} ({(wins["ties"] / games) * 100:.1f}%)</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="stats">Your choices: {user_history}</p>', unsafe_allow_html=True)
