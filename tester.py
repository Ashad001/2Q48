import numpy as np
import tensorflow as tf
from grid import Grid
from QDQN import QuantumDQNAgent # From https://github.com/DineshDhanji/2Q48/blob/master/QDQN.py
import time

# Hyperparameters
n_qubits = 16  # Number of qubits (state space size)
n_actions = 4  # 'w', 'a', 's', 'd'
n_layers = 3
batch_size = 32
episode_num = 14  # Last episode number from checkpoints/

# Initialize the environment and agent
env = Grid(size=4)
agent = QuantumDQNAgent(
    n_qubits=n_qubits, n_actions=n_actions, n_layers=n_layers, batch_size=batch_size
)

# Load the trained model
model_path = f"./checkpoints/qdqn_weights_{episode_num}.keras"  # Provide the path to your saved model
agent.load(model_path)

# Test the agent by playing the game
state = env.reset()  # Reset the environment to get the initial state
done = False
total_reward = 0

# Exploration parameters
stuck = False  # Flag to check if the agent is stuck in a loop
move = -1  # No previous move initially
count = 0  # Counter for the number of times the same action is repeated
action = 0

# Play the game by interacting with the environment
while not done:
    state_flat = np.array(state).flatten()
    q_values = agent.model.predict(np.expand_dims(state_flat, axis=0))[0]

    # Take the action in the environment
    next_state, reward, done = env.step(agent.action_map[action])
    state = next_state  # Update state with the next state
    total_reward += reward  # Update total reward

    # Action selection (exploitation by default)
    if stuck:
        # If stuck, take a random action for exploration
        action = np.random.choice(n_actions)
        print("Agent is stuck! Taking random action.")
        stuck = False  # Reset stuck flag
    else:
        # Otherwise, take the action with the highest Q-value (exploitation)
        q_values = q_values * (1 - done) - 1e9 * done + reward  # Mask Q-values of terminal states
        action = np.argmax(q_values)

    # Log Q-values and action taken
    print(f"Q-values: {q_values}")
    print(f"Action taken: {action}")
    # Optionally render the environment to see the progress
    env.render()

    # Detect if the agent is stuck in a loop (i.e., repeating the same action multiple times)
    if action == move:
        count += 1
    else:
        move = action
        count = 0
    if count >= 3:  # If the agent repeats the same action  times, it's stuck
        stuck = True
        count = 0  # Reset counter for stuck detection

    # Pause for better visual inspection (optional)
    # time.sleep(0.1)  # Optional: adds a small delay for rendering to be visible

    if done:
        print(f"Game Over! Total Reward: {total_reward}")
        time.sleep(5)  
        

# Print the final result
