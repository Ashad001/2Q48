import tensorflow as tf
import numpy as np
import pennylane as qml
import random


class QuantumDQNAgent:
    def __init__(
        self,
        n_qubits,
        n_actions,
        n_layers,
        batch_size=64,
        learning_rate=0.001,
        discount_factor=0.99,
        epsilon=1.0,
        epsilon_decay=0.995,
        min_epsilon=0.01,
    ):
        # Initialize hyperparameters and Q-network
        self.n_qubits = n_qubits  # Number of qubits
        self.state_size = (
            n_qubits  # State size is equal to the number of qubits (4 x 4 = 16)
        )

        self.action_size = n_actions  # Number of actions (moves: up, down, left, right)
        self.n_layers = n_layers  # Number of layers in the quantum circuit

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        self.action_map = {0: "w", 1: "a", 2: "s", 3: "d"}

        # Create the Q-network and target network
        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_model()

        # Initialize replay memory
        self.replay_memory = []
        self.batch_size = batch_size

    def build_model(self):
        # Quantum circuit model
        q_dev = qml.device("default.qubit", wires=self.n_qubits)

        @qml.qnode(q_dev)
        def quantum_circuit(inputs, weights):
            """Parameterized quantum circuit for Q-value prediction."""
            qml.AngleEmbedding(inputs, wires=range(self.n_qubits))
            qml.BasicEntanglerLayers(weights, wires=range(self.n_qubits))
            return [qml.expval(qml.PauliZ(wires=i)) for i in range(self.n_qubits)]

        weight_shapes = {"weights": (self.n_layers, self.state_size)}  # (layers, wires)
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(
                    shape=(self.state_size,)
                ),  # Input size = n_qubits = 16 tiles
                qml.qnn.KerasLayer(
                    quantum_circuit,
                    weight_shapes=weight_shapes, # 16 qubits, 3 layers
                    output_dim=self.n_qubits,
                ),
                tf.keras.layers.Dense(self.action_size, activation="linear"),
            ]
        )

        # Compile the model with an appropriate optimizer and loss function
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss="mse",
        )
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def choose_action(self, state):
        state_flat = np.array(state).flatten()  # Flatten the state
        if np.random.rand() <= self.epsilon:
            # Random action (exploration)
            return np.random.choice(self.action_size)
        else:
            # Choose action based on Q-values from the network (exploitation)
            q_values = self.model.predict(np.expand_dims(state_flat, axis=0))[0]
            print("Q-values", q_values)  
            return np.argmax(q_values)

    def replay(self):
        if len(self.replay_memory) < self.batch_size:
            return

        # Sample minibatch from replay memory
        minibatch = random.sample(self.replay_memory, self.batch_size)

        states = []
        targets = []
        for state, action, reward, next_state, done in minibatch:
            state_flat = np.array(state).flatten()  # Flatten the state
            next_state_flat = np.array(next_state).flatten()  # Flatten the next state

            target = reward
            if not done:
                # Calculate target using Double Q-Learning
                next_q_values = self.model.predict(
                    np.expand_dims(next_state_flat, axis=0)
                )[0]
                next_action = np.argmax(next_q_values)
                target = (
                    reward
                    + self.discount_factor
                    * self.target_model.predict(
                        np.expand_dims(next_state_flat, axis=0)
                    )[0][next_action]
                )

            # Get current Q-values
            target_full = self.model.predict(np.expand_dims(state_flat, axis=0))[0]
            target_full[action] = target  # Use the action index directly

            states.append(state_flat)
            targets.append(target_full)

        # Train the Q-network
        self.model.fit(np.array(states), np.array(targets), epochs=1, verbose=0)

        # Update target model periodically
        if len(self.replay_memory) % 1000 == 0:
            self.update_target_model()

        # Decay epsilon
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay

    def remember(self, state, action, reward, next_state, done):
        self.replay_memory.append((state, action, reward, next_state, done))

    def load(self, model_path):
        self.model.load_weights(model_path)
        self.update_target_model()

    def save(self, model_path):
        self.model.save_weights(model_path)
