import random

print("Welcome to Rock, Paper, Scissors!")

choices = ["rock", "paper", "scissors"]

while True:  # Loop to allow replay
    player_choice = input("Enter your choice (rock, paper, scissors): ").lower()

    # Loop until the player enters a valid choice
    while player_choice not in choices:
        print("Invalid choice. Please select one of the 3 options.")
        player_choice = input("Enter your choice (rock, paper, scissors): ").lower()

    computer_choice = random.choices(choices, weights=[0.4, 0.35, 0.25], k=1)[0]
    print("The computer chose " + computer_choice + " !")

    if player_choice == computer_choice:
         print("it's a tie!")
    elif (player_choice == "rock" and computer_choice == "scissors") or \
         (player_choice == "paper" and computer_choice == "rock") or \
         (player_choice == "scissors" and computer_choice == "paper"):
         print("You win !")
    else:
         print("The computer won !")

         # Ask to play again
    play_again = input("Play again? (y/n): ").lower()
    if play_again != "y":
        break  # Exit the loop if user doesn't want to continue

print("Thanks for playing!")
