import os
import numpy as np
import tensorflow as tf
from grid import Grid
from utils.logger import *

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Logger setup
episode_logger = get_logger("episodes_run", see_time=True)
action_logger = get_logger("actions_run", see_time=False)
reward_logger = get_logger("rewards_run", see_time=False)

class DQNAgent:
    def __init__(self, size, state_size, action_size):
        self.size = size
        self.state_size = state_size
        self.action_size = action_size
        self.model = self._build_model()
        self.env = Grid(size)

        # Logging initialization
        log_message("DQNAgent initialized for running", episode_logger)

    def _build_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(128, input_dim=self.state_size, activation='relu'))
        model.add(tf.keras.layers.Dense(128, activation='relu'))
        model.add(tf.keras.layers.Dense(self.action_size, activation='linear'))
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mse')

        log_message("Model built for running", episode_logger)
        return model

    def act(self, state):
        act_values = self.model.predict(state)
        action = np.argmax(act_values[0])
        log_message(f"Action predicted: {action}", action_logger)
        return action

    def load(self, name):
        self.model.load_weights(name)
        log_message(f"Model weights loaded from {name}", episode_logger)

    def run(self, episodes):
        for e in range(episodes):
            state = np.reshape(self.env.reset(), [1, self.state_size])
            done = False
            total_reward = 0
            time_step = 0
            while not done:
                action = self.act(state)
                next_state, reward, done = self.env.step(action)
                total_reward += reward
                next_state = np.reshape(next_state, [1, self.state_size])
                state = next_state
                
                self.env.render()

                if done:
                    log_message(f"Episode {e + 1}/{episodes} finished with score {self.env.score} and reward {total_reward}", episode_logger)
                    reward_logger.info(f"Episode {e + 1}, Reward: {total_reward}")
                    break

                time_step += 1

if __name__ == "__main__":
    size = 4
    state_size = size * size
    action_size = 4  # Up, Down, Left, Right
    episodes = 10
    agent = DQNAgent(size, state_size, action_size)
    
    # Load the pre-trained model weights
    agent.load("model.weights.h5")
    
    # Run the environment using the pre-trained model
    agent.run(episodes)
